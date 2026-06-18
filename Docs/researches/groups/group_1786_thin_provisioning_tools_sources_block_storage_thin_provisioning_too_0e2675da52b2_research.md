# Group Research: thin-provisioning-tools subset A group 1786

Scope checked against `Docs/research_subset_a.md`: `sources/block-storage/thin-provisioning-tools` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools.rs

Primary production multiplexer binary for thin-provisioning-tools. It registers the normal public commands for cache, era, and thin metadata operations, then dispatches by command name.

Key behavior:
- Builds a `Vec<Box<dyn Command>>` containing `cache_check`, `cache_dump`, `cache_metadata_size`, `cache_repair`, `cache_restore`, `cache_writeback`, era check/dump/invalidate/repair/restore, and many thin commands.
- Strips the leading executable basename when invoked as `pdata_tools`, allowing `pdata_tools <command> <args>`.
- Also compares the next argument basename to each command name, so symlink-style invocation can work through path basenames.
- Prints a compact command list and returns `exitcode::USAGE` when no command or an unknown command is provided.

Dependencies are limited to `std::ffi::OsStr`, `std::path::Path`, `std::process::exit`, and `thinp::commands::*`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools_dev.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools_dev.rs

Development-tool multiplexer binary. It mirrors `pdata_tools.rs` but only exposes dev/debug commands gated elsewhere by feature configuration.

Key behavior:
- Registers synthetic metadata and damage-generation commands: `era_generate_metadata`, `cache_generate_metadata`, `cache_generate_damage`, `thin_generate_metadata`, `thin_generate_damage`.
- Registers exploratory/stat tooling: `thin_explore` and `thin_stat`.
- Strips the `pdata_tools_dev` executable basename and dispatches on the next basename.
- Emits usage and `exitcode::USAGE` for missing or unknown commands.

This file is intentionally small and delegates all command-specific parsing and execution to `thinp::commands::*`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/bin/pdata_tools_dev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/check.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/check.rs

Implements binary cache metadata validation. It checks the superblock, cache mappings, optional hints, discard bitset, and metadata space map, with limited repair support for metadata leaks and the `needs_check` flag.

Main structures:
- `CacheCheckOptions`: input device, engine options, skip flags, `ignore_non_fatal`, `auto_repair`, `clear_needs_check`, and report handle.
- `format1::MappingChecker`: validates v1 mappings, including valid/dirty flags, invalid entries, origin bounds, and duplicate origin blocks.
- `format2::MappingChecker`: validates v2 mappings with a separate checked dirty bitset, forbids dirty bits on unmapped blocks, validates origin bounds and duplicates.
- `HintChecker`: placeholder array visitor that currently accepts hint blocks without semantic checks.

Core flow:
- Opens an `IoEngine` with write access only when auto-repair or clearing `needs_check`.
- Reads cache superblock at `SUPERBLOCK_LOCATION` and rejects v2+ superblocks without a dirty bitset root.
- Infers origin block count from discard geometry only when clean shutdown and discard fields are populated.
- Walks mapping arrays with metadata space-map accounting, selecting v1 or v2 logic by `sb.version`.
- Walks hint array when present and policy hint width is 4 bytes.
- Walks discard bitset when present.
- If full checks ran, unpacks the metadata space-map root and detects leaks against observed metadata references.
- With `auto_repair` or `clear_needs_check`, repairs metadata leaks and clears `needs_check`.

Notable details:
- Unknown cache metadata versions error out.
- Hints are structurally walked but not semantically validated.
- Skip flags bypass metadata space-map leak checking because complete reference accounting requires all relevant roots.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/check.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/damage_generator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/damage_generator.rs

Development helper for deliberately corrupting cache metadata. It supports one operation: creating metadata space-map leaks.

Key elements:
- `DamageOp::CreateMetadataLeaks { nr_blocks, expected_rc, actual_rc }`.
- `CacheDamageOpts`: engine options, selected operation, and output path.
- `damage_metadata`: opens the output metadata device writable, reads the cache superblock, unpacks the metadata space-map root, and delegates to `devtools::damage_generator::create_metadata_leaks`.

This module is feature-oriented test/dev infrastructure, not a production repair path.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/damage_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/dump.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/dump.rs

Converts binary cache metadata into the cache intermediate representation, normally written as XML. It handles both cache metadata formats and can optionally tolerate/repair traversal errors while dumping.

Main components:
- `format1::MappingEmitter`: emits valid v1 mappings and records valid cache blocks in a `FixedBitSet`.
- `format2::MappingEmitter`: reads dirty state from a separate checked dirty bitset and emits valid v2 mappings.
- `HintEmitter`: emits hints only for cache blocks that had valid mappings.
- `OutputVisitor`: wraps another `MetadataVisitor` and adds output-context error handling.
- `CacheDumpOptions`: input path, optional output path, engine options, and repair flag.

