# Group Research: group_1787_thin_provisioning_tools_sources_block_storage_thin_provisioning_too_27f95b0eaf7b

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/thin-provisioning-tools`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/report.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/report.rs

This file implements `CopyProgress` adapters for copier operations.

`IgnoreProgress` is a no-op implementation used by tests or callers that do not need progress reporting. `ProgressReporter` wraps a shared `Report` and a mutex-protected `AccumulatedStats` structure. `update()` computes temporary progress including an in-flight batch, while `inc_stats()` commits completed batch stats into the accumulator.

Important behavior:
- Tracks total blocks, copied blocks, read errors, and write errors.
- Updates the report subtitle only when either error counter is nonzero.
- Uses `checked_div(...).unwrap_or(100)` so zero total blocks produce 100% progress.
- Designed for concurrent copier threads through `Arc<Report>` and `Mutex`.

Integration points:
- Depends on `crate::copier::{CopyProgress, CopyStats}`.
- Uses `crate::report::Report` for UI/progress display.
- Used by copier frontends to surface copy progress and error counts.

Risks and notes:
- Mutex poisoning is not recovered; `unwrap()` will panic after a prior panic inside the lock.
- Progress percentage truncates to integer percent and casts to `u8`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/report.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier.rs

This file implements `RescueCopier`, a page-level salvage copier for damaged devices or files.

`RescueCopier<T: FileExt>` copies one logical block at a time, but reads and writes the block page by page. This lets the copier preserve readable pages even when some pages within a block fail. It records a block-level read error if any page read fails and a block-level write error if any selected page write fails.

Important behavior:
- Requires `block_size`, source offset, and destination offset to be page aligned.
- `from_path()` opens source and destination with `O_EXCL | O_DIRECT`.
- `do_read()` reads each 4096-byte page and records successful page indexes in a `FixedBitSet`.
- `do_write()` writes only pages that were successfully read.
- A block counts as copied only if all page reads and writes succeeded.

Integration points:
- Implements the shared `Copier` trait.
- Uses `io_engine::buffer::Buffer` for aligned direct-I/O memory.
- Uses `CopyOp`, `CopyStats`, and `CopyProgress` from the copier module.
- Used when partial recovery is more important than all-or-nothing block copying.

Risks and notes:
- Read failures do not zero unread pages; they are simply skipped on write.
- A partial read plus successful writes still reports a read error and does not increment `nr_copied`.
- It uses one reusable buffer, so it is single-copy-loop stateful rather than internally parallel.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier/tests.rs

This file tests `RescueCopier` with an injectable-error `Ramdisk`.

The test harness stamps deterministic page contents into source and destination devices, invalidates page ranges to simulate read/write failures, runs randomized `CopyOp` batches, and verifies destination pages after the copy.

Important components:
- `mk_random_ops()` creates randomized source-to-destination block mappings.
- `CopySourceIndicator` maps destination pages back to source pages.
- `CopyVerifier` validates every destination page against the expected deterministic seed.
- `CopierTest` owns source/destination ramdisks, fault sets, stamping, invalidation, copy, and verification helpers.

Test coverage:
- Complete successful block copy.
- Partial copy with unreadable source pages.
- Partial copy with unwritable destination pages.
- Combined unreadable source and unwritable destination pages.

Integration points:
- Uses `Ramdisk` error injection and `Generator` deterministic buffers.
- Uses `Stamper` and `visit_blocks()` from copier test utilities.
- Exercises `RescueCopier<Ramdisk>` through the public `Copier` trait.

Risks and notes:
- Random operation order increases coverage variety but means exact operation ordering is not deterministic.
- Assertions check expected failing source/destination block numbers for fixed invalidated ranges.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/rescue_copier/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier.rs

This file implements `SyncCopier`, a block-oriented copier with ordered, aggregated reads and a writer thread.

`SyncCopier<T>` copies batches of `CopyOp` values using `ReadBlocks` and `WriteBlocks` abstractions. It sorts read and write requests by device location, aggregates adjacent operations into larger I/O calls, and pipelines reading with a single writer thread through a bounded channel.

Important behavior:
- Rejects configurations where `block_size > buffer_size`.
- Supports separate source/destination devices and `in_file()` copying behind one mutex for same-file operations.
- Page-aligns optional source and destination byte offsets.
- `do_reads()` sorts source blocks, aggregates adjacent reads, and records per-op success in a `RoaringBitmap`.
- `do_writes()` writes only blocks whose reads succeeded, similarly sorting and aggregating destination writes.
- `copy()` chunks work by buffer capacity, reports read/write errors, joins the writer thread, and commits final stats.

Integration points:
- Generic over `ReadBlocks + WriteBlocks + Send`.
- `from_path()` opens files with `O_DIRECT` and wraps `File` into the chosen I/O adapter.
- Used with `SimpleBlockIo` or `VectoredBlockIo` depending on caller needs.

Risks and notes:
- `progress.update(&stats)` in the writer thread passes cumulative shared stats, while `inc_stats()` is called at the end with the final stats; progress consumers must tolerate that pattern.
- Same-file copying serializes read/write through a shared mutex, which avoids concurrent same-file access but limits parallelism.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier/tests.rs

This file tests `SyncCopier` across ordered, reversed, random, partial, and failure-heavy copy workloads.

The harness stamps deterministic block contents, invalidates block-aligned byte ranges in `Ramdisk`, copies through `SyncCopier<SimpleBlockIo<Ramdisk>>`, and validates destination contents with source-to-destination reverse mappings.

Important components:
- `mk_ops()` creates direct mappings from arbitrary source and destination sequences.
- `mk_random_ops()` creates randomized subsets.
- `CopySourceIndicator` maps destination blocks to source blocks.
- `CopyVerifier` checks copied blocks, untouched blocks, and skipped failed blocks.
- `CopierTest` centralizes device setup, stamping, invalidation, copy, and verification.

Test coverage:
- Full mirroring.
- Source-sorted, destination-sorted, and random copy order.
- Skipping read-failed blocks.
- Skipping write-failed blocks.
- All reads failing and all writes failing.
- Copy lengths smaller than the buffer and not a multiple of buffer capacity.

Integration points:
- Uses the same copier traits and test utilities as production copier code.
- Validates `CopyStats` counts and error-vector content.

Risks and notes:
- The tests use `SimpleBlockIo`, so they verify copier batching logic against per-block I/O semantics, not all vectored-I/O edge cases.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/sync_copier/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/test_utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/test_utils.rs

This file provides reusable copier test helpers.

`BlockVisitor` abstracts visiting sequential logical blocks. `visit_blocks()` calls a visitor for every block number from zero to `nr_blocks - 1`. `Stamper<T: FileExt>` writes deterministic generated data to each block of a device using a seed XORed with the block number.

Important behavior:
- Uses page-aligned `Buffer` allocation.
- `Stamper::offset()` supports byte-offset stamping.
- `visit()` fills the buffer with `Generator::fill_buffer()` and writes it with `write_all_at()`.

Integration points:
- Used by copier tests to stamp source/destination fixtures.
- Depends on `random::Generator`, `io_engine::buffer::Buffer`, and `FileExt`.

Risks and notes:
- Intended for tests; no production error recovery beyond returning `anyhow::Result`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/test_utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/wrapper.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/wrapper.rs

This file implements `ThreadedCopier`, a small worker-thread wrapper around any `Copier`.

`ThreadedCopier::run()` consumes batches of `CopyOp` values from an `mpsc::Receiver`, runs the wrapped copier, and terminates with an error on the first reported read or write failure.

Important behavior:
- Runs copying in a spawned thread and returns a `JoinHandle<Result<()>>`.
- Converts copier errors into contextual `anyhow!("copy failed: ...")`.
- Treats nonempty `read_errors` or `write_errors` as fatal, reporting the first failed source or destination block.

Integration points:
- Used where higher-level code wants a copier worker that receives batches asynchronously.
- Relies on shared `CopyProgress`.

Risks and notes:
- Stops on the first failing batch rather than attempting recovery.
- Error reporting includes only the first failed block in each failure vector.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/wrapper.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/devtools/damage_generator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/devtools/damage_generator.rs

This file contains devtool support for intentionally damaging metadata space-map reference counts.

It can find blocks with a target reference count and rewrite their bitmap entries to a different count, creating metadata leak/corruption scenarios for testing repair/check tooling.

Important behavior:
- `find_blocks_of_rc()` scans metadata space-map bitmap entries for ref counts below 3, or the ref-count B-tree for higher counts.
- `adjust_bitmap_entries()` rewrites selected bitmap entries and updates their checksums.
- `create_metadata_leaks()` randomly selects blocks with an expected refcount and changes them to an actual refcount.

Integration points:
- Uses metadata space-map structures, B-tree walking, `IoEngine`, and checksum code.
- Exposed only under the `devtools` feature through `devtools/mod.rs`.

Risks and notes:
- High-refcount mutation paths are explicitly `todo!()`.
- The implemented path handles expected and actual refcounts below or equal to the bitmap-small/overflow boundary only where no B-tree updates are needed.
- This intentionally corrupts metadata and is not normal production repair code.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/devtools/damage_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/devtools/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/devtools/mod.rs

This module conditionally exports development-only tooling.

It exposes:
- `damage_generator` when the `devtools` feature is enabled.

Integration points:
- Reached from `lib.rs` under `#[cfg(feature = "devtools")]`.

