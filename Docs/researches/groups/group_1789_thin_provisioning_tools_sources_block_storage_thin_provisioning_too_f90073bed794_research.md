# Group Research: group_1789_thin_provisioning_tools_sources_block_storage_thin_provisioning_too_f90073bed794

Scope checked against `Docs/research_subset_a.md`: `sources/block-storage/thin-provisioning-tools` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/report.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/report.rs

This file implements the shared reporting, logging, prompting, and progress-monitor abstraction used by thin-provisioning-tools commands.

Key elements:
- `LogLevel` models fatal, error, warning, info, and debug levels. `verbose_args()` adds a hidden `-v` count argument, and `parse_log_level()` maps verbosity count onto `LogLevel`.
- `ReportOutcome` records aggregate success/non-fatal/fatal state. `combine()` preserves the worst outcome seen.
- `Report` wraps a `ReportInner` behind mutexes, making report output safe to share across worker threads via `Arc<Report>`.
- `ReportInner` defines the output surface: titles, subtitles, progress, log messages, stdout-forced output, completion, and interactive prompt input.
- `PBInner` uses `indicatif::ProgressBar`, including suspend/resume around prompt input.
- `SimpleInner` emits to stderr and throttles progress messages to once every five seconds.
- `QuietInner` suppresses output and returns empty prompt input.
- `ProgressMonitor` spawns a background thread that polls a processed-count closure every 500 ms and reports percentage progress.

Interactions:
- Used by `thin/check.rs`, `thin/ls.rs`, `thin/dump.rs`, `thin/repair.rs`, `thin/restore.rs`, migration code, and devtools.
- `Report::to_stdout()` is intentionally separate from normal logging for parseable command output such as `TRANSACTION_ID=...`.

Risks and notes:
- `ProgressMonitor::new()` computes `processed() * 100 / total`; callers must avoid `total == 0`.
- Mutex poisoning uses `unwrap()`, so panics inside report users can cascade.
- `QuietInner::get_prompt_input()` silently returns empty input, which is appropriate only for noninteractive paths.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/report.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/run_iter.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/run_iter.rs

This file provides `RunIter`, a compact iterator over boolean runs in a `RoaringBitmap`.

Key elements:
- `RunIter { len, current, bits }` walks the index space `0..len`.
- Each `next()` returns `(bool, Range<u32>)`, where the boolean is whether the range is present in the bitmap.
- Consecutive equal membership values are coalesced into one range.
- Unit tests cover empty input, all-false input, alternating false/true regions, and trailing false runs.

Interactions:
- This is a general utility for converting sparse bitmap state into contiguous runs.
- It depends on the `roaring` crate.

Risks and notes:
- The iterator checks `bits.contains()` at every position, so runtime is linear in `len`, not in compressed bitmap cardinality.
- It assumes `len` fits in `u32`, matching `RoaringBitmap`’s key type.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/run_iter.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/shrink/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/shrink/mod.rs

This file only declares the shrink toplevel module:

- `pub mod toplevel;`

It has no logic of its own. Its purpose is to expose `src/shrink/toplevel.rs` to the crate module tree.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/shrink/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/shrink/toplevel.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/shrink/toplevel.rs

This file implements range-remapping helpers for shrinking or relocating block ranges.

Key elements:
- `BlockRange = Range<u64>` and `range_len()` provide basic block-range utilities.
- `build_remaps(ranges, free)` maps source ranges into available free ranges, splitting source ranges when needed.
- It returns `Err("Insufficient free space")` if the free ranges cannot cover all requested input ranges.
- `find_first()` performs a binary search over sorted remaps to locate the first overlapping remap.
- `remap(r, remaps)` maps an input range through sorted `(from_range, to_start)` remap rules, preserving unmapped gaps as original ranges.

Tests:
- `build_remaps` tests cover one-to-one, one-to-many, many-to-one, many-to-many, empty/noop, exact-fit, insufficient-space, and boundary-value cases.
- `remap_test` covers no remaps, before/after remap ranges, partial overlaps, full overlaps, and multiple remap strides.

Interactions:
- This is a pure helper module with no I/O.
- Remaps must be sorted by `from.start` for `remap()` correctness.

Risks and notes:
- `build_remaps()` assumes callers supply non-overlapping, meaningful ranges. It does not validate ordering or overlap.
- `remap()` relies on sorted remaps and does not enforce that precondition.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/shrink/toplevel.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/block_time.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/block_time.rs

This file defines the on-disk value type for thin mapping btrees.

Key elements:
- `BlockTime { block: u64, time: u32 }` stores a data block number and a 24-bit mapping time.
- `Unpack::disk_size()` returns 8 bytes.
- `unpack()` reads a little-endian `u64`, extracts the high 40 bits as `block`, and the low 24 bits as `time`.
- `Pack::pack()` writes `(block << 24) | time`.
- `Display` formats as `<block> @ <time>`.

