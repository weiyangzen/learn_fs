<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_reloc_types.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_reloc_types.h

## Purpose
`core_reloc_types.h` is a CO-RE fixture header defining source and target BTF shapes for field, enum, type-id, and type-based relocations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 27717 bytes across 1363 lines.

## Important APIs, Types, and Functions
- Dependencies: `<stdint.h>`, `<stdbool.h>`.
- Important macros/constants: `__bpf_aligned`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Key functions/subprograms:
- line 4 `preserce_ptr_sz_fn`: `void preserce_ptr_sz_fn(long x) {}`
- Header fixture content: 0 struct/union/enum/typedef markers provide BTF type material for consumers.

## Control Flow
There is no direct BPF attach entry in this file. Control flow is compile-time inclusion: other objects consume its declarations/macros/types so that clang, BTF generation, libbpf CO-RE relocation, or the verifier sees the intended shapes.
Local flow is organized through `preserce_ptr_sz_fn`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `int valid[10];`
- line 15 `int comm_len;`
- line 16 `bool local_task_struct_matches;`
- line 24 `long long len;`
- line 25 `long long off;`
- line 26 `int read_ctx_sz;`
- line 27 `bool read_ctx_exists;`
- line 28 `bool buf_exists;`
- line 29 `bool len_exists;`
- line 30 `bool off_exists;`
- plus 248 more entries of the same pattern.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Signal is compile/load-time BTF or declaration availability for other selftest objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_reloc_types.h -->
