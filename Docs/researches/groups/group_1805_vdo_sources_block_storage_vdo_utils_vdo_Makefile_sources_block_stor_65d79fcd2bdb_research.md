# Group Research: VDO User Utility Core Support Files

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/vdo`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/Makefile -->
# File Research: sources/block-storage/vdo/utils/vdo/Makefile

Builds the VDO userspace utility suite and its shared static library `libvdo.a`.

Key details:
- Defines `VDO_VERSION = 8.3.2.1` and passes it as `CURRENT_VERSION`.
- Builds command binaries such as `vdoaudit`, `vdocalculatesize`, `vdodebugmetadata`, `vdodumpblockmap`, `vdodumpmetadata`, `vdoforcerebuild`, `vdoformat`, `vdolistmetadata`, `vdoreadonly`, and `vdostats`.
- Installs script-only/nonbuilt tools `adaptlvm` and `vdorecover`.
- Links against `../uds/libuds.a` plus `dl`, `pthread`, `z`, `rt`, `m`, and `uuid`; `vdoformat` also links `blkid`.
- Uses strict warning policy with `-Werror`, compiler-specific warning suppression for clang, and generated `.deps/*.d` dependency files.

Risk notes:
- `clean` removes local objects, archive, dependencies, and built programs but delegates manpage cleanup to `man`.
- Build behavior depends on UDS library availability in `../uds`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/adaptlvm -->
# File Research: sources/block-storage/vdo/utils/vdo/adaptlvm

Bash helper for temporarily exposing an LVMVDO backing volume as writable, then restoring the normal read-only LVMVDO activation.

Key details:
- CLI shape is `adaptlvm [ setRO | setRW ] <volume_group>/<logical_volume>`.
- `setRW` finds the VDO pool name through `lvdisplay`, locates the `_vdata` device-mapper table, deactivates the LVM LV, and creates a temporary `/dev/mapper/${VG}-${LV}` device with the backing table.
- `setRO` removes that temporary mapper device and reactivates the original LV.
- Supports extra LVM flags through `EXTRA_LVM_ARGS`.

Risk notes:
- The device lookup test uses command substitution around `grep -q`; because `grep -q` emits no output, the condition is logically suspect and may always take the “not found” path.
- Installs a trap for `cleanup 2`, but no `cleanup` function is defined in this file.
- Unquoted variable usage appears in several device-manager and LVM commands, so unusual VG/LV names could break parsing or command invocation.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/adaptlvm -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/blockMapUtils.c -->
# File Research: sources/block-storage/vdo/utils/vdo/blockMapUtils.c

Implements user-space traversal and lookup helpers for the VDO block map.

Key details:
- `examineBlockMapEntries()` walks every block-map tree root and recursively visits mapped child pages.
- `readAndExaminePage()` reads a block-map page, validates it, calls the supplied `MappingExaminer` for every entry, and descends into valid data-block PBNs when height remains.
- `findLBNPage()` computes tree slots for a logical block number and walks from the relevant root page to the leaf page.
- `findLBNMapping()` resolves a single LBN to a mapped PBN and mapping state, returning the zero block with `UNMAPPED` state for missing mappings.
- `readBlockMapPage()` validates page version, nonce, initialized bit, and expected PBN; invalid or wrong-location pages are treated as uninitialized after warning.

Risk notes:
- Traversal calls the examiner before checking whether a location is mapped, so examiners must handle unmapped entries.
- Invalid pages are softened into uninitialized pages, which is useful for diagnostic tools but can hide metadata damage unless warnings are monitored.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/blockMapUtils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/blockMapUtils.h -->
# File Research: sources/block-storage/vdo/utils/vdo/blockMapUtils.h

Declares the block-map inspection API used by VDO diagnostic utilities.

Key details:
- Defines `MappingExaminer`, a callback over block-map slot, tree height, PBN, and mapping state.
- Exposes whole-map traversal via `examineBlockMapEntries()`.
- Exposes targeted lookup helpers `findLBNPage()` and `findLBNMapping()`.
- Exposes `readBlockMapPage()` for direct page reads with nonce/PBN validation.

Dependencies:
- Pulls in `encodings.h`, `physicalLayer.h`, and `userVDO.h`, so callers operate on decoded VDO state and abstract physical I/O.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/blockMapUtils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/constants.h -->
# File Research: sources/block-storage/vdo/utils/vdo/constants.h

Central constant set for userspace VDO metadata and configuration limits.

Key details:
- Defines block geometry: `VDO_BLOCK_SIZE = 4096`, `VDO_SECTOR_SIZE = 512`, `VDO_SECTORS_PER_BLOCK = 8`, and `VDO_ZERO_BLOCK = 0`.
- Defines block-map shape: `VDO_BLOCK_MAP_ENTRIES_PER_PAGE = 812`, tree height `5`, flat origin `1`, and default root count `60`.
- Defines journal defaults: recovery journal `32 * 1024` blocks, slab journal `224` blocks, minimum slab journal `2` blocks.
- Defines maximums for zones, slab bits, slabs, simultaneous restoration reads, threads, and user VIOs.

Research relevance:
- These constants anchor almost every format calculation in `encodings.c`, `vdoConfig.c`, and block-map traversal.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/constants.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/encodings.c -->
# File Research: sources/block-storage/vdo/utils/vdo/encodings.c

Implements VDO userspace on-disk encoding, decoding, validation, layout construction, slab configuration, and checksum handling.

Key details:
- Defines current format headers for geometry v5.0, legacy geometry v4.0, block map v2.0, recovery journal v7.0, slab depot v2.0, layout v3.0, superblock v12.0, component data v41.0, and volume version v67.0.
- `vdo_parse_geometry_block()` validates magic `dmvdo001`, header version/size, geometry fields, and CRC32 checksum.
- `vdo_validate_block_map_page()` checks block-map page version 4.1, initialized flag, nonce, and expected PBN.
- Provides block-map forest sizing through `vdo_compute_new_forest_pages()`.
- Encodes/decodes recovery journal, slab depot, layout, VDO component, and complete component state payloads.
- `vdo_initialize_layout()` creates the fixed VDO partition layout: block map at the beginning, slab summary and recovery journal at the end, and slab depot in remaining space.
- `vdo_validate_config()` enforces slab size power-of-two constraints, journal constraints, physical/logical limits, and expected physical/logical sizes.
- `vdo_encode_super_block()` writes component data and checksum while asserting it fits in one sector to reduce torn-write exposure.

Risk notes:
- Version validation is strict; unsupported minor/major versions are rejected rather than upgraded in place.
- `decode_layout()` checks required partitions and total coverage by summing partition counts, but partition linked-list order is allocation order and not necessarily disk order.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/encodings.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/encodings.h -->
# File Research: sources/block-storage/vdo/utils/vdo/encodings.h

Defines VDO’s userspace-visible on-disk structures and inline packing/unpacking helpers.

Key details:
- Declares versioned headers, geometry blocks, volume regions, index config, block-map entries/pages, recovery journal formats, reference count sectors, slab journal blocks, slab summary entries, layout partitions, VDO config, VDO component state, and aggregate component states.
- Block-map entries are five-byte packed records containing a 36-bit PBN and four-bit mapping state.
- Recovery journal entries encode a block-map slot plus mapping/unmapping locations.
- Slab journal supports compact data-only entries and fuller entries with block-map increment type bitmap.
- Provides endian-safe inline helpers for versions, headers, block-map entries, recovery headers, journal points, slab journal entries, and geometry region starts.
- Declares all major encode/decode/validate functions implemented by `encodings.c`.

Research relevance:
- This is the central format contract for VDO userspace tools; persisted enum values and packed structures must stay stable.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/encodings.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/fileLayer.c -->
# File Research: sources/block-storage/vdo/utils/vdo/fileLayer.c

Implements `PhysicalLayer` over a regular file or block device using direct I/O.

Key details:
- `FileLayer` stores the `PhysicalLayer` vtable, block count, block offset, fd, alignment, and name.
- Allocates direct-I/O-compatible buffers aligned to the underlying file/device block size.
- `fileReader()` and `fileWriter()` apply `fileOffset`, bounds-check against `blockCount`, repair unaligned caller buffers with temporary aligned buffers, and use `pread`/`pwrite`.
- `setupFileLayer()` validates existence, opens read-only or read-write direct, detects block device status, reads size through `BLKGETSIZE64` or `stat`, and enforces requested block-count consistency.
- Read-only layers use `noWriter()`, returning `EPERM`.

Risk notes:
- `performIO()` handles short I/O by looping, but any zero-length result becomes `VDO_UNEXPECTED_EOF`.
- Alignment is taken from `st_blksize`, which is pragmatic for direct I/O but may not capture every device-specific alignment constraint.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/fileLayer.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/fileLayer.h -->
# File Research: sources/block-storage/vdo/utils/vdo/fileLayer.h

Declares constructors for file-backed `PhysicalLayer` implementations.

Key details:
- `makeFileLayer()` creates a read-write layer with expected block count.
- `makeReadOnlyFileLayer()` creates a read-only layer and computes block count from the backing file/device.
- `makeOffsetFileLayer()` creates a read-write layer with a block offset applied to all I/O.

Research relevance:
- This is the common I/O bridge for format, metadata dump, audit, and offline state utilities.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/fileLayer.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/man/Makefile -->
# File Research: sources/block-storage/vdo/utils/vdo/man/Makefile

Installs VDO utility man pages.

Key details:
- `INSTALLFILES` includes manpages for `adaptlvm`, all built VDO utilities, and `vdorecover`.
- `all` and `clean` are no-ops.
- `install` creates `$(DESTDIR)/$(mandir)/man8` and installs each manpage mode `644`.
- Defaults `mandir` to `/usr/man`.

Risk notes:
- The install path is `$(DESTDIR)/$(mandir)`, so if `mandir` is absolute the double slash is harmless but nonstandard-looking.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/man/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/messageStatsReader.c -->
# File Research: sources/block-storage/vdo/utils/vdo/messageStatsReader.c

Parses text-form VDO statistics into `struct vdo_statistics`.

Key details:
- Uses small helpers `skip_string()`, `read_u64()`, `read_u32()`, `read_block_count_t()`, `read_string()`, `read_bool()`, and `read_u8()`.
- Contains generated-style readers for nested stats groups: allocator, commit, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash lock, errors, bio stats, memory usage, and index stats.
- `read_vdo_statistics()` walks the complete expected stats message in order and populates all fields in `struct vdo_statistics`.
- Public entry point is `read_vdo_stats(char *buf, struct vdo_statistics *stats)`.

Risk notes:
- Parsing is tightly coupled to exact field labels and expected order; missing or renamed fields return `VDO_UNEXPECTED_EOF`.
- `skip_string()` uses `strstr` from the current pointer, so it can skip over unexpected intervening text rather than enforcing immediate field adjacency.
- Some integer readers use `%lu` for `u64`/`block_count_t`, which assumes the typedef layout matches `unsigned long` on the build target.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/messageStatsReader.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/parseUtils.c -->
# File Research: sources/block-storage/vdo/utils/vdo/parseUtils.c

Implements CLI/config parsing helpers for VDO user tools.

Key details:
- `parseUInt()` parses unsigned integers with inclusive lower/upper bounds.
- `parseInt()` parses signed integers.
- `parseUInt64()` parses base-10 unsigned 64-bit values.
- `parseSize()` parses byte sizes with optional binary unit suffixes `B`, `K`, `M`, `G`, `T`, `P`; LVM mode defaults unitless values to MiB, otherwise bytes.
- `parseIndexConfig()` converts sparse and memory-size strings into UDS `index_config`, defaulting memory to 256 MB.
- Memory parser accepts fractional strings `0.25`, `0.5`/`0.50`, and `0.75` plus integer values.

Risk notes:
- `parseUInt64()` does not explicitly check `endPtr == arg`, so an empty/non-numeric string can depend on `strtoull` behavior rather than a direct empty-input check.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/parseUtils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/parseUtils.h -->
# File Research: sources/block-storage/vdo/utils/vdo/parseUtils.h

Declares VDO userspace parse helpers.

Key details:
- Defines `UdsConfigStrings` with `sparse` and `memorySize` string fields.
- Declares integer, 64-bit integer, size, and index-config parsers.
- Includes `indexer.h` and `encodings.h`, tying parsed UDS settings to the persisted `struct index_config`.

Research relevance:
- Used by formatting and sizing tools to turn command-line strings into validated numeric/UDS configuration.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/parseUtils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/physicalLayer.h -->
# File Research: sources/block-storage/vdo/utils/vdo/physicalLayer.h

Defines the abstract synchronous block I/O interface used by VDO userspace tools.

Key details:
- `PhysicalLayer` is a vtable-style struct with destroy, block-count, buffer allocation, reader, and writer callbacks.
- Readers and writers operate in VDO block units using `physical_block_number_t` and block count.
- Buffer allocator exists so implementations can provide direct-I/O-compatible buffers.

Research relevance:
- This abstraction lets metadata logic operate over regular files, block devices, read-only files, or offset layers without knowing the backend.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/physicalLayer.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/printUtils.c -->
# File Research: sources/block-storage/vdo/utils/vdo/printUtils.c

Formats sizes for display.

Key details:
- Defines binary KB/MB/GB/TB/PB constants.
- `getSizeString()` either formats the raw numeric size or delegates to human-readable formatting.
- `setReadablePrintString()` emits two-decimal suffix strings for P/T/G/M/K/B ranges.

Risk notes:
- Raw output uses `sprintf(printString, "%ld", size)` for `u64`, which is type-sensitive and not fully portable.
- Uses strict greater-than thresholds, so exactly `1 MB` is formatted as `1024.00K`, not `1.00M`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/printUtils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/printUtils.h -->
# File Research: sources/block-storage/vdo/utils/vdo/printUtils.h

Declares small display-formatting helpers.

Key details:
- Defines `PRINTSTRINGSIZE` as `20`.
- Declares `getSizeString()` and `setReadablePrintString()`.
- Includes `types.h` for `u64`.

Research relevance:
- Shared by user-facing tools that need consistent byte/block display strings.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/printUtils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/slabSummaryReader.c -->
# File Research: sources/block-storage/vdo/utils/vdo/slabSummaryReader.c

Reads and merges the VDO slab summary from metadata storage.

Key details:
- `readSlabSummary()` returns success immediately if the slab depot has zero zones.
- Allocates one zone’s slab-summary blocks with the physical layer allocator.
- Locates `VDO_SLAB_SUMMARY_PARTITION` from decoded layout and reads the first zone.
- For multiple zones, reads each zone’s summary block set into a temporary buffer and copies interleaved entries into the primary entry array.

Risk notes:
- If `vdo_get_partition()` fails, the allocated `entries` buffer is not freed before returning.
- Multi-zone merge assumes entries are distributed by `entry_number = zone; entry_number < MAX_VDO_SLABS; entry_number += zones`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/slabSummaryReader.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/slabSummaryReader.h -->
# File Research: sources/block-storage/vdo/utils/vdo/slabSummaryReader.h

Declares slab-summary loading support.

Key details:
- Exposes `readSlabSummary(UserVDO *vdo, struct slab_summary_entry **entriesPtr)`.
- Includes `encodings.h`, `types.h`, and `userVDO.h`.

Minor note:
- The closing include-guard comment says `SLAB_SUMMARY_UTILS_H`, while the actual guard is `SLAB_SUMMARY_READER_H`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/slabSummaryReader.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/statistics.h -->
# File Research: sources/block-storage/vdo/utils/vdo/statistics.h

Defines the VDO statistics ABI consumed by stats readers/writers.

Key details:
- `STATISTICS_VERSION = 36`.
- Defines nested statistic groups for allocator, commit pipeline, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash locks, error counts, bio categories, memory usage, and UDS index.
- `struct vdo_statistics` combines capacity/use counters, mode/recovery fields, nested statistics, bios by stage, memory usage, and index stats.
- File header documents companion files that must be updated when adding statistics.

Research relevance:
- `messageStatsReader.c` mirrors this structure field by field; drift between text stats and this struct breaks parsing/reporting.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/statistics.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/status-codes.c -->
# File Research: sources/block-storage/vdo/utils/vdo/status-codes.c

Registers VDO-specific status codes and maps internal errors to OS errno values.

Key details:
- Defines `vdo_status_list[]` names/messages for all VDO errors.
- `vdo_register_status_codes()` registers the VDO error block once using `vdo_perform_once()`.
- Duplicate registration is treated as success for static-link scenarios where multiple objects register the same block.
- `vdo_status_to_errno()` returns existing negative errors unchanged, maps small positive errno values to negative errno, maps `VDO_NO_SPACE` to `-ENOSPC`, maps `VDO_READ_ONLY` to `-EIO`, and logs/defaults other VDO/UDS errors to `-EIO`.

Research relevance:
- Bridges internal userspace/kernel-style status codes to system-facing error returns.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/status-codes.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/status-codes.h -->
# File Research: sources/block-storage/vdo/utils/vdo/status-codes.h

Declares the VDO status-code block.

Key details:
- Places VDO errors after the UDS error-code block.
- Enumerates VDO-specific errors from `VDO_NOT_IMPLEMENTED` through `VDO_NOT_READ_ONLY`.
- Exposes `vdo_status_list`, `vdo_register_status_codes()`, and `vdo_status_to_errno()`.

Research relevance:
- Shared error vocabulary across encoding, config, I/O, block-map, and stats utilities.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/status-codes.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/types.h -->
# File Research: sources/block-storage/vdo/utils/vdo/types.h

Defines core scalar aliases and persisted enums for VDO userspace metadata handling.

Key details:
- Provides aliases for block counts, block sizes, logical/physical block numbers, nonces, pages, roots, slabs, slots, threads, zones, and sequence numbers.
- Defines persisted `enum vdo_state` and helpers for read-only rebuild and recovery-required states.
- Defines persisted journal operation, partition ID, metadata type, block-map slot, and block-mapping-state values.
- Defines `struct data_location` and packed `struct slab_config`.

Research relevance:
- Many enum values are persisted on disk, so compatibility depends on preserving numeric values and packing.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/userVDO.c -->
# File Research: sources/block-storage/vdo/utils/vdo/userVDO.c

Implements lifecycle, loading, saving, and slab-address helpers for user-space VDO objects.

Key details:
- `makeUserVDO()` wraps a `PhysicalLayer` in a heap-allocated `UserVDO`.
- `freeUserVDO()` destroys decoded component state allocations and frees the wrapper.
- `loadVolumeGeometry()` reads block 0 and parses geometry.
- `loadVDOWithGeometry()` reads the superblock at the geometry data-region start, decodes component states, optionally validates config/nonce/size, then computes derived slab fields.
- `writeVolumeGeometryWithVersion()` encodes magic, geometry, checksum, and writes block 0.
- `saveSuperBlock()` and `saveVDO()` write encoded superblock and optional geometry.
- `getSlabNumber()`, `getSlabBlockNumber()`, and `isValidDataBlock()` validate PBNs against slab depot boundaries and data-block area.

Risk notes:
- `getPartition()` calls `errx(1, ...)` on missing partition, so callers using it opt into process exit rather than recoverable error handling.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/userVDO.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/userVDO.h -->
# File Research: sources/block-storage/vdo/utils/vdo/userVDO.h

Declares the `UserVDO` aggregate and its load/save/address helper API.

Key details:
- `UserVDO` contains the physical layer, volume geometry, one-block superblock buffer, decoded component states, and derived slab parameters.
- Declares construction/destruction, geometry loading, superblock loading, full VDO loading, geometry writing, superblock saving, full saving, slab parameter derivation, slab/PBN lookups, data-block validation, and partition lookup.
- Provides inline `writeVolumeGeometry()` using `VDO_DEFAULT_GEOMETRY_BLOCK_VERSION`.

Research relevance:
- This is the high-level object most VDO utilities use after opening a physical layer.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/userVDO.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoConfig.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoConfig.c

Implements VDO formatting, minimum-size calculation, geometry initialization, partition clearing, and offline state changes.

Key details:
- `initializeLayoutFromConfig()` creates the default layout with block-map roots, recovery journal, slab summary, and slab depot.
- `configureRecoveryJournal()` starts journal sequence at `1` with zero logical and block-map usage.
- `configureVDO()` initializes layout, slab config/depot, derived slab params, auto logical size when unset, block-map state, and `VDO_NEW` state.
- `calculateMinimumVDOFromConfig()` computes fixed metadata size plus one slab.
- `computeIndexBlocks()` asks UDS for index size and requires a multiple of VDO block size.
- `initializeVolumeGeometry()` places index region at block 1 and data region after the index.
- `formatVDOWithNonce()` registers status codes, validates config, creates `UserVDO`, configures metadata, clears block-map and recovery-journal partitions, and saves geometry/superblock.
- `forceVDORebuild()` and `setVDOReadOnlyMode()` update inactive superblock state.

Risk notes:
- `configureAndWriteVDO()` writes an allocated geometry block before encoding it later via `saveVDO()`, so the first write appears to be a placeholder/zeroing step.
- `clearPartition()` chooses a power-of-two buffer size based on partition size divisibility, up to 4096 blocks.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoConfig.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoConfig.h -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoConfig.h

Declares VDO formatting and configuration helper APIs.

Key details:
- Exposes recovery-journal initialization, full formatting, minimum-size calculation, layout initialization, UDS index block computation, geometry initialization, deterministic nonce/UUID formatting, force rebuild, and offline read-only marking.
- Notes that `initializeLayoutFromConfig()` is exposed for testing.
- Pulls in UDS `indexer.h`, VDO `encodings.h`, and core types.

Research relevance:
- This header is the main entry point for tools such as `vdoformat`, `vdocalculatesize`, `vdoforcerebuild`, and `vdoreadonly`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoConfig.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoStats.h -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoStats.h

Declares the VDO stats read/write API.

Key details:
- `read_vdo_stats()` parses a buffer into `struct vdo_statistics`.
- `vdo_write_stats()` writes a stats structure to stdout.
- Includes `types.h`; the concrete stats structure is declared in `statistics.h`.

Research relevance:
- `messageStatsReader.c` implements the read side; the write side is provided elsewhere in the utility tree.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoStats.h -->