Interactions:
- Used throughout mapping tree traversal, dump, restore, check, ls, delta, rmap, and migration metadata iteration.

Risks and notes:
- `time` is not range-checked before packing; values above 24 bits would overlap the encoded block field.
- `block << 24` assumes block numbers fit in the remaining 40 bits of the on-disk format.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/block_time.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/check.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/check.rs

This is the main thin metadata consistency checker. It verifies superblock roots, device/details consistency, mapping btrees, mapped-block counts, data space map counts, metadata space map counts, and optionally repairs leak-only space map discrepancies.

Key elements:
- `ThinCheckOptions` carries input path, engine options, `sb_only`, `skip_mappings`, `ignore_non_fatal`, `auto_repair`, `clear_needs_check`, root overrides, and report.
- `inc_superblock()` accounts for the primary superblock and metadata snapshot in the metadata reference aggregator.
- `NodeMap` records discovered btree nodes using packed type bits: none, leaf, internal, or error. It tracks internal child metadata, leaf nodes, and node-local errors.
- `LayerHandler` implements `ReadHandler` for internal btree layers. It verifies checksums, unpacks internal nodes, records children, increments metadata reference counts, and batches node-map updates.
- `read_internal_nodes()` walks mapping trees breadth/layer-wise to reduce seek-heavy depth-first behavior.
- `examine_leaf_()` validates mapping-tree leaves: checksum, header fields, value size, max entries, block number, entry count, key order, padding, and data-block bounds.
- `LeafHandler` reads leaves in batches, increments the data reference aggregator for valid mappings, and stores `NodeSummary`.
- `summarize_tree()` and `count_mapped_blocks()` verify parent key ranges, underfull nodes, ordering, overlap, and aggregate mapping counts per tree.
- `check_mapped_blocks()` compares computed mapping counts against `DeviceDetail.mapped_blocks`.
- `get_thins_from_superblock()` loads and cross-checks top-level mapping roots and device details.
- `get_thins_from_metadata_snap()` handles metadata snapshots, including devices exclusive to the snapshot.
- `compare_space_maps()` diffs reconstructed aggregators against on-disk space maps, distinguishing leaks from bad reference counts.
- `check()` orchestrates the full command, including optional `clear_needs_check_flag()` and leak repair via `repair_space_map()`.
- `check_with_maps()` exposes validated metadata/data aggregators for callers that need allocated-block maps.

Interactions:
- Depends heavily on pdata btree, btree utilities, space map aggregators/loaders/repairers, superblock parsing, `DeviceDetail`, `BlockTime`, and `Report`.
- Uses background futures to read on-disk data and metadata space maps while mapping traversal runs.
- Uses `ProgressMonitor` for combined metadata/data scanning progress.

Risks and notes:
- Fixed worker counts (`NR_THREADS = 4`, `NR_UNPACKERS = 4`) are hard-coded.
- Several thread closures ignore errors during internal-node collection, deferring detection to later node summaries.
- Non-fatal checking mode changes structural validation, especially underfull and max-entry divisibility checks.
- Auto-repair only handles leak-style discrepancies; bad reference counts remain fatal.
- The metadata snapshot path intentionally avoids comparing on-disk space maps.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/check.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/damage_generator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/damage_generator.rs

This devtool file creates controlled thin metadata damage.

Key elements:
- `SuperblockOverrides` can override `mapping_root`, `details_root`, and `metadata_snapshot`.
- `override_superblock()` reads the superblock, applies requested root/snapshot overrides, and writes it back.
- `DamageOp` supports:
  - `CreateMetadataLeaks { nr_blocks, expected_rc, actual_rc }`
  - `OverrideSuperblock(SuperblockOverrides)`
- `ThinDamageOpts` carries engine options, selected operation, and output path.
- `damage_metadata()` opens the output metadata writable, reads the superblock and metadata space map root, then dispatches to either metadata leak creation or superblock override.

Interactions:
- Uses devtools `create_metadata_leaks()`.
- Uses `EngineBuilder`, `SMRoot`, `unpack`, and thin superblock helpers.
- Compiled only when devtools are enabled via `thin/mod.rs`.

Risks and notes:
- This intentionally corrupts metadata and should only be used for test/dev workflows.
- It directly writes superblock root fields without validating the resulting metadata graph.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/damage_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/delta.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/delta.rs

This file implements `thin_delta`: comparing mappings from two snapshots/devices/roots and emitting XML delta output.

