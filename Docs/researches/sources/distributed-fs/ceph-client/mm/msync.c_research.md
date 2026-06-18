# sources/distributed-fs/ceph-client/mm/msync.c

Purpose: implements the `msync` syscall for synchronizing shared file-backed mappings over a virtual address range. Modern `MS_ASYNC` is intentionally a no-op for I/O initiation; `MS_SYNC` delegates to filesystem `fsync` over mapped file ranges, and `MS_INVALIDATE` rejects locked mappings.

Important APIs/types/functions: syscall `msync`, `find_vma`, `vfs_fsync_range`, `get_file`, `fput`, and mmap read locking helpers. Key types are `mm_struct`, `vm_area_struct`, `file`, and file offsets (`loff_t`).

Control flow: the syscall strips address tags, validates flags, page alignment, mutually exclusive `MS_ASYNC`/`MS_SYNC`, page-aligns length, detects overflow, and returns success for empty ranges. It takes `mmap_read_lock`, finds the first VMA, and loops until the end address. Gaps are ignored for work purposes but recorded as a final `-ENOMEM`; with pure `MS_ASYNC`, a gap returns immediately because no further work is needed. `MS_INVALIDATE` fails with `-EBUSY` on locked VMAs. For each shared file-backed VMA under `MS_SYNC`, it computes file offsets from VMA start and `vm_pgoff`, takes a file reference, drops `mmap_lock`, calls `vfs_fsync_range(file, fstart, fend, 1)`, releases the file, and reacquires the read lock if more VMAs remain.

State and persistence: it does not change VMA topology. Persistent effects are filesystem-specific writeback/synchronization side effects from `vfs_fsync_range`. It may return a remembered `-ENOMEM` for holes even if all mapped parts synced successfully. File references protect the file while the mmap lock is dropped.

Dependencies and integration points: integrates with VMA lookup in `mmap.c`, VFS `fsync` implementations, shared mapping semantics, locked-VMA state, and tagged address handling. Filesystem clients with mmap support, including distributed filesystems in this source tree, observe this through their `fsync` operation rather than through direct code in `msync.c`.

Risks: dropping and reacquiring `mmap_lock` around filesystem sync means VMA topology can change; the loop restarts lookup at the next virtual address. Offset computation must avoid syncing the wrong file range. `MS_ASYNC` behavior may surprise legacy expectations but is explicitly documented in the code. Locked mappings with invalidation must fail consistently.

Test signals: `msync` tests for invalid flags, unaligned addresses, length overflow, empty range, holes returning `-ENOMEM`, `MS_ASYNC` no-op behavior, `MS_SYNC` on private vs shared and anonymous vs file-backed mappings, `MS_INVALIDATE` against mlocked VMAs, and filesystem error propagation from `vfs_fsync_range`.
