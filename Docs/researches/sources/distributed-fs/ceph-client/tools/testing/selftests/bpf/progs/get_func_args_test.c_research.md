<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_test.c

## Purpose
`get_func_args_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3750 bytes across 167 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<errno.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_func_arg`, `bpf_get_func_arg_cnt`, `bpf_get_func_ret`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1)
- line 10 `SEC("fentry/bpf_fentry_test1")` -> int BPF_PROG(test1)
- line 43 `SEC("fexit/bpf_fentry_test2")` -> int BPF_PROG(test2)
- line 70 `SEC("fmod_ret/bpf_modify_return_test")` -> int BPF_PROG(fmod_ret_test, int _a, int *_b, int _ret)
- line 99 `SEC("fexit/bpf_modify_return_test")` -> int BPF_PROG(fexit_test, int _a, int *_b, int _ret)
- line 126 `SEC("tp_btf/bpf_testmod_fentry_test1_tp")` -> int BPF_PROG(tp_test1)
- line 146 `SEC("tp_btf/bpf_testmod_fentry_test2_tp")` -> int BPF_PROG(tp_test2)
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1)`
- line 44 `BPF_PROG`: `int BPF_PROG(test2)`
- line 71 `BPF_PROG`: `int BPF_PROG(fmod_ret_test, int _a, int *_b, int _ret)`
- line 100 `BPF_PROG`: `int BPF_PROG(fexit_test, int _a, int *_b, int _ret)`
- line 127 `BPF_PROG`: `int BPF_PROG(tp_test1)`
- line 147 `BPF_PROG`: `int BPF_PROG(tp_test2)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_fentry_test1`, `fexit/bpf_fentry_test2`, `fmod_ret/bpf_modify_return_test`, `fexit/bpf_modify_return_test`, `tp_btf/bpf_testmod_fentry_test1_tp`, `tp_btf/bpf_testmod_fentry_test2_tp`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 14 `__u64 a = 0, z = 0, ret = 0;`
- line 15 `__s64 err;`
- line 42 `__u64 test2_result = 0;`
- line 47 `__u64 a = 0, b = 0, z = 0, ret = 0;`
- line 48 `__s64 err;`
- line 69 `__u64 test3_result = 0;`
- line 74 `__u64 a = 0, b = 0, z = 0, ret = 0;`
- line 75 `__s64 err;`
- line 98 `__u64 test4_result = 0;`
- plus 8 more entries of the same pattern.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_test.c -->