Risks and notes:
- Keeps damaging/corruption helper code out of default builds.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/devtools/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/dump_utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/dump_utils.rs

This file provides shared helpers for metadata dump paths.

`OutputError` is a marker error used to distinguish output failures from metadata/input failures. `output_context()` wraps `anyhow::Result` with that context. The file also defines an `ArrayVisitor` variant returning `anyhow::Result` and `walk_array_blocks()` for reading and visiting array blocks with checksum/type validation.

Important behavior:
- Reads each array block through `IoEngine`.
- Verifies block type is `checksum::BT::ARRAY`.
- Unpacks array blocks with path-aware array errors.
- Calls caller-supplied visitor with the logical array-block index.

Integration points:
- Used by era dump paths to traverse array metadata and map output errors separately.
- Depends on `pdata::array`, `pdata::unpack`, and `checksum`.

Risks and notes:
- Stops on the first array I/O, checksum, parse, or visitor error.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/dump_utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/check.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/check.rs

This file implements era metadata checking.

`check()` opens an era metadata device, validates the superblock version, optionally stops at superblock-only checking, then verifies writeset bitsets and era-array values.

Important behavior:
- Builds a metadata space map and increments the superblock location as reserved.
- Reads and validates the era superblock.
- Walks the writeset B-tree and checks each writeset bitset with metadata-space-map accounting.
- `EraChecker` validates that no era-array value exceeds `current_era`.
- Reports fatal errors through `Report` and returns an error if any fatal issue is found.

Integration points:
- Uses `EngineBuilder`, `read_superblock`, `btree_to_map`, `read_bitset_checked_with_sm`, and `ArrayWalker`.
- Shares `Writeset` and array validation types with restore/dump code.

