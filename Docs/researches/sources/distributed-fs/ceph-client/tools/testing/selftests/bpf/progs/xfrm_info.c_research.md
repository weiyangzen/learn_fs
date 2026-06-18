<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xfrm_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xfrm_info.c

## Purpose
This tc program tests BPF kfuncs for setting and retrieving XFRM metadata on skb contexts.

## Important APIs, Types, and Functions
It declares local `struct bpf_xfrm_info___local` with `if_id` and `link`, globals `req_if_id` and `resp_if_id`, and kfuncs `bpf_skb_set_xfrm_info` and `bpf_skb_get_xfrm_info`. Entry points are `set_xfrm_info` and `get_xfrm_info`.

## Control Flow
`set_xfrm_info` creates an info struct from `req_if_id`, calls the set kfunc, and returns `TC_ACT_SHOT` on failure or `TC_ACT_UNSPEC` on success. `get_xfrm_info` calls the get kfunc, drops on failure, stores returned `if_id` in `resp_if_id`, and otherwise leaves packet processing unspecified.

## State and Persistence
BSS globals persist requested and observed interface IDs for userspace assertions. XFRM metadata is attached to or read from the packet context.

## Dependencies and Integration Points
The file depends on BTF kfunc availability, tc program context, `bpf_tracing_net.h`, and XFRM-enabled kernel support. Userspace tests configure globals and inspect `resp_if_id`.

## Risks
Kfuncs are configuration and kernel-version dependent. The local struct must stay compatible with the kernel BTF layout under preserve-access-index expectations.

## Test Signals
Successful set/get should return `TC_ACT_UNSPEC` and copy the expected interface ID into `resp_if_id`; kfunc failures produce `TC_ACT_SHOT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xfrm_info.c -->
