# Chunk Research: sources/virtualization/spdk/lib/blob/blobstore.c lines 9616-10533

## Scope

This report covers only `sources/virtualization/spdk/lib/blob/blobstore.c` lines 9616-10533 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify helper definitions, callback contexts, and earlier load/esnap setup paths referenced by this chunk. This is the final chunk of the file; it closes public blob property helpers, implements blobstore growth paths, manages external-snapshot backing-device channels, exposes esnap accessors, and registers logging/tracing.

## APIs And Entry Points

- `spdk_blob_get_xattr_value()` returns a public xattr value pointer and length after `blob_verify_md_op()` validates metadata-thread context.
- `spdk_blob_get_xattr_names()`, `spdk_xattr_names_get_count()`, `spdk_xattr_names_get_name()`, and `spdk_xattr_names_free()` expose a transient array of public xattr name pointers.
- `spdk_bs_get_bstype()` and `spdk_bs_set_bstype()` get/set the blobstore type field by value.
- `spdk_blob_is_read_only()`, `spdk_blob_is_snapshot()`, `spdk_blob_is_clone()`, `spdk_blob_is_thin_provisioned()`, and `spdk_blob_is_esnap_clone()` expose blob state predicates.
- `spdk_blob_get_parent_snapshot()` and `spdk_blob_get_clones()` query the in-memory snapshot/clone lists.
- `spdk_bs_grow()` loads a blobstore on a resized device and grows on-disk metadata during load.
- `spdk_bs_grow_live()` grows an already-loaded blobstore on its metadata thread.
- Esnap APIs: `spdk_blob_get_esnap_id()`, `spdk_blob_set_esnap_bs_dev()`, `spdk_blob_get_esnap_bs_dev()`, and `spdk_blob_is_degraded()`.
- Internal esnap channel helpers include `blob_esnap_get_io_channel()`, `blob_esnap_destroy_bs_dev_channels()`, `blob_esnap_destroy_one_channel()`, and `blob_esnap_destroy_bs_channel()`.
- The file ends with `SPDK_LOG_REGISTER_COMPONENT(blob)`, `SPDK_LOG_REGISTER_COMPONENT(blob_esnap)`, and `SPDK_TRACE_REGISTER_FN(blob_trace, "blob", TRACE_GROUP_BLOB)`.

## Control Flow

Xattr name enumeration is two-pass: count `TAILQ` entries, allocate one `struct spdk_xattr_names` plus pointer slots, then store borrowed `xattr->name` pointers. The public wrapper only enumerates user-visible xattrs, not internal xattrs.

Blob snapshot/clone queries are list based. `spdk_blob_is_snapshot()` checks `bs->snapshots`; `spdk_blob_is_clone()` treats a non-invalid, non-external parent id as a clone and asserts thin provisioning. `spdk_blob_get_clones()` uses the usual SPDK sizing pattern: return `-ENOMEM` with required count when the caller buffer is missing or too small.

`spdk_bs_grow()` validates the device/options, allocates load state, reads and validates the super block, then optionally grows the on-disk used-cluster mask and super block before resuming normal load. Growth is refused for unclean blobstores.

`spdk_bs_grow_live()` runs on `bs->md_thread`, reads the super block, rejects shrink/no-space cases, writes an updated dirty super block, then swaps in a larger `used_clusters` bit pool under `bs->used_lock`. It intentionally leaves the blobstore unclean until a later clean unload writes the rest of used metadata.

Esnap channel lookup is lazy per blobstore channel. `blob_esnap_get_io_channel()` checks an RB tree by blob id, creates a backing-device channel on miss, inserts it, and returns it. Teardown either removes channels for one blob across all blobstore channels, optionally aborting queued I/O, or removes all esnap channels when a blobstore channel is destroyed.

`spdk_blob_set_esnap_bs_dev()` delegates to earlier freeze/hotplug machinery: freeze blob I/O, destroy cached esnap channels, optionally update parent references, release the old backing device, install the new `back_bs_dev`, unfreeze, and complete.

## State, Dependencies, Risks

The xattr names object owns only the pointer array; name strings are still owned by the blob xattr list. Growth mutates super-block fields and runtime accounting including `size`, `used_cluster_mask_len`, `total_clusters`, `total_data_clusters`, `num_free_clusters`, `used_clusters`, `open_blobids`, `super_blob`, and `bstype`.

This chunk depends on SPDK `TAILQ`/`RB` containers, bit arrays/pools, metadata sequences, DMA allocation, thread affinity, IO channel iteration, blobstore LBA conversion helpers, `struct spdk_bs_dev` callbacks, and earlier helpers such as `blob_verify_md_op()`, `blob_is_esnap_clone()`, `bs_alloc()`, `bs_super_validate()`, `bs_write_super()`, `bs_load_read_used_pages()`, and `blob_set_back_bs_dev()`.

Key risks: borrowed xattr-name lifetime, grow requiring clean metadata, metadata reserved-space limits for the expanded used-cluster mask, live-grow crash consistency after only the super block is written, per-thread serialization assumptions in the esnap RB tree, and queued I/O aborts during esnap backing-device replacement.

## Cross-Chunk References

- Previous chunk defines xattr set/remove/get helpers and continues into `spdk_blob_get_xattr_value()` at line 9616.
- Earlier initialization defines `blob_esnap_channel`, RB tree generation, `blob_is_esnap_clone()`, metadata-thread verification, snapshot lookup, backing-device reference release, and `set_bs_dev_ctx`.
- Earlier load/recovery code owns `spdk_bs_load_ctx`, `bs_load_read_used_pages()`, and `bs_load_complete()`, which `spdk_bs_grow()` resumes after optional growth.
- Earlier snapshot and parent-setting paths populate `bs->snapshots`, clone lists, `parent_id`, esnap xattrs, and `back_bs_dev`.
- There is no next chunk; the file ends at line 10533 with logging and trace registration.