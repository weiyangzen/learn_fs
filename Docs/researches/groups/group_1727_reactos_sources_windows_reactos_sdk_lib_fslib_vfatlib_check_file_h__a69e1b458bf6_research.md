# Group Research: ReactOS VFAT/VFATX filesystem library subset A

Scope verified against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.h

Defines the checker’s auxiliary file-attribute override interface, mainly for paths that should be dropped or undeleted during FAT repair.

Key elements:
- `FD_TYPE` models override actions: none, drop, undelete.
- `FDSC` stores an 8.3 fixed-name entry, its action type, first child, and sibling link.
- `fp_root` is the global root of the override descriptor tree.
- Declares conversion and lookup helpers: `file_name`, `file_cvt`, `file_add`, `file_cd`, `file_type`, `file_modify`, `file_unused`.

Dependencies:
- Uses `MSDOS_NAME` from `msdos_fs.h`.
- Used by directory scanning/checking code to resolve user-specified file operations against FAT directory entries.

Research notes:
- This is a pure interface header; behavior lives elsewhere in the checker.
- The model assumes fixed 8.3 names for matching, even when the checker also tracks VFAT long names separately.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fsck.fat.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fsck.fat.h

Central shared header for FAT checking structures, boot-sector layouts, directory-entry metadata, FAT state, and global checker flags.

Key elements:
- Provides ReactOS-specific endian and packing compatibility around the imported dosfstools-style checker code.
- Defines packed `boot_sector`, `boot_sector_16`, `info_sector`, and `DIR_ENT`.
- `DOS_FILE` is the in-memory directory tree node with short entry, long name, offsets, parent/next/first links.
- `DOS_FS` describes a mounted FAT filesystem: FAT geometry, root/data offsets, cluster counts, loaded FAT, cluster owners, label.
- FAT helper macros define EOF, bad-cluster, and extension-bit handling across FAT12/16/32 effective entry sizes.

Dependencies:
- Includes `msdos_fs.h`.
- Under ReactOS includes `rosglue.h` for checker globals and allocation/printing remaps.
- Non-ReactOS builds declare traditional dosfsck globals such as `interactive`, `rw`, `verbose`, `test`, and `mem_queue`.

Research notes:
- The header is the contract between low-level FAT parsing, directory scanning, LFN handling, and the top-level `VfatChkdsk`.
- `FAT_EXTD(fs)` depends on `fs->eff_fat_bits`; callers must initialize FAT geometry before interpreting FAT values.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fsck.fat.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.c

Implements virtual filesystem I/O for the FAT checker, including delayed write tracking and ReactOS NT-handle based disk access.

Key elements:
- `CHANGE` records queued writes: data buffer, byte offset, size, and next pointer.
- ReactOS path wraps `NtReadFile`, `NtWriteFile`, `NtClose`, and a local `WIN32lseek` using `CurrentOffset`.
- `fs_open` opens the target volume and locks it when opened read-write.
- `fs_isdirty`, `fs_lock`, and `fs_dismount` call filesystem control codes for dirty check, lock/unlock, and dismount.
- `fs_read` reads from disk, then overlays any queued pending writes that overlap the requested range.
- `fs_test` probes readability.
- `fs_write` either writes immediately or queues a `CHANGE`.
- `fs_close` optionally flushes queued changes and returns whether anything changed.

Dependencies:
- Includes `vfatlib.h`, which pulls in ReactOS NDK APIs and checker headers.
- Uses `FsCheckFlags` through `rosglue.h` macros for immediate-write/read-write behavior.

Research notes:
- ReactOS volume I/O is sector-aligned to 512 bytes for reads/writes, preserving unaligned caller semantics by read-modify-write.
- Potential edge case: ReactOS `fs_read` and `fs_test` align based on `size`, not `seek_delta + size`; unaligned positions with aligned sizes can require more bytes than allocated/read.
- Delayed writes let checker logic reason over a patched filesystem image before deciding whether to commit.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.h

Declares the checker’s virtual disk I/O API.

Key elements:
- `fs_open` has a Unix path signature outside ReactOS and a `PUNICODE_STRING` volume-root signature in ReactOS.
- Core APIs: `fs_read`, `fs_test`, `fs_write`, `fs_close`, `fs_changed`.
- ReactOS-only APIs: `fs_isdirty`, `fs_lock`, `fs_dismount`.

Dependencies:
- Relies on `off_t`; on ReactOS this is provided through the broader included checker/library headers.
- Publicly mirrors the implementation in `io.c`.

Research notes:
- This header abstracts checker code from immediate vs deferred write behavior.
- ReactOS additions expose Windows volume lifecycle operations needed by `VfatChkdsk`.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.c

Implements VFAT long-filename parsing, validation, repair prompts, checksum repair, and orphan cleanup.

