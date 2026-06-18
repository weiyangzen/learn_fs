<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_mremap_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_mremap_vdso.c

## Purpose

`test_mremap_vdso.c` verifies that a process can move the vDSO mapping with `mremap()` when it is not sealed, and that the process continues or exits cleanly afterward. It protects the ABI around the special vDSO mapping.

## Important APIs, Types, and Functions

`try_to_remap()` reserves a destination with `mmap()`, then calls `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)` on the vDSO. `vdso_sealed()` parses `/proc/self/smaps` for `[vdso]` and `VmFlags: sl`. `main()` uses `getauxval(AT_SYSINFO_EHDR)`, forks a child, retries with increasing page-sized guesses, and exits via a raw syscall on i386.

## Control Flow and State

The parent plans one kselftest result, skips sealed vDSO cases, then forks. The child locates and moves the vDSO, exiting with the remap result. The parent inspects wait status and reports pass/fail. State is the child's address space only; no persistent mapping changes affect the parent.

## Dependencies and Integration Points

It depends on auxv vDSO discovery, `/proc/self/smaps`, `mmap`, `mremap`, fork/wait, and kselftest result helpers. It integrates with memory-management and x86 vDSO ABI tests.

## Risks and Test Signals

Risks include rejecting legal vDSO moves, moving only part of the vDSO, failing on sealed mappings without a skip, or glibc crashing after the move. Passing output shows the child exits zero after remapping; failure reports child crash or nonzero exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_mremap_vdso.c -->
