# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.h

Purpose: public declarations and data structures for the netlink helper implementation.

Important APIs/types/functions: declares `struct rtnl_handle`, handle flags, `NLMSG_TAIL`, `nl_ext_ack_fn_t`, `rtnl_open`, `rtnl_close`, `rtnl_talk`, and all attribute append helpers. `rtnl_open` and `rtnl_talk` are marked `warn_unused_result` to push callers to check failures.

Control flow: header only; it shapes caller behavior through prototypes and macros.

State and persistence behavior: `struct rtnl_handle` stores socket FD, local/peer addresses, sequence/dump counters, protocol, optional dump file pointer, and flags. The header owns no state itself.

Dependencies and integration points: includes `linux/netlink.h` and `linux/rtnetlink.h`; consumed by BPF selftest code that needs rtnetlink request construction.

Risks: exposes low-level mutable fields, so callers can desynchronize sequence/protocol state if they modify the struct incorrectly. `NLMSG_TAIL` assumes `nlmsg_len` is valid and aligned enough for appending.

Test signals: indirect; callers check helper return values and resulting kernel netlink responses.