Risks and notes:
- Superblock validation only checks version greater than 1.
- Nonfatal handling is delegated to lower-level walkers through `ignore_non_fatal`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/check.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/dump.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/dump.rs

This file implements era metadata dumping to the visitor/XML intermediate representation.

It can emit physical metadata, including writesets and the era array, or logical metadata where pending writesets are folded into effective per-block era values.

Important components:
- `EraEmitter` visits array blocks and emits each block's era.
- `Archive`/`EraArchive<T>` store writeset-derived era deltas compactly.
- `LogicalEraEmitter` overlays archived writeset-era data on top of era-array values.
- `OutputVisitor` wraps downstream visitor calls with `OutputError` context.
- `dump_writeset()` emits contiguous marked-bit ranges.
- `get_writesets_ordered()` combines archived writesets and current writeset, enforcing contiguous era coverage.

Public entry points:
- `dump_metadata()`
- `dump_metadata_logical()`
- `dump(EraDumpOptions)`

Integration points:
- Reads from `IoEngine`, walks B-trees/arrays, reads bitsets, and writes through `era::xml::XmlWriter` or any `MetadataVisitor`.
- Used directly by era dump CLI and by era repair as a source stream for `Restorer`.

Risks and notes:
- Logical dumping requires all writesets to be readable and ordered.
- Duplicate current-era writeset detection is explicit.
- `repair` mode is passed to lower-level readers as the permissive/ignore-nonfatal flag.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/dump.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/invalidate.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/invalidate.rs

This file implements `era_invalidate` style output: it emits XML ranges of data blocks changed since a threshold era.

Important components:
- `BitsetCollator` ORs writeset bit arrays into a composed bitset.
- `EraArrayCollator` marks blocks whose era-array value is at or above the threshold.
- `mark_blocks_since()` combines writesets at/after the threshold and, when needed, the era array.
- XML helpers emit `<blocks>`, `<range begin=... end=...>`, and single `<block block=...>` elements.

Public entry point:
- `invalidate(EraInvalidateOptions)`

Integration points:
- Opens metadata through `EngineBuilder`.
- Reads normal or metadata-snapshot superblock depending on engine options.
- Uses `ArrayWalker`, `btree_to_map`, `Writeset`, and shared XML attribute helpers.

Risks and notes:
- Writeset and era-array walking uses non-repair mode.
- Range output uses end-exclusive ranges.
- The `archived_begin` comparison determines when era-array data must supplement writesets.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/invalidate.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/ir.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/ir.rs

This file defines the in-memory intermediate representation and visitor interface for era metadata.

Data structures:
- `Superblock`: UUID, data block size, block count, current era.
- `Writeset`: era number and number of bits.
- `MarkedBlocks`: contiguous marked range.
- `Era`: data block and its era value.
- `Visit`: continue/stop control value.

`MetadataVisitor` defines callbacks for:
- Superblock begin/end.
- Writeset begin/end and writeset marked blocks.
- Era array begin/end and individual era entries.
- End-of-file.

Integration points:
- Used by XML parsing/writing, dump, restore, repair, and metadata generator paths.
- Provides a stable stream format between readers and writers.

Risks and notes:
- The visitor interface does not enforce ordering itself; implementations such as `Restorer` enforce section state.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/ir.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/metadata_generator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/metadata_generator.rs

This devtools-gated file generates synthetic era metadata.

`MetadataGenerator` emits metadata through the same `MetadataVisitor` interface used by dump/restore. `CleanShutdownMeta` generates a clean-shutdown superblock, a sequence of random writesets, and a random era array.

Important behavior:
- `IndependentSequence` creates random contiguous marked ranges with independent per-block probability.
- `CleanShutdownMeta` validates `current_era > 0` and `nr_writesets <= current_era`.
- Generated writesets cover eras from `current_era - nr_writesets + 1` through `current_era`.
- `format()` feeds generated metadata into `Restorer` through `WriteBatcher`.

Public entry point:
- `generate_metadata(EraGenerateOpts)`

Integration points:
- Uses `Restorer` to materialize generated visitor events into real on-disk metadata.
- Uses `EngineBuilder` and metadata space-map allocation.

Risks and notes:
- Random generation makes exact output nondeterministic.
- Feature-gated under `devtools`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/metadata_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/mod.rs

This is the era module declaration file.

It exports:
- `check`
- `dump`
- `invalidate`
- `ir`
- `repair`
- `restore`
- `superblock`
- `writeset`
- `xml`

It conditionally exports:
- `metadata_generator` under the `devtools` feature.

Integration points:
- Used by `lib.rs` to expose era functionality to the crate.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/repair.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/repair.rs

This file implements era metadata repair by dump-and-restore.

`repair()` opens an input metadata device and an output metadata device, reads the input superblock, creates a fresh metadata space map and `WriteBatcher` for output, and streams repaired dump output into a `Restorer`.

Important behavior:
- Input is opened read-only through `EngineBuilder`.
- Output is opened writable through `EngineBuilder`.
- Calls `dump_metadata(..., repair = true)` so lower-level dump readers use repair/permissive mode.
- Uses `Restorer` to build new era metadata structures on the output device.

Integration points:
- Bridges `era::dump` and `era::restore`.
- Uses `core_metadata_sm`, `WriteBatcher`, and superblock reading.

Risks and notes:
- Repair behavior depends heavily on dump readers' ability to tolerate damaged structures.
- It does not use the `Report` beyond storing it in context.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/repair.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/restore.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/restore.rs

