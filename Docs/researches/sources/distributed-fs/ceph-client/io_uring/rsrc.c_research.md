# sources/distributed-fs/ceph-client/io_uring/rsrc.c

Purpose: manages registered io_uring resources: fixed files, fixed user buffers, kernel bvec buffers for uring_cmd users, resource updates, buffer cloning, memory accounting, and fixed-buffer import.

Important APIs/types/functions: memory helpers `io_account_mem()`, `io_unaccount_mem()`, `io_validate_user_buf_range()`. Resource helpers `io_rsrc_node_alloc()`, `io_rsrc_data_alloc/free()`, `io_free_rsrc_node()`. Registration/update entry points include `io_sqe_files_register/unregister()`, `io_sqe_buffers_register/unregister()`, `io_register_rsrc()`, `io_register_rsrc_update()`, `io_register_files_update()`, `io_files_update_prep()`, `io_files_update()`, `io_register_clone_buffers()`, and exported `io_buffer_register_bvec()`/`io_buffer_unregister_bvec()`. Import helpers include `io_import_reg_buf()`, `io_import_reg_vec()`, and `io_prep_reg_iovec()`.

Control flow: file registration allocates a table, takes fds with `fget()`, rejects io_uring files, wraps them in resource nodes, and populates allocation bitmaps. Buffer registration validates iov ranges, pins pages, coalesces huge folios when possible, accounts locked/pinned pages, fills bvecs, and stores nodes. Updates replace selected nodes with rollback-by-count semantics. Fixed-buffer import validates ranges and directions, then builds `iov_iter` over bvecs. Clone buffers locks source/destination rings in address order, shares `io_mapped_ubuf` refs, and optionally replaces destination tables.

State and persistence: state is `ctx->file_table`, `ctx->buf_table`, node refs/tags, fixed-file allocation bitmaps, pinned folios, user locked-vm and mm pinned-vm accounting, per-ring caches for nodes/ubufs, and shared buffer refs between cloned rings. Tags are persisted until resource release and produce aux CQEs.

Dependencies/integration: depends on VFS files, page pinning/unpinning, hugetlb/folio APIs, io_uring fixed file table, memmap accounting, uring_cmd block request bvecs, read/write fixed-buffer import, and registration dispatch.

Risks/test signals: risks include memory-accounting imbalance, huge-page double accounting, range overflow, direction misuse, node ref leaks, clone replace corner cases, and handling sparse/tagged entries. Test with sparse file/buffer tables, resource tags, huge-page buffers, fixed read/write vectors, kernel bvec registration, clone across rings with different users rejected, and fault injection during update/registration.
