# Group Research: group_1154_mdadm_sources_block_storage_mdadm_probe_roms_c_sources_block_storag_3bf37459a131

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/block-storage/mdadm`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/probe_roms.c -->
# File Research: sources/block-storage/mdadm/probe_roms.c

Purpose: scans legacy x86 option ROM space, mainly the adapter ROM window from `0xc0000` to `0xf0000`, and exposes discovered adapter ROM ranges to a callback.

Key behavior:
- `probe_roms_init(align)` validates `align` as `512` or `2048`, initializes adapter ROM resource storage, installs a `SIGBUS` handler, opens `/dev/mem`, and `mmap`s the option ROM physical range.
- `probe_roms_exit()` restores `SIGBUS`, closes `/dev/mem`, unmaps memory, and frees adapter ROM resource nodes.
- `probe_roms()` scans video ROM, extension ROM, and adapter ROM regions. It checks `0xaa55` signatures, length byte at offset `2`, checksum validity, and PCI data pointer at offset `0x18`.
- `scan_adapter_roms(scan_fn fn)` iterates discovered adapter ROM resources and passes virtual start/end/data pointers to the callback.

Important implementation details:
- Reads are wrapped in `probe_address8()` and `probe_address16()` so a `SIGBUS` during `/dev/mem` access marks the probe failed rather than crashing immediately.
- The scanner trusts the length byte only if checksum passes and the range fits before the upper bound.
- Adapter ROM resource list starts with one preallocated node and allocates more only when additional ROMs are found.
- `isa_bus_to_virt()` maps physical ISA addresses into the single mmap region.

Dependencies:
- Includes `probe_roms.h`, `mdadm.h`, Linux endian/types helpers, `/dev/mem`, `mmap`, and signal wrapper `signal_s`.
- Intended consumers are mdadm code paths that need to inspect BIOS/option-ROM metadata.

Risks and notes:
- Requires privileged `/dev/mem` access and is platform-specific to legacy x86 ROM layout.
- Pointer arithmetic is done on `void *` in `isa_bus_to_virt`, relying on compiler extension behavior.
- `roms_deinit()` frees `adapter_rom_resources` but does not reset the pointer to `NULL`; repeated init/exit cycles depend on normal call ordering.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/probe_roms.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/probe_roms.h -->
# File Research: sources/block-storage/mdadm/probe_roms.h

Purpose: public interface for the option ROM probing helper.

Exports:
- `probe_roms_init(unsigned long align)`
- `probe_roms_exit(void)`
- `probe_roms(void)`
- `scan_adapter_roms(scan_fn fn)`
- `scan_fn`, a callback receiving `start`, `end`, and `data` pointers for a discovered ROM.

Notes:
- The header has no include guard.
- It deliberately exposes only lifecycle, scan, and callback traversal APIs; ROM resource internals remain private to `probe_roms.c`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/probe_roms.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/pwgr.c -->
# File Research: sources/block-storage/mdadm/pwgr.c

Purpose: static-linking stub for passwd/group lookup.

Behavior:
- Defines `getpwnam()` and `getgrnam()` to always return `NULL`.
- The file comment says static binaries cannot link passwd/group support, so mdadm builds can omit that functionality.

Dependencies:
- Includes `<stdlib.h>`, `<pwd.h>`, and `<grp.h>` only for matching declarations/types.

Impact:
- Any caller must tolerate lookup failure.
- This file intentionally changes feature behavior for static builds rather than emulating NSS.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/pwgr.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/raid5extend.c -->
# File Research: sources/block-storage/mdadm/raid5extend.c

Purpose: old RAID5 reshape helper logic for translating physical disk/chunk positions from an `n` disk layout to an `m` disk layout.

Key behavior:
- `phys2log(phys, stripe, n, layout)` maps a physical disk in a RAID5 stripe to a logical data block number, returning `-1` for parity and `-2` for unsupported layout.
- `raid5_extend(...)` reads 4 KiB blocks from old member fds, skips parity, computes the destination stripe/disk in the new geometry using `log2phys()`, seeks, and writes the block to the new fd.

Important source-shape note:
- As read, this file is not standalone buildable C: it lacks includes, return types on `raid5_extend`, declarations for variables such as `pd` and `dstripe`, and definitions for helpers like `log2phys()`, `error()`, and layout constants.
- It appears to be historical or draft code rather than a normal mdadm compilation unit.

Risks:
- No short-read/short-write retry handling.
- Fixed static `4096` byte buffer assumes block granularity and uses `chunksize / 4096`.
- No parity generation; it relocates data blocks only.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/raid5extend.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/raid6check.c -->
# File Research: sources/block-storage/mdadm/raid6check.c

Purpose: standalone RAID6 consistency checker and repair utility, based on mdadm restriping logic.

Main flow:
- `main()` opens an md device, reads sysfs metadata, requires RAID6 and non-degraded state, prints geometry and component devices, opens component devices with `O_RDWR | O_DIRECT`, then calls `check_stripes()`.
- Supports normal check mode: `md_device start_stripe length_stripes [autorepair]`.
- Supports manual repair mode: `md_device repair stripe failed_slot_1 failed_slot_2`.

Core checking:
- `check_stripes()` locks each stripe by writing `suspend_lo`/`suspend_hi`, reads one chunk from every member, maps P/Q/data slots using `geo_map()`, calculates P and Q via `qsyndrome()`, classifies mismatch bytes with `raid6_collect()`, summarizes per 4 KiB page with `raid6_stats()`, and reports likely failed slots.
- DDF layouts are handled differently from native md layouts: DDF syndrome order follows raid disk numbers with zeroes for P/Q, while md syndrome order starts after Q and skips P.

Repair paths:
- `autorepair()` repairs pages only when the suspected role maps to a real block index. It handles Q-only mismatches by recomputing Q and data/P mismatches by XOR recovery.
- `manual_repair()` accepts two user-specified failed slots and uses RAID6 recovery helpers for D+P, D+D, or Q-involved repairs.
- Writes are done directly to member devices at `offset + start * chunk_size`.

Dependencies:
- Prototypes functions implemented in `restripe.c`: `geo_map`, `is_ddf`, `qsyndrome`, `make_tables`, `raid6_datap_recov`, `raid6_2data_recov`, `xor_blocks`.
- Uses mdadm sysfs helpers, `xmalloc`, RAID layout constants, and Linux direct IO behavior.

Safety properties:
- Locks stripes and ignores termination signals during critical read/repair windows.
- Refuses degraded arrays at startup.
- Restores suspend sysfs values and signal handlers via `unlock_all_stripes()`.

Risks and edge cases:
- Direct writes do not retry partial writes beyond checking aggregate byte count.
- `int disk[chunk_size >> CHECK_PAGE_BITS]` and similar VLAs depend on chunk size and stack availability.
- `autorepair()` indexes `block_index_for_slot[disk[j]]` after accepting `disk[j] >= -2`; the code relies on pointer biasing (`block_index_for_slot += 2`) being correct.
- Manual repair trusts operator-provided failed slots.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/raid6check.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/restripe.c -->
# File Research: sources/block-storage/mdadm/restripe.c

Purpose: shared RAID geometry, parity/syndrome, recovery, save, restore, and optional test logic used for reshaping/restriping arrays.

Geometry:
- `geo_map(block, stripe, raid_disks, level, layout)` maps logical data/P/Q roles to physical disk numbers for RAID0/4/5/6, including native md and DDF-style RAID6 algorithms.
- `is_ddf(layout)` identifies DDF rotating RAID6 layouts.

Parity and RAID6 math:
- `xor_blocks()` computes P parity byte by byte.
- `qsyndrome()` computes RAID6 P and Q.
- `make_tables()` builds GF multiplication, exponent, inverse, and log tables.
- `raid6_2data_recov()` and `raid6_datap_recov()` are adapted from Linux RAID6 recovery logic.

Stripe movement:
- `save_stripes()` reads data chunks from an old geometry into a buffer or backup file. It can reconstruct missing data using parity or RAID6 recovery if enough members are readable.
- `restore_stripes()` reads saved data from a file or buffer, rebuilds parity/Q for the destination geometry, and writes complete stripes to member devices.
- Both functions require stripe-aligned lengths.

Optional test harness:
- Under `#ifdef MAIN`, provides `test_stripes()`, `getnum()`, and a CLI `main()` for save/restore/test operations against explicit device files.

