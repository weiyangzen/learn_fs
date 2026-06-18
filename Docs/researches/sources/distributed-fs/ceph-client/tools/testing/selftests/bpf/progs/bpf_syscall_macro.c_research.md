<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_syscall_macro.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_syscall_macro.c

## Purpose

Syscall tracing selftest for architecture-specific PT_REGS and BPF_KSYSCALL argument extraction macros.

## Important APIs, Types, and Functions

- BPF sections: `ksyscall/prctl`, `ksyscall/splice`, `license`
- Important functions/callbacks: `BPF_KPROBE`, `BPF_KSYSCALL`
- BPF helpers/kfunc-like calls: `bpf_get_current_pid_tgid`, `bpf_probe_read_kernel`
- Mutable globals/test result fields: `arg1`, `arg2`, `arg3`, `arg4_cx`, `arg4`, `arg5`, `arg1_core`, `arg2_core`, `arg3_core`, `arg4_core_cx`, `arg4_core`, `arg5_core`, `option_syscall`, `arg2_syscall`, `arg3_syscall`, `arg4_syscall`, and 8 more

## Control Flow and Data Flow

Kprobe and ksyscall programs filter on `filter_pid`, then copy raw syscall argument registers and CO-RE macro-decoded arguments into globals for comparison.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `arg1`, `arg2`, `arg3`, `arg4_cx`, `arg4`, `arg5`, `arg1_core`, `arg2_core`, `arg3_core`, `arg4_core_cx`, `arg4_core`, `arg5_core`, `option_syscall`, `arg2_syscall`, `arg3_syscall`, `arg4_syscall`, `arg5_syscall`, `filter_pid`, `splice_fd_in`, `splice_off_in`, and 4 more

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_core_read.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_current_pid_tgid`, `bpf_probe_read_kernel`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `arg1`, `arg2`, `arg3`, `arg4_cx`, `arg4`, `arg5`, `arg1_core`, `arg2_core` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_syscall_macro.c -->