Core flow:
- Reads the cache superblock.
- Emits an IR superblock containing block size, cache block count, policy name, and hint width.
- Emits mappings using v1 inline dirty flags or v2 dirty bitset.
- Emits hints filtered to valid mappings.
- Emits superblock end and EOF.
- `dump` writes XML to a requested output file or stdout via `cache::xml::XmlWriter`.

Notable details:
- v2 dump requires `dirty_root`; missing root is an error.
- If dirty bitset entries are damaged during repair-mode dumping, dirty defaults to true.
- Discard IR methods exist, but this dump path does not emit discard ranges.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/dump.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/hint.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/hint.rs

Defines the on-disk cache policy hint value type. It is a fixed 4-byte payload.

Key behavior:
- `Hint { hint: [u8; 4] }` is `Clone`, `Copy`, and `Default`.
- Implements `Unpack` with `disk_size() == 4`, copying the first four bytes from input.
- Implements `Pack` by writing each byte back in order.

This type is used by cache dump, restore, check, and metadata generation for policy hint arrays.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/hint.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/ir.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/ir.rs

Defines the cache metadata intermediate representation and visitor interface used between dump, XML, restore, and synthetic generation.

Types:
- `Superblock`: UUID string, block size, cache block count, policy name, hint width.
- `Map`: cache block, origin block, dirty flag.
- `Hint`: cache block plus arbitrary byte vector.
- `Discard`: begin/end range, although current cache dump/restore paths mostly ignore discards.
- `Visit`: `Continue` or `Stop`.
- `MetadataVisitor`: event-style callbacks for superblock, mappings, hints, discards, and EOF.

This abstraction decouples binary traversal from XML serialization and binary rebuild.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/ir.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/mapping.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/mapping.rs

Defines the on-disk cache mapping entry. Each entry packs an origin block and low-bit flags into one little-endian `u64`.

Key elements:
- `MAX_ORIGIN_BLOCKS = 1 << 48`.
- `MappingFlags`: `Valid = 1`, `Dirty = 2`.
- `Mapping { oblock: u64, flags: u32 }`.
- `is_valid`, `is_dirty`, and `set_dirty` helpers.

Encoding:
- On unpack, low 16 bits become flags and upper bits become `oblock`.
- On pack, writes `(oblock << 16) | flags`.
- `disk_size() == 8`.

This type is central to cache check, dump, restore, and writeback.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/mapping.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/metadata_generator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/metadata_generator.rs

Development module for generating synthetic cache metadata and mutating selected superblock fields.

Main types:
- `MetadataGenerator` trait with `generate_metadata`.
- `CacheGenerator`: block size, cache block count, origin block count, resident/dirty percentages, metadata version, hotspot size.
- `CacheFormatOpts`, `MetadataOp`, and `CacheGenerateOpts`.

Generation behavior:
- Emits an IR superblock with policy `smq` and 4-byte hints.
- Chooses resident cache blocks randomly.
- Chooses origin blocks in randomly placed hotspot runs, then pairs origin blocks with cache blocks.
- Emits sorted mappings by cache block, with dirty state based on configured percentage.
- Emits default 4-byte hints for resident cache blocks.
- Restores generated IR into binary metadata through `cache::restore::Restorer`.

Mutation operations:
- Set `needs_check`.
- Set `clean_shutdown`.
- Set superblock version directly. Comments warn this does not convert formats and can intentionally create invalid/leaky metadata.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/metadata_generator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/metadata_size.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/metadata_size.rs

Estimates cache metadata device size and validates cache block size constraints.

Key behavior:
- Accepts `CacheMetadataSizeOptions { nr_blocks, max_hint_width }`.
- `check_cache_block_size` requires block size to be a nonzero multiple of 32 KiB and at most 1 GiB.
- `metadata_size` estimates:
  - 16 bytes per mapped cache block.
  - 4 MiB transaction overhead.
  - hint size as `nr_blocks * (max_hint_width + 8)`.
- Caps estimate at `MAX_METADATA_BLOCKS * BLOCK_SIZE`.

This is calculation-only and does no device I/O.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/metadata_size.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/mod.rs

Cache module declaration file.

Always exported:
- `check`, `dump`, `hint`, `ir`, `mapping`, `metadata_size`, `repair`, `restore`, `superblock`, `writeback`, `xml`.

Feature-gated under `devtools`:
- `metadata_generator`.
- `damage_generator`.

This file defines module availability boundaries for production versus development commands.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/repair.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/repair.rs

Implements cache metadata repair by dumping readable metadata and restoring it into a fresh output metadata device.