Key elements:
- Defines packed `LFN_ENT`, matching the 32-byte VFAT long-name directory slot format.
- Parser state is module-global: collected Unicode name buffer, checksum, expected slot, slot offsets, and part count.
- `cnv_unicode` converts UTF-16LE name data to multibyte output, escaping unconvertible characters with FAT-style escape notation.
- `lfn_add_slot` consumes LFN directory entries, validates sequence numbers, checksum, reserved field, and start cluster.
- `lfn_get` attaches collected LFN slots to the following short directory entry after checksum validation.
- `lfn_fix_checksum` updates alias checksums across an LFN slot range.
- `lfn_check_orphaned` deletes or leaves unattached LFN fragments depending on mode.

Dependencies:
- Uses `fs_write` for in-place repairs.
- Uses `file_name` to display short aliases.
- Uses checker globals/macros: `interactive`, `rw`, `mem_queue`, `get_key`, `qalloc`, `alloc`, `free`.

Research notes:
- Noninteractive behavior is conservative for many structural LFN problems, but auto-fixes reserved/start fields; ReactOS only auto-deletes orphaned LFN slots when read-write is enabled.
- The parser is stateful and assumes directory traversal calls `lfn_add_slot` for consecutive LFN entries and `lfn_get` on the following non-LFN entry.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.h

Declares the VFAT long-filename parser and repair helpers.

Key elements:
- `lfn_reset` clears parser state.
- `lfn_add_slot` processes one VFAT LFN directory slot.
- `lfn_get` returns the reconstructed long name for a matching short entry.
- `lfn_check_orphaned` handles unfinished/unattached long-name state.
- `lfn_fix_checksum` repairs checksum bytes over a slot range.

Dependencies:
- Requires `DIR_ENT` and `off_t` from surrounding checker headers.

Research notes:
- This header exposes a small state-machine API; callers must preserve directory-entry ordering.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/msdos_fs.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/msdos_fs.h

Defines MS-DOS/FAT directory constants and the packed on-disk directory-entry layout.

Key elements:
- Constants for sector size, directory-entry density, FAT attribute bits, deleted/free markers, and fixed 8.3 names.
- `struct msdos_dir_entry` maps the 32-byte FAT directory entry with timestamps, cluster fields, and file size.
- ReactOS packing uses `pshpack1.h`/`poppack.h`; GCC builds also use `__attribute__((packed))`.

Dependencies:
- Included by checker headers such as `file.h` and `fsck.fat.h`.

Research notes:
- `SECTOR_SIZE` is fixed at 512 here; formatter code separately uses disk geometry bytes per sector.
- `IS_FREE` treats zero name byte and deleted marker as free directory entries.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/msdos_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/rosglue.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/rosglue.h

Adapts imported checker code to the ReactOS runtime.

Key elements:
- Defines `__attribute__` away for non-GNU compilers, with a packing warning.
- Remaps `printf` to `VfatPrint`.
- Remaps allocation calls to `vfalloc`, `vfcalloc`, and `vffree`.
- Defines `FSCHECK_*` bit flags and maps traditional dosfsck globals to `FsCheckFlags`, `FsCheckTotalFiles`, and `FsCheckMemQueue`.
- Forces `atari_format` to `FALSE`.

Dependencies:
- Expects globals and print/allocation functions from the ReactOS VFAT library/checker integration.

Research notes:
- This is the main compatibility layer that lets dosfstools-derived code compile in ReactOS user-mode filesystem libraries.
- Because `interactive`, `rw`, and related names are macros, side effects depend on global `FsCheckFlags`.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/rosglue.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/swab.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/swab.h

Imported Linux byte-swap helper header for endian conversion support.

Key elements:
- Defines raw constant/runtime byte swaps for 16-, 32-, and optionally 64-bit integer types.
- Provides architecture override hooks such as `__arch__swab16`.
- Uses GCC constant-folding when available.
- Exposes kernel-style aliases only under `__KERNEL__`.

Dependencies:
- Includes `compiler.h` and expects Linux-style `__u16`, `__u32`, `__u64`, and attribute macros.

Research notes:
- This is compatibility infrastructure, not FAT-specific logic.
- In this ReactOS subtree it supports byteorder headers used by the checker port on relevant architectures.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/swab.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.c

Provides shared helpers for FAT12/FAT16/FAT32 formatting.

Key elements:
- `GetShiftCount` computes a shift value for power-of-two division, used to avoid 64-bit division.
- `CalcVolumeSerialNumber` derives a FAT volume serial from current system time fields.
- `FatWipeSectors` zero-fills the target volume in cluster-sized chunks and reports progress.

Dependencies:
- Uses ReactOS NDK time and file APIs through `vfatlib.h`.
- Calls `UpdateProgress` from `vfatlib.c`.
- Allocates through the process heap.

