<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_many_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_many_args.c

## Purpose
`fentry_many_args.c` is an fentry tracing selftest validating typed argument capture and recursion behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1176 bytes across 39 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,
- line 10 `SEC("fentry/bpf_testmod_fentry_test7")` -> int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,
- line 20 `SEC("fentry/bpf_testmod_fentry_test11")` -> int BPF_PROG(test2, __u64 a, void *b, short c, int d, void *e, char f,
- line 31 `SEC("fentry/bpf_testmod_fentry_test11")` -> int BPF_PROG(test3, __u64 a, __u64 b, __u64 c, __u64 d, __u64 e, __u64 f,
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,`
- line 21 `BPF_PROG`: `int BPF_PROG(test2, __u64 a, void *b, short c, int d, void *e, char f,`
- line 32 `BPF_PROG`: `int BPF_PROG(test3, __u64 a, __u64 b, __u64 c, __u64 d, __u64 e, __u64 f,`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_testmod_fentry_test7`, `fentry/bpf_testmod_fentry_test11`, `fentry/bpf_testmod_fentry_test11`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 19 `__u64 test2_result = 0;`
- line 30 `__u64 test3_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_many_args.c -->