Main flow:
- `CacheRepairOptions`: input, output, engine options, report.
- Opens input read-only and output writable.
- Reads input cache superblock to preserve metadata version.
- Creates a fresh metadata space map and `WriteBatcher` for output.
- Constructs `cache::restore::Restorer` with the input version.
- Calls `dump_metadata(input_engine, restorer, sb, true)` so dump traversal runs in repair mode and feeds restore directly.

This is a binary-to-binary rebuild path through the cache IR visitor interface.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/repair.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/restore.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/restore.rs

Converts cache XML/IR into binary cache metadata. It owns the `Restorer` visitor used by `cache_restore`, `cache_repair`, and synthetic metadata generation.

Main structures:
- `CacheRestoreOptions`: input XML, output device, metadata version, engine options, report, and `omit_clean_shutdown`.
- `Restorer`: stateful `MetadataVisitor` with array builders for mappings, v2 dirty bitset, hints, discard root, pending roots, buffered dirty word, and section state.
- Internal `Section` state machine enforces superblock/mappings/hints/finalized ordering.

Restore behavior:
- On `superblock_b`, allocates the superblock block, initializes mapping and hint arrays, optionally initializes v2 dirty array, and creates an empty discard bitset root.
- On mapping, writes a valid `Mapping`; v1 stores dirty in mapping flags, v2 records dirty in a packed bitset.
- On hint, converts hint data to the fixed 4-byte `Hint`.
- On finalization, completes arrays, builds metadata space map, constructs binary `cache::superblock::Superblock`, and writes it at block 0.
- Discard visitor methods currently accept and ignore discard events.
- EOF requires prior finalization.

Notable details:
- `hint` uses `try_into().unwrap()` on hint data, so malformed XML hint widths can panic rather than return a structured error.
- Restored metadata uses zero discard geometry and an empty discard root.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/restore.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/superblock.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/superblock.rs

Defines cache superblock layout, parsing, validation by checksum type, and writing.

Key constants:
- `SPACE_MAP_ROOT_SIZE = 128`.
- `SUPERBLOCK_LOCATION = 0`.
- Cache metadata magic `0o6142003`.
- policy name size 16 bytes and UUID size 16 bytes.

Main types:
- `SuperblockFlags { clean_shutdown, needs_check }`.
- `Superblock`: flags, block/version, policy data, space-map root, mapping/dirty/hint/discard roots, discard geometry, block counts, compatibility flags, and hit/miss counters.

Read path:
- Reads a 4 KiB block.
- Requires `metadata_block_type` to report `BT::CACHE_SUPERBLOCK`.
- Parses little-endian fields with `nom`.
- Includes `dirty_root` only for version >= 2.
- Trims policy name at the first NUL byte.

Write path:
- Packs fields into a zeroed block at superblock location.
- Writes flags, zero UUID, magic, policy name, roots, geometry, counters, policy version.
- Writes optional dirty root if present.
- Computes cache superblock checksum and writes the block.

Notable detail: the read path checks checksum-derived block type but does not explicitly compare the parsed magic field.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/superblock.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/writeback.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/writeback.rs

Implements offline cache writeback: copy dirty blocks from fast/cache device back to origin device, then optionally clear dirty state in metadata.

Main components:
- `WritebackSelector` trait chooses which mapped cache blocks need copy.
- `V1Selector`: uses dirty bit in v1 mapping entries.
- `V2Selector`: uses separate dirty bitset loaded into `RoaringBitmap`.
- `AllSelector`: used after unclean shutdown to conservatively copy all valid mappings.
- `MappingCounter`: counts valid mappings matching a predicate.
- `WritebackBatcher`: walks mapping array and emits `CopyOp`s to a channel.
- `BitsetUpdater`: low-level cursor for clearing bits in the v2 on-disk dirty bitset.
- `ThreadedCopier`: runs copy batches in a worker thread and accumulates cleaned/read-failed/write-failed bitmaps.
- `CacheWritebackOptions`: metadata, origin, fast device paths, offsets, buffer size, failed-list flag, metadata-update flag, retries, report.

Copy strategy:
- Validates metadata version <= 2 and page-aligned offsets.
- Builds selector based on clean shutdown and metadata version.
- First tries vectored synchronous copy.
- Retries failed blocks with simple block I/O.
- Optionally retries with rescue copier for configured retry count.
- Tracks copied and failed cache blocks in roaring bitmaps.

Metadata update:
- v1 clears dirty flags in mapping array blocks and rewrites checksummed array blocks.
- v2 clears bits in the dirty bitset and rewrites checksummed array blocks.
- Reports fatal if not all blocks copied and returns an error.