Research notes:
- `FatWipeSectors` allocates one cluster-sized zero buffer, then handles any trailing sectors after whole-cluster writes.
- `GetShiftCount` assumes power-of-two inputs for correct sector-size and cluster-size division use.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.h

Declares shared VFAT formatting helpers.

Key elements:
- `GetShiftCount`
- `CalcVolumeSerialNumber`
- `FatWipeSectors`

Dependencies:
- Requires ReactOS types and `PFORMAT_CONTEXT`, normally supplied by `vfatlib.h`.

Research notes:
- This header is included by `vfatlib.h`, making helpers available to `fat12.c`, `fat16.c`, and `fat32.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/common.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat12.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat12.c

Implements FAT12 volume formatting.

Key elements:
- Writes a FAT16-style boot-sector structure populated for FAT12.
- Initializes both FAT copies with FAT12 reserved cluster entries.
- Zeroes the fixed-size root directory.
- Chooses default cluster size: 4 KiB for fixed media, 512 bytes for removable/floppy media.
- Calculates FAT size from sector count, reserved sectors, root directory sectors, FAT count, and 12-bit entries.
- Supports full format by calling `FatWipeSectors` before writing metadata.

Dependencies:
- Uses `FAT16_BOOT_SECTOR` from `vfatlib.h`.
- Uses `CalcVolumeSerialNumber`, `GetShiftCount`, `FatWipeSectors`, and `UpdateProgress`.
- Uses `NtWriteFile` for direct metadata writes.

Research notes:
- Boot-sector signature is written at the end of the allocated sector buffer.
- Root entries are fixed at 512, matching classic FAT12/FAT16 root-directory layout.
- Label conversion truncates/pads to 11 OEM bytes.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat12.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat16.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat16.c

Implements FAT16 volume formatting.

Key elements:
- Writes FAT16 BPB/boot sector and signature.
- Initializes both FAT copies with media byte, reserved cluster, clean shutdown, and EOC markers.
- Zeroes the fixed root directory.
- Selects default cluster size by partition length: 1 KiB under 16 MiB, 2 KiB under 128 MiB, 4 KiB under 256 MiB, otherwise 8 KiB.
- Calculates FAT sectors for 16-bit entries.
- Supports quick and full format.

Dependencies:
- Uses shared VFAT boot-sector structures and helpers from `vfatlib.h`/`common.c`.
- Writes through `NtWriteFile`.

Research notes:
- Like FAT12, FAT16 uses a fixed root directory and two FAT copies.
- Assumes FAT16 formatting is selected only for partitions in an appropriate size range by `VfatFormat`.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat16.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat32.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat32.c

Implements FAT32 volume formatting.

Key elements:
- Writes primary and backup FAT32 boot sectors.
- Writes FSInfo sectors and backup FSInfo sectors.
- Initializes both FAT copies, including root directory cluster 2 as EOC.
- Writes an empty root directory cluster.
- Chooses default cluster size by partition length: 4 KiB under 8 GiB, 8 KiB under 16 GiB, 16 KiB under 32 GiB, otherwise 32 KiB.
- Computes `FATSectors32` and adjusts for the edge case where usable FAT entries are fewer than data clusters.

Dependencies:
- Uses `FAT32_BOOT_SECTOR`, `FAT32_FSINFO`, and FSInfo signature constants from `vfatlib.h`.
- Uses common serial, shift, wipe, and progress helpers.
- Uses `NtWriteFile`.

Research notes:
- Reserved sectors are fixed at 32, FSInfo at sector 1, backup boot at sector 6, root cluster at 2.
- `FsInfo->FreeCount` reserves the root cluster by subtracting one from computed free clusters.
- Formatter writes the backup FSInfo free count as unknown.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat32.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.c

Top-level ReactOS VFAT format and check API.

Key elements:
- Globals bridge checker state: `ChkdskCallback`, `FsCheckFlags`, `FsCheckMemQueue`, `FsCheckTotalFiles`.
- `VfatFormat` opens the volume, queries geometry/partition information, selects FAT12/16/32, locks the volume, dispatches to the formatter, dismounts/unlocks, and closes.
- FAT type selection uses existing MBR partition type when known, otherwise partition size/start-offset heuristics; GPT is size-based with a 32 GiB FAT limit.
- `UpdateProgress` converts sector increments into callback progress percentages.
- `VfatPrintV` and `VfatPrint` route checker/formatter text to FMIFS output callbacks.
- `VfatChkdsk` wires ReactOS parameters into the dosfstools-derived checker: open, dirty check, boot/FAT/root scan, bad-cluster scan, reclaim, free-count update, verification, optional commit, reporting, dismount/unlock, close.

Dependencies:
- Calls `Fat12Format`, `Fat16Format`, `Fat32Format`.
- Calls checker functions declared through `check/dosfsck.h` and related headers: `read_boot`, `read_fat`, `scan_root`, `fix_bad`, `reclaim_file`, `reclaim_free`, `update_free`, `file_unused`, `qfree`, `fs_*`.

Research notes:
- `VfatChkdsk` sets read-write only when `FixErrors` is true; otherwise it can detect dirty/corrupt state without committing changes.
- If `fs_open` fails with access denied, it asks the callback via `VOLUMEINUSE` whether to continue.
- There is a risky cleanup path: after failed `fs_open`, it calls `fs_close(FALSE)` even though a valid handle may not exist.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.h

Primary internal header for the ReactOS VFAT library.

Key elements:
- Pulls in C runtime, Windows-compatible types, ReactOS NDK I/O/kernel/object/RTL APIs, and FMIFS callbacks.
- Includes checker API via `check/dosfsck.h`.
- Defines packed `FAT16_BOOT_SECTOR`, `FAT32_BOOT_SECTOR`, and `FAT32_FSINFO`.
- Defines FSInfo signatures.
- Defines `FORMAT_CONTEXT` for progress callbacks.
- Defines `FAT_TYPE` enum.
- Declares FAT12/16/32 formatters, progress update, and print functions.

Dependencies:
- Includes `common.h` after defining `FORMAT_CONTEXT`.
- Used by all VFAT formatter and checker integration files.

Research notes:
- The boot-sector structures are manually laid out with offsets in comments and packed to match on-disk format.
- This header is both formatter infrastructure and checker integration point, since it includes the imported check API.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/CMakeLists.txt -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/CMakeLists.txt

Build definition for the VFATX library.

Key elements:
- Builds `vfatxlib` from `fatx.c`, `vfatxlib.c`, and `vfatxlib.h`.
- Adds precompiled header support using `vfatxlib.h`.
- Links `chkstk`.
- Links `-lgcc` for non-MSVC builds.
- Depends on `psdk`.

Research notes:
- The library is separate from `vfatlib`; FATX formatting is compiled as its own FMIFS-style filesystem library component.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/fatx.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/fatx.c

Implements FATX formatting logic.

Key elements:
- Local `GetShiftCount` and `CalcVolumeSerialNumber` duplicate VFAT helper behavior.
- `FatxWriteBootSector` writes the 4096-byte FATX boot sector.
- `Fatx16WriteFAT` and `Fatx32WriteFAT` initialize a single FAT copy depending on cluster count.
- `FatxWriteRootDirectory` writes a root directory area filled with `0xff`.
- `FatxFormat` builds a FATX boot sector, uses 32 sectors per cluster, one FAT, computes cluster/FAT size, writes boot sector, FAT, and root directory.

Dependencies:
- Uses `vfatxlib.h` structures and `VfatxUpdateProgress`.
- Uses ReactOS NDK time/RTL APIs and `NtWriteFile`.

Research notes:
- FATX switches to 32-bit FAT entries when cluster count exceeds 65525.
- All on-disk positioning assumes 512-byte sectors plus a 4096-byte FATX boot sector.
- Full non-quick format is incomplete; it only contains a FIXME to fill remaining sectors.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/fatx.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.c

Top-level VFATX FMIFS-style API.

Key elements:
- `VfatxFormat` opens the target volume, queries geometry and partition information, initializes progress context, and calls `FatxFormat`.
- Rejects `BackwardCompatible == TRUE` as unsupported.
- Builds synthetic partition information for non-fixed media.
- `VfatxChkdsk` is unimplemented but returns success.
- `VfatxUpdateProgress` reports percentage changes through the callback.

Dependencies:
- Uses `FatxFormat` from `fatx.c`.
- Uses ReactOS NDK object/I/O APIs and FMIFS callback codes.

Research notes:
- Unlike `VfatFormat`, this function does not lock/dismount/unlock the volume around formatting.
- `Label` and `ClusterSize` parameters are accepted by signature but unused.
- The unimplemented check path means FATX has formatter support but no real consistency checker here.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.h

Internal header for the ReactOS VFATX library.

Key elements:
- Includes ReactOS user-mode NDK types, process/thread/loader types, I/O functions, and FMIFS APIs.
- Defines packed `FATX_BOOT_SECTOR`, a 4096-byte structure with signature, volume ID, sectors per cluster, FAT count, unknown field, and unused padding.
- Defines VFATX `FORMAT_CONTEXT`.
- Declares `FatxFormat` and `VfatxUpdateProgress`.

Dependencies:
- Used by both `fatx.c` and `vfatxlib.c`.

Research notes:
- FATX boot-sector layout is much simpler than FAT12/16/32 BPBs.
- The header exposes only formatter internals; no FATX checking API is declared beyond the exported implementation signature in `vfatxlib.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatxlib/vfatxlib.h -->