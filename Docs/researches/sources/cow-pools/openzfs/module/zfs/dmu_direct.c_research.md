# File Research: sources/cow-pools/openzfs/module/zfs/dmu_direct.c

## Scope

DMU direct-I/O implementation. It reads and writes page-backed ABDs directly through ZIO without populating normal dbuf/ARC data buffers, while still coordinating with dbuf dirty records, override BPs, checksums, RACCT accounting, and UIO direct pages.

## Main Interfaces

- ABD direct paths: `dmu_read_abd()`, `dmu_write_abd()`.
- Single-dbuf write helper: `dmu_write_direct()`.
- Kernel UIO paths: `dmu_read_uio_direct()`, `dmu_write_uio_direct()`.
- Internal ABD/IO callbacks: `make_abd_for_dbuf()`, `dmu_read_abd_done()`, `dmu_write_direct_ready()`, `dmu_write_direct_done()`.

## State And Control Flow

`make_abd_for_dbuf()` builds an ABD matching a dbuf-sized read target. If the caller’s ABD range does not cover the full dbuf, it allocates zero-fill pre/post ABDs and gangs them with the caller sub-ABD so the ZIO can read a full block into the correct portion.

`dmu_write_abd()` holds dbufs for the target range, creates a root ZIO, slices the caller ABD per dbuf, accounts direct write bytes, and calls `dmu_write_direct()` for each block. It waits for the root ZIO before releasing dbufs so error cleanup can safely undirty records.

`dmu_write_direct()` dirties the dbuf as clone/direct-I/O with no data buffer, selects write policy with `WP_DMU_SYNC | WP_DIRECT_WR`, records the old BP for nopwrite comparison, disables nopwrite when an earlier dirty record exists, marks the dirty record as direct write and `DR_IN_DMU_SYNC`, accounts space use, and issues `zio_write()`. If there is no parent ZIO, it waits synchronously.

`dmu_write_direct_done()` frees the ZIO ABD, sets the dbuf to uncached with no data buffer, delegates override publication to `dmu_sync_done()`, and on error uses `dbuf_undirty()` to roll back the open-context dirty record. It frees the temporary BP allocated for the write.

`dmu_read_abd()` holds dbufs without issuing ARC reads, creates a root ZIO, and for each dbuf waits out in-progress reads, obtains the current BP from the dbuf or dirty record, then either copies cached data/zeros holes or issues a direct `zio_read()` into a full-block ABD. The dbuf mutex is held while creating the ZIO so the copied BP cannot race with dirty-record destruction. Direct read RACCT accounting is only charged for actual ZIO reads, not holes or ARC hits.

Kernel UIO direct helpers map pinned pages from `uio_dio.pages` into ABDs and advance the uio only after successful read/write.

## Dependencies

Depends on dbuf dirty records and override states, `dmu_sync_ready()`/`dmu_sync_done()` from `dmu.c`, write policy selection, ABD page/gang APIs, ZIO read/write, object bookmarks, DSL dataset IDs, RACCT helpers, and platform UIO direct-page pinning.

## Correctness Notes

Direct writes intentionally leave no `db_buf`, `dr_data`, or `db_data` attached to the dbuf. Error cleanup relies on holding dbufs until ZIO completion. Reads must use a full dbuf-sized ZIO even for partial caller ranges, hence the gang ABD construction. The BP source may be a committed BP, pending block clone, or unsynced direct-I/O dirty record; the dbuf mutex protects that lifetime while the ZIO copies the BP.
