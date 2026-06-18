# sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/ovs-dpctl.py

## Purpose
`ovs-dpctl.py` is a Python generic-netlink control utility for the kernel Open vSwitch datapath. It is used by `openvswitch.sh` to create/delete datapaths, add/delete vports, add/dump/delete flows, receive upcalls, and print psample events without depending on the full userspace Open vSwitch tool stack.

## Important APIs, types, and functions
- Generic-netlink family constants cover `ovs_datapath`, `ovs_vport`, `ovs_flow`, `ovs_packet`, and `psample` usage.
- Parsing helpers (`intparse`, `parse_flags`, `parse_ct_state`, `convert_mac`, `convert_ipv4`, `convert_ipv6`, `parse_attrs`) translate dpctl-like strings into netlink attributes.
- `ovs_dp_msg` extends `genlmsg` with `dpifindex`, matching OVS generic-netlink message headers.
- `ovsactions` defines `OVS_ACTION_ATTR_*` layouts and parsers/formatters for output, recirc, ct/nat, clone, set/set_masked, trunc, drop, userspace, sample, and psample actions.
- `ovskey` defines `OVS_KEY_ATTR_*` flow key layouts and parsers/formatters for ports, Ethernet, IPv4/IPv6, ARP, TCP/UDP/SCTP, ICMP, CT state/zone/mark, recirc, dp hash, skb mark, and tunnel metadata.
- `OvsPacket` listens for `OVS_PACKET_CMD_MISS`, `ACTION`, and `EXECUTE` upcalls and dispatches to an `OvsFlow` handler.
- `OvsDatapath` wraps datapath `GET/NEW/DEL`; `OvsVport` wraps vport `GET/NEW/SET/DEL`; `OvsFlow` wraps flow `NEW/DEL/GET` and upcall formatting.
- `PsampleEvent` binds the `psample` multicast group and prints sample rate, group, cookie, and packet data.
- `main` exposes subcommands: `show`, `add-dp`, `del-dp`, `add-if`, `del-if`, `dump-flows`, `add-flow`, `del-flows`, and `psample-events`.

## Control flow
Startup imports pyroute2 and exits with a clear message if missing or too old. `main` registers custom `ovskey` and `ovsactions` atoms with pyroute2, parses command-line arguments, constructs socket helpers, and dispatches by subcommand. Add/show/delete operations perform an OVS datapath lookup before vport or flow operations. `add-flow` parses the user flow and action strings into nested NLAs, then sends `OVS_FLOW_CMD_NEW`. Upcall modes keep the process in a blocking netlink receive loop and print decoded MISS/ACTION events.

## State and persistence
The script itself persists no files. Its durable effects are kernel datapaths, vports, flows, tunnel links created through pyroute2 `IPRoute`, and live netlink sockets. For `add-if -u` and `add-dp -u`, the process stays alive to keep upcall sockets registered; killing that process changes kernel upcall delivery state.

## Dependencies and integration points
It depends on `pyroute2 >= 0.6`, Python `ipaddress`, generic netlink, the Open vSwitch kernel module, and netlink UAPI compatibility. `openvswitch.sh` shells out to it for all datapath operations, and several tests grep its upcall/psample textual output. Tunnel vport creation integrates with kernel lightweight tunnel devices through `pyroute2.iproute.IPRoute` when `--lwt` is enabled.

## Risks and edge cases
The parser supports only the flow/action subset implemented in this file; unsupported OVS syntax raises `ValueError`. Some parsing code assumes delimiters exist and can index past an empty string for malformed input. Long clone recursion requires a high recursion limit. Several default arguments instantiate sockets at definition time (`OvsPacket()`, `NDB()`, `OvsVport()`), which is acceptable for the selftest but can surprise reuse. Kernel and pyroute2 NLA map drift is a primary compatibility risk.

## Test signals
Functional signals come from `openvswitch.sh`: datapaths show expected ports, flow dumps expose counters and actions, unsafe flow additions fail, upcall handlers print decoded `MISS upcall` and `userspace action command`, and `psample-events` prints expected rate/group/cookie/data lines.