This file restores era metadata from the visitor/XML intermediate representation into on-disk metadata.

`Restorer` implements `MetadataVisitor` and builds writeset arrays, the writeset B-tree, the era array, metadata space map, and final era superblock.

Important behavior:
- Enforces section ordering with `Section::{None, Superblock, Writeset, EraArray, Finalized}`.
- Allocates superblock location during `superblock_b()` and fails if it is already occupied.
- Builds each writeset as an `ArrayBuilder<u64>` bitset.
- `writeset_blocks()` converts marked block ranges into u64 bitset entries.
- Builds the era array with `ArrayBuilder<u32>`.
- `finalize()` completes all structures, builds metadata space map, and writes a clean-shutdown superblock.
- `eof()` requires finalization to have occurred.

Public entry point:
- `restore(EraRestoreOptions)`

Integration points:
- Reads XML via `era::xml::read()`.
- Uses `WriteBatcher`, `ArrayBuilder`, `BTreeBuilder`, metadata space-map code, and superblock writer.

Risks and notes:
- Assumes writeset marked ranges arrive in usable order for buffered bitset emission.
- Some internal paths use `unwrap()` where prior section-state checks are expected to guarantee presence.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/restore.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/superblock.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/superblock.rs

This file defines era superblock on-disk packing and unpacking.

Important structures and constants:
- `SPACE_MAP_ROOT_SIZE = 128`
- `SUPERBLOCK_LOCATION = 0`
- `SuperblockFlags`
- `Superblock`

Important behavior:
- `unpack()` parses the on-disk superblock fields with `nom`.
- `read_superblock()` reads a metadata block, verifies checksum type `BT::ERA_SUPERBLOCK`, and parses it.
- `read_superblock_snap()` follows `metadata_snap` from the actual superblock.
- `pack_superblock()` serializes fields with little-endian layout.
- `write_superblock()` writes to block zero, calculates checksum, and writes through `IoEngine`.

Integration points:
- Used by era check, dump, invalidate, repair, restore, and metadata generator.
- Uses `Writeset` for current writeset fields.

Risks and notes:
- UUID is parsed but not stored in the returned production `Superblock`.
- `write_superblock()` ignores its `_loc` parameter and always writes `SUPERBLOCK_LOCATION`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/superblock.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/writeset.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/writeset.rs

This file defines the on-disk writeset value type.

`Writeset` contains:
- `nr_bits: u32`
- `root: u64`

It implements:
- `Unpack` with disk size 12 bytes.
- `Pack` as little-endian `u32` followed by little-endian `u64`.

Integration points:
- Stored in era writeset B-trees.
- Used by era superblock current-writeset field, dump, check, invalidate, and restore paths.

Risks and notes:
- It is a compact POD-style metadata value with no validation beyond parse/pack structure.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/writeset.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/xml.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/era/xml.rs

This file implements XML serialization and parsing for era metadata IR.

`XmlWriter<W>` implements `MetadataVisitor` and writes:
- `<superblock uuid=... block_size=... nr_blocks=... current_era=...>`
- `<writeset era=... nr_bits=...>`
- Compact `<marked block_begin=... len=...>` ranges or verbose `<bit block=... value=...>` entries.
- `<era_array>` and `<era block=... era=...>` entries.

Parsing:
- `parse_superblock()`, `parse_writeset()`, `parse_writeset_bit()`, `parse_writeset_blocks()`, and `parse_era()` validate known attributes.
- `handle_event()` dispatches quick-xml events to a `MetadataVisitor`.
- `read()` streams XML into the visitor until EOF or visitor stop.

Integration points:
- Dump emits XML through `XmlWriter`.
- Restore reads XML through `read()` into `Restorer`.
- Uses shared XML attribute parsing helpers from `crate::xml`.

Risks and notes:
- `parse_superblock()` reports missing `nr_blocks` with attribute name `"nr_cache_blocks"`, likely a diagnostic typo.
- Attribute iteration uses `unwrap()` on XML attributes, so malformed attribute objects can panic rather than return `anyhow`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/era/xml.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/file_utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/file_utils.rs

This file provides filesystem and block-device utility functions.

Important behavior:
- Uses `libc::stat64` to classify regular files and block devices.
- `is_file_or_blk()` returns true for regular files or block devices.
- `is_file()` checks only regular files.
- `device_size()` issues `BLKGETSIZE64` through the crate ioctl macros.
- `file_size()` returns regular-file byte size or block-device capacity.
- `create_sized_file()` creates/truncates a file and sizes it by seeking to `nr_bytes - 1` and writing one zero byte.

Integration points:
- Used by IO engines and packer code to compute block counts.
- Depends on `ioctl.rs` request code generation.

Risks and notes:
- `create_sized_file()` creates sparse files for large sizes.
- `file_size()` rejects paths that are neither regular files nor block devices.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/file_utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/grid_layout.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/grid_layout.rs

This file implements a simple right-aligned text grid renderer.

`GridLayout` accumulates rows of string fields, computes per-column widths, and writes aligned lines to any `Write`.

Important behavior:
- `field()` appends a field to the current row.
- `new_row()` finalizes the current row and updates maximum column count.
- `calc_field_widths()` computes maximum string length per column.
- `render()` right-aligns each field and appends a space after every column.

Integration points:
- Useful for CLI/status table output elsewhere in the crate.

Risks and notes:
- Uses byte length through `String::len()`, so non-ASCII display widths are not handled.
- Current row is not rendered unless `new_row()` has been called.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/grid_layout.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/async_.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/async_.rs

This file implements an optional `io_uring`-backed `AsyncIoEngine`.