Dependencies:
- Includes `mdadm.h`, `xmalloc.h`, and `<stdint.h>`.
- Shares symbols with `raid6check.c`.

Risks and notes:
- Comments explicitly call `xor_blocks()` inefficient.
- IO paths generally treat short read/write as failure, with limited retry behavior.
- The code uses global RAID6 tables and global `zero` buffer, so it is not designed as isolated thread-safe library state.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/restripe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/sha1.c -->
# File Research: sources/block-storage/mdadm/sha1.c

Purpose: GPL SHA1 implementation imported from GNU code, used by mdadm for stable UUID derivation and hashing.

API implemented:
- `sha1_init_ctx()`
- `sha1_read_ctx()`
- `sha1_finish_ctx()`
- `sha1_stream()`
- `sha1_buffer()`
- `sha1_process_bytes()`
- `sha1_process_block()`

Implementation details:
- Maintains five SHA1 state words, total byte count, buffered partial block, and 32-word internal buffer.
- Handles endian conversion through `SWAP`.
- Handles unaligned input conditionally using `_STRING_ARCH_unaligned` and an `alignof` fallback.
- `sha1_stream()` reads in 4096-byte blocks and handles partial reads/EOF carefully.
- Compression function unrolls all 80 SHA1 rounds using macros `F1` through `F4`, constants `K1` through `K4`, and ring-buffer message expansion.

