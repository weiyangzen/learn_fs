# Chunk Research: sources/virtualization/spdk/lib/blob/blobstore.c lines 1-9615

## Scope

This chunk covers the first 9,615 lines of SPDK's `lib/blob/blobstore.c` in subset A (`sources/virtualization/spdk`). It contains most of the blobstore core: option initialization, blob allocation/free, metadata parse/serialize/load/persist, blobstore init/load/dump/unload/destroy, public blob create/open/close/delete/resize/I/O APIs, snapshot/clone/inflate/parent-changing flows, shallow copy, cluster allocation/free coordination, iteration, and the start of xattr accessors.

Report written to `Docs/researches/chunks/chunk_sources_virtualization_spdk_lib_blob_blobstore_c_1_1_9615_123117d3cfe4_research.md`.

## Major APIs And Entry Points

- Blobstore lifecycle: `spdk_bs_init()`, `spdk_bs_load()`, `spdk_bs_dump()`, `spdk_bs_unload()`, `spdk_bs_destroy()`
- Blob lifecycle: `spdk_bs_create_blob[_ext]()`, `spdk_bs_open_blob[_ext]()`, `spdk_blob_close()`, `spdk_blob_sync_md()`, `spdk_blob_resize()`, `spdk_bs_delete_blob()`
- I/O: `spdk_blob_io_read/write/unmap/write_zeroes()`, `spdk_blob_io_readv/writev[_ext]()`
- Snapshot/clone/parent: `spdk_bs_create_snapshot()`, `spdk_bs_create_clone()`, `spdk_bs_inflate_blob()`, `spdk_bs_blob_decouple_parent()`, `spdk_bs_blob_shallow_copy()`, `spdk_bs_blob_set_parent()`, `spdk_bs_blob_set_external_parent()`
- Iteration/xattrs: `spdk_bs_iter_first()`, `spdk_bs_iter_next()`, `spdk_blob_set_xattr()`, `spdk_blob_remove_xattr()`, and `spdk_blob_get_xattr_value()` starts at the chunk tail.

## Core Findings

The chunk’s central invariant is that metadata operations run on `bs->md_thread`, enforced by `blob_verify_md_op()`. Allocation state is protected by `bs->used_lock`, with separate maps for metadata pages, blob ids, open blob ids, and data clusters. Blob metadata has `active` and `clean` copies so in-flight persists can complete without losing newer dirty changes.

Metadata persistence is crash-aware: mark super dirty, write new non-root pages, write root page last, then zero old pages and clear/release truncated clusters and extent pages. Loading validates CRCs and descriptors, then either uses persisted masks or replays metadata pages for recovery when the store is dirty/old/forced.

The data path maps allocated I/O to the primary device and unallocated thin ranges to a backing device. Writes to unallocated thin clusters allocate/copy-on-write a cluster, optionally copying from a snapshot/external backing device, then update metadata on the md thread. Cross-cluster requests are split.

Snapshot, clone, delete, inflate, and parent-change operations are high-risk state machines. They freeze I/O, use internal xattrs for recovery markers, temporarily override `md_ro`, update parent/backing devices, and rely on cleanup callbacks to restore locks and flags.

## Cross-Chunk References

This chunk declares and calls external snapshot helpers whose definitions are outside the range: `blob_esnap_channel_compare()`, `blob_esnap_destroy_bs_dev_channels()`, `blob_esnap_destroy_bs_channel()`, and `blob_set_back_bs_dev_frozen()`. The remaining xattr/status/query APIs continue after line 9615.