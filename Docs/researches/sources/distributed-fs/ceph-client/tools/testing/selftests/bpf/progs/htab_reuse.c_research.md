<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_reuse.c

## Purpose
`htab_reuse.c` is a hash-map selftest or benchmark covering lookup, update, delete, reuse, or memory pressure behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 775 bytes across 35 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- Important macros/constants: `HTAB_NDATA`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Map/type declarations observed:
- line 14 declares map type `BPF_MAP_TYPE_HASH`
- line 30 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct htab_val {
- line 19 `SEC(".maps")` -> #define HTAB_NDATA 256
- line 35 `SEC(".maps")` -> next declaration

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 25 `__u32 seq;`
- line 26 `__u64 data[HTAB_NDATA];`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_reuse.c -->
