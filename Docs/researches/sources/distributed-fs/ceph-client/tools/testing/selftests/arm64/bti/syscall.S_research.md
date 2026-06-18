# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/syscall.S

Purpose: raw syscall wrapper for BTI freestanding binaries.

Important APIs/types/functions: `syscall` function starts with `bti c`, moves syscall number from `w0` to `w8`, shifts arguments down from `x1..x7` to `x0..x6`, executes `svc #0`, and returns.

Control flow: direct wrapper from C-like varargs ABI to Linux arm64 syscall ABI.

State and persistence: no persistent state.

Dependencies/integration: used by `system.c` and `signal.c`; emits GNU property note.

Risks and test signals: supports up to seven passed values in the wrapper convention; all callers in this suite fit.
