<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.h -->
# sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.h

## Purpose
Generated header declaring MPTCP path-manager Generic Netlink policies, ops table, and command callback prototypes.

## Important APIs, Types, and Functions
Declares external policy arrays for each PM command and `mptcp_pm_nl_ops[11]`. It also declares doit/dump callbacks such as `mptcp_pm_nl_add_addr_doit()`, `mptcp_pm_nl_del_addr_doit()`, `mptcp_pm_nl_get_addr_dumpit()`, `mptcp_pm_nl_set_limits_doit()`, `mptcp_pm_nl_set_flags_doit()`, and userspace PM announce/remove/subflow operations.

## Control Flow
The header has no runtime flow; it is a compile-time contract between generated netlink metadata and callback implementations.

## State and Persistence
No state is stored. It declares static objects defined in `mptcp_pm_gen.c` and functions defined elsewhere.

## Dependencies and Integration Points
Depends on netlink, genetlink, and MPTCP PM UAPI headers. Included by `mptcp_pm_gen.c` and PM implementation files that need generated policy and prototype declarations.

## Risks
The array size and prototypes must stay in sync with generated C and callback implementations. Manual edits can break YNL regeneration or genl family registration. Include order must provide `struct sk_buff`, `struct genl_info`, and `struct netlink_callback`.

## Test Signals
Compile coverage after YNL regeneration, all PM commands linking successfully, and no prototype mismatch warnings with callback implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.h -->
