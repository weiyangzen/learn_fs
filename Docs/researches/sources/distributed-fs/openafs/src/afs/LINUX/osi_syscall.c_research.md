## sources/distributed-fs/openafs/src/afs/LINUX/osi_syscall.c

Purpose: Linux kernel-module syscall-hook support for OpenAFS PAG and `afs_syscall` entry points when `LINUX_KEYRING_SUPPORT` is not used. With keyring support enabled, `osi_syscall_init` and `osi_syscall_clean` are no-op stubs because PAG state is tracked through keyrings instead of group IDs.

Important APIs and state: exports `osi_syscall_init(void)` and `osi_syscall_clean(void)`, and maintains static syscall-table pointers and saved entries such as `afs_sys_call_table`, `afs_ni_syscall`, architecture-specific 32-bit tables, `sys_setgroupsp`, and `sys_setgroups32p`. It references AFS handlers `afs_syscall`, `afs_xsetgroups`, `afs_xsetgroups32`, and 32-bit compatibility variants. It uses `SYSCALLTYPE`, `POINTER2SYSCALL`, and `SYSCALL2POINTER` to normalize table entry width for SPARC64/S390X, IA64, PPC64, AMD64 compat, and common Linux builds.

Control flow: initialization locates the native syscall table with `osi_find_syscall_table(0)`, detects an already-installed AFS syscall, saves the existing `__NR_afs_syscall` and `setgroups` handlers, and replaces them with OpenAFS dispatchers. AMD64 and SPARC64 also probe a 32-bit syscall table with `osi_find_syscall_table(1)` and patch IA32/SPARC compat `afs_syscall` and `setgroups` slots. IA64 uses hand-written function-descriptor stubs, PPC64 creates TOC-aware jump stubs, and S390X can allocate low-memory jump pages if module code is too high for syscall-table entries. Cleanup reverses all table patches and frees S390X jump pages.

Dependencies and integration: this file depends on Linux syscall numbers, OpenAFS PAG group hooks, architecture compile-time probes, and `osi_find_syscall_table`. It integrates with the global module lifecycle; a bad restore can leave kernel syscall slots pointing at unloaded module text.

State and persistence: the only persistent state is in live kernel memory: saved syscall-table entries, allocated trampoline pages, and patched syscall table slots. No on-disk state is created.

Risks: direct syscall-table patching is high risk and kernel-version/architecture fragile. Failures include incomplete cleanup, double installation, pointer-width mistakes, W^X/protection conflicts, stale trampoline pages, and races with concurrent syscalls. The keyring no-op path is lower risk but must match the rest of the build configuration.

Test signals: boot/load/unload module tests, `setpag`/PAG retention across `setgroups`, `fs sysname`/PIOCTL exercises through `afs_syscall`, 32-bit compatibility syscall tests on AMD64/SPARC64/PPC64, repeated load/unload cycles, and negative tests for already-occupied syscall slots.
