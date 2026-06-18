<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_cls_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_cls_redirect.c

## Purpose
`freplace_cls_redirect.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 722 bytes across 34 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/stddef.h>`, `<linux/bpf.h>`, `<linux/pkt_cls.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_sk_release`.
Map/type declarations observed:
- line 11 declares map type `BPF_MAP_TYPE_SOCKMAP`
Attach sections and exported entry points:
- line 15 `SEC(".maps")` -> int freplace_cls_redirect_test(struct __sk_buff *skb)
- line 17 `SEC("freplace/cls_redirect")` -> int freplace_cls_redirect_test(struct __sk_buff *skb)
- line 34 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 18 `freplace_cls_redirect_test`: `int freplace_cls_redirect_test(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `freplace/cls_redirect`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `freplace_cls_redirect_test`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 20 `int ret = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_cls_redirect.c -->