Key elements:
- Local `RunBuilder` coalesces adjacent mappings where thin blocks and data blocks advance together.
- `MappingRecorder` implements `NodeVisitor<BlockTime>` and records contiguous `DataMapping` runs from a mapping tree.
- `get_mappings(engine, root)` walks a mapping tree and returns coalesced data mappings.
- `MappingStream` wraps a mapping iterator and supports partial consumption of a run.
- `dump_delta_mappings(left, right, visitor)` performs the core merge-style comparison:
  - `LeftOnly`
  - `RightOnly`
  - `Same`
  - `Differ`
- `dump_diff()` resolves `Snap::DeviceId` through the top-level mapping tree or accepts `Snap::RootBlock` directly, builds output superblock IR, emits diff begin/end events, and streams deltas to a `DeltaVisitor`.
- `ThinDeltaOptions` selects input metadata, engine options, report, two snapshots, and verbose XML mode.
- `delta()` opens metadata, reads current or snapshot superblock, validates superblock consistency, selects simple or verbose XML writer, and emits the diff.

Interactions:
- Uses `delta_visitor.rs` for delta model and XML writers.
- Uses `metadata_repair::is_superblock_consistent()` before comparing.
- Uses `btree_to_map::<u64>()` to resolve device IDs to mapping roots.
- Uses `SMRoot` to populate `nr_data_blocks` in output IR.

Risks and notes:
- Mapping timestamps are ignored by design; comparison is based on data block addresses.
- The algorithm assumes mapping vectors are ordered by thin block, as produced by btree walking.
- Errors such as missing roots are reported as command failures.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/delta.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/delta/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/delta/tests.rs

This file contains unit tests for delta run construction and delta comparison.

Key elements:
- `DeltaCollector` implements `DeltaVisitor` and stores all received `Delta` values.
- `test_build_runs_()` drives the private `RunBuilder` with keys/data values and compares emitted `DataMapping` runs.
- `test_build_runs()` verifies adjacent mapping coalescing and split runs.
- `test_delta()` builds left/right `DataMapping` inputs, converts compact tuple expectations into `Delta` variants, runs `dump_delta_mappings()`, and compares exact output.

Covered cases:
- Left input ending after right input.
- Right input ending after left input.
- Same regions.
- Left-only and right-only gaps.
- Differing mappings over the same thin-block range.

Interactions:
- Tests private implementation via `use super::*`.
- Uses `ir::Visit` only to satisfy the `DeltaVisitor` trait.

Risks and notes:
- Tests focus on in-memory merge behavior, not btree walking, XML serialization, or device/root resolution.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/delta/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/delta_visitor.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/delta_visitor.rs

This file defines the delta data model, visitor trait, and XML writers for `thin_delta`.

Key elements:
- `DataMapping` describes a same-side run: thin begin, data begin, length.
- `DiffMapping` describes equal thin range mapped to different left/right data blocks.
- `Delta` variants are `LeftOnly`, `RightOnly`, `Differ`, and `Same`.
- `Snap` identifies either a `DeviceId` or explicit `RootBlock`.
- `DeltaVisitor` defines superblock, diff, and delta callbacks.
- `DeltaRunBuilder` merges adjacent deltas of the same type when thin ranges are adjacent.
- `SimpleXmlWriter` emits compact empty tags such as `<left_only begin=... length=.../>`.
- `VerboseXmlWriter` groups deltas by type tag and emits `<range>` children with data block fields.
- Shared XML helpers emit `<superblock>` and `<diff>` begin/end tags.

Interactions:
- Used by `thin/delta.rs` and its tests.
- Uses `quick_xml::Writer` and repository XML attribute helper `mk_attr()`.
- Consumes `thin::ir::Superblock` for superblock output.

Risks and notes:
- `DeltaRunBuilder` merges by delta type and thin adjacency only; for `Differ` and same-side mappings it does not verify data-address adjacency before extending the run. This matches compact reporting by thin range, but verbose users should note that a merged range may hide internal data discontinuities if upstream emits such deltas.
- XML writers return `Visit::Continue`; stop behavior is not used here.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/delta_visitor.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/device_detail.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/device_detail.rs

This file defines the on-disk value type for the thin device details btree.

Key elements:
- `DeviceDetail` fields:
  - `mapped_blocks: u64`
  - `transaction_id: u64`
  - `creation_time: u32`
  - `snapshotted_time: u32`
- `Display` prints all four fields in a compact diagnostic form.
- `Unpack::disk_size()` returns 24 bytes.
- `unpack()` reads the fields little-endian.
- `Pack::pack()` writes the fields little-endian.

Interactions:
- Used by check, ls, dump, restore, repair, migration metadata, and metadata repair root inference.
- Stored in the device details btree keyed by thin device ID.

Risks and notes:
- It is a simple POD-style disk structure; validation of semantic consistency is done by callers.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/device_detail.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/dump.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/dump.rs

This file implements metadata dumping to XML or human-readable output.

