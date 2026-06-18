# sources/distributed-fs/ceph-client/arch/um/os-Linux/start_up.c

## Purpose
Runs early host capability checks before UML kernel boot, selecting seccomp or ptrace userspace mode and validating required host features.

## Important APIs, Types, and Functions
`check_ptrace()` verifies syscall-number rewriting, then `check_sysemu()` verifies `PTRACE_SYSEMU_SINGLESTEP`. `init_seccomp()` tests installing a seccomp trap filter and extracts startup register/fp state from a signal mcontext. `uml_seccomp_config()` parses `seccomp=off|auto|on`. `get_host_cpu_features()` parses `/proc/cpuinfo`. `os_early_checks()` runs coredump, temp exec, seccomp, ptrace, SMP compatibility, and register initialization checks.

## Control Flow, State, and Persistence
Boot-time globals include `seccomp_config` and temporary `seccomp_test_stub_data`. Successful seccomp sets global `using_seccomp`; fallback ptrace initializes register templates from a ptraced child. The decisions persist for all userspace contexts.

## Dependencies and Integration Points
Works with `registers.c`, `mem.c`, SKAS process code, signal stacks, raw syscalls, seccomp BPF, ptrace constants, and command-line setup. It gates whether SMP can be used.

## Risks and Test Signals
Risks include false capability detection, host kernel ptrace/seccomp quirks, seccomp already-filtered environments, close_range dependency, and mandatory `seccomp=on` failures. Test across kernels/containers, `seccomp=on/auto/off`, SMP configs, coredump limits, and noexec tempdirs.
