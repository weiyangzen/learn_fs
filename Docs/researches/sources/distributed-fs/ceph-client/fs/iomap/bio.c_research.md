<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/bio.c -->
# sources/distributed-fs/ceph-client/fs/iomap/bio.c

## Purpose

`sources/distributed-fs/ceph-client/fs/iomap/bio.c` implements the block-backed read backend for iomap buffered I/O. It batches folio read ranges into bios, submits them, completes folio read state on bio completion, handles integrity payload allocation/verification plumbing, and provides a synchronous single-folio-range read helper for write-begin read-around.

## Important APIs, Types, and Functions

Exported symbols are `iomap_bio_read_folio_range()`, `iomap_bio_read_ops`, and `iomap_bio_read_folio_range_sync()`. Internal helpers include `__iomap_read_end_io()`, `iomap_read_end_io()`, `iomap_fail_buffered_read()`, `iomap_fail_reads()`, `iomap_bio_submit_read()`, `iomap_read_bio_set()`, and `iomap_read_alloc_bio()`.

Important state includes the global `failed_read_list`, `failed_read_lock`, and `failed_read_work`, plus per-read `struct iomap_read_folio_ctx` fields `read_ctx`, `read_ctx_file_offset`, `cur_folio`, `ops`, and optional `rac`.

## Control Flow

As buffered iomap reads encounter mapped extents, `iomap_bio_read_folio_range()` tries to append the current folio range to the existing bio when sectors are contiguous, the iomap maximum bio size has room, and `bio_add_folio()` succeeds. Otherwise it submits the existing bio through `ctx->ops->submit_read()` and allocates a new bio sized for the remaining iomap range, with a single-page fallback allocation to avoid partial-page read handling. It sets readahead flags when applicable, initializes sector and end_io, and adds the current folio range.

Submission is through `iomap_bio_submit_read()`, which allocates integrity metadata when `IOMAP_F_INTEGRITY` is set and calls `submit_bio()`. Completion enters `iomap_read_end_io()`. Successful bios call `__iomap_read_end_io()` immediately, which walks all folio segments and calls `iomap_finish_folio_read()` with success, frees integrity metadata, and drops the bio. Failed bios are queued to `failed_read_list` and processed by `iomap_fail_reads()` workqueue context to avoid nested inode-lock acquisition in filesystem error reporting.

`iomap_bio_read_folio_range_sync()` builds an on-stack one-vector bio, submits it synchronously with `submit_bio_wait()`, optionally verifies integrity data, frees integrity metadata, and returns the block-layer error.

## State and Persistence Behavior

The file does not persist filesystem metadata. It drives reads from block devices into page-cache folios and updates folio read/uptodate/error state through `iomap_finish_folio_read()`. Integrity metadata is attached per bio and freed on completion. Failed read bios temporarily live on a global bio list until the workqueue finishes them.

## Dependencies and Integration Points

It depends on the iomap iterator contract, `struct iomap_read_ops`, block-layer bio allocation/submission, `fs_bio_set` or filesystem-provided biosets, bio integrity helpers, page-cache folios, and the buffered-io completion function from `buffered-io.c`. Filesystems using iomap can install `iomap_bio_read_ops` as their read ops for block-backed buffered reads.

## Risks and Edge Cases

The error path intentionally defers completion to process context; changing that can reintroduce nested `i_lock` or filesystem-error-reporting deadlocks. Bio allocation has a nofail folio-add path after allocation and a single-page fallback, but callers still depend on valid `ctx->ops->submit_read()` and coherent iomap sector ranges.

Integrity payload allocation must match freeing and synchronous verification must only run when the submit succeeded. Readahead paths use reduced GFP flags and mark bios `REQ_RAHEAD`; allocation failure handling must avoid leaving the current folio locked forever.

## Test Signals

Useful tests include sequential buffered reads merging into larger bios, non-contiguous extents forcing submission, iomap max-bio-size boundaries, readahead bio flags, allocation fallback to one vector under fault injection, block read errors completing folios through workqueue context, integrity-enabled reads allocating/freeing payloads, synchronous read-around success and integrity verification failure, and no folio read completion leaks under short or failed bios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/bio.c -->