Key elements:
- `RunBuilder` coalesces adjacent `ir::Map` entries when thin block, data block, and time are contiguous/equal.
- `MappingVisitor` walks mapping leaves and emits coalesced `map` callbacks to a `MetadataVisitor`.
- `OutputVisitor` wraps a metadata visitor and adds output context to visitor errors.
- `OutputFormat` parses `"xml"` and `"human_readable"`.
- `ThinDumpOptions` controls input/output paths, engine options, repair mode, skip mappings, superblock overrides, selected devices, and format.
- `emit_leaf()` verifies a metadata block is a btree node, unpacks a mapping leaf, and emits its mappings.
- `read_for()` reads blocks in engine batch-size chunks.
- `emit_entries()` handles metadata entries as either leaf blocks or shared-definition references.
- `to_superblock_ir()` converts on-disk or rebuilt in-core superblocks into output IR.
- `dump_metadata()` emits full metadata IR: superblock, shared defs, devices, mapping leaves, and EOF.
- `dump_with_formatter()` reads or rebuilds the superblock, builds metadata with or without mappings, optimizes shared definitions, and dumps it.
- `dump()` selects writer target and formatter.

Interactions:
- Uses `metadata.rs` to build and optimize metadata.
- Uses `metadata_repair.rs` when `repair` mode asks for `read_or_rebuild_superblock()`.
- Uses `xml::XmlWriter` or `HumanReadableWriter`.
- Reads mapping leaves through `IoEngine`.

Risks and notes:
- `emit_leaf()` requires leaf blocks; internal blocks in entry lists are treated as errors.
- `skip_mappings` still emits device metadata but no mapping entries.
- Repair mode can dump from rebuilt superblock state, which may be heuristic if original superblock is corrupt.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/dump.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/human_readable_format.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/human_readable_format.rs

This file implements a human-readable metadata writer over the common `MetadataVisitor` interface.

Key elements:
- `HumanReadableWriter<W: Write>` owns a writer.
- `superblock_b()` prints a single `begin superblock` line with uuid, time, transaction, flags, version, data block size, number of data blocks, and optional metadata snapshot.
- `device_b()` prints device ID, mapped block count, transaction, creation time, and snapshot time.
- `map()` prints thin/data ranges and mapping time.
- `ref_shared()` prints shared subtree references.
- `eof()` flushes the writer.
- Uses metadata version `2` as the default if IR does not provide one.

Interactions:
- Selected by `thin/dump.rs` when output format is `human_readable`.
- Implements `thin::ir::MetadataVisitor`.

Risks and notes:
- `map()` computes `m.thin_begin + m.len - 1`; zero-length maps would underflow, though map producers normally avoid zero-length entries.
- This is output-only and does not provide a parser.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/human_readable_format.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/ir.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/ir.rs

This file defines the thin metadata intermediate representation and visitor interface.

Key elements:
- `Superblock` IR includes uuid, time, transaction, optional flags/version, data block size, number of data blocks, and optional metadata snapshot.
- `Device` IR includes device ID, mapped blocks, transaction, creation time, and snapshot time.
- `Map` IR describes a logical thin range mapped to a data range with time and length.
- `Visit` is `Continue` or `Stop`.
- `MetadataVisitor` defines callbacks for:
  - superblock begin/end
  - shared definition begin/end
  - device begin/end
  - map
  - shared reference
  - EOF

Interactions:
- Used as the common exchange layer between dump, restore, XML, human-readable formatting, metadata generation, and delta output.
- Visitors mostly return `Visit::Continue`; stop propagation is supported by the trait but not broadly used in these files.

Risks and notes:
- This IR is intentionally minimal and trusts producers for ordering and validity constraints.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/ir.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/ls.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/ls.rs

This file implements `thin_ls`, listing thin devices and optionally computing mapped, shared, exclusive, and highest-mapped usage fields.

Key elements:
- `OutputField` enumerates supported columns: device ID, mapped/exclusive/shared/highest in blocks, sectors, bytes, pretty units, and device timestamps/transaction.
- `FromStr` parses field names such as `DEV`, `MAPPED_BLOCKS`, `EXCLUSIVE`, and `SNAP_TIME`.
- `LsTable` formats rows with `GridLayout`, converting block counts to sectors/bytes using data block size and `SECTOR_SHIFT`.
- The btree traversal machinery mirrors `thin/check.rs` but uses `RestrictedTwoAggregator` and `HashVec` to track reference counts and summaries.
- `NodeSummary` includes `nr_shared` in addition to mapping counts and key ranges.
- `read_internal_nodes()`, `collect_nodes_in_use()`, `read_leaf_nodes()`, and `count_mapped_blocks()` discover and summarize mapping btrees.
- `examine_leaf_()` initially treats all leaf mappings as shared until exclusive leaves can be revisited.
- `read_exclusive_leaves()` identifies metadata leaves with reference count 1 and recomputes shared data block counts using data refcounts.
- `count_data_mappings()` loads device mapping roots, initializes restricted metadata/data aggregators, monitors progress, and returns summaries per root.
- `ls()` validates metadata consistency, reads device details, decides whether expensive counting is required, and renders output.