Important components:
- `AsyncReader` streams sorted logical block requests through larger pooled IO blocks.
- `IoData` owns submitted iovecs and borrowed `IOBlock`s until completion.
- `AsyncIoEngine` wraps a direct-I/O file, block count, and `RingPool`.

Important behavior:
- Uses 16 rings and queue depth 256.
- Validates IO block sizes between 4 KiB and 16 MiB.
- Batches up to 64 contiguous IO blocks per readv request.
- On completion, calls the read handler for each requested logical block and returns buffers to the pool.
- Implements `IoEngine::{read, read_many, write, write_many, read_blocks}` with `io_uring`.

Integration points:
- Feature-gated under `io_uring` in `io_engine/mod.rs`.
- Shares logical-block mapping helpers with the sync engine.

Risks and notes:
- Uses raw pointers in submitted user data and buffer-pool memory; correctness depends on completion processing returning every block.
- `unsafe impl Send/Sync` is used for `AsyncIoEngine`.
- Some submission errors are converted to generic I/O errors.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/async_.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/base.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/base.rs

This file defines core IO-engine traits, constants, aligned `Block` allocation, and vectored file I/O wrappers.

Important definitions:
- `PAGE_SIZE = 4096`, `BLOCK_SIZE = 4096`, `SECTOR_SHIFT = 9`.
- `Block`: page-aligned 4 KiB metadata block with location.
- `ReadHandler`: callback interface for streaming reads.
- `IoEngine`: common metadata block read/write API.
- `VectoredIo`: abstraction over `preadv64`/`pwritev64`.

Important behavior:
- `Block::new()` allocates aligned raw memory.
- `Block::zeroed()` returns a zero-filled block.
- `get_nr_blocks()` derives metadata block count from file/device byte size.
- `VectoredIo` is implemented for `File` and `&File`.

Integration points:
- Foundation for sync, async, spindle, core, and test IO engines.
- Used by metadata code throughout the crate.

Risks and notes:
- `Block::get_data()` returns a mutable slice from `&self`, relying on external alias discipline.
- Raw allocation/deallocation is manual.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/base.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/buffer.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/buffer.rs

This file defines `Buffer`, a general aligned byte buffer for direct I/O.

Important behavior:
- Allocates `size` bytes with caller-specified alignment.
- Exposes data through `get_data()`.
- Deallocates using the same layout in `Drop`.
- Implements unsafe `Send` and `Sync`.

Integration points:
- Used by copier buffers, ramdisk storage, packer chunks, and test stamping.

Risks and notes:
- Like `Block`, `get_data()` returns mutable data from `&self`; users must avoid aliasing misuse.
- Allocation failure panics.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/buffer.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/buffer_pool.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/buffer_pool.rs

This file implements a fixed-size aligned IO buffer pool.

Important structures:
- `IOBlock`: location plus raw data pointer.
- `BufferPool`: contiguous allocation divided into reusable blocks.

Important behavior:
- Allocates `nr_blocks * block_size` bytes aligned to `block_size`.
- Initializes a stack of available `IOBlock`s.
- `get(loc)` pops a block and tags it with the requested location.
- `put(block)` returns the block for reuse.
- Exposes block size, block count, and empty state.

Integration points:
- Used by sync and async stream readers to read larger IO blocks and split them into logical metadata blocks.

Risks and notes:
- `IOBlock` is `Clone`, so callers must avoid returning duplicate handles to the same memory.
- Pool does not check that returned blocks came from the pool.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/buffer_pool.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/core.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/core.rs

This test-only file implements an in-memory `CoreIoEngine`.

Important behavior:
- Allocates a contiguous aligned memory area sized by number of 4 KiB blocks.
- `read()` copies a block from memory into a new `Block`.
- `write()` copies from a `Block` into memory.
- `read_many()` and `write_many()` loop over single-block operations.
- `trash_block()` writes a zero block at a location.

Integration points:
- Available only under `#[cfg(test)]` from `io_engine/mod.rs`.
- Useful for unit tests that need an `IoEngine` without filesystem I/O.

Risks and notes:
- `read_blocks()` is unimplemented with `todo!()`.
- Raw memory is exposed through unsafe copy operations.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/core.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/gaps.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/gaps.rs

This file builds run/gap batches from block-number sequences for efficient vectored I/O.

Important components:
- `RunOp::Run(begin, end)` and `RunOp::Gap(begin, end)` represent end-exclusive ranges.
- `find_runs()` groups adjacent requested blocks and optionally includes small gaps.
- `batch_adjacent()` groups adjacent runs/gaps into contiguous batches.
- `split_batches()` limits batch length.
- `generate_runs()` is the public pipeline.
- `count_gaps()` counts total gap blocks.

Integration points:
- Used by `SyncIoEngine::read_many_()` to combine requested reads with small gap buffers into larger `preadv` calls.

Test coverage:
- Single/multiple runs.
- Large and small gaps.
- Unordered input behavior.
- Singleton runs.
- Batching and max-size splitting.

Risks and notes:
- Input is not sorted internally; unordered input produces order-sensitive runs.
- Gap inclusion can read extra blocks into disposable buffers.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/gaps.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/mod.rs

This module file wires together IO-engine implementations.

Always exported modules:
- `base`
- `buffer`
- `buffer_pool`
- `gaps`
- `spindle`
- `sync`
- `utils`

Always re-exported:
- `base::*`
- `SpindleIoEngine`
- `SyncIoEngine`

Feature/test exports:
- `async_`, `AsyncIoEngine`, and `ring_pool` under `io_uring`.
- `core` and `ramdisk` under tests.

