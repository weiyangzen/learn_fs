# sources/distributed-fs/ceph-client/include/linux/nfs_page.h

Purpose: Declares NFS page request and pageio batching infrastructure for read/write aggregation, mirrors, commit grouping, and async request lifecycle.

Important APIs, types, and functions: Important types are `struct nfs_page`, `struct nfs_pageio_ops`, `struct nfs_rw_ops`, `struct nfs_pgio_mirror`, and `struct nfs_pageio_descriptor`. APIs create requests from pages/folios, initialize descriptors, add/complete/resend requests, test aggregation, join/lock/unlock page groups, wait on async counters, and access request folios/pages/inodes/offsets. Detected source surface: 286 lines; includes `linux/kref.h`, `linux/list.h`, `linux/nfs_xdr.h`, `linux/pagemap.h`, `linux/sunrpc/auth.h`, `linux/wait.h`; macros `NFS_PAGEIO_DESCRIPTOR_MIRROR_MAX`, `_LINUX_NFS_PAGE_H`; structs `folio`, `inode`, `kref`, `list_head`, `nfs_commit_info`, `nfs_direct_req`, `nfs_inode`, `nfs_io_completion`, `nfs_lock_context`, `nfs_page`, `nfs_pageio_descriptor`, `nfs_pageio_ops`, `nfs_pgio_header`, `nfs_pgio_mirror`, `nfs_rw_ops`, `nfs_write_verifier`, `page`, `pnfs_layout_segment`, and 1 more; enums none; typedefs none; function-like declarations/helpers `folio_page`, `folio_size`, `int`, `list_entry`, `nfs_async_iocounter_wait`, `nfs_generic_pg_test`, `nfs_join_page_group`, `nfs_list_add_request`, `nfs_list_entry`, `nfs_list_move_request`, `nfs_list_remove_request`, `nfs_lock_request`, `nfs_page_clear_headlock`, `nfs_page_group_lock`, `nfs_page_group_sync_on_bit`, `nfs_page_group_sync_on_bit_locked`, `nfs_page_group_unlock`, `nfs_page_max_length`, and 11 more.

Control flow: Buffered read/write paths create `nfs_page` requests, group compatible ranges, aggregate them into pageio descriptors and mirrors, issue RPC headers through rw ops, and complete or resend failed groups.

State and persistence behavior: Request state includes list membership, page/folio reference, open and lock contexts, offsets/counts, wb flags, refcount, and group head relationships. Descriptor state persists during batching and mirrors pNFS layouts.

Dependencies and integration points: Depends on lists, pagemap, waits, SUNRPC auth, NFS XDR, krefs, open contexts, and pNFS/RPC completion paths.

Risks and test signals: Risks are request refcount leaks, page group lock deadlocks, incorrect coalescing across credentials/locks/layouts, and resend loops. Test writeback batching, pNFS mirrors, O_DIRECT interaction, folio sizes, and error cleanup.