Interactions:
- Uses `is_superblock_consistent()` before listing.
- Uses `btree_to_map::<DeviceDetail>()` for device details.
- Uses `btree_to_value_vec()` to collect mapping roots.
- Shares many concepts with `thin/check.rs`, but computes reporting stats instead of repair decisions.

Risks and notes:
- Counting fields trigger a full mapping scan; metadata-only fields avoid that cost.
- Device details are zipped with mapping summaries; this relies on consistent btree ordering and prior superblock consistency.
- Hard-coded worker counts and batch sizes mirror the checker.
- If metadata contains errors during counting, the command fails rather than rendering partial usage.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/ls.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata.rs

This file builds and optimizes an in-memory representation of thin metadata from on-disk or rebuilt superblock state.

Key elements:
- `Entry` is either a concrete mapping leaf block or a shared-definition reference.
- `Mapping` holds a `KeyRange` and ordered entries.
- `Device`, `Def`, and `Metadata` model devices, shared definitions, and full metadata.
- `CoreSuperblock` represents a rebuilt in-core superblock with explicit device mapping/detail data.
- `ThinSuperblock` is either `OnDisk(Superblock)` or `InCore(CoreSuperblock)`.
- `CollectLeaves` implements `LeafVisitor<BlockTime>`, recording leaf visits and repeated visits as `Entry::Ref`.
- `collect_leaves()` walks mapping roots with a `RestrictedSpaceMap` to detect reused leaves.
- `build_metadata_with_dev()` loads device roots/details from on-disk btrees or in-core devices, optionally filtering selected devices.
- `build_metadata_without_mappings()` emits device details with empty maps.
- `Gatherer` from `runs.rs` is used to identify shared atomic leaf runs.
- `optimise_metadata()` builds shared `Def` entries and rewrites device entry lists to use refs for shared runs.

Interactions:
- Used by dump and repair.
- Depends on btree walkers, leaf walkers, space maps, `BlockTime`, `DeviceDetail`, and superblock types.

Risks and notes:
- Several `FIXME` comments note incomplete `KeyRange` handling.
- `entry_map.get(&root).unwrap()` assumes every mapping root was successfully collected.
- Optimization is leaf/run based; actual map content emission still happens later when dump reads those leaf blocks.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_generator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_generator.rs

This devtools file sketches metadata generation and simple metadata mutation operations.

Key elements:
- `MetadataGenerator` trait emits metadata into a `MetadataVisitor`.
- `ThinGenerator` currently implements `generate_metadata()` as a TODO stub returning `Ok(())`.
- `format()` creates a core metadata space map, write batcher, and quiet `Restorer`, then asks `ThinGenerator` to generate metadata.
- `set_needs_check()` reads the superblock, toggles `needs_check`, and writes it back.
- `ThinFormatOpts` carries desired data block size and number of data blocks, but is not yet used.
- `MetadataOp` supports `Format(ThinFormatOpts)` and `SetNeedsCheck(bool)`.
- `generate_metadata()` opens the output writable and dispatches by operation.

Interactions:
- Uses `Restorer` as the write path for generated metadata.
- Exposed only under the `devtools` feature.

Risks and notes:
- Formatting is not functionally implemented because `ThinGenerator` emits no superblock/devices/EOF.
- `ThinFormatOpts` is currently ignored.
- The useful implemented operation is setting/clearing `needs_check`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair.rs

This file contains superblock/root repair logic. It scans metadata blocks, infers plausible mapping and details roots, validates compatibility, and rebuilds usable superblock state when the on-disk superblock is corrupt or inconsistent.

Key elements:
- `SuperblockOverrides` lets callers override transaction ID, data block size, and number of data blocks.
- `devices_identical()` checks that mapping top-level and details trees have identical thin IDs.
- `lower_bound()` and `upper_bound()` support finding details-root candidates by mapping count.
- `DevInfo`, `MappingsInfo`, and `DetailsInfo` summarize candidate btree subtrees.
- `NodeCollector` scans every metadata block:
  - verifies node blocks
  - classifies value sizes as top-level/mapping/details candidates
  - recursively gathers subtree summaries
  - tracks examined and referenced blocks
  - separates unreferenced roots into mapping-device and details candidates
