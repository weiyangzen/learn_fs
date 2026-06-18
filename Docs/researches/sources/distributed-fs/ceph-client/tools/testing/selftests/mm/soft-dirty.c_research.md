# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/soft-dirty.c

Purpose: tests classic pagemap soft-dirty bit semantics for normal pages, VMA reuse, THP, mprotect transitions, file mappings, and VMA merge propagation.

Important APIs and functions: `test_simple()` loops clear/write/observe; `test_vma_reuse()` checks newly allocated or reused VMAs; `test_hugepage()` validates THP behavior; `test_mprotect()` covers anonymous and shared file mappings; `test_merge()` constructs merge cases with `mmap()`, `mremap()`, and `mprotect()`.

Control flow: `main()` skips if soft-dirty is unsupported, opens `/proc/self/pagemap`, sets a 19-test plan, and runs scenarios in sequence.

State and dependencies: state is process-local mappings and `/proc/self/clear_refs` effects via `clear_softdirty()`. A temporary file is created, unlinked immediately, and mapped for file tests. Depends on `vm_util.h` and `thp_settings.h`.

Risks and test signals: failures indicate stale/missing pagemap soft-dirty bits, incorrect VMA-level `VM_SOFTDIRTY` propagation across merges, or THP soft-dirty regressions. THP subtests skip when allocation fails.