Notable details:
- `list_failed_blocks` is stored in options but not used in this file.
- `BitsetUpdater` relies on monotonically increasing cleaned block iteration.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/writeback.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/xml.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/cache/xml.rs

Serializes and parses cache metadata XML using the cache IR visitor interface.

Writer behavior:
- `XmlWriter<W>` emits indented XML.
- Writes `<superblock>` with `uuid`, `block_size`, `nr_cache_blocks`, `policy`, `hint_width`.
- Writes `<mappings>` and empty `<mapping cache_block=... origin_block=... dirty=.../>` entries.
- Writes `<hints>` and empty `<hint cache_block=... data=.../>` entries, base64-encoding hint data.
- Includes discard writer methods for `<discards>` and `<discard>`, though the current dump path does not call them.
- Flushes on EOF.

Parser behavior:
- Parses superblock, mapping, and hint elements.
- Validates required attributes and rejects unknown attributes/tags.
- Decodes hint data from base64.
- Ignores text and comments.
- Calls visitor EOF on XML EOF and stops when visitor returns `Visit::Stop`.

Notable details:
- Parser does not handle discard XML tags despite writer methods existing for discards.
- Attribute iteration uses `unwrap()` on XML attributes, so malformed attributes can panic.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/cache/xml.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/checksum.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/checksum.rs

Central checksum helper for identifying and writing thin-provisioning metadata block checksums.

Key behavior:
- Computes CRC32C over bytes after the first checksum word and XORs with `0xffffffff`.
- Defines salted XOR constants for thin, cache, era superblocks, bitmap, index, btree node, and array blocks.
- `BT` enum classifies block types: thin/cache/era superblock, node, index, bitmap, array, unknown.
- `metadata_block_type` reads the on-disk first `u32`, recomputes checksum, XORs to identify the salt, and returns `BT`.
- `write_checksum` writes the checksum for a requested `BT` into the first word of a 4 KiB block.

Notable details:
- Requires exact 4096-byte buffers for both read classification and checksum writing.
- Rejects `BT::UNKNOWN` when writing.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/checksum.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_check.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_check.rs

Clap command wrapper for `cache_check`.

CLI:
- Flags: `--auto-repair`, `--clear-needs-check-flag`, `--ignore-non-fatal-errors`, `--quiet`, `--super-block-only`, `--skip-hints`, `--skip-discards`, `--skip-mappings`.
- Positional input metadata device/file.
- Adds version, verbose, and hidden engine-selection args.

Runtime behavior:
- Builds report and parses log level.
- Validates input exists, is a file/block device, is at least one block, and does not look like XML.
- Parses cache `EngineOptions`.
- Constructs `CacheCheckOptions` and delegates to `cache::check::check`.
- Converts errors through shared `to_exit_code`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_check.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_dump.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_dump.rs

Clap command wrapper for `cache_dump`.

CLI:
- `--repair` / `-r` to repair while dumping.
- `--output` / `-o FILE` for XML output, otherwise stdout.
- Positional input metadata device/file.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses cache engine options.
- Builds `CacheDumpOptions` and calls `cache::dump::dump`.
- Uses a simple report only for validation/errors.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_dump.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_damage.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_damage.rs

Development command wrapper for deliberate cache metadata damage generation.

