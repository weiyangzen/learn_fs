# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_backup.h

Purpose: declares TTM backup storage helpers for temporarily replacing pages with opaque handles backed by shmem during shrink/backup operations.

Important APIs/types/functions: inline helpers encode a backup handle as an invalid `struct page *` with the low bit set, detect such handles, and decode them back. External APIs drop a backup handle, copy a backed-up page into a destination page, back up a page, finalize backup storage, query available backup bytes, and create a shmem backup file.

Control flow: backup code creates shmem storage, backs pages up by handle, stores encoded handles in page arrays, later copies or drops them, and finalizes the storage file.

State and persistence: backup state is in the shmem `struct file` and encoded page-array handles. It is runtime swap/backup state, not durable persistence.

Dependencies and integration: depends on memory management and shmem headers. Integrated by TTM TT backup, pool backup/restore, and BO shrinking.

Risks and test signals: low-bit pointer tagging assumes real page pointers are aligned. Mishandling handles as real pages can crash. Test mixed page/handle arrays, backup/drop/copy ordering, low-memory behavior, writeback modes, and cleanup of shmem files.
