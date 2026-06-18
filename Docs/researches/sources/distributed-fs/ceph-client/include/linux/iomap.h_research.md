# sources/distributed-fs/ceph-client/include/linux/iomap.h

Purpose: This header defines the filesystem iomap interface for translating file offsets to storage mappings and driving buffered I/O, writeback, fiemap, hole/data seeking, page faults, DAX, and direct I/O.

Important APIs, types, and functions: Core mapping state is `struct iomap`; operation callbacks are `struct iomap_ops`, `iomap_write_ops`, `iomap_writeback_ops`, `iomap_read_ops`, and `iomap_dio_ops`. Public functions include `iomap_iter`, buffered write/read/readahead helpers, dirty folio handling, zero/truncate/unshare, fiemap/seek/bmap, writeback ioend helpers, direct I/O `iomap_dio_rw`, and swapfile activation.

Control flow: High-level operations initialize `iomap_iter`, call filesystem `iomap_begin` to map a range, process the trimmed length, then call `iomap_end` for commit/unreserve. Buffered paths get folios, fill dirty ranges, and write back via ioends and bios. Direct I/O builds bios from mapped extents and completes through optional filesystem end_io hooks.

State and persistence: `iomap` instances carry mapping type, flags, device/DAX target, inline data, private filesystem state, and validity cookies. `iomap_ioend` tracks writeback completion aggregation and split-parent relationships. `iomap_writepage_ctx` persists current writeback mapping and pending context.

Dependencies and integration points: Integrates with address_space, folios, block devices, bios, DAX, fiemap, swap, readahead, direct I/O, reflink/COW filesystems, and integrity metadata.

Risks: Mapping flags have strong semantics: stale mappings must be remapped, shared extents must be unshared, unwritten extents require completion conversion, and inline data must stay page-bounded. Incorrect ioend merging can corrupt completion accounting. Direct-I/O flags affect alignment, page-fault retry, and stable-data requirements.

Test signals: Cover holes, delalloc, mapped, unwritten, inline, shared COW, stale validation, short writes, writeback split/merge, dirty folio batching, direct I/O alignment/fallback, DAX faults, fiemap, seek hole/data, swap activation, and block/no-block config paths.