Dependencies:
- Includes `sha1.h`, `<stddef.h>`, `<string.h>`, optional `unlocked-io.h`.

Notes:
- Comments in `sha1_read_ctx()` and `sha1_finish_ctx()` require result buffers to be aligned for 32-bit access on some systems.
- SHA1 is not collision-resistant for security use, but mdadm uses it here for compact deterministic identifiers, not cryptographic authentication.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/sha1.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/sha1.h -->
# File Research: sources/block-storage/mdadm/sha1.h

Purpose: declares the SHA1 context type and public SHA1 functions.

Key contents:
- Include guard `SHA1_H`.
- Determines a 32-bit unsigned integer type `sha1_uint32` using libc types or preprocessor checks against `INT_MAX`, `SHRT_MAX`, and `LONG_MAX`.
- Defines `struct sha1_ctx` with state words `A` through `E`, total byte counters, buffer length, and 32-word buffer.
- Declares block, byte, stream, buffer, finish, read, and init functions.
- Provides C++ `extern "C"` wrappers.

Notes:
- Comments state `sha1_process_block()` requires `LEN` to be a multiple of 64, while `sha1_process_bytes()` accepts arbitrary lengths.
- Public digest output size is 20 bytes.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/sha1.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/super-ddf.c -->
# File Research: sources/block-storage/mdadm/super-ddf.c

Purpose: mdadm external metadata handler for SNIA DDF RAID metadata. It supports DDF containers, virtual disks/subarrays, member metadata loading/writing, mdmon state updates, spare activation, and mdadm reporting/export operations.

On-disk model:
- DDF metadata lives near the end of devices, with an anchor header locating primary and secondary headers plus sections.
- Multi-byte fields are stored big-endian through wrapper types `be16`, `be32`, and `be64`.
- Defines DDF structures for headers, controller data, physical disk records, virtual disk records, VD configuration records, spare assignments, disk data, and bad block logs.
- `struct ddf_super` is the in-memory aggregate. It holds global metadata (`phys`, `virt`, controller, headers), local disk list `dlist`, virtual config list `conflist`, pending-add list, current subarray context, and DDF sizing parameters.

Loading:
- `load_ddf_headers()` reads the anchor from the last 512 bytes, optionally performs extended search in the last 32 MiB, validates CRC/revision, loads primary/secondary headers, and chooses the active header by sequence/openflag.
- `load_ddf_global()` loads controller, physical disk, and virtual disk sections.
- `load_ddf_local()` loads per-device disk data, config records, spare records, and merges VD configs into `conflist`, including secondary BVD records.
- `load_super_ddf()` loads one member device.
- `load_super_ddf_all()` loads a whole running DDF container by inspecting sysfs member devices and choosing the best sequence.

Layout mapping:
- `layout_md2ddf()` converts md RAID levels/layouts to DDF PRL/RLQ/SRL fields.
- `layout_ddf2md()` converts supported DDF layouts back to md array geometry.
- Supported practical mappings include linear/concat, RAID0, RAID1, RAID4, RAID5 left/right/asymmetric/symmetric subset, RAID6 DDF rotating layouts, and RAID10 forms that map to DDF secondary BVD structures.
- Unsupported combinations report explicit errors.

Creation and writing:
- `init_super_ddf()` creates a new DDF container, reserves 32 MiB at the end, initializes headers, controller data, physical disk table, and virtual disk table.
- `init_super_ddf_bvd()` creates a virtual disk inside an existing container.
- `add_to_super_ddf()` adds physical devices to containers; `add_to_super_ddf_bvd()` assigns member extents to a virtual disk.
- `_write_super_to_disk()` writes primary, secondary, and anchor metadata to each device.
- `__write_ddf_structure()` writes header, controller, physical, virtual, config, and disk-data records with CRC updates and openflag transitions.
- `store_super_ddf()` either writes a specific device’s DDF metadata or clears the last search region during cleanup.

Reporting and identity:
- `examine_super_ddf()`, `brief_examine_super_ddf()`, `brief_examine_subarrays_ddf()`, `export_examine_super_ddf()`, `detail_super_ddf()`, and `brief_detail_super_ddf()` implement mdadm display/export paths.
- `uuid_from_ddf_guid()` hashes DDF GUIDs via SHA1.
- `uuid_of_ddf_subarray()` compensates for vendors such as LSI whose volume GUIDs can vary between boots by hashing container GUID, name, and member number.
- `getinfo_super_ddf()` reports container info; `getinfo_super_ddf_bvd()` reports subarray/member info.