Integration points:
- Central import point for metadata tooling and copier code.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/ramdisk.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/ramdisk.rs

This test-only file implements a mock direct-I/O ramdisk with error injection.

Important behavior:
- Stores data in an aligned shared `Buffer`.
- Tracks invalid pages in a shared `RoaringBitmap`.
- `invalidate(bytes)` marks all pages overlapping a byte range as faulty.
- `VectoredIo` read/write methods fail the entire vectored operation if any covered page is invalid.
- `FileExt` read/write methods fail when their range overlaps invalid pages.

Integration points:
- Used heavily by copier and IO utility tests.
- Simulates direct-I/O page-alignment and bad-sector behavior.

Risks and notes:
- Internally indexes sizes as `u32`, so it is for small test devices.
- Clones share both data and invalid-page state.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/ramdisk.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/ring_pool.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/ring_pool.rs

This file implements a pool of `io_uring::IoUring` instances.

Important behavior:
- `RingPool::new(count, queue_depth)` creates rings and an availability queue.
- `with_ring()` blocks on a condition variable until a ring is available, locks it, runs the caller closure, then returns the ring and notifies one waiter.
- `len()` and `is_empty()` expose pool state.

Integration points:
- Used by `AsyncIoEngine` to support concurrent callers without sharing one ring directly.

Risks and notes:
- If the closure panics, the ring is not returned to `available_rings`.
- The closure return type is generic, so errors are caller-managed.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/ring_pool.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/spindle.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/spindle.rs

This file implements `SpindleIoEngine`, an IO engine optimized for slow random-access disks.

It preloads selected metadata blocks, compresses them into memory, and serves reads from the compressed cache when possible. Reads/writes outside cached metadata blocks fall back to direct synchronous file I/O.

Important behavior:
- Scans a `RoaringBitmap` of metadata-interest blocks.
- Reads present ranges in chunks, sends them to a packer thread, and compresses recognized metadata blocks.
- `pack_block()` uses metadata block type to choose pack format.
- `read_()` unpacks cached blocks or reads from disk.
- `write_()` removes stale cache entry and writes through to disk.
- Public `SpindleIoEngine` wraps mutable state in `RwLock`.

Integration points:
- Uses pack VM/node encoding, checksum block typing, `RunIter`, and direct-I/O files.
- Implements `IoEngine`.

Risks and notes:
- `read_blocks()` is unimplemented.
- Cache memory can be large by design.
- Writes invalidate only the exact block cache entry.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/spindle.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/sync.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/sync.rs

This file implements `SyncIoEngine`, the direct synchronous file-backed metadata IO engine.

Important components:
- `SyncReader` streams logical 4 KiB block reads through larger pooled IO blocks.
- `SyncIoEngine` wraps an `O_DIRECT` file and metadata block count.
- `find_runs_nogap()` batches adjacent write blocks.

Important behavior:
- Opens files with `O_DIRECT`, optionally `O_EXCL`.
- `read()` and `write()` use positional single-block I/O.
- `read_many_()` combines requested blocks into `preadv` batches using `generate_runs()` and gap buffers.
- `write_many_()` uses contiguous write batches without gap insertion.
- `read_blocks()` maps logical blocks to larger IO blocks and uses handler callbacks.

Integration points:
- Main default `IoEngine` implementation re-exported by `io_engine/mod.rs`.
- Depends on `VectoredBlockIo`, gap generation, buffer pools, and adjacent chunking utilities.

Risks and notes:
- Gap reads intentionally read unrequested blocks into throwaway buffers.
- Uses assertions to enforce expected block ordering in some internal paths.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/sync.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/sync/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/sync/tests.rs

This file tests `SyncIoEngine::write_many_()` vector layout.

It uses `mockall` to mock the `VectoredIo` trait, stamps synthetic metadata blocks, and verifies that generated iovecs point to the expected buffers at expected offsets.

Important behavior:
- `allocate_test_blocks()` creates zeroed `Block`s and stamps each with its block number plus a valid NODE checksum.
- `test_write_many()` computes expected contiguous runs and configures the mock to validate position, iovec count, base pointers, lengths, and block contents.
- Tests cover empty input, contiguous blocks, gaps, long runs, and splitting beyond `UIO_MAXIOV`.

Integration points:
- Exercises private helper `find_runs_nogap()` and `SyncIoEngine::write_many_()`.

Risks and notes:
- Focuses on write batching, not read gap batching.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/sync/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/utils.rs

This file defines block-I/O adapters and logical-to-physical IO-block mapping helpers.

Important components:
- `ReadBlocks` and `WriteBlocks` traits.
- `VectoredBlockIo<T: VectoredIo>` for vectored reads/writes.
- `SimpleBlockIo<T: FileExt>` for per-block positional I/O.
- `map_small_blocks_to_io()` maps sorted logical 4 KiB blocks to larger IO block bitmasks.
- `process_io_block_result()` splits a larger IO block result back into logical block callbacks.

Important behavior:
- `VectoredBlockIo::read_blocks()` retries after failures by skipping the first failing block, supports optional partial-read acceptance, and zero-fills partial buffers.
- `VectoredBlockIo::write_blocks()` skips failing blocks and continues.
- `SimpleBlockIo` returns one result per buffer using exact positional reads/writes.

Integration points:
- Used by copier code, sync/async IO engines, and tests.
- Bridges `FileExt`, `VectoredIo`, and higher-level copier abstractions.

Risks and notes:
- Some write errors are labeled `"read failed"` in `VectoredBlockIo::write_blocks()`.
- `map_small_blocks_to_io()` assumes sorted/grouped input for optimal mapping.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/utils/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/utils/tests.rs

This file tests `VectoredBlockIo` and `SimpleBlockIo` under injected ramdisk faults.

Important components:
- `TestContext` creates a `Ramdisk`, block size, offset, and expected faulty block bitmap.
- `ReadWriteTest` runs read/write operations over block ranges.
- `VectoredIoValidator` models vectored behavior where a failing block can cause earlier batch results to fail up to the last fault.
- `SimpleIoValidator` expects only individually faulty blocks to fail.

Test coverage:
- Reads and writes starting at a faulty block.
- Reads and writes overlapping a faulty block.
- Faults at the end of the device.
- Operations before a fault that should succeed.
- Both vectored and simple block-I/O adapters.

Integration points:
- Validates semantics consumed by `SyncCopier` and `SyncIoEngine`.

Risks and notes:
- Tests use fixed 8 KiB logical blocks on a 64 KiB ramdisk.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/io_engine/utils/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/ioctl.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/ioctl.rs

This file ports Linux asm-generic ioctl request-code construction to Rust.

Important behavior:
- Defines `RequestType` as `c_int` on musl and `c_ulong` otherwise.
- Defines architecture-dependent direction and size bit constants for MIPS/PowerPC/SPARC versus common architectures.
- Exposes masks and shifts for ioctl fields.
- Exports macros:
  - `ioc!`
  - `request_code_none!`
  - `request_code_read!`
  - `request_code_write!`
  - `request_code_readwrite!`

Integration points:
- Used by `file_utils.rs` to define `BLKGETSIZE64`.
- Available crate-wide through macro export.

Risks and notes:
- Mirrors Linux ABI details; correctness depends on target architecture cfgs matching kernel expectations.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/ioctl.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/ioctl/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/ioctl/tests.rs

This file validates ioctl request-code macro output against known block-device ioctl constants.

Test coverage:
- `request_code_none!(0x12, 119)` equals expected `BLKDISCARD`.
- `request_code_read!(0x12, 114, usize)` equals expected `BLKGETSIZE64`.
- `request_code_write!(0x12, 113, usize)` equals expected `BLKBSZSET`.

The expected constants vary by:
- MIPS/PowerPC/SPARC style direction encoding versus common architectures.
- 32-bit versus 64-bit pointer width.

Integration points:
- Protects `ioctl.rs` ABI compatibility for `file_utils` block-device operations.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/ioctl/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/lib.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/lib.rs

This is the crate root module declaration file.

It enables test-only quickcheck crates and exposes major modules:
- cache, checksum, commands, copier, dump_utils, era, file_utils, grid_layout, io_engine, ioctl, math, pack, pdata, report, run_iter, shrink, thin, units, utils, version, write_batcher, xml.

Conditional exports:
- `random` under test or `devtools`.
- `devtools` under the `devtools` feature.

It also re-exports:
- `utils::hashvec`

Integration points:
- Defines the public module surface for the thin-provisioning-tools Rust crate.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/math.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/math.rs

This file provides a generic integer ceiling-division helper.

`div_up(v, divisor)` computes:
- `(v + divisor - 1) / divisor`

It is generic over copyable numeric types implementing `Add`, `Sub`, `Div`, and `From<u8>`.

Test coverage:
- Exact division.
- One-over exact division.
- Larger non-exact division.

Integration points:
- Used for block/page range calculations in copier tests, ramdisk invalidation, era invalidate, and array builder sizing.

Risks and notes:
- Does not guard against divisor zero.
- Can overflow on `v + divisor - 1` for maximum integer values.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/math.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/delta_list.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pack/delta_list.rs

This file converts u64 sequences into compact delta runs.

`Delta` variants:
- `Base { n }`
- `Const { count }`
- `Pos { delta, count }`
- `Neg { delta, count }`

`to_delta()` emits a base value and then compresses constant, increasing, and decreasing arithmetic runs using wrapping arithmetic where needed.

Integration points:
- Used by `pack::vm` to encode numeric arrays such as B-tree keys and values.

Test coverage:
- Empty and single-element sequences.
- Positive/negative arithmetic progressions.
- Constant runs.
- Mixed patterns.
- Wrapping edge cases around `u64::MAX`.
- Round-trip through a local `from_delta()` helper.

Risks and notes:
- Count semantics represent additional emitted values after the base/current value.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/delta_list.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pack/mod.rs

This module file exposes pack subsystem modules.

Public modules:
- `node_encode`
- `toplevel`
- `vm`

Private module:
- `delta_list`

Integration points:
- `spindle.rs` and `pack/toplevel.rs` use node encoding and VM packing to compact metadata blocks.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/node_encode.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pack/node_encode.rs

This file packs recognized metadata block layouts into the pack VM format.

Important behavior:
- Defines `PackError` for parse and write failures.
- Parses B-tree node headers enough to identify leaf/internal node, max entries, and value size.
- `pack_btree_node()` emits:
  - literal header,
  - packed u64 keys,
  - packed shifted u64 values for leaf nodes with u64 values,
  - packed u64 values for internal nodes,
  - literal tail data when needed.
- Superblock, bitmap, index, and array packers currently emit literal bytes.

Integration points:
- Used by pack toplevel and spindle metadata cache packing.
- Delegates numeric compression to `pack::vm`.

Risks and notes:
- Non-u64 leaf values are not semantically packed; their tail is emitted literally.
- Parse failures are generic `ParseError`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/node_encode.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/toplevel.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pack/toplevel.rs