- `compare_time_counts()` ranks mapping roots by newest mapping times and counts.
- `find_root_pairs()` pairs mapping and details candidates with matching device counts/mapping counts and identical device ID sets.
- `to_found_roots()` creates full on-disk root candidates.
- `to_partial_found_roots()` handles the case where mapping trees exist but details trees are missing by constructing in-core device details.
- `find_roots()` drives scanning and candidate pairing.
- `is_superblock_consistent()` checks normal superblock mapping/details root consistency.
- `is_superblock_consistent_()` checks whether an existing superblock matches found roots.
- `rebuild_superblock()` constructs either an on-disk or in-core `ThinSuperblock`, selecting data block size, transaction ID, data block count, and time from overrides, reference superblock, and inferred roots.
- `Override for Superblock` applies user overrides conservatively.
- `read_or_rebuild_superblock()` first tries the on-disk superblock, then falls back to rebuilt state.

Interactions:
- Used by `thin/dump.rs` repair mode and `thin/repair.rs`.
- Uses btree key-set/map helpers, `DeviceDetail`, `BlockTime`, `SMRoot`, and superblock pack/unpack helpers.

Risks and notes:
- Root recovery is heuristic when details trees are missing; in-core rebuilt details assume all devices are shared snapshots for data safety.
- `NodeCollector::collect_infos()` scans every block, which is expensive but appropriate for repair.
- Candidate selection uses `found_roots[0]` when rebuilding; logging exposes candidates for diagnosis, but automatic choice can matter.
- Overrides never shrink inferred transaction/data block counts below recovered values.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair/sorting_roots_tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair/sorting_roots_tests.rs

This file tests `compare_time_counts()` from metadata repair.

Covered cases:
- Empty left versus non-empty right sorts after right.
- Non-empty left versus empty right sorts before right.
- Two empty maps compare equal.
- Greater newest time on left sorts before right.
- Greater newest time on right sorts after right.
- Equal time but greater count on left sorts before right.
- Equal time but greater count on right sorts after right.

Interactions:
- Uses `super::*` to test private sorting behavior.
- Supports candidate ordering in `find_root_pairs()`.

Risks and notes:
- Tests are focused on ordering only; they do not cover full root-pair selection.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_repair/sorting_roots_tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_size.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_size.rs

This file estimates required thin metadata size.

Key elements:
- `MIN_DATA_BLOCK_SIZE` is 64 KiB.
- `MAX_DATA_BLOCK_SIZE` is 1 GiB.
- `ThinMetadataSizeOptions` carries `nr_blocks` and `max_thins`.
- `check_data_block_size()` validates nonzero, multiple-of-64-KiB block size and maximum size.
- `metadata_size()` estimates bytes by:
  - taking half of max mapping leaf capacity as assumed residency
  - computing mapping leaf count with `div_up`
  - adding one superblock and one root per max thin
  - capping metadata blocks at `MAX_METADATA_BLOCKS`
  - multiplying by metadata `BLOCK_SIZE`

Interactions:
- Uses `calc_max_entries::<BlockTime>()` to estimate mapping entries per node.

Risks and notes:
- This is an estimate, not an exact allocator simulation.
- `ThinMetadataSizeOptions` uses `nr_blocks`, but data block size validation is separate.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/metadata_size.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/base.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/base.rs

This file implements thin-device migration orchestration: opening source/destination devices, generating copy streams, and copying mapped regions.

Key elements:
- `DEFAULT_BUFFER_SIZE` is 131,072 sectors, documented as 64 MiB.
- `SourceArgs` carries source path and optional delta ID.
- `DestArgs` distinguishes destination block device versus file.
- `ThinMigrateOptions` carries source, destination, zeroing flag, buffer size, and report.
- `open_source()`:
  - opens the thin source read-only with `O_DIRECT`
  - resolves it to a device-mapper name
  - reads thin and pool tables
  - resolves pool metadata device path
  - requires the thin device to be read-only
  - creates a `ThinStream` from the metadata snapshot and thin ID
- `open_dest_dev()` opens destination block device with `O_EXCL | O_DIRECT`, verifies it is a block device, and checks size.
- `open_dest_file()` creates/truncates a regular file to expected size or checks block-device size.
- `copy_regions()` creates vectored block I/O, a `SyncCopier`, `CopyOpBatcher`, threaded copier, and progress reporter. It turns stream `Copy` chunks into same-offset copy operations.
- `migrate()` wires the scanner, source, destination, buffer size, and copy loop.

Interactions:
- Uses `devices.rs` to inspect device-mapper topology.
- Uses `stream.rs` for copy/skip chunks.
- Uses copier infrastructure for batched threaded copying.

Risks and notes:
- `zero_dest` is present in options but unused in this file.
- `SourceArgs.delta_id` is present but not used; `Discard` chunks are still `todo!()`.
- Source must be a read-only thin device; this protects consistency during migration.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/base.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/devices.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/devices.rs

This file provides Linux device-mapper and udev helpers for thin migration.

