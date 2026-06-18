# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_vdso.c

Purpose: tests powerpc signal delivery paths with the VDSO mapped normally, moved, and unmapped, covering both VDSO trampoline and stack trampoline fallback behavior.

Important APIs/types/functions: `search_proc_maps()` locates mappings; `sigusr1_handler()` increments `took_signal`; `test_sigreturn_vdso()` drives mapping changes using `mmap()`, `mremap()`, `munmap()`, and `mprotect()`.

Control flow: the test confirms `[vdso]` exists, sends a signal, remaps the VDSO to a fresh anonymous address and signals again, unmaps it entirely, makes the stack executable, and sends a third signal. Assertions verify each signal was delivered.

State and persistence behavior: mutates only the current process address space and stack protections. No external files are changed, though `/proc/self/maps` is read repeatedly.

Dependencies and integration points: relies on Linux VDSO mapping names, GNU `mremap` flags, and kselftest harness.

Risks and test signals: uses `assert()`, intentionally kept enabled. Failures abort immediately on mapping or signal delivery mismatch.
