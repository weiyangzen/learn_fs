<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/inner_array_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/inner_array_lookup.c

## Purpose
`inner_array_lookup.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 802 bytes across 45 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_map_lookup_elem`.
Map/type declarations observed:
- line 7 declares map type `BPF_MAP_TYPE_ARRAY`
- line 14 declares map type `BPF_MAP_TYPE_HASH_OF_MAPS`
Attach sections and exported entry points:
- line 11 `SEC(".maps")` -> struct outer_map {
- line 18 `SEC(".maps")` -> .values = {
- line 24 `SEC("raw_tp/sys_enter")` -> int handle__sys_enter(void *ctx)
- line 45 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 25 `handle__sys_enter`: `int handle__sys_enter(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `.maps`, `raw_tp/sys_enter`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `handle__sys_enter`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 27 `int outer_key = 2, inner_key = 3;`
- line 28 `int *val;`
- line 29 `void *map;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/inner_array_lookup.c -->
