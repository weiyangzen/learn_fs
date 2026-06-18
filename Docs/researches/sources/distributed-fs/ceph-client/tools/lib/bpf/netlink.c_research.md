<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/netlink.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/netlink.c

## Purpose
This file implements libbpf's rtnetlink and generic-netlink support for XDP program attach/detach/query and TC qdisc/filter hook management.

## APIs, Types, and Functions
Public APIs are `bpf_xdp_attach()`, `bpf_xdp_detach()`, `bpf_xdp_query()`, `bpf_xdp_query_id()`, `bpf_tc_hook_create()`, `bpf_tc_hook_destroy()`, `bpf_tc_attach()`, `bpf_tc_detach()`, and `bpf_tc_query()`. Netlink helpers include `libbpf_netlink_open()`, `libbpf_netlink_close()`, `netlink_recvmsg()`, `alloc_iov()`, `libbpf_netlink_recv()`, `libbpf_netlink_send_recv()`, `parse_genl_family_id()`, and `libbpf_netlink_resolve_genl_family_id()`. XDP helpers include `__bpf_set_link_xdp_fd_replace()`, `__dump_link_nlmsg()`, `get_xdp_info()`, and `parse_xdp_features()`. TC helpers include `clsact_config()`, `qdisc_config()`, `attach_point_to_config()`, `tc_get_tcm_parent()`, `tc_qdisc_modify()`, `tc_qdisc_create_excl()`, `tc_qdisc_delete()`, `__bpf_tc_detach()`, `__get_tc_info()`, `get_tc_info()`, and `tc_add_fd_and_name()`.

## Control Flow, State, and Persistence
`libbpf_netlink_send_recv()` opens a netlink socket with `NETLINK_EXT_ACK`, binds to discover the local netlink PID, stamps the request with a time-based sequence, sends the request, and dispatches replies through `libbpf_netlink_recv()`. The receive loop peeks with `MSG_TRUNC` to size the buffer, reallocates as needed, validates PID and sequence, handles multipart responses, reports kernel extack strings through `libbpf_nla_dump_errormsg()`, and calls parser callbacks until continue/next/done.

XDP attach builds `RTM_SETLINK` with nested `IFLA_XDP` attributes for FD, flags, and optional expected old FD when replacement is requested. Detach is attach with FD `-1`. Query sends `RTM_GETLINK`, parses `IFLA_XDP` nested attributes into program IDs and attach mode, then optionally resolves the generic-netlink `netdev` family and queries feature flags plus zero-copy max segments. `bpf_xdp_query_id()` selects one program ID based on requested mode and attach mode.

TC hook creation/deletion maps ingress/egress to `clsact` qdisc or uses an explicit qdisc for `BPF_TC_QDISC`. TC attach validates hook/options, builds `RTM_NEWTFILTER` with BPF kind and nested options containing the program FD, generated name from `bpf_prog_get_info_by_fd()`, and direct-action flag, requests echo, and parses returned handle/priority/program ID. TC detach builds `RTM_DELTFILTER`, either flushing for hook destroy or deleting a specific handle/priority. TC query builds `RTM_GETTFILTER` and parses BPF filter info.

State is mostly stack-local request/response metadata. Persistent kernel state is changed by XDP attaches/detaches and TC qdisc/filter create/delete operations. Output state is written into option structs through `OPTS_SET()`.

## Dependencies and Integration
The implementation depends on Linux rtnetlink, generic netlink, netdev, pkt_cls, BPF, Ethernet protocol constants, sockets, time, local `bpf.h`, `libbpf.h`, `libbpf_internal.h`, and `nlattr.h`. It integrates public libbpf networking APIs with kernel route and generic netlink subsystems and uses `bpf_prog_get_info_by_fd()` to name TC filters.

## Risks and Test Signals
Risks include time-based sequence collisions across concurrent requests, strict PID/sequence validation rejecting unexpected multicast/unicast replies, kernel feature differences for `NETLINK_EXT_ACK` and `netdev` generic family, fixed `libbpf_nla_req` buffer size causing `-EMSGSIZE`, invalid XDP flag combinations, TC attach-point parent validation, cleanup behavior when qdisc/filter operations partially fail, and required privileges for network configuration. Test signals should include netlink unit tests for malformed responses, XDP attach/replace/detach/query on a test interface, query fallback when `netdev` family is absent, TC clsact create/attach/query/detach/destroy, custom qdisc validation, extack logging, and option-size compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/netlink.c -->
