<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio.h -->
# sources/distributed-fs/ceph-client/include/linux/uio.h

Purpose: defines kernel scatter/gather buffer descriptors and the `iov_iter` abstraction used to copy, pin, extract, and advance over user buffers, kernel vectors, bio vectors, folio queues, xarrays, and discard sinks.

Important APIs and types: `struct kvec` describes kernel vectors. `enum iter_type` identifies `ITER_UBUF`, `ITER_IOVEC`, `ITER_BVEC`, `ITER_KVEC`, `ITER_FOLIOQ`, `ITER_XARRAY`, and `ITER_DISCARD`. `struct iov_iter` stores direction (`data_source`), nofault mode, current offset/count, segment state, and a union of backing representations. `struct iov_iter_state` snapshots offset/count/segment state; `struct uio_meta` wraps protection metadata plus an iterator. Key helpers include type predicates, `iov_iter_rw()`, `iov_iter_count()`, `iov_iter_truncate()/reexpand()`, `iov_iter_save_state()/restore()`, copy helpers (`copy_to_iter`, `copy_from_iter`, full/reverting variants, nofault/nocache/flushcache/machine-check variants), page extraction helpers, import helpers (`import_iovec`, `import_ubuf`, `iovec_from_user`), and `extract_iter_to_sg()`.

Control flow: syscall and I/O paths import user iovecs or initialize kernel iterators, validate total lengths, then repeatedly copy or extract pages while `iov_iter_advance()` moves the cursor. Full-copy wrappers revert partial progress on short copy. Page extraction returns pinned pages for user-backed iterators and unpinned references for other iterator classes, signaled by `iov_iter_extract_will_pin()`.

State and persistence: iterator state is transient per I/O operation: current offset, remaining count, segment index, and backing pointer. It does not persist data, but incorrect advancement or failure rollback can corrupt higher-level file/socket/block I/O semantics.

Dependencies and integration points: depends on UAPI `linux/uio.h`, memory/folio/page types, `check_copy_size()`, architecture copy features, xarray, scatterlist, and bio vectors. It is central to VFS read/write, networking, block direct I/O, splice-like paths, and filesystem data movement.

Risks and test signals: risks include length overflow before validation, copying in the wrong direction, failing to revert on partial full-copy helpers, misinterpreting user-backed pin lifetime, `ITER_UBUF` overlay assumptions, and config-specific copy semantics. Test with vectored read/write, short copy fault injection, direct I/O page pin accounting, xarray/bvec/kvec iterators, nofault paths, and KASAN/UBSAN coverage around bounds and alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio.h -->
