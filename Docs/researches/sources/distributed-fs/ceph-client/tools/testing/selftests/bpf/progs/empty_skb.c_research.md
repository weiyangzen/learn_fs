<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/empty_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/empty_skb.c

## Purpose
`empty_skb.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 817 bytes across 44 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_clone_redirect`, `bpf_skb_adjust_room`.
Attach sections and exported entry points:
- line 6 `SEC("license")` -> int ifindex;
- line 11 `SEC("lwt_xmit")` -> int redirect_ingress(struct __sk_buff *skb)
- line 18 `SEC("lwt_xmit")` -> int redirect_egress(struct __sk_buff *skb)
- line 25 `SEC("tc")` -> int tc_redirect_ingress(struct __sk_buff *skb)
- line 32 `SEC("tc")` -> int tc_redirect_egress(struct __sk_buff *skb)
- line 39 `SEC("tc")` -> int tc_adjust_room(struct __sk_buff *skb)
Key functions/subprograms:
- line 12 `redirect_ingress`: `int redirect_ingress(struct __sk_buff *skb)`
- line 19 `redirect_egress`: `int redirect_egress(struct __sk_buff *skb)`
- line 26 `tc_redirect_ingress`: `int tc_redirect_ingress(struct __sk_buff *skb)`
- line 33 `tc_redirect_egress`: `int tc_redirect_egress(struct __sk_buff *skb)`
- line 40 `tc_adjust_room`: `int tc_adjust_room(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `lwt_xmit`, `lwt_xmit`, `tc`, `tc`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `redirect_ingress`, `redirect_egress`, `tc_redirect_ingress`, `tc_redirect_egress`, `tc_adjust_room`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 8 `int ifindex;`
- line 9 `int ret;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/empty_skb.c -->
