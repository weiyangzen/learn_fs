# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/merge.c

## Purpose

`merge.c` is a broad VMA merge regression suite. It validates when adjacent VMAs should merge or remain separate across `mprotect()`, `mremap()`, `MREMAP_DONTUNMAP`, forked anonymous-vma state, KSM process-wide merge flags, uprobes, and `mseal()`.

## Important APIs, Types, and Functions

The test uses kselftest harness fixtures, `mmap()`, `mprotect()`, `munmap()`, `mremap()`, `prctl(PR_SET_MEMORY_MERGE)`, `perf_event_open()` for uprobes, `sys_mseal()`, and `procmap` query helpers from `vm_util.h`. `map_carveout()` reserves a 30-page `PROT_NONE` arena. `do_fork()` forks and reopens the procmap fd in the child. Fixtures `merge` and `merge_with_fork` share page size, carveout, and procmap state.

## Control Flow

The early tests create page-aligned carveout subregions, use `mprotect()` to split VMAs into RO/RW regions, fault selected subranges to attach anonymous VMA state, then change protections back and assert a single merged VMA via `find_vma_procmap()`. Fork tests ensure forked anonymous-vma chains inhibit unsafe merging. The uprobe test creates a file-backed executable mapping with a perf uprobe and moves subranges with `mremap()` to exercise merged executable VMA metadata. KSM tests toggle `PR_SET_MEMORY_MERGE` and verify newly adjacent anonymous mappings still merge. The mremap series moves unfaulted/faulted chunks around and checks merge boundaries. The `merge_with_fork` variants compare forked versus unforked results for `MREMAP_DONTUNMAP` moves into adjacent unfaulted/faulted regions.

## State and Persistence Behavior

All mappings live inside per-test carveout regions and are cleaned by fixture teardown. Some tests fork and only the child performs VMA assertions. `PR_SET_MEMORY_MERGE` is cleared unconditionally in teardown. The uprobe test creates and removes `./foo`. `mseal()` tests intentionally create sealed VMAs that cannot be unmapped individually, so they use a separate carveout and avoid normal teardown expectations for that mapping.

## Dependencies and Integration Points

It depends on `PROCMAP_QUERY` helpers, KSM prctl support, `__NR_mseal` where available, perf uprobe support under `/sys/bus/event_source/devices/uprobe/type`, and kernel VMA merge internals. It is tightly integrated with mm regressions around `anon_vma`, `vm_pgoff`, merge eligibility, sealed mappings, and multi-process VMA lineage.

## Risks and Edge Cases

The suite encodes precise expected VMA boundaries; small kernel semantic changes in merge eligibility can flip assertions. Forked tests use parent-return/child-continue control flow through `do_fork()`. Uprobe setup may skip if sysfs support is absent. Sealed VMA tests cannot always clean mappings after success. The fixture comments note that close of procmap may fail in parent after fork.

## Test Signals

Primary signals are procmap start/end assertions after each operation. Negative signals are expected non-merges for forked or incompatible VMAs. Skip signals cover absent KSM process merge support, missing uprobe event source, or missing `mseal`.
