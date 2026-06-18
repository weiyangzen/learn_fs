# sources/distributed-fs/ceph-client/include/linux/userfaultfd_k.h

## Purpose
This header is the kernel-internal userfaultfd interface for registering VMAs, handling missing/minor/write-protect faults, atomic page fill/move/poison operations, and mm lifecycle notifications.

## Important APIs, types, and functions
Key items are `userfaultfd_ctx`, `vm_uffd_ops`, `uffd_flags_t`, `mfill_atomic_mode`, `handle_userfault()`, `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, `mfill_atomic_poison()`, `mwriteprotect_range()`, `uffd_wp_range()`, `move_pages()`, registration/release helpers, VMA flag predicates, and fork/mremap/unmap preparation/completion hooks. Disabled builds return conservative no-op or `SIGBUS`/false results.

## Control flow, state, and persistence
Fault paths call `handle_userfault()` when VMA flags are armed. UFFD operations fill, continue, poison, write-protect, or move pages under context waitqueues and `map_changing_lock`. Fork, mremap, unmap, and release paths notify or clear contexts so userspace fault handlers see coherent events. State includes waitqueues, refcount, requested features, released flag, mmap-changing counter, mm pointer, and VMA `vm_userfaultfd_ctx`; no disk persistence is involved.

## Dependencies and integration points
It depends on mm, swap, page-table UFFD helpers, hugetlb, fcntl flags, and userfaultfd UAPI. It integrates deeply with page fault handling, VMA merge/split, filemap/pagecache operations, huge PMD sharing, swap PTE markers, and mm teardown.

## Risks and test signals
Risks include lock ordering violations among waitqueues, lost wakeups, PTE marker misuse, huge-PMD sharing with UFFD-WP/minor, fault-around installing mappings without notification, and feature mismatch with userspace. Tests should cover missing/minor/WP faults, fork/mremap/unmap events, atomic fill modes, async WP markers, hugetlb/file-backed VMAs, disabled config, and race stress around release.
