## sources/distributed-fs/ceph-client/fs/iomap/ioend.c

Purpose: manages `iomap_ioend` lifecycle for buffered writeback, buffered reads, direct ioend completion, ioend merging, sorting, splitting, and bioset initialization. It exports the shared `iomap_ioend_bioset`.

Important APIs: `iomap_init_ioend` initializes an ioend embedded in a bio. `iomap_ioend_writeback_submit` finalizes and submits writeback bios, including integrity generation. `iomap_add_to_ioend` batches dirty folio ranges into ioends. `iomap_finish_ioends`, `iomap_ioend_try_merge`, `iomap_sort_ioends`, and `iomap_split_ioend` provide completion batching and filesystem post-processing helpers.

Control flow: dirty folio writeback calls `iomap_add_to_ioend`, which decides ioend flags from iomap type and flags, submits the previous ioend if merging is unsafe, allocates a new bio-backed ioend, and adds the folio. Completion enters `ioend_writeback_end_bio`; errors are pushed to `failed_ioend_work` to avoid nested locking in fs-error reporting, while success finishes folio writeback immediately. `iomap_finish_ioend` collapses child split ioends into the parent, records the first error, verifies read integrity, and dispatches to direct/read/write finishers.

State and persistence: ioends hold transient state: inode, logical offset/size, starting sector, flags, parent pointer, error, and list links. Persistence is through submitted block I/O and later filesystem completion; EOF-extending writeback clamps `io_size` to incore EOF to avoid recovery exposing zero padding. Checkpoint-like durability is not owned here, but ordering and completion state directly affect writeback correctness.

Dependencies and integration points: depends on buffer/page writeback, cgroup writeback accounting, block bios, integrity helpers, list sorting, and iomap tracepoints. Filesystems supply `iomap_writepage_ctx` ops and may use splitting for zone append or maximum extent limits.

Risks and test signals: risks include merging ioends with incompatible completion work, long completion stalls, parent/child split accounting, stale EOF size on appends, error handling from workqueue context, and integrity verification failure. Test with unwritten/shared extents, dropbehind folios, boundary extents, zone append splits, physical discontinuity, writeback errors, integrity-enabled read/write, and concurrent appending writes.
