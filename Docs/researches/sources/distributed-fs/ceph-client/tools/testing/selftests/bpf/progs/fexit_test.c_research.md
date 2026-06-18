<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_test.c

## Purpose
`fexit_test.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1748 bytes across 80 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1, int a, int ret)
- line 10 `SEC("fexit/bpf_fentry_test1")` -> int BPF_PROG(test1, int a, int ret)
- line 18 `SEC("fexit/bpf_fentry_test2")` -> int BPF_PROG(test2, int a, __u64 b, int ret)
- line 26 `SEC("fexit/bpf_fentry_test3")` -> int BPF_PROG(test3, char a, int b, __u64 c, int ret)
- line 34 `SEC("fexit/bpf_fentry_test4")` -> int BPF_PROG(test4, void *a, char b, int c, __u64 d, int ret)
- line 43 `SEC("fexit/bpf_fentry_test5")` -> int BPF_PROG(test5, __u64 a, void *b, short c, int d, __u64 e, int ret)
- line 52 `SEC("fexit/bpf_fentry_test6")` -> int BPF_PROG(test6, __u64 a, void *b, short c, int d, void *e, __u64 f, int ret)
- line 65 `SEC("fexit/bpf_fentry_test7")` -> int BPF_PROG(test7, struct bpf_fentry_test_t *arg)
- line 74 `SEC("fexit/bpf_fentry_test8")` -> int BPF_PROG(test8, struct bpf_fentry_test_t *arg)
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1, int a, int ret)`
- line 19 `BPF_PROG`: `int BPF_PROG(test2, int a, __u64 b, int ret)`
- line 27 `BPF_PROG`: `int BPF_PROG(test3, char a, int b, __u64 c, int ret)`
- line 35 `BPF_PROG`: `int BPF_PROG(test4, void *a, char b, int c, __u64 d, int ret)`
- line 44 `BPF_PROG`: `int BPF_PROG(test5, __u64 a, void *b, short c, int d, __u64 e, int ret)`
- line 53 `BPF_PROG`: `int BPF_PROG(test6, __u64 a, void *b, short c, int d, void *e, __u64 f, int ret)`
- line 66 `BPF_PROG`: `int BPF_PROG(test7, struct bpf_fentry_test_t *arg)`
- line 75 `BPF_PROG`: `int BPF_PROG(test8, struct bpf_fentry_test_t *arg)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fexit/bpf_fentry_test1`, `fexit/bpf_fentry_test2`, `fexit/bpf_fentry_test3`, `fexit/bpf_fentry_test4`, `fexit/bpf_fentry_test5`, `fexit/bpf_fentry_test6`, `fexit/bpf_fentry_test7` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 17 `__u64 test2_result = 0;`
- line 25 `__u64 test3_result = 0;`
- line 33 `__u64 test4_result = 0;`
- line 42 `__u64 test5_result = 0;`
- line 51 `__u64 test6_result = 0;`
- line 64 `__u64 test7_result = 0;`
- line 73 `__u64 test8_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_test.c -->
