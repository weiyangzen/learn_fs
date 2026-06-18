<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_tailcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_tailcall.c

## Purpose
`epilogue_tailcall.c` is a struct_ops epilogue selftest covering return-value handling through direct calls, subprograms, or tail calls. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1323 bytes across 58 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"../test_kmods/bpf_testmod.h"`, `"../test_kmods/bpf_testmod_kfunc.h"`.
- BPF API surface: program-array dispatch.
- Helper/kfunc calls: `bpf_kfunc_st_ops_test_epilogue`, `bpf_tail_call`.
Map/type declarations observed:
- line 26 declares map type `BPF_MAP_TYPE_PROG_ARRAY`
Attach sections and exported entry points:
- line 10 `SEC("license")` -> static __noinline __used int subprog(struct st_ops_args *args)
- line 18 `SEC("struct_ops/test_epilogue_subprog")` -> int BPF_PROG(test_epilogue_subprog, struct st_ops_args *args)
- line 31 `SEC(".maps")` -> .values = {
- line 37 `SEC("struct_ops/test_epilogue_tailcall")` -> int test_epilogue_tailcall(unsigned long long *ctx)
- line 44 `SEC(".struct_ops.link")` -> struct bpf_testmod_st_ops epilogue_tailcall = {
- line 49 `SEC(".struct_ops.link")` -> struct bpf_testmod_st_ops epilogue_subprog = {
- line 54 `SEC("syscall")` -> int syscall_epilogue_tailcall(struct st_ops_args *args)
Key functions/subprograms:
- line 12 `subprog`: `static __noinline __used int subprog(struct st_ops_args *args)`
- line 19 `BPF_PROG`: `int BPF_PROG(test_epilogue_subprog, struct st_ops_args *args)`
- line 38 `test_epilogue_tailcall`: `int test_epilogue_tailcall(unsigned long long *ctx)`
- line 55 `syscall_epilogue_tailcall`: `int syscall_epilogue_tailcall(struct st_ops_args *args)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops/test_epilogue_subprog`, `.maps`, `struct_ops/test_epilogue_tailcall`, `.struct_ops.link`, `.struct_ops.link`, `syscall`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `subprog`, `BPF_PROG`, `test_epilogue_tailcall`, `syscall_epilogue_tailcall`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_tailcall.c -->