Key elements:
- `split_device_number()` splits `rdev` into major/minor using an 8-bit minor mask.
- `DeviceNr` represents a block device major/minor pair and can be created from `rdev` or devicemapper `Device`.
- `DmIndex` builds a map from `DeviceNr` to DM names using `DM::list_devices()`.
- `PoolTable` captures thin-pool metadata device, data device, and data block size.
- `ThinTable` captures pool device and thin ID.
- `parse_dev()`, `parse_thin_table()`, and `parse_pool_table()` parse DM table argument strings with `nom`.
- `DmInfo` converts from devicemapper `DeviceInfo` and exposes name, uuid, dev number, open count, event number, and flags.
- `DmScanner` owns a `DM` handle and index, and provides:
  - `get_table()`
  - `get_info()`
  - `dev_to_name()`
  - `file_to_name()`
  - `dev_to_path()` via udev enumeration
- Public helpers return parsed thin table, pool table, and device info.

Interactions:
- Used by migration base code.
- Depends on `devicemapper`, `udev`, Unix file metadata, and `nom`.

Risks and notes:
- `split_device_number()` uses a simple 8-bit minor mask, which may not match Linux’s full modern `dev_t` major/minor encoding for all devices.
- `DmIndex` is built once and can go stale if DM devices change.
- `get_table()` requires exactly one target row.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/devices.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/metadata.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/metadata.rs

This file reads thin metadata needed for migration streams.

Key elements:
- `ArcEngine` aliases shared `IoEngine`.
- `read_by_thin_id()` performs a btree lookup by thin ID and returns a cloned unpacked value, or errors if missing.
- `read_device_detail()` reads a `DeviceDetail` from the details tree.
- `read_mapping_root()` reads the per-thin mapping tree root from the top-level mapping tree.
- `ThinIterator` stores thin ID, data block size, a `BTreeIterator<BlockTime>`, and mapped block count.
- `ThinIterator::new()` reads the metadata snapshot superblock, finds the device detail and mapping root for the thin ID, and constructs a mapping iterator.

Interactions:
- Used by `ThinStream` in `stream.rs`.
- Uses `read_superblock_snap()`, so migration reads a metadata snapshot rather than live mutable roots.

Risks and notes:
- Missing metadata snapshot or missing thin ID fails stream construction.
- The iterator depends on mapping btree ordering.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/mod.rs

This file declares and re-exports migration submodules:

- `pub mod base;`
- `pub mod devices;`
- `pub mod metadata;`
- `pub mod stream;`
- `pub use base::*;`

It makes the high-level migration API from `base.rs` available through the `thin::migrate` module.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/stream.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/stream.rs

This file defines migration stream abstractions and implementations.

Key elements:
- `ChunkContents` is `Copy`, `Skip`, or `Discard`.
- `Chunk` stores offset, length, and contents.
- `Stream` trait provides `next_chunk()` and `size_hint()`.
- `DevStream` emits a single `Copy` chunk covering an entire file/device.
- `ThinStream` wraps `ThinIterator` and emits:
  - `Copy` chunks for contiguous mapped thin blocks
  - `Skip` chunks for gaps before the next mapped thin block
  - `None` at end of mappings
- `ThinStream::contiguous_run()` advances the btree iterator through adjacent logical thin blocks.
- A `DeltaStream` sketch exists only inside a block comment.

Interactions:
- `ThinStream` is used by migration copy logic in `base.rs`.
- Uses `ThinIterator` from `metadata.rs`.

Risks and notes:
- `ChunkContents::Discard` exists but no active stream emits it in this file.
- `ThinStream::size_hint()` reports mapped data size, not full virtual device size.
- Offsets and lengths are based on metadata data block size units as used by migration copy code.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/migrate/stream.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/mod.rs

This file declares the thin module tree.

Always included modules:
- `block_time`, `check`, `delta`, `delta_visitor`, `device_detail`, `dump`, `human_readable_format`, `ir`, `ls`, `metadata`, `metadata_repair`, `metadata_size`, `migrate`, `repair`, `restore`, `rmap`, `runs`, `shrink`, `superblock`, `trim`, `xml`

Feature-gated devtools modules:
- `metadata_generator`
- `damage_generator`
- `stat`

Interactions:
- Central module index for the thin-provisioning implementation.
- Determines which dev-only files are compiled behind the `devtools` feature.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/repair.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/repair.rs

This file implements high-level thin metadata repair by reading damaged input metadata and writing repaired output metadata.

Key elements:
- `ThinRepairOptions` carries input path, output path, engine options, report, and superblock overrides.
- `new_context()` opens the input read-only and output writable.
- `repair()`:
  - reads or rebuilds superblock state via `read_or_rebuild_superblock()`
  - builds metadata from input using `build_metadata()`
  - optimizes shared metadata definitions with `optimise_metadata()`
  - creates output metadata space map and `WriteBatcher`
  - creates a `Restorer`
  - calls `dump_metadata()` to replay the rebuilt metadata into the output

