<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_exit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_exit.c

## Purpose
`epilogue_exit.c` is a struct_ops epilogue selftest covering return-value handling through direct calls, subprograms, or tail calls. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1940 bytes across 82 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"../test_kmods/bpf_testmod.h"`, `"../test_kmods/bpf_testmod_kfunc.h"`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_kfunc_st_ops_test_epilogue`.
Attach sections and exported entry points:
- line 10 `SEC("license")` -> /* save __u64 *ctx to stack */
- line 42 `SEC("struct_ops/test_epilogue_exit")` -> {
- line 61 `SEC(".struct_ops.link")` -> struct bpf_testmod_st_ops epilogue_exit = {
- line 66 `SEC("syscall")` -> int syscall_epilogue_exit0(void *ctx)
- line 75 `SEC("syscall")` -> int syscall_epilogue_exit1(void *ctx)
Key functions/subprograms:
- line 43 `test_epilogue_exit`: `__naked int test_epilogue_exit(void)`
- line 45 `volatile`: `asm volatile (`
- line 68 `syscall_epilogue_exit0`: `int syscall_epilogue_exit0(void *ctx)`
- line 77 `syscall_epilogue_exit1`: `int syscall_epilogue_exit1(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops/test_epilogue_exit`, `.struct_ops.link`, `syscall`, `syscall`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_epilogue_exit`, `volatile`, `syscall_epilogue_exit0`, `syscall_epilogue_exit1`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Uses `__success` annotations; a passing test is successful verifier load despite nearby edge cases.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_exit.c -->
