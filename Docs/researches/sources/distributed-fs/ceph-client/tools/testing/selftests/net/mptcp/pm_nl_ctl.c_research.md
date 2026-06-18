# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/pm_nl_ctl.c

## Purpose
`pm_nl_ctl.c` is the in-tree command-line client for the MPTCP path-manager generic-netlink API used by the selftests. It can add/delete/get/dump/flush endpoint tables, set/get limits, set endpoint flags, send userspace-PM announce/remove/create-subflow/destroy-subflow commands, listen on an MPTCP socket, and stream PM multicast events in a parseable text format.

## Important APIs, Types, And Functions
The utility uses `NETLINK_GENERIC`, generic netlink controller commands, `linux/mptcp.h`, nested route attributes, and MPTCP PM commands such as `MPTCP_PM_CMD_ADD_ADDR`, `GET_ADDR`, `DEL_ADDR`, `SET_LIMITS`, `SET_FLAGS`, `ANNOUNCE`, `REMOVE`, `SUBFLOW_CREATE`, and `SUBFLOW_DESTROY`. Core functions are `init_genl_req()`, `nl_error()`, `do_nl_req()`, `resolve_mptcp_pm_netlink()`, `genl_parse_getfamily()`, `capture_events()`, `add_addr()`, `del_addr()`, `get_addr()`, `dump_addrs()`, `flush_addrs()`, `get_set_limits()`, `set_flags()`, `announce_addr()`, `remove_addr()`, `csf()`, `dsf()`, `add_listener()`, and `main()`.

## Control Flow
`main()` opens a generic netlink socket, resolves the MPTCP PM family id and event multicast group through `CTRL_CMD_GETFAMILY`, then dispatches on the first subcommand. Request builders manually append netlink attributes into a 1 KiB stack buffer after the generic-netlink header. Endpoint commands create nested `MPTCP_PM_ATTR_ADDR` attributes with family, IPv4/IPv6 address, id, flags, port, and interface index. Userspace PM commands additionally carry connection tokens and remote-address nests. Dump/get responses are parsed and printed in stable selftest-oriented lines. `events` joins the PM event multicast group and loops forever printing `type`, token, family, addresses, ports, ids, errors, backup, and server-side flags to stderr.

## State, Persistence, And Dependencies
The program has no persistent state. Kernel-visible state changes occur through the path-manager endpoint table or active MPTCP connections identified by token. `listen` creates a blocking MPTCP listener and pauses until killed. Dependencies are Linux generic netlink, MPTCP UAPI headers, interface index resolution, and privileges sufficient for PM netlink operations in the target namespace.

## Integration Points
Shell tests call this utility through `ip netns exec <ns> ./pm_nl_ctl ...`. `mptcp_lib.sh` wraps it behind `mptcp_lib_pm_nl_*` helpers, while `mptcp_join.sh`, `pm_netlink.sh`, and `userspace_pm.sh` depend on its exact output and event text. It is also the userspace-PM control path for creating/destroying subflows by token.

## Risks
All netlink messages are hand-built in fixed-size buffers, so adding attributes can risk overflow if not checked. Some numeric fields are parsed with `atoi()` and copied in host byte order to match current UAPI expectations; invalid inputs generally call `error(1, ...)`. Output format is part of the selftest contract and brittle. The event loop never exits on its own and must be killed by callers. The custom `unknown` flag is intentionally selftest-only.

## Test Signals
For command mode, success is zero exit and expected stdout or no error ACK. `nl_error()` prints kernel extack messages and exits on failure. For event mode, useful signals are lines containing expected event types and attributes consumed by `mptcp_lib_evts_get_info()` and event-count checks. For `listen`, creation/closure events and successful subflow connections are the observable outcomes.