CLI:
- Required command group currently only `--create-metadata-leaks`.
- Leak options: `--expected REFCONT`, `--actual REFCOUNT`, `--nr-blocks NUM`.
- Required output device `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses cache engine options.
- Converts selected command into `DamageOp::CreateMetadataLeaks`.
- Calls `cache::damage_generator::damage_metadata`.
- Uses `process::exit(1)` for impossible/unknown command match fallback.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_damage.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_metadata.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_metadata.rs

Development command wrapper for synthetic cache metadata generation and superblock mutation.

CLI command group:
- `--format`.
- `--set-superblock-version NUM`.
- `--set-needs-check[=BOOL]`.
- `--set-clean-shutdown[=BOOL]`.

Format options:
- `--cache-block-size` sectors, default 128.
- `--hotspot-size`, default 1.
- `--nr-cache-blocks`, default 10240.
- `--nr-origin-blocks`, default 1048576.
- `--percent-dirty`, default 50.
- `--percent-resident`, default 80.
- `--metadata-version` restricted to 1 or 2, default 2.
- Required `--output/-o`.

Runtime behavior:
- Parses cache engine options.
- Converts selected operation into `MetadataOp`.
- Delegates to `cache::metadata_generator::generate_metadata`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_generate_metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_metadata_size.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_metadata_size.rs

Command wrapper for estimating cache metadata size.

CLI:
- Requires either `--nr-blocks NUM` or both `--device-size SIZE` and `--block-size SIZE`.
- `--max-hint-width BYTES`, default 4.
- `--unit`, default sector.
- `--numeric-only[=short|long]`.
- Adds version args.

Runtime behavior:
- Converts device size/block size into cache block count via `div_up`.
- Validates cache block size with `check_cache_block_size`.
- Rejects device size smaller than block size.
- Calls `cache::metadata_size::metadata_size`.
- Formats output as full unit text, short suffix, long unit suffix, or raw numeric value.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_metadata_size.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_repair.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_repair.rs

Command wrapper for `cache_repair`.

CLI:
- Required `--input/-i FILE`.
- Required `--output/-o FILE`.
- `--quiet`.
- Hidden dummy positional for `lvconvert` compatibility.
- Adds verbose, version, and engine args.

Runtime behavior:
- Builds report and parses verbosity.
- Validates input exists, is not tiny, and output exists/is large enough.
- Parses cache engine options.
- Constructs `CacheRepairOptions` and delegates to `cache::repair::repair`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_repair.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_restore.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_restore.rs

Command wrapper for converting cache XML metadata to binary metadata.

CLI:
- Required `--input/-i FILE`.
- Required `--output/-o FILE`.
- `--metadata-version` restricted to 1 or 2, default 2.
- `--omit-clean-shutdown`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists and output exists/is large enough.
- Parses cache engine options.
- Builds `CacheRestoreOptions` and calls `cache::restore::restore`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_restore.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_writeback.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/cache_writeback.rs

Command wrapper for cache writeback.

CLI:
- Required `--metadata-device`, `--origin-device`, and `--fast-device`.
- Optional sector offsets for origin and fast devices.
- Optional `--buffer-size-meg`.
- Optional `--retry-count`, default 0.
- Flags: `--quiet`, `--no-metadata-update`, `--list-failed-blocks`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates metadata, origin, and fast device paths.
- Parses cache engine options.
- Runs a full `cache_check` first; on failure reports that metadata needs `cache_check`/possibly `cache_repair` and returns `DATAERR`.
- Converts buffer megabytes to sectors by multiplying by 2048.
- Delegates to `cache::writeback::writeback`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/cache_writeback.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/engine.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/engine.rs

Shared I/O engine option parsing and `IoEngine` construction for commands.

Core types:
- `EngineType`: `Sync`, `Spindle`, and optionally `Async` under `io_uring`.
- `ToolType`: `Thin`, `Cache`, `Era`, `Other`.
- `EngineOptions`: tool type, engine type, and metadata snapshot flag.
- `EngineBuilder`: path, options, write flag, and exclusive-open flag.

Behavior:
- Adds hidden `--io-engine` CLI option.
- Parses `sync`, `spindle`, and conditionally `async`.
- Enables `use_metadata_snap` only for thin/era tools when the command has metadata snapshot option present on command line.
- For thin spindle mode, computes valid metadata blocks from the thin metadata space map, falling back to all blocks if reading fails.
- Cache and era spindle valid-block helpers are `todo!()`, so selecting spindle engine for those tool types will panic if reached.
- Builds `SyncIoEngine`, `AsyncIoEngine`, or `SpindleIoEngine`.

Notable detail: `thin_valid_blocks` uses a sync engine independently to inspect metadata allocation even when the final engine type is spindle.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/engine.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_check.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_check.rs

Command wrapper for validating era metadata.

CLI:
- `--ignore-non-fatal-errors`.
- `--quiet`.
- `--super-block-only`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and does not look like XML.
- Parses era engine options.
- Builds `EraCheckOptions` and delegates to `era::check::check`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_check.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_dump.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_dump.rs

Command wrapper for dumping era metadata to XML.

CLI:
- `--logical` to fold unprocessed write sets into final era array.
- `--repair/-r`.
- Optional `--output/-o`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses era engine options.
- Builds `EraDumpOptions` and calls `era::dump::dump`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_dump.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_generate_metadata.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_generate_metadata.rs

Development command wrapper for synthetic era metadata creation.

CLI:
- Required command `--format`.
- Options: `--block-size` sectors default 128, `--nr-blocks` default 10240, `--current-era` default 0, `--nr-writesets` default 0.
- Required `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses era engine options.
- Builds `MetadataOp::Format(EraFormatOpts)`.
- Delegates to `era::metadata_generator::generate_metadata`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_generate_metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_invalidate.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_invalidate.rs

Command wrapper for listing blocks changed since a given era.

CLI:
- `--metadata-snapshot`.
- Required `--written-since ERA`.
- Optional `--output/-o`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses era engine options, including metadata snapshot flag.
- Builds `EraInvalidateOptions` with threshold from `--written-since`.
- Calls `era::invalidate::invalidate`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_invalidate.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_repair.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_repair.rs

