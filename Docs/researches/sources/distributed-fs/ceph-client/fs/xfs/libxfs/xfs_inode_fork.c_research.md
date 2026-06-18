# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.c

Purpose: Materializes and flushes inode forks. It converts local, extent, btree, device, and metadata-btree fork formats between on-disk dinode storage and in-core `struct xfs_ifork`, manages fork memory, verifies local fork contents, and enforces extent-count capacity.

Important APIs: `xfs_init_local_fork`, `xfs_iformat_data_fork`, `xfs_iformat_attr_fork`, `xfs_ifork_init_attr`, `xfs_ifork_zap_attr`, `xfs_broot_alloc`, `xfs_broot_realloc`, `xfs_idata_realloc`, `xfs_idestroy_fork`, `xfs_iextents_copy`, `xfs_iflush_fork`, `xfs_iext_state_to_fork`, `xfs_ifork_init_cow`, `xfs_ifork_verify_local_data`, `xfs_ifork_verify_local_attr`, `xfs_iext_count_extend`, and `xfs_ifork_is_realtime`.

Control flow: local forks are copied from the dinode, with symlink data overallocated for null termination. Extent forks validate every disk bmbt record and insert decoded records into the in-core extent tree. Btree forks validate root shape and copy the root into an in-core btree block while leaving extents lazily unread. Data fork formatting dispatches by inode mode and fork format, including special metadata btrees for realtime rmap/refcount. Attr formatting mirrors this for attr fork formats. Flush dispatches by current fork format and log flags, copying local bytes, encoding extents, converting btree roots, writing device numbers, or delegating metadata btree flush.

State and persistence: owns `if_format`, `if_nextents`, `if_needextents`, `if_bytes`, `if_data`, `if_broot`, and CoW fork allocation. Persistence is through `xfs_iflush_fork`, which writes fork payloads into dinodes according to inode log item fields.

Dependencies and integration: integrates with bmap btree conversion, attr/dir/symlink verifiers, realtime metadata btrees, tracepoints, inode log items, and the in-core extent tree.

Risks and test signals: risks include trusting fork size/counts, lazy extent state ordering, btree root resizing, attr fork cleanup after errors, and large extent counter upgrades. Tests should exercise local directory/symlink validation, attr fork conversions, btree-to-extents transitions, CoW fork init, delayed allocation filtering in `xfs_iextents_copy`, and debug lock assertions during flush.