Runtime/mdmon behavior:
- `ddf_open_new()` validates new subarrays against metadata and marks broken devices faulty.
- `ddf_set_array_state()` updates consistency and init-state bits.
- `ddf_set_disk()` updates physical disk state and virtual disk state when devices fail or become in-sync.
- `ddf_sync_metadata()` writes pending metadata updates.
- `ddf_process_update()` dispatches metadata updates by DDF magic to physical, virtual, or VD config handlers.
- `ddf_prepare_update()` preallocates memory needed for config updates.
- `ddf_activate_spare()` finds dedicated or global spares for degraded arrays, reserves space, returns mdinfo entries for replacements, and emits VD config metadata updates.

Space and state management:
- `get_extents()` and `find_space()` track used extents per physical disk.
- `reserve_space()` chooses devices with adequate free extents for new subarrays.
- `get_bvd_state()`, `secondary_state()`, and `get_svd_state()` derive DDF optimal/degraded/failed/partially-optimal state from physical disk availability.
- `ddf_update_vlist()` refreshes each disk’s list of virtual disks and spare/global-spare flags.
- `ddf_remove_failed()` compacts failed transitional physical disk records no longer in use.
- `kill_subarray_ddf()` and `_kill_subarray_ddf()` remove virtual disks.

Superswitch integration:
- Exports `struct superswitch super_ddf` with DDF-specific implementations for examine, load, store, create, validate, compare, container content, mdmon hooks, update processing, spare activation, UUID extraction, and default geometry.
- Marks `.external = 1`, `.swapuuid = 0`, `.name = "ddf"`.

Risks and notes:
- This is high-blast-radius metadata code: it writes raw member-device metadata and manages active mdmon updates.
- Correctness relies on CRC validation, endian conversions, careful sequence/openflag handling, and keeping global versus local DDF records synchronized.
- Extended DDF header search exists for hardware that does not place the anchor in the final sector.
- DDF secondary RAID support is deliberately limited; `check_secondary()` only accepts md-compatible RAID10-like BVD layouts.
- `update_super_ddf_dummy()` is a placeholder so mdadm has a non-null update path, but it does not perform real metadata mutation.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/super-ddf.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/super-gpt.c -->
# File Research: sources/block-storage/mdadm/super-gpt.c

Purpose: pseudo metadata handler for devices with GPT partition tables.

Behavior:
- GPT is not usable for creating or assembling md arrays directly.
- It exists so mdadm can load, examine, store, and report partition-table metadata when preparing bare devices whose partitions may become md members.

Key functions:
- `load_gpt()` reads protective MBR, validates GPT partition type, reads GPT header at sector size offset, validates GPT signature, limits partition count to less than 128, and reads partition entries.
- `examine_gpt()` prints GPT magic, revision, and partition extents.
- `store_gpt()` writes stored GPT/entry data back, calls `fsync()`, then asks the kernel to reread partitions with `BLKRRPART`.
- `getinfo_gpt()` fills mdinfo with text/name `"gpt"` and component size derived from highest partition ending LBA.
- `validate_geometry()` always rejects GPT as normal md metadata.

Risks and notes:
- Comments acknowledge incomplete GPT writing: backup GPT copy and non-512-byte block handling are FIXME areas.
- Load uses actual sector size for reading header/entries, but store comments still note 512-byte assumptions.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/super-gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/super-mbr.c -->
# File Research: sources/block-storage/mdadm/super-mbr.c

Purpose: pseudo metadata handler for DOS/MBR partition tables.

Behavior:
- MBR is not usable for creating or assembling md arrays directly.
- It lets mdadm examine, load, store, and report partition table state for devices whose partitions may be used elsewhere.

Key functions:
- `load_super_mbr()` reads the first sector, validates `MBR_SIGNATURE_MAGIC`, and stores the 512-byte MBR.
- `examine_mbr()` prints magic and non-empty partition entries, using direct `sb->parts[i]` access because entries are not properly aligned.
- `store_mbr()` preserves the existing boot/pad area from disk, writes the updated MBR, calls `fsync()`, and issues `BLKRRPART`.
- `getinfo_mbr()` fills mdinfo text/name `"mbr"` and computes component size from the highest partition end.
- `validate_geometry()` always rejects MBR as normal md metadata.

Risks and notes:
- Store path allocates `old` but if the final write fails, `old` has already been freed and `super` remains owned by `st`.
- The code intentionally avoids treating partition tables as real RAID superblocks.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/super-mbr.c -->