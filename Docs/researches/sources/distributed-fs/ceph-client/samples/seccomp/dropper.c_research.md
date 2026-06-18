# sources/distributed-fs/ceph-client/samples/seccomp/dropper.c

## Purpose

This user-space utility installs a simple seccomp filter that returns a chosen errno, or kills, for one syscall number on one audit architecture before executing another program.

## Important APIs, Types, and Functions

The main functions are `install_filter()` and `main()`. It uses `AUDIT_ARCH_*`, BPF statements over `struct seccomp_data.arch` and `.nr`, `SECCOMP_RET_ERRNO`, `SECCOMP_RET_KILL`, `prctl(PR_SET_NO_NEW_PRIVS)`, `prctl(PR_SET_SECCOMP)`, and `execv()`.

## Control Flow

`main()` parses `arch`, `syscall_nr`, `errno`, program path, and arguments. `install_filter()` builds a short filter: if arch matches and syscall number matches, return the configured errno or kill action; otherwise allow. After installing it, `main()` execs the target program.

## State and Persistence Behavior

The seccomp filter persists across `execv()`, so it constrains the launched program. No other state is persisted.

## Dependencies and Integration Points

It depends on seccomp filter support and audit architecture constants. It is useful for fault-injection against arbitrary programs.

## Risks and Edge Cases

An incorrect architecture value silently allows all syscalls on the real arch. `errno` is masked through `SECCOMP_RET_DATA`. Filtering essential syscalls can make the target fail before meaningful testing.

## Test Signals

Run with `AUDIT_ARCH_X86_64`, a target syscall such as `openat`, and a small command; verify the syscall returns the selected errno or the process is killed with `-1`.
