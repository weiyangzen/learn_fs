# Group Research: group_1790_thin_provisioning_tools_sources_block_storage_thin_provisioning_too_c7dd3b5d3d30

Scope verified against `Docs/research_subset_a.md`: `sources/block-storage/thin-provisioning-tools` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/shrink.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/shrink.rs

## Purpose
Implements thin-pool data-device shrink support. It identifies mapped data blocks above a requested new data-block count, copies those blocks into free ranges below the new limit when requested, and rewrites either XML metadata or binary metadata so mappings point at the new locations and the superblock advertises the smaller data-device size.

## Main Components
- `copy_regions()` opens the data device read/write, wraps it in `VectoredBlockIo`, builds a `SyncCopier`, feeds block-level `CopyOp`s through `CopyOpBatcher`, and runs the copy work in a `ThreadedCopier`.
- `MappingCollector` implements `MetadataVisitor` to split mapped data ranges into `below` and `above` `RangeSet`s relative to the target `nr_blocks`.
- `MappingCollector::get_remaps()` computes gaps below the target size and delegates to shared shrink logic `build_remaps()` to map above-limit ranges into those free gaps.
- `DataRemapper` is another `MetadataVisitor` wrapper. It mutates the streamed superblock `nr_data_blocks` and rewrites affected mapping records through `remap()`.
- `build_remaps_from_metadata()` and `build_remaps_from_xml()` run the collection pass over binary metadata and XML metadata respectively.
- `rewrite_xml()` performs the two-pass XML path.
- `rebuild_metadata()` performs the binary metadata path, reconstructing metadata through `Restorer` and `WriteBatcher`.
- `shrink()` dispatches by `ThinShrinkOptions::binary_mode`.

## Behavior
The shrink algorithm is intentionally two-pass. First it reads all mappings to discover data ranges that are already below the new boundary and data ranges that must move. Ranges crossing the boundary are split: the below portion contributes to occupied space, and the above portion contributes to remap demand. Free gaps inside `0..nr_blocks` become destinations.

If `do_copy` is true, data blocks are physically copied before metadata is rewritten. The data block size comes from metadata as sectors shifted by `SECTOR_SHIFT`. `copy_regions()` expands remap ranges into individual source/destination block operations and batches them into the threaded copy pipeline.

Metadata rewriting preserves thin-device/device/shared-definition traversal structure and changes only:
- the superblock `nr_data_blocks`,
- mapping `data_begin` and `len` values that intersect or exceed the new boundary.

For XML, the input is opened exclusively, the XML superblock is read for block size, the input is seeked back between passes, and output is written through `XmlWriter`. For binary metadata, the input engine reads the superblock, builds and optimizes in-memory metadata, computes remaps by dumping metadata to the collector, then restores remapped metadata into a newly created output engine using a core metadata space map.

## Dependencies and Interactions
This file ties together:
- generic shrink range logic from `crate::shrink::toplevel`,
- thin metadata dump/restore visitor infrastructure,
- XML streaming parser/writer,
- synchronous and vectored IO engines,
- threaded copy infrastructure,
- metadata space-map allocation and `WriteBatcher`.

## Research Notes
The key invariant is that remapped metadata must be consistent with any optional data copy. The file assumes `build_remaps()` can satisfy all above-boundary ranges from free below-boundary gaps; if not, errors propagate before rewriting. `DataRemapper::map()` uses streamed mapping splitting, so large metadata can be transformed without materializing XML records in memory.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/shrink.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/stat.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/stat.rs

## Purpose
Provides statistics operations for thin metadata: data block reference-count histograms, metadata block reference-count histograms, and data mapping run-length histograms.

## Main Components
- `RefCounter` implements `NodeVisitor<u32>` for overflow ref-count btree values and accumulates a `BTreeMap<ref_count, count>` behind a `Mutex`.
- `gather_btree_index_entries()` loads bitmap index entries from a btree-backed space map.
- `gather_metadata_index_entries()` reads the metadata-space-map index block directly via `load_metadata_index()`.
- `stat_low_ref_counts_in_bitmap()` counts small bitmap refcounts in the range `1..=2`.
- `stat_low_ref_counts()` reads bitmap blocks, verifies each block is a bitmap via checksum type, unpacks `Bitmap`, and counts low inline refcounts.
- `stat_overflow_ref_counts()` walks the overflow ref-count tree and merges counts through `RefCounter`.
- `stat_data_block_ref_counts()` and `stat_metadata_block_ref_counts()` combine bitmap low counts and overflow tree counts.
- `RunLengthCounter` implements `NodeVisitor<BlockTime>` and uses `RunBuilder` to coalesce consecutive mapping runs.
- `stat_data_run_lengths()` walks each device mapping btree root from the top-level mapping tree.
- `ThinStatOpts`, `StatOp`, and `stat()` expose the command entry point.