Command wrapper for rebuilding era binary metadata to another device/file.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and output exists/is large enough.
- Parses era engine options.
- Builds `EraRepairOptions` and delegates to `era::repair::repair`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_repair.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_restore.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/era_restore.rs

Command wrapper for converting era XML metadata to binary.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input and output paths.
- Parses era engine options.
- Builds `EraRestoreOptions` and delegates to `era::restore::restore`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/era_restore.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/mod.rs

Command module registry and shared command trait.

Exports production command modules:
- Cache: check, dump, metadata_size, repair, restore, writeback.
- Era: check, dump, invalidate, repair, restore.
- Thin: check, delta, dump, ls, metadata pack/size/unpack, migrate, repair, restore, rmap, shrink, trim.
- Shared `engine` and `utils`.

Feature-gated devtools:
- Cache damage/generation.
- Era metadata generation.
- Thin explore, damage/generation, stat.

Defines `Command<'a>` trait with `name()` and `run(args)` returning an exit code.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_check.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_check.rs

Command wrapper for validating thin-provisioning metadata.

CLI:
- Flags: `--auto-repair`, `--clear-needs-check-flag`, `--ignore-non-fatal-errors`, `--metadata-snap/-m`, `--quiet`, `--super-block-only`, `--skip-mappings`.
- Options: `--override-mapping-root`, `--override-details-root`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and is not XML.
- Parses thin engine options including metadata snapshot.
- Builds `ThinCheckOptions` and calls `thin::check::check`.
- Uses clap conflicts to prevent unsafe combinations such as auto-repair with metadata snapshot or override roots.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_check.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_delta.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_delta.rs

Command wrapper for comparing mappings between two thin devices/snapshots.

CLI:
- `--metadata-snap/-m`.
- `--verbose`.
- First endpoint: `--thin1`/`--snap1` or `--root1`.
- Second endpoint: `--thin2`/`--snap2` or `--root2`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Manually enforces that both endpoints are provided because of a noted clap group limitation.
- Builds `Snap::DeviceId` or `Snap::RootBlock` for each side.
- Parses thin engine options and calls `thin::delta::delta`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_delta.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_dump.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_dump.rs

Command wrapper for dumping thin metadata.

CLI:
- Flags: `--quiet`, `--repair/-r`, `--skip-mappings`.
- Options: `--data-block-size`, repeated `--dev-id`, `--format xml|human_readable`, `--metadata-snap[=BLOCKNR]`, `--nr-data-blocks`, `--output/-o`, `--transaction-id`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Parses thin engine options.
- Collects selected device IDs if provided.
- Builds `ThinDumpOptions`, including repair overrides and output format.
- Delegates to `thin::dump::dump`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_dump.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_explore.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_explore.rs

Development TUI for exploring thin metadata btrees interactively.

Main features:
- Uses `termion` for raw terminal/input and `ratatui` for rendering.
- Displays superblock fields, metadata/data space-map summaries, mapping/details roots, and data block size.
- Provides panels for superblock, device details tree, top-level mapping tree, and bottom-level thin-device mapping tree.
- Supports navigation with `j`/down, `k`/up, `l`/right, `h`/left, and quit with `q`.
- Can start from a decoded `--node-path` emitted by thin check errors.

Internal design:
- `Events` owns an input thread and channel.
- `Adjacent` trait compresses adjacent runs for display.
- Generic `NodeWidget` renders btree headers and entries.
- `Panel` trait abstracts rendering/input/path traversal for each metadata view.
- `perform_action` reads child btree nodes from the sync engine and pushes/pops panels.

CLI:
- Optional `--node-path/-p`.
- Required input device/file.
- Adds version args only.

Notable detail: this is read-only and opens `SyncIoEngine::new(path, false)`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_explore.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_damage.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_damage.rs

Development command wrapper for damaging thin metadata.

CLI command group:
- `--create-metadata-leaks` with `--expected`, `--actual`, `--nr-blocks`.
- `--override` with at least one superblock override.

