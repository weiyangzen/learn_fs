# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.c

Implements the shared persistent allocator used by NILFS metadata files such as DAT and ifile. It manages grouped allocation state with descriptor blocks, bitmap blocks, and entry blocks, using `struct nilfs_palloc_req` as the prepare/commit/abort transaction carrier.

Key behavior:
- Computes group, descriptor, bitmap, and entry block offsets from entry numbers and metadata entry sizing.
- Initializes allocator metadata via `nilfs_palloc_init_blockgroup`.
- Caches recently used descriptor, bitmap, and entry buffers through `nilfs_palloc_cache`.
- Allocates entries by scanning group descriptors for free slots, setting bitmap bits atomically, and decrementing free counts.
- Frees entries singly or in batches, clearing bitmap bits, incrementing descriptor free counts, deleting empty entry blocks, and deleting empty bitmap blocks.
- Counts maximum allocatable entries and detects out-of-range used counts.

Concurrency and integration: bitmap changes use per-block-group locks from `nilfs_mdt_bgl_lock`; cache access is protected by a spinlock. Storage access is delegated to metadata-file helpers in `mdt.c` such as `nilfs_mdt_get_block`, `nilfs_mdt_delete_block`, and `nilfs_mdt_mark_dirty`.

Risk/notes: correctness depends on bitmap and descriptor counts staying synchronized. The code warns on double frees but still continues cleanup paths. A comment notes descriptor block initialization does not support block sizes larger than page size.