Interactions:
- Combines `metadata_repair`, `metadata`, `dump`, and `restore`.
- Uses the same visitor pipeline as dump/restore, but source and destination are metadata devices.

Risks and notes:
- Repair quality depends on `read_or_rebuild_superblock()` root inference if the original superblock is corrupt.
- It writes to a separate output metadata device/file rather than modifying input in place.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/repair.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/restore.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/restore.rs

This file restores thin metadata from XML/IR into an output metadata device.

Key elements:
- `MappingRC` implements `RefCounter<BlockTime>` backed by a data `SpaceMap`, maintaining data block reference counts while btrees are built.
- `MappedSection` identifies the current mapping section as a shared definition or device.
- `Restorer` implements `MetadataVisitor` and owns restore state:
  - write batcher
  - report
  - shared subtree definitions
  - current map builder
  - current device details
  - source superblock IR
  - built devices
  - data space map
  - parser section state
  - superblock overrides
- `begin_section()` creates a `NodeBuilder<BlockTime>` for a def or device.
- `end_section()` completes the current node builder into btree node summaries.
- `build_device_details()` builds details and top-level mapping btrees.
- `release_subtrees()` drops temporary references held by prebuilt shared definitions.
- `finalize()` builds data space map, metadata space map, writes final superblock, and marks restore finalized.
- Visitor methods enforce ordering: one superblock, defs/devices inside superblock, maps only inside def/device, refs only inside device sections, and EOF after finalization.
- `restore()` opens input XML, creates output engine and write batcher, constructs a restorer with overrides, and parses XML into it.

Interactions:
- Used directly by `thin_restore`, indirectly by `repair.rs`, and by devtools metadata generation.
- Depends on btree builders, write batcher, disk/metadata space map writers, XML parser, and superblock packing.

Risks and notes:
- `map()` expands each run one block at a time into the node builder, so very large runs rely on builder efficiency.
- Shared definitions are prebuilt then released after devices reference them.
- Invalid section nesting/order is detected explicitly.
- Data block size validation requires 128..=2,097,152 sectors and 128-sector alignment.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/restore.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/rmap.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/rmap.rs

This file implements reverse mapping from physical data block ranges back to thin device/logical ranges.

Key elements:
- `RmapRegion` stores data begin/end, device ID, and thin begin.
- `RmapRegion::adjacent()` extends the current region only when device ID, data block, and thin block are contiguous.
- `RmapRegion::compare()` sorts output by data begin, data end, device ID, and thin begin.
- `RmapVisitor` implements `NodeVisitor<BlockTime>`:
  - current device ID is set before walking each device tree
  - mapping entries outside requested regions are ignored
  - adjacent entries are coalesced
- `ThinRmapOptions` carries input path, engine options, requested data regions, and report.
- `rmap()` reads the superblock, loads top-level mapping roots, walks each mapping tree with a restricted metadata space map, sorts completed reverse-map regions, and prints lines to stdout.

Interactions:
- Uses `btree_to_map::<u64>()` to find per-device roots.
- Uses `BTreeWalker::new_with_sm()` to avoid repeated metadata traversal issues.

Risks and notes:
- Region membership is checked by linear scan over requested ranges for every mapping entry.
- Output is text-only and sorted after collection.
- TODO notes mention possible multithreading; current implementation walks devices serially.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/rmap.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/runs.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/thin/runs.rs

This file implements `Gatherer`, which decomposes sequences of block IDs into atomic shared/non-shared runs.

Key elements:
- Internal `Entry` stores neighbor blocks in a `BTreeSet`.
- `Gatherer` tracks:
  - previous block in current sequence
  - head and tail bitsets
  - adjacency entries
  - reverse predecessor map
  - shared heads
- `new_seq()` terminates the previous sequence.
- `next(b)` records adjacency from previous block to `b`, marks heads, detects multiple predecessors, and marks shared nodes.
- `complete_heads_and_tails()` marks extra tails for branches/cycles and marks following blocks as heads.
- `extract_seq()` follows first neighbors from a head until a tail.
- `gather()` finalizes the last sequence and returns `(Vec<u64>, shared)` atomic runs.
- Unit tests cover empty input, simple runs, prefix/suffix sharing, overlapping runs, branches, and cycles.

Interactions:
- Used by `metadata.rs` to identify shared leaf runs and create reusable metadata definitions during dump/repair.

Risks and notes:
- `extract_seq()` follows the first sorted neighbor, so branch handling depends on prior tail/head splitting.
- Bitsets are allocated with `nr_entries`; callers must provide a capacity covering all block IDs used.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/thin/runs.rs -->