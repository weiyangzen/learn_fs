<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf.c

## Purpose
`fexit_bpf2bpf.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4285 bytes across 179 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/stddef.h>`, `<linux/if_ether.h>`, `<linux/ipv6.h>`, `<linux/bpf.h>`, `<linux/tcp.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_probe_read_kernel`, `bpf_prog_test_load`, `bpf_skb_load_bytes`.
Attach sections and exported entry points:
- line 17 `SEC("fexit/test_pkt_access")` -> int BPF_PROG(test_main, struct sk_buff *skb, int ret)
- line 32 `SEC("fexit/test_pkt_access_subprog1")` -> int BPF_PROG(test_subprog1, struct sk_buff *skb, int ret)
- line 65 `SEC("fexit/test_pkt_access_subprog2")` -> int test_subprog2(struct args_subprog2 *ctx)
- line 89 `SEC("fexit/test_pkt_access_subprog3")` -> int BPF_PROG(test_subprog3, int val, struct sk_buff *skb, int ret)
- line 104 `SEC("freplace/get_skb_len")` -> int new_get_skb_len(struct __sk_buff *skb)
- line 116 `SEC("freplace/get_skb_ifindex")` -> int new_get_skb_ifindex(int val, struct __sk_buff *skb, int var)
- line 146 `SEC("freplace/get_constant")` -> int new_get_constant(long val)
- line 156 `SEC("freplace/test_pkt_write_access_subprog")` -> int new_test_pkt_write_access_subprog(struct __sk_buff *skb, __u32 off)
- line 179 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 18 `BPF_PROG`: `int BPF_PROG(test_main, struct sk_buff *skb, int ret)`
- line 33 `BPF_PROG`: `int BPF_PROG(test_subprog1, struct sk_buff *skb, int ret)`
- line 66 `test_subprog2`: `int test_subprog2(struct args_subprog2 *ctx)`
- line 90 `BPF_PROG`: `int BPF_PROG(test_subprog3, int val, struct sk_buff *skb, int ret)`
- line 105 `new_get_skb_len`: `int new_get_skb_len(struct __sk_buff *skb)`
- line 117 `new_get_skb_ifindex`: `int new_get_skb_ifindex(int val, struct __sk_buff *skb, int var)`
- line 147 `new_get_constant`: `int new_get_constant(long val)`
- line 157 `new_test_pkt_write_access_subprog`: `int new_test_pkt_write_access_subprog(struct __sk_buff *skb, __u32 off)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `fexit/test_pkt_access`, `fexit/test_pkt_access_subprog1`, `fexit/test_pkt_access_subprog2`, `fexit/test_pkt_access_subprog3`, `freplace/get_skb_len`, `freplace/get_skb_ifindex`, `freplace/get_constant`, `freplace/test_pkt_write_access_subprog` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `test_subprog2`, `BPF_PROG`, `new_get_skb_len`, `new_get_skb_ifindex`, `new_get_constant`, `new_test_pkt_write_access_subprog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `__u64 test_result = 0;`
- line 20 `int len;`
- line 31 `__u64 test_result_subprog1 = 0;`
- line 35 `int len;`
- line 61 `__u64 args[5];`
- line 62 `__u64 ret;`
- line 64 `__u64 test_result_subprog2 = 0;`
- line 69 `__u64 ret;`
- line 70 `int len;`
- line 88 `__u64 test_result_subprog3 = 0;`
- plus 7 more entries of the same pattern.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf.c -->
