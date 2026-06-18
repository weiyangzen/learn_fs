<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_modify.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_modify.c

## Purpose
`for_each_hash_modify.c` is a bpf_for_each_map_elem callback-iteration selftest. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 597 bytes across 30 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map lookup/update/delete or map-side state; map-element callback iteration.
- Helper/kfunc calls: `bpf_for_each_map_elem`, `bpf_map_delete_elem`, `bpf_map_update_elem`.
Map/type declarations observed:
- line 9 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct {
- line 13 `SEC(".maps")` -> static int cb(struct bpf_map *map, __u64 *key, __u64 *val, void *arg)
- line 22 `SEC("tc")` -> int test_pkt_access(struct __sk_buff *skb)
Key functions/subprograms:
- line 15 `cb`: `static int cb(struct bpf_map *map, __u64 *key, __u64 *val, void *arg)`
- line 23 `test_pkt_access`: `int test_pkt_access(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `cb`, `test_pkt_access`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_modify.c -->
