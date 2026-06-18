# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pfnmap.c

Purpose: validates core `VM_PFNMAP` behavior for mappings such as `/dev/mem`, ensuring unsupported memory-management operations fail cleanly while splitting, shrinking, moving, and forking mappings remain safe.

Important APIs and functions: `find_ram_target()` parses `/proc/iomem`; `pfnmap_init()` opens and probes the target file; `test_read_access()` traps `SIGSEGV`; fixture tests cover disallowed `madvise()`, `munmap()` splits, fixed `mremap()`, shrink/expand behavior, and child access after `fork()`.

Control flow: `main()` optionally accepts an alternate file after `--`, initializes fd/offset, then runs the kselftest harness with a fresh two-page shared read-only mapping per fixture.

State and dependencies: state is process-local aside from the open file descriptor and selected offset. It depends on `check_vmflag_pfnmap()`, `/proc/iomem`, `/dev/mem` or another PFNMAP file, and privilege/kernel policy allowing the mapping.

Risks and test signals: expected signals are `EINVAL` for forbidden advices, successful split/fixed-remap/shrink/fork reads, and failed expansion. It often skips when physical addresses are hidden or `/dev/mem` is restricted.
