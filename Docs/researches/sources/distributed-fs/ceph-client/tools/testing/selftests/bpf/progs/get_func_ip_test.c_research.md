<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_test.c

## Purpose
`get_func_ip_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2232 bytes across 105 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_fentry_test1`, `bpf_get_func_ip`, `bpf_modify_return_test`.
Attach sections and exported entry points:
- line 6 `SEC("license")` -> extern int bpf_fentry_test1(int a) __ksym;
- line 26 `SEC("fentry/bpf_fentry_test1")` -> int BPF_PROG(test1, int a)
- line 36 `SEC("fexit/bpf_fentry_test2")` -> int BPF_PROG(test2, int a)
- line 46 `SEC("kprobe/bpf_fentry_test3")` -> int test3(struct pt_regs *ctx)
- line 56 `SEC("kretprobe/bpf_fentry_test4")` -> int BPF_KRETPROBE(test4)
- line 66 `SEC("fmod_ret/bpf_modify_return_test")` -> int BPF_PROG(test5, int a, int *b, int ret)
- line 76 `SEC("?kprobe")` -> int test6(struct pt_regs *ctx)
- line 88 `SEC("uprobe//proc/self/exe:uprobe_trigger")` -> int BPF_UPROBE(test7)
- line 98 `SEC("uretprobe//proc/self/exe:uprobe_trigger")` -> int BPF_URETPROBE(test8, int ret)
Key functions/subprograms:
- line 20 `unused`: `int unused(void)`
- line 27 `BPF_PROG`: `int BPF_PROG(test1, int a)`
- line 37 `BPF_PROG`: `int BPF_PROG(test2, int a)`
- line 47 `test3`: `int test3(struct pt_regs *ctx)`
- line 57 `BPF_KRETPROBE`: `int BPF_KRETPROBE(test4)`
- line 67 `BPF_PROG`: `int BPF_PROG(test5, int a, int *b, int ret)`
- line 77 `test6`: `int test6(struct pt_regs *ctx)`
- line 89 `BPF_UPROBE`: `int BPF_UPROBE(test7)`
- line 99 `BPF_URETPROBE`: `int BPF_URETPROBE(test8, int ret)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_fentry_test1`, `fexit/bpf_fentry_test2`, `kprobe/bpf_fentry_test3`, `kretprobe/bpf_fentry_test4`, `fmod_ret/bpf_modify_return_test`, `?kprobe`, `uprobe//proc/self/exe:uprobe_trigger` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `unused`, `BPF_PROG`, `BPF_PROG`, `test3`, `BPF_KRETPROBE`, `BPF_PROG`, `test6`, `BPF_UPROBE` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 25 `__u64 test1_result = 0;`
- line 35 `__u64 test2_result = 0;`
- line 45 `__u64 test3_result = 0;`
- line 55 `__u64 test4_result = 0;`
- line 65 `__u64 test5_result = 0;`
- line 75 `__u64 test6_result = 0;`
- line 87 `__u64 test7_result = 0;`
- line 97 `__u64 test8_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_test.c -->
