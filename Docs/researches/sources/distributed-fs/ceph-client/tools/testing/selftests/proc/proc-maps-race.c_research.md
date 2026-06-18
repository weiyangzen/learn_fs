# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-maps-race.c

Purpose: stress-tests `/proc/$pid/maps` and the `PROCMAP_QUERY` ioctl while a traced child concurrently mutates VMAs. It targets output tearing at page boundaries during VMA split, resize, and remap operations.

Important APIs and functions: kselftest fixtures manage a child with shared `struct vma_modifier_info`. Core helpers include `read_two_pages()`, `read_boundary_lines()`, `capture_mod_pattern()`, `query_addr_at()`, and VMA operations using `mmap`, `mprotect`, and `mremap`. It validates `struct procmap_query` returned by `ioctl(PROCMAP_QUERY)`.

Control flow: setup maps many alternating-protection VMAs in a child, opens `/proc/$child/maps`, captures the boundary crossing two pages, and locates VMAs that straddle that boundary. Each test first captures expected modified/restored patterns, then runs a timed loop where the child repeatedly mutates and restores VMAs while the parent reads boundary lines and queries VMAs.

State and persistence: process-shared anonymous memory holds synchronization locks, condition variable, current state, operation callbacks, and child mapping addresses. No persistent files are written.

Dependencies and integration: depends on pthread process-shared synchronization, procfs maps, anonymous mappings, `mremap` features including `MREMAP_DONTUNMAP`, and the kernel procmap ioctl ABI from `linux/fs.h`.

Risks and test signals: timing and page-boundary assumptions are central. It deliberately allows a small set of duplicated/restored-line patterns that are legal under concurrent modification. Failures signal torn maps iteration, wrong next-VMA handling, or `PROCMAP_QUERY` inconsistency under races.
