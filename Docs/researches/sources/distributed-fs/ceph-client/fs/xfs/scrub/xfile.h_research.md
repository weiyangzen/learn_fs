<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.h -->
## sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.h

Purpose: Declares the xfile interface used by online scrub code to treat a hidden shmem file as pageable temporary memory.

Important APIs and types: `struct xfile` contains the backing `struct file *`. Public functions are `xfile_create`, `xfile_destroy`, `xfile_load`, `xfile_store`, `xfile_discard`, `xfile_seek_data`, `xfile_get_folio`, and `xfile_put_folio`. `XFILE_MAX_FOLIO_SIZE` captures the largest page-cache folio size, and `XFILE_ALLOC` requests allocation in `xfile_get_folio`. `xfile_bytes` reports allocated backing bytes from `i_blocks`.

Control flow and integration: This header is the narrow contract between scrub data structures and the implementation in `scrub/xfile.c`. Consumers can either copy data in/out by offset or lock one folio directly when a staged object is guaranteed not to cross a folio boundary.

State and persistence: The only state visible to callers is the opaque handle and page-cache allocation accounting. No on-disk XFS state is represented here.

Dependencies: Requires VFS `struct file`, inode helpers, folio types, page size constants, and sector shift definitions from included kernel/XFS headers.

Risks: The header exposes the raw `file` field, so misuse by consumers could bypass xfile assumptions. Direct folio users must respect the no-cross-folio contract and always call `xfile_put_folio`.

Test signals: Build coverage with and without scrub consumers, direct folio get/put pairing checks, and tests that staged byte accounting changes after store/discard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.h -->