Override options:
- `--mapping-root`.
- `--details-root`.
- `--metadata-snap`.
- Required `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses thin engine options.
- Builds `DamageOp::CreateMetadataLeaks` or `DamageOp::OverrideSuperblock`.
- Delegates to `thin::damage_generator::damage_metadata`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_damage.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_metadata.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_metadata.rs

Development command wrapper for synthetic thin metadata generation and `needs_check` mutation.

CLI:
- Command group: `--format` or `--set-needs-check[=BOOL]`.
- Format options: `--block-size` sectors default 128, `--nr-data-blocks` default 10240.
- Required `--output/-o`.
- Adds version and engine args.

Runtime behavior:
- Parses thin engine options.
- Builds `MetadataOp::Format` or `MetadataOp::SetNeedsCheck`.
- Delegates to `thin::metadata_generator::generate_metadata`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_generate_metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_ls.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_ls.rs

Command wrapper for listing thin volumes in a pool.

CLI:
- `--no-headers`.
- `--metadata-snap/-m`.
- `--format/-o` comma-delimited output fields parsed as `OutputField`.
- Required positional input.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Defaults fields to device ID, mapped blocks, creation time, and snapshotted time.
- Parses thin engine options.
- Builds `ThinLsOptions` and delegates to `thin::ls::ls`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_ls.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_pack.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_pack.rs

Command wrapper for packing used thin metadata blocks into a compressed file.

CLI:
- Required `--input/-i DEV`.
- Required `--output/-o FILE`.
- `--force/-f` to skip overwrite confirmation.
- Adds version args.

Runtime behavior:
- Validates input exists, is not tiny, and is not XML.
- Unless forced, calls `check_overwrite_metadata` on output.
- Delegates to `pack::toplevel::pack`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_pack.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_size.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_size.rs

Command wrapper for estimating thin metadata size.

CLI:
- Required `--block-size/-b SIZE`.
- Required `--pool-size/-s SIZE`.
- Required `--max-thins/-m NUM`.
- `--unit/-u`, default sector.
- `--numeric-only/-n[=short|long]`.
- Adds version args.

Runtime behavior:
- Parses storage-size units to bytes.
- Validates data block size with `check_data_block_size`.
- Rejects pool size smaller than block size.
- Computes `nr_blocks = pool_size / block_size`.
- Calls `thin::metadata_size::metadata_size`.
- Formats output as full unit, short suffix, long suffix, or numeric-only.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_size.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_unpack.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_unpack.rs

Command wrapper for unpacking compressed thin metadata into a binary metadata device/file.

CLI:
- Required `--input/-i FILE`.
- Required `--output/-o DEV`.
- `--force/-f` to skip overwrite confirmation.
- Adds version and engine args, though unpack delegates directly to pack layer.

Runtime behavior:
- Validates input exists.
- Unless forced, prompts if output appears to already contain metadata.
- Delegates to `pack::toplevel::unpack`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_metadata_unpack.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_migrate.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_migrate.rs

Command wrapper for migrating a thin volume from one pool/destination to another.

CLI:
- `--source-dev DEVICE`.
- Hidden `--delta-id THIN_ID`.
- Destination: `--dest-dev DEVICE` or `--dest-file FILE`.
- Optional `--buffer-size-meg`.
- Hidden `--zero-dest`.
- `--quiet`.
- Adds verbose, version, and engine args, though this wrapper does not pass parsed engine options to migrate.

Runtime behavior:
- Manually requires source and destination.
- Converts buffer megabytes to sectors by multiplying by 2048.
- Builds `thin::migrate::ThinMigrateOptions` and calls `migrate::migrate`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_migrate.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_repair.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_repair.rs

Command wrapper for repairing thin metadata into a different device/file.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- Optional repair overrides: `--data-block-size`, `--nr-data-blocks`, `--transaction-id`.
- `--quiet`.
- Hidden dummy positional for `lvconvert` compatibility.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input exists, is not tiny, and output exists/is large enough.
- Parses thin engine options.
- Builds `ThinRepairOptions` with `SuperblockOverrides`.
- Delegates to `thin::repair::repair`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_repair.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_restore.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_restore.rs

Command wrapper for converting thin XML metadata to binary metadata.

CLI:
- Required `--input/-i`.
- Required `--output/-o`.
- Optional overrides: `--data-block-size`, `--nr-data-blocks`, `--transaction-id`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates input and output.
- Parses thin engine options.
- Builds `ThinRestoreOptions` with superblock overrides.
- Delegates to `thin::restore::restore`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_restore.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_rmap.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_rmap.rs

Command wrapper for reverse-mapping data-device block ranges to thin mappings.

CLI:
- Required repeated `--region BLOCK_RANGE`, parsed as `start..end`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Validates input exists and is not tiny.
- Converts `RangeU64` helper values into `std::ops::Range<u64>`.
- Parses thin engine options.
- Builds `ThinRmapOptions` and calls `thin::rmap::rmap`.

Notable detail: comments note clap cannot place the positional after multiple `--region` arguments in the desired style.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_rmap.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_shrink.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_shrink.rs

Command wrapper for shrinking inactive thin pool metadata/data.

CLI:
- Required XML/binary input `--input/-i`.
- Required output `--output/-o`.
- Required data device `--data`.
- Required new pool size `--nr-blocks`.
- `--no-copy` to skip data movement.
- `--binary` to perform binary metadata rebuild rather than XML rewrite.
- Adds version args.

Runtime behavior:
- Parses into `ThinShrinkOptions`.
- Always validates input path.
- In binary mode, also requires non-tiny input and valid output metadata file.
- If copying is enabled, validates data device path.
- Delegates to `thin::shrink::shrink`.

Header comment credits prior Python implementation by Nikhil Kshirsagar.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_shrink.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_stat.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_stat.rs

Development command wrapper for thin metadata statistics.

CLI:
- `--op`, default `data_blocks`.
- Supported operations: `data_blocks`, `metadata_blocks`, `data_run_len`.
- Required positional input.
- Adds version and engine args.

Runtime behavior:
- Parses thin engine options.
- Maps operation string to `StatOp`.
- Delegates to `thin::stat::stat`.
- Unknown operation returns `exitcode::USAGE`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_stat.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_trim.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/thin_trim.rs

Command wrapper for issuing offline discard requests for free thin-pool data space.

CLI:
- Required `--metadata-dev`.
- Required `--data-dev`.
- `--quiet`.
- Adds verbose, version, and engine args.

Runtime behavior:
- Validates metadata device exists and is not tiny, and data device exists.
- Parses thin engine options.
- Runs full `thin_check` before trimming; if metadata check fails, reports to run `thin_check`/possibly `thin_repair` and returns `DATAERR`.
- Builds `ThinTrimOptions` and calls `thin::trim::trim`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/thin_trim.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/utils.rs

Shared command utility functions for path validation, range parsing, report selection, overwrite prompting, XML/metadata sniffing, and error-to-exit-code conversion.

Key items:
- `RangeU64` parses `start..end`, requiring two unsigned integers and `end > start`.
- `check_input_file`: requires regular file or block device, with clear ENOENT handling.
- `check_file_not_tiny`: requires at least 4096 bytes.
- `check_output_file`: requires at least 40960 bytes.
- `mk_report`: quiet report, terminal progress bar report, or simple report depending on flags/stderr TTY.
- `check_not_xml`: reads first 16 bytes and rejects files that look like XML metadata.
- `is_metadata`: reads first block and classifies known thin/cache/era superblock checksums.
- `check_overwrite_metadata`: prompts before overwriting a path that appears to contain metadata.
- `to_exit_code`: reports errors unless root cause is broken pipe and maps success to `OK`, failure to `USAGE`.

Notable details:
- XML sniffing treats read errors as non-XML in `check_not_xml`.
- Broken pipe handling accounts for both direct `io::Error` and `Arc<io::Error>` as wrapped by `quick_xml`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/utils/range_parsing_tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/commands/utils/range_parsing_tests.rs

Unit tests for `RangeU64` parsing in `commands::utils`.

Covered cases:
- Valid full-range form: `0..18446744073709551615`.
- Missing separator: `0`, `0.10`.
- Separator without values: `..`.
- Extra characters or extra separators: `0..10,`, `0..10..`.
- Invalid begin/end tokens.
- Negative begin/end values.
- End not greater than begin, including `0..0`.

These tests verify that range parsing is strict and unsigned.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/commands/utils/range_parsing_tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/base.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/base.rs

Defines core block-copy abstractions used by cache writeback and thin migration/copy code.

Types:
- `Block = u64`.
- `CopyOp { src, dst }`.
- `CopyStats { nr_blocks, nr_copied, read_errors, write_errors }`.
- `CopyProgress` trait for progress updates during and after a copy batch.
- `Copier` trait with `copy(&mut self, ops, progress) -> CopyStats`.

Semantics:
- Copy operations are block-index based.
- Trait documentation expects callers to sort operations in useful order, such as by destination for spindle-friendly writes.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/base.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/batcher.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/batcher.rs

Batching helper for copy operations.

Key behavior:
- `CopyOpBatcher` accumulates `CopyOp`s up to a configured batch size.
- `push` appends and sends the batch when capacity is reached.
- `complete` sends remaining operations.
- `send_ops` sorts each batch by destination block before sending over a `SyncSender<Vec<CopyOp>>`.

Purpose:
- Larger batches improve chances of adjacent destination ordering and better sequential I/O, especially for spindle devices.
- Used by cache writeback to hand batches to a copy worker thread.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/batcher.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/copier/mod.rs

Copier module registry and public re-export surface.

Modules:
- `base`, `batcher`, `report`, `rescue_copier`, `sync_copier`, `wrapper`.
- `test_utils` only under test or `devtools`.

Re-exports:
- Base copier types and traits.
- Copier progress/report helpers.
- `RescueCopier`.
- `SyncCopier`.

This file defines the common copy subsystem surface used by higher-level cache and thin operations.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/copier/mod.rs -->