This file implements top-level metadata pack and unpack commands.

Pack format:
- Header contains magic, version, block size, and number of blocks.
- Payload is a sequence of zlib-compressed chunks.
- Each compressed chunk stores block number plus VM-packed metadata block data for recognized metadata blocks.

Important behavior:
- `pack()` divides input blocks into shuffled chunks across CPU-count worker threads.
- `crunch()` reads ranges, detects metadata block type, packs recognized blocks, and flushes compressed groups every 1024 metadata blocks.
- `unpack()` creates/sizes output, starts decode workers, reads compressed chunks, unpacks blocks, and writes them at original block numbers.
- Only blocks with recognized metadata checksums are packed; unknown blocks are omitted and unpack as zeroes due to file sizing.

Integration points:
- Uses `checksum::metadata_block_type`, `node_encode`, `pack::vm`, `file_utils`, and direct positional file I/O.

Risks and notes:
- `read_header()` error message for unsupported version formats the expected version rather than the actual version.
- Decode worker uses `unwrap()` on VM unpack and asserts recognized metadata type.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/toplevel.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/vm.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pack/vm.rs

This file implements the bytecode VM used to pack and unpack metadata byte streams.

Important pieces:
- `Tag` enum defines instruction opcodes for setting base values, positive/negative deltas, constants, counts, literals, and shifted u64 runs.
- Packing helpers encode counts, deltas, u64 sequences, shifted u64 sequences, and literal bytes.
- `VM` tracks current u64 base value and total emitted bytes while interpreting instructions.
- `unpack()` runs the VM until a requested byte count is emitted.

Important behavior:
- `pack_u64s()` uses `delta_list::to_delta()`.
- `pack_shifted_u64s()` splits u64s into high bits and low 24 bits for better compression.
- `ShiftedRun` recursively unpacks high and low streams, then recombines values.

Integration points:
- Used by node encoding, top-level unpack, and spindle cache unpack.

Test coverage:
- Literal packing.
- u64 sequence packing.
- Property tests for arbitrary u64 vectors.
- Property tests for shifted u64 packing.

Risks and notes:
- Several invalid opcode/width paths panic rather than return errors.
- Empty u64 vectors are not supported by `pack_u64s()` callers/tests.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pack/vm.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array.rs

This file defines persistent array block format helpers and errors.

Important structures:
- `ArrayBlockHeader`: checksum placeholder, max entries, actual entries, value size, block number.
- `ArrayBlock<V>`: header plus typed values.
- `ArrayError`: path-aware errors for I/O, array block validation, value validation, index context, aggregation, and B-tree errors.

Important behavior:
- `unpack_array_block()` validates value size, max entries fitting in metadata block size, and `nr_entries <= max_entries`, then parses typed values.
- `pack_array_block()` serializes header and values.
- `calc_max_entries<V>()` computes maximum typed entries per 4 KiB block.

Integration points:
- Used by array walkers, era array dump/check/invalidate, and array builder.
- Depends on `pdata::unpack::{Pack, Unpack}` and `io_engine::BLOCK_SIZE`.

Risks and notes:
- Header checksum is written as zero here; callers must apply metadata block checksum after packing.
- Error display concatenates aggregate errors without separators.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array/tests.rs

This file tests persistent array block pack/unpack round trips.

Important behavior:
- `mk_random_block()` creates an `ArrayBlock<u64>` with random values and a valid header.
- `pack_unpack_empty_block()` verifies empty array blocks preserve header and have no values.
- `pack_unpack_fully_populated_block()` verifies a full array block preserves header and all values.

Integration points:
- Exercises `pack_array_block()`, `unpack_array_block()`, and `calc_max_entries()`.

Risks and notes:
- Tests focus on valid round trips, not malformed header validation paths.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder.rs

This file builds persistent arrays from ordered sparse/indexed values.

Important components:
- `ArrayBlockBuilder<V>` buffers values into array blocks.
- `ArrayBuilder<V>` builds array blocks plus a B-tree mapping array-block indexes to block locations.
- `ArrayIO<V>` writes packed array blocks through `WriteBatcher`.

Important behavior:
- `push_value()` enforces bounds and increasing array index order.
- Gaps within the current block are filled with `Default::default()`.
- `complete()` emits all remaining blocks, including default-filled trailing blocks.
- `ArrayBuilder::complete()` builds a B-tree index over emitted array block locations and returns its root.
- `write_array_block()` allocates a metadata block, packs the array block, writes it with checksum type `BT::ARRAY`, and returns its location.

Integration points:
- Used by era restore to build writeset bitset arrays and era arrays.
- Depends on `WriteBatcher`, B-tree builder, checksum, math, and array packing.

Risks and notes:
- Out-of-order insertion is rejected.
- Empty arrays may produce no array blocks depending on capacity; callers should understand expected array size semantics.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/test_utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/test_utils.rs

This file provides test utilities for building arrays and inspecting their layout.

Important components:
- `ArrayLayout` stores emitted array block locations plus the B-tree layout.
- Accessors expose height, node counts, root node, nodes/leaves by height, array blocks, and first array block under a tree node.
- `build_array_blocks()` builds raw array blocks from a value slice.
- `build_array_from_values()` builds array blocks and manually builds a B-tree layout from array-block mappings.

Integration points:
- Used by array-builder tests to validate physical layout and B-tree structure.
- Reuses B-tree builder test utilities.

Risks and notes:
- `build_array_from_values()` asserts that values are nonempty.
- Layout introspection assumes B-tree test utilities remain aligned with production builder behavior.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/test_utils.rs -->