## Behavior
Reference-count statistics are gathered from the two-level space-map representation. Low counts stored directly in bitmap entries are counted by scanning bitmap blocks. Larger or overflowed counts are counted by walking the ref-count btree. The data space map and metadata space map differ in how bitmap index entries are discovered, hence the separate gather helpers.

Run-length statistics read the top-level mapping btree to find per-thin-device mapping roots, then walk each mapping btree. `RunBuilder` receives ordered `(thin block, data block, time)` tuples and emits a completed run when continuity breaks. `end_walk()` flushes the final pending run.

Output is printed as tabular stdout:
- ref-count operations print `ref-count`, `times`, percentage, total allocated blocks, and average ref count;
- run-length operation prints `length`, `counts`, percentage, total runs/leaves, and average run length.

## Dependencies and Interactions
The file depends on btree traversal, btree-to-map conversion, metadata block checksums, space-map unpacking, thin block-time values, the superblock reader, and command engine construction.

## Research Notes
The visitor structs use `Mutex` and `AtomicU64` because `BTreeWalker` visitor APIs are shareable/concurrency-friendly, even though the visible call sites walk synchronously. Error messages intentionally collapse lower-level walk errors for user-facing stat commands.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/stat.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/superblock.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/superblock.rs

## Purpose
Defines binary parsing and writing for thin-provisioning metadata superblocks.

## Main Components
- Constants:
  - `MAGIC = 27022010`
  - `SUPERBLOCK_LOCATION = 0`
  - `UUID_SIZE = 16`
  - `SPACE_MAP_ROOT_SIZE = 128`
- `SuperblockFlags` currently exposes the `needs_check` bit and implements `Display`.
- `Superblock` contains decoded superblock fields used by the tooling: flags, block number, version, time, transaction ID, metadata snapshot block, data/metadata space-map roots, mapping/details roots, data block size, and metadata block count.
- `unpack()` uses `nom` little-endian parsers to decode the on-disk layout.
- `read_superblock()` reads a block through `IoEngine`, validates checksum block type `BT::THIN_SUPERBLOCK`, and unpacks it.
- `read_superblock_snap()` follows `metadata_snap` from the live superblock and reads the snapshot superblock.
- `pack_superblock()` writes the on-disk layout with a placeholder checksum.
- `write_superblock()` serializes, checksums, and writes a superblock.

## Behavior
The parser reads but does not expose the UUID. On write, UUID bytes are emitted as zeros. The metadata block size is not stored from the struct; it is written as the fixed library `BLOCK_SIZE >> SECTOR_SHIFT`.

`read_superblock()` treats an unexpected checksum block type as a bad checksum in the superblock, then reports unpack failure separately. `read_superblock_snap()` requires a nonzero `metadata_snap` pointer.

## Dependencies and Interactions
This file is central to thin commands that need binary metadata roots. It depends on checksum helpers, block constants, and the `IoEngine` block abstraction.

## Research Notes
The write API accepts a `_loc` parameter but always writes `SUPERBLOCK_LOCATION` by constructing `Block::zeroed(SUPERBLOCK_LOCATION)`. Callers should not expect arbitrary-location superblock writes from this function.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/superblock.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/trim.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/trim.rs

## Purpose
Implements `thin_trim`: discard unused regions of a thin-pool data device based on the data space-map allocation bitmap in metadata.

## Main Components
- `RangeIterator` iterates allocated ranges from unpacked space-map bitmap blocks.
- `find_first_set()` finds the next nonzero refcount entry in a bitmap slice.
- `find_first_unset()` finds the next zero refcount entry in a bitmap slice.
- `ioctl_blkdiscard()` wraps Linux `BLKDISCARD`.
- `read_bitmaps()` reads all bitmap blocks referenced by the data space-map bitmap index btree.
- `trim_data_device()` validates data device size, iterates allocated ranges, and issues discard calls for gaps between allocated ranges.
- `ThinTrimOptions`, `Context`, `mk_context()`, and `trim()` form the command entry point.

## Behavior
The command reads the thin metadata superblock, unpacks the data space-map root, computes the data block size in bytes, and checks the data device is at least `root.nr_blocks * block_size`. It then reads every bitmap block named by the bitmap index.

`RangeIterator` yields used ranges, not free ranges. `trim_data_device()` tracks `last_seen`; every gap before the next used range is discarded using byte offsets and lengths. After iteration, any trailing free region up to `root.nr_blocks` is also discarded.

Bitmap entries are considered used if they are anything other than `BitmapEntry::Small(0)`. This includes small nonzero counts and non-small/overflow encodings.

## Dependencies and Interactions
The file relies on:
- command engine creation,
- `file_size()` for data-device validation,
- Linux ioctl request construction,
- btree walking/conversion for bitmap index entries,
- space-map bitmap unpacking,
- report debug logging.

## Research Notes
All bitmap blocks are read up front. A comment notes this may exceed 64k bitmap blocks for very large pools, but the implementation still materializes the full vector. `RangeIterator::new()` validates that provided bitmaps cover `nr_blocks`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/trim.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/xml.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/xml.rs

## Purpose
Implements thin metadata XML serialization and parsing using the thin intermediate representation visitor interface.

## Main Components
- `XmlWriter<W>` wraps `quick_xml::Writer<W>` with two-space indentation.
- `METADATA_VERSION` defaults emitted XML superblocks to version `2` when the IR superblock has no explicit version.
- `impl MetadataVisitor for XmlWriter<W>` serializes superblocks, shared definitions, devices, mappings, shared refs, and EOF flush.
- `parse_superblock()`, `parse_device()`, `parse_single_map()`, `parse_range_map()`, and `parse_def()` convert XML element attributes into IR structs.
- `handle_event()` maps `quick_xml` events onto visitor calls.
- `read()` streams an XML input into any `MetadataVisitor`.
- `SBVisitor` and `read_superblock()` provide a lightweight way to extract the first XML superblock.

## XML Model
The writer emits:
- `<superblock uuid time transaction flags? version data_block_size nr_data_blocks metadata_snap?>`
- `<def name>`
- `<device dev_id mapped_blocks transaction creation_time snap_time>`
- empty `<single_mapping origin_block data_block time>` for length 1 mappings,
- empty `<range_mapping origin_begin data_begin length time>` for longer mappings,
- empty `<ref name>`.

The parser recognizes the same element set. Unknown attributes or unknown tags are errors. Text and comments are ignored after trimming.

## Behavior
Parsing is streaming and visitor-driven. A visitor can stop traversal by returning `Visit::Stop`; this is used by `SBVisitor` after the first superblock start tag. EOF calls `visitor.eof()` and stops.

Required attributes are enforced with shared XML helpers. Optional superblock attributes are `flags`, `version`, and `metadata_snap`. Required attributes include core sizing and identity fields such as `uuid`, `time`, `transaction`, `data_block_size`, and `nr_data_blocks`.

## Dependencies and Interactions
This file is used by dump/restore/shrink paths that consume or produce XML metadata. It depends on `crate::thin::ir` for the metadata visitor and data structs, and on top-level `crate::xml` helpers for attribute conversion and validation.

## Research Notes
Several `attributes()` loops call `unwrap()` on XML attribute results, so malformed attribute decoding can panic rather than returning an `anyhow` error. `read_superblock()` also unwraps the collected superblock after `read()`, so an XML input with no superblock would panic.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/xml.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/units.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/units.rs

## Purpose
Defines storage unit parsing, display, byte conversion, and pretty-print sizing utilities used by command-line options and output.

## Main Components
- `Units` enum covers bytes, 512-byte sectors, decimal SI units through exabytes, and binary IEC units through exbibytes.
- `Units::size_bytes()` maps each unit to its byte multiplier.
- `Units::to_string_short()` returns display suffixes such as `b`, `s`, `KiB`, `MB`, and `EiB`.
- `Units::to_letter()` returns legacy one-letter suffixes, using lowercase for binary prefixes and uppercase for decimal prefixes.
- `FromStr for Units` accepts long names, short names, and legacy letters.
- `Display for Units` emits long unit names.
- `to_units()` converts byte counts to an `f64` in the requested unit.
- `StorageSize` pairs a multiple with a unit and validates against `u64` byte overflow.
- `FromStr for StorageSize` parses leading digits plus optional unit, defaulting unitless values to sectors.
- `to_pretty_print_size()` chooses a rounded binary unit/multiple intended to keep values at or below 8192 where possible.
- Embedded tests cover parsing, overflow rejection, round-tripping, and pretty-print edge cases.

## Behavior
`StorageSize::new()` prevents overflow by checking `multiple <= u64::MAX / unit.size_bytes()`. `size_bytes()` can therefore multiply directly. Unitless strings represent sectors, preserving block-device convention.

Pretty-printing uses binary units only. It chooses an initial unit from the highest set bit, shifts to get a multiple, and rounds into the next unit when the multiple exceeds 8192. It may return a rounded value whose exact byte equivalent exceeds `u64::MAX`, so it returns `(u64, Units)` rather than `StorageSize`.

## Compatibility Details
The parser intentionally distinguishes decimal uppercase legacy letters (`K`, `M`, `G`, etc.) from binary lowercase letters (`k`, `m`, `g`, etc.). It also accepts IEC spellings like `KiB`.

## Research Notes
There are small display inconsistencies in the file: `to_string_short()` returns `"Tib"` for `Tebibyte`, while parser support uses `"TiB"`; `Display for Units` returns `"terabyte"` for `Kibibyte`'s `Tebibyte` variant. Tests do not cover those display strings.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/units.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/adjacent_chunks.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/utils/adjacent_chunks.rs

## Purpose
Provides an iterator that groups a sorted slice of `u64` block numbers into adjacent consecutive chunks capped by a maximum length.

## Main Components
- `AdjacentChunks<'a>` stores the input slice, `max_len`, and current start index.
- `AdjacentChunks::new()` constructs the iterator.
- `Iterator for AdjacentChunks` returns borrowed subslices `&'a [u64]`.
- `adjacent_chunks()` is a convenience constructor.

## Behavior
Each `next()` starts at the current position and extends while:
- the end index remains inside the slice,
- chunk length is less than `max_len`,
- the next value equals the previous value plus one using `saturating_add(1)`.

The iterator yields non-overlapping subslices and advances `start` to the end of the yielded chunk.

## Research Notes
This helper assumes caller-provided ordering when “adjacent” semantics are desired. A `max_len` of zero still yields one-element chunks because `end` is initialized to `start + 1` before the cap is checked.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/adjacent_chunks.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/future.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/utils/future.rs

## Purpose
Provides a tiny thread-backed future abstraction without async/await.

## Main Components
- `spawn_future<F, T>(work)` creates an `mpsc` channel, spawns a thread, runs `work`, sends the result, and returns a `FnOnce() -> T` closure that blocks on receive.

## Behavior
The returned closure is the join/retrieve handle. Calling it blocks until the worker sends the result. The worker thread itself is not joined explicitly; successful result delivery is the synchronization point.

Type bounds require both the work closure and its result to be `Send + 'static`.

## Failure Behavior
The function panics if:
- the worker panics before sending,
- sending fails,
- receiving fails.

## Research Notes
This is useful for simple parallel computations where the caller wants delayed blocking. It does not propagate panics as structured errors and does not expose cancellation.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/future.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/hashvec.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/utils/hashvec.rs

## Purpose
Implements `HashVec<T>`, a compact associative container that maps `u32` logical indexes to dense vector slots while preserving value iteration over insertion order.

## Main Components
- `map: HashMap<u32, u32>` maps external indexes to positions in `entries`.
- `entries: Vec<T>` stores values densely.
- `Default` delegates to `new()`.
- `new()` and `with_capacity()` construct empty containers.
- `insert()` updates an existing index in place or appends a new value and stores its vector position.
- `get()` and `get_mut()` access by external index.
- `len()`, `is_empty()`, `reserve()`, and `values()` expose collection utilities.

## Behavior
Updating an existing key replaces the existing vector element and does not change iteration order or length. Inserting a new key appends to `entries`, so `values()` iterates in first-insertion order, not key order.

## Research Notes
`T: Clone` is required for the whole impl because `insert()` uses `value.clone()` in the update branch before moving `value` in the insertion branch. The map index type is fixed to `u32`, with a TODO noting possible parameterization.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/hashvec.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/utils/mod.rs

## Purpose
Declares the public utility submodules for this crate.

## Main Components
- `adjacent_chunks`
- `future`
- `hashvec`
- `prof`
- `ranged_bitset_iter`

## Research Notes
This file contains only module declarations. It establishes the crate-visible namespace for the small helpers researched in this group.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/prof.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/utils/prof.rs

## Purpose
Provides simple Linux `/proc`-based memory usage reporting for debug logs.

## Main Components
- `get_memory_usage()` reads `/proc/self/statm`, extracts the resident page count, and returns resident memory in MiB assuming 4096-byte pages.
- `print_mem(report, msg)` logs `"<msg>: <meg> meg"` through `Report::debug()`.

## Behavior
`get_memory_usage()` returns IO errors from opening/reading `statm`, but uses `unwrap()` for field extraction and numeric parsing. `print_mem()` unwraps the entire memory read.

## Dependencies and Interactions
The helper is Linux-specific because it hardcodes `/proc/self/statm` and a 4096-byte page size. It depends on the project `Report` abstraction for output.

## Research Notes
This is diagnostic-only utility code. It is not robust to non-Linux platforms, unusual page sizes, or unexpected `statm` contents.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/prof.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/ranged_bitset_iter.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/utils/ranged_bitset_iter.rs

## Purpose
Defines an iterator over set bits in a specified index range of a `FixedBitSet`.

## Main Components
- `RangedBitsetIter<'a>` stores a borrowed bitset, the target `Range<usize>`, and current index.
- `RangedBitsetIter::new()` initializes iteration at `range.start`.
- `Iterator` implementation returns set bit indexes as `u64`.
- Manual unsafe `Send` and `Sync` implementations are provided.

## Behavior
`next()` scans linearly from `current` to `range.end`, returning the next index whose bit is set. It advances past every checked index, so each set bit is yielded once.

## Safety Notes
The file states the unsafe impls are safe because `FixedBitSet` is already `Sync` and `Send`. Since the iterator only holds an immutable reference plus owned range/current values, cross-thread sharing follows from the underlying bitset reference being safe.

## Research Notes
This is a simple range filter over `FixedBitSet`; it does not use bitset-internal fast search primitives, so cost is proportional to the full range length, not the number of set bits.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/utils/ranged_bitset_iter.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/version.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/version.rs

## Purpose
Centralizes command-line version handling.

## Main Components
- `tools_version!` macro expands to `env!("CARGO_PKG_VERSION")`.
- `version_args(cmd)` adds an exclusive `-V`/`--version` boolean flag to a `clap::Command`.
- `display_version(matches)` checks the `VERSION` flag, writes the package version and newline to stdout, flushes, and exits with status 0.

## Behavior
Broken pipe and stdout write/flush errors are ignored deliberately. If the version flag is absent, `display_version()` returns normally.

## Dependencies and Interactions
This module depends on `clap` for argument definition and `std::io::Write` for output. It is meant to be reused by individual thin-provisioning tool binaries.

## Research Notes
The version flag uses the argument id `"VERSION"` and is exclusive, so it should short-circuit other command modes when present.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/version.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/write_batcher.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/write_batcher.rs

## Purpose
Provides a write-back batching layer for metadata block writes, combining allocation through a space map with queued block writes to an `IoEngine`.

## Main Components
- `WriteBatcher` owns:
  - shared `engine`,
  - shared/mutexed metadata `SpaceMap`,
  - `batch_size`,
  - queued `Block`s,
  - `allocations: RangeSet<u64>` recording allocated block numbers.
- `new()` constructs the batcher and preallocates the queue.
- `alloc()` allocates a metadata block and returns an uninitialized `Block::new(loc)`.
- `alloc_zeroed()` allocates and returns `Block::zeroed(loc)`.
- `clear_allocations()` swaps out and returns the allocation range set.
- `write()` checksums a block, updates an already queued block with the same location if present, otherwise flushes when full and appends the block.
- `read()` returns a copy of the most recent queued block for a location or reads through to the engine.
- `flush_()` writes a supplied queue via `engine.write_many()`.
- `flush()` drains and writes the current queue.
- `Drop` asserts that final flush succeeds.

## Behavior
The queue is write-coalescing for blocks still in memory: writing the same location again updates the latest queued copy rather than enqueueing a duplicate. Reads also observe queued writes before durable writes, preserving read-your-writes behavior.

Allocation tracking inserts each allocated block into a `RangeSet`, coalescing adjacent allocations. Comments note that allocations are a hint for potentially modified blocks because callers can later decrement/free blocks through the space map.

## Dependencies and Interactions
This file is used by metadata restore/rebuild paths that need block allocation and batched writes. It depends on project checksum block types, IO engine abstraction, and the metadata space-map trait.

## Research Notes
`flush_()` ignores per-block results inside the `Vec<io::Result<()>>` returned by `write_many()` and only propagates the outer IO error. `Drop` uses `assert!`, so a flush failure during destruction can panic.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/write_batcher.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/write_batcher/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/write_batcher/tests.rs

## Purpose
Tests `WriteBatcher` allocation tracking, out-of-space behavior, batched writes, write coalescing, and read-your-writes behavior.

## Main Components
- `MockEngine` implements `IoEngine` with `mockall`.
- `MockTestSpaceMap` implements both `RefCount` and `SpaceMap`.
- `NR_BLOCKS` is `65536`.
- `runs_out_of_space_should_fail()` allocates every block from a real `CoreSpaceMap` and verifies the next allocation fails.
- `allocated_ranges_should_be_coalesced()` returns shuffled block allocations from a mock space map, then verifies `RangeSet` coalesces them into `0..65536`.
- `writes_should_be_performed_in_batch()` expects three `write_many()` calls of 16 blocks after writing 48 blocks with batch size 16.
- `write_hit()` writes the same block twice, expects only one durable write, and verifies the second payload wins.
- `read_hit()` writes a block, reads it before flushing, and verifies the queued payload is returned.

## Behavior Under Test
The tests confirm:
- allocation failure surfaces as an error,
- `RangeSet` allocation tracking is independent of allocation order,
- full queues flush automatically,
- repeated writes to a queued block are coalesced,
- reads consult the queue before the engine.

## Dependencies and Interactions
The tests use `mockall`, `rand` shuffling and deterministic `SmallRng`, checksum block type `BT::NODE`, `CoreSpaceMap`, and IO buffer traits from the main IO engine abstraction.

## Research Notes
The batching test relies on `Drop` to flush final batches where applicable. The mock engine expectations focus on batch size and payload equivalence rather than testing per-block error propagation.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/write_batcher/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/xml.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/xml.rs

## Purpose
Provides shared XML attribute parsing and construction helpers used by thin metadata XML code and likely other XML readers/writers in the crate.

## Main Components
- `string_val()` unescapes an attribute value and returns it as `String`.
- `parse_val<T>()` parses raw attribute bytes as UTF-8 and then as `T`.
- `u64_val()`, `u32_val()`, and `bool_val()` specialize numeric/boolean parsing.
- `bad_attr()` returns a formatted error for unknown attributes.
- `check_attr()` unwraps required attributes or reports a missing-attribute error.
- `missing_attr()` formats the missing-attribute error.
- `mk_attr()` creates a `quick_xml::Attribute` from a byte key and displayable value.
- `mk_attr_()` formats a displayable value into owned bytes.

## Behavior
String values are XML-unescaped, while numeric and boolean values are parsed from raw attribute bytes. Writer helpers format values with `Display` and store them in owned byte buffers.

## Dependencies and Interactions
This file is the low-level companion to `thin/xml.rs`. It depends on `quick_xml` attribute and name types, `Cow`, `Display`, and `anyhow`.

## Research Notes
The error strings have minor formatting issues: unknown-attribute output joins `"attribute "` and `"in tag"` through an optional attribute-name fragment, and missing-attribute output omits the closing quote after the tag name. These are presentation issues, not parser behavior issues.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/xml.rs -->