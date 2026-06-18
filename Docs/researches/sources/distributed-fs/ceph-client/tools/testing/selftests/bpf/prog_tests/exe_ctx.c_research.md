# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exe_ctx.c

## Purpose
Tests execution context behavior for generated `test_ctx` BPF programs.

## Important APIs, types, and functions
Uses `test_ctx.skel.h`, syscall helpers, and the selftest harness. `test_exe_ctx()` loads/attaches the skeleton and triggers relevant syscalls to validate context values.

## Control flow and state
Runtime state is skeleton BSS/output and the current task/syscall context. The file does not persist external artifacts.

## Dependencies and integration points
Depends on generated skeleton and syscall tracepoint/kprobe support. Integrated as `test_exe_ctx()`.

## Risks and test signals
Risks are hook availability and context layout drift. Passing signals are skeleton assertions or BSS checks succeeding after syscall trigger.
