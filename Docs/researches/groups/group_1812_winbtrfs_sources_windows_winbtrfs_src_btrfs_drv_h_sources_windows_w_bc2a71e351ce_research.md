# Group Research: group_1812_winbtrfs_sources_windows_winbtrfs_src_btrfs_drv_h_sources_windows_w_bc2a71e351ce

Scope checked against `Docs/research_subset_a.md`: `sources/windows/winbtrfs` is included in subset A. Every source file listed for this work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/btrfs_drv.h -->
# File Research: sources/windows/winbtrfs/src/btrfs_drv.h

## Role

`btrfs_drv.h` is the central private driver header for WinBtrfs. It establishes Windows kernel build compatibility, global constants, core in-memory filesystem objects, lock helpers, debug/logging shims, and cross-module function prototypes for most of the driver.

## Major Definitions

- Build and compatibility setup: forces `_WIN32_WINNT`/`NTDDI_VERSION`, includes `ntifs.h`, `ntddk.h`, Mount Manager and WDM headers, then pulls in on-disk Btrfs definitions from `btrfs.h` and the public ioctl ABI from `btrfsioctl.h`.
- Driver constants: pool tags, known extended attribute names and CRC hashes, maximum extent sizes, compression extent size, read-ahead granularity, Btrfs volume prefix, Linux/WSL reparse tags, and Windows feature constants missing from older headers.
- Core file model:
  - `fcb_nonpaged` owns file resources, paging resources, directory child locks, and section object pointers.
  - `fcb` is the in-memory inode/file-control block with FSRTL header, subvolume/inode identity, security descriptor, file locks/oplocks, cached extents, hardlinks, xattrs, alternate data stream state, directory-child hash/index lists, dirty flags, and metadata-change flags.
  - `file_ref` models a name/path reference to an FCB, including parent/child links, open counts, delete-on-close/POSIX-delete state, and dirty tracking.
  - `ccb` is the per-open context, carrying create options, directory query cursor, privileges, access mask, filename, case-sensitivity state, EA index, LXSS flag, and send-stream state.
- Tree and root model:
  - `tree`, `tree_data`, `tree_holder`, `traverse_ptr`, `root`, `root_nonpaged`, and batch/rollback structs define the in-memory B-tree cache and mutation staging model.
  - `batch_operation` covers deletes/inserts for inode refs, extrefs, dir items, xattrs, extent data, free-space entries, and generic tree items.
- Storage model:
  - `device`, `space`, `chunk`, `changed_extent`, `changed_extent_ref`, `partial_stripe`, `range_lock`, and `sys_chunk` represent devices, allocation ranges, chunks, delayed extent reference updates, RAID/stripe bookkeeping, and system chunks.
  - `write_data_stripe`, `write_data_context`, and `tree_write` describe multi-device write operations and delayed tree writes.
- Volume/control objects:
  - `device_extension` is the main VCB. It owns mount options, superblock, sector/checksum sizes, device/chunk/root/tree lists, all major locks, dirty FCB/fileref/subvolume lists, cache lookasides, flush thread state, calculation threads, balance/scrub/send state, and root/dummy FCBs.
  - `control_device_extension`, `bus_device_extension`, `volume_device_extension`, `pdo_device_extension`, and `volume_child` model non-filesystem control/bus/PnP devices and discovered Btrfs volumes.
- Background operations:
  - `calc_job`, `drv_calc_thread`, and `drv_calc_threads` define the checksum/compression worker queue used by `calcthread.c`.
  - `balance_info`, `scrub_info`, and `scrub_error` hold long-running balance and scrub state.
  - `send_info` tracks send-subvolume worker state.

## Inline Logic

- Lock helpers wrap shared/exclusive acquisition and release of `Vcb->fcb_lock`, with SAL annotations.
- `map_user_buffer` maps MDL-backed IRP buffers or falls back to `Irp->UserBuffer`.
- `unix_time_to_win` and `win_time_to_unix` convert Btrfs timestamps to Windows 100ns FILETIME epoch and back.
- `get_raid0_offset` maps a logical RAID0 offset to stripe offset and stripe index.
- `make_file_id` packs a subvolume id and inode into Windows' 64-bit file-id space.
- `keycmp`, `sector_align`, `is_subvol_readonly`, `get_extent_data_len`, and `get_extent_data_refcount` provide common Btrfs key, alignment, readonly, and extent-ref helpers.
- `fcb_oplock` abstracts old/new FSRTL advanced FCB header layouts; `fast_io_possible` combines oplock, lock, and readonly checks.
- `write_fcb_compressed` centralizes compression eligibility: excludes NODATACOW, metadata/cache/root inodes, page files, and NOCOMPRESS unless mount force-compression is set.
- `fcb_alloc_size` maps directory/sparse/regular allocation-size reporting.

## Cross-Module API Surface

This header declares the driver-wide interfaces for:

- Driver/device lifecycle and PnP: `AddDevice`, mount manager thread/callbacks, disk/volume arrival and removal, PDO/volume helpers, boot helpers.
- B-tree operations: item find/next/prev, load/free tree, insert/delete item, batch commit, rollback, tree-difference scanning.
- Create/open/name handling: open FCB/fileref, load directories, add directory children, lookup by inode/name, mode inheritance.
- Read/write/flush: file read/write paths, extent insertion, chunk allocation, physical I/O, checksums, tree checksums, partial stripe flushing, cache flushing.
- Free space and extent tree: free-space cache loading/updating, space-list add/subtract/merge, extent refcount changes, changed-extent tracking.
- User-visible IRP handlers: create, read, write, directory control, security, file information, EA, FSCTL, device control, PnP.
- Compression/checksum workers: zlib/lzo/zstd compress/decompress, compressed write path, checksum/compression job helpers, calculation thread routine.
- Balance, scrub, send, registry, reparse, security mapping, galois/RAID6 math, worker thread jobs, cache manager callbacks.

## Dependencies

- Depends on Windows kernel primitives: `ERESOURCE`, `FAST_MUTEX`, `KEVENT`, `KSPIN_LOCK`, `FILE_OBJECT`, `IRP`, `VPB`, `MDL`, FSRTL headers, oplocks, cache manager, Mount Manager, PnP notifications, and kernel process/thread APIs.
- Depends on local on-disk format definitions from `btrfs.h` and public WinBtrfs ioctl structs from `btrfsioctl.h`.
- Provides declarations consumed by almost every `.c` file in `src`.

## Research Notes

- This is a high-coupling driver umbrella header, not a narrow interface file. It intentionally centralizes the private ABI among subsystems.
- Locking is an important theme: SAL lock annotations document intended order, notably `tree_lock` before `fcb_lock`, and chunk locking is optionally instrumented under `DEBUG_CHUNK_LOCKS`.
- Several compatibility definitions fill gaps between MSVC, MinGW/GCC, older WDKs, and newer Windows FS features. This header is therefore both architectural glue and portability glue.
- The header includes private declarations for newer Windows runtime APIs and PEB structures, implying some routines dynamically probe OS behavior rather than depending only on static WDK availability.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/btrfs_drv.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/btrfsioctl.h -->
# File Research: sources/windows/winbtrfs/src/btrfsioctl.h

## Role

`btrfsioctl.h` is the public-ish WinBtrfs ioctl/FSCTL ABI header. It defines control codes and packed request/response structures used by user-mode tools and driver FSCTL handling.

## Control Codes

The file defines Btrfs-specific FSCTL/IOCTL values from function codes `0x829` through `0x84a`, including:

- File identity and metadata: `FSCTL_BTRFS_GET_FILE_IDS`, `GET_INODE_INFO`, `SET_INODE_INFO`, `GET_UUID`, `GET_CSUM_INFO`.
- Subvolume operations: create subvolume, create snapshot, received subvolume, reserve/find/send subvolume, read send buffer.
- Device and usage operations: get devices, get usage, add/remove device, resize, query filesystems, probe volume, unload.
- Balance operations: start/query/pause/resume/stop balance.
- Scrub operations: start/query/pause/resume/stop scrub.
- Unix-like metadata operations: `MKNOD`, get/set xattrs.
- Statistics: reset device stats.

## Data Structures

- File and inode reporting: `btrfs_get_file_ids`, `btrfs_inode_info`, and `btrfs_set_inode_info`.
- Snapshot/subvolume creation: `btrfs_create_snapshot`, `btrfs_create_snapshot32`, and `btrfs_create_subvol`; the 32-bit variants use `POINTER_32` to keep WOW64 ABI compatibility.
- Device/usage reporting: `btrfs_device`, `btrfs_usage_device`, `btrfs_usage`, `btrfs_filesystem_device`, and `btrfs_filesystem`.
- Balance: option flags, profile/range/limit/usage/convert filters in `btrfs_balance_opts`, status flags, `btrfs_query_balance`, and `btrfs_start_balance`.
- Scrub: status flags, per-error data/metadata union in `btrfs_scrub_error`, and aggregate `btrfs_query_scrub`.
- Unix/xattr/send/resize/checksum helpers: `btrfs_mknod`, `btrfs_received_subvol`, `btrfs_set_xattr`, `btrfs_find_subvol`, `btrfs_send_subvol`, `btrfs_send_subvol32`, `btrfs_resize`, and `btrfs_csum_info`.

## ABI Characteristics

- Many structs use trailing one-element arrays (`name[1]`, `devices[1]`, `data[1]`, `clones[1]`) for variable-length buffers.
- Wide-character names are used for Windows-facing names; raw `char` data is used for xattrs.
- The header includes `btrfs.h`, so public ioctl structures expose Btrfs types such as `BTRFS_UUID` and `KEY`.
- Compression constants in this file define the user-visible values for any/zlib/lzo/zstd.

## Research Notes

- This header is an ABI boundary. Field ordering, integer widths, pointer-size variants, and control-code values should be treated as stable.
- The methods vary by operation: many use direct I/O, xattr/send/find/csum use buffered I/O, and unload uses `METHOD_NEITHER`.
- The file explicitly says no copyright is claimed, unlike most driver implementation files.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/btrfsioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/cache.c -->
# File Research: sources/windows/winbtrfs/src/cache.c

## Role

`cache.c` installs WinBtrfs cache manager callbacks for lazy writer and read-ahead paths.

## Behavior

- Defines the global `CACHE_MANAGER_CALLBACKS cache_callbacks`.
- `acquire_for_lazy_write`:
  - Converts `Context` to `PFILE_OBJECT`, then to `fcb`.
  - Acquires `fcb->Vcb->tree_lock` shared.
  - Acquires the FCB header resource exclusive.
  - Records `fcb->lazy_writer_thread`.
  - Sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`.
- `release_from_lazy_write`:
  - Clears `lazy_writer_thread`.
  - Releases the FCB resource and then `tree_lock`.
  - Clears top-level IRP if it still equals the cache top-level marker.
- `acquire_for_read_ahead`:
  - Acquires the FCB resource shared.
  - Sets top-level IRP to cache top-level marker.
- `release_from_read_ahead`:
  - Releases the FCB resource.
  - Clears the top-level IRP marker if still present.
- `init_cache` wires these four callbacks into `cache_callbacks`.

## Dependencies

- Includes `btrfs_drv.h` for FCB/VCB structures, `TRACE`, and Windows kernel types.
- Used where `CcInitializeCacheMap` receives `&cache_callbacks`.

## Research Notes

- Lazy writer takes `tree_lock` before the FCB resource, matching the broader lock-order discipline in the driver.
- Lazy writer uses exclusive FCB resource acquisition, while read-ahead uses shared acquisition.
- The callbacks respect the cache manager's nonblocking `Wait` parameter by returning `false` if either required resource cannot be acquired.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/calcthread.c -->
# File Research: sources/windows/winbtrfs/src/calcthread.c

## Role

`calcthread.c` implements the driver calculation worker system for per-sector checksums and compression/decompression jobs.

## Main Components

- `calc_thread_main(device_extension* Vcb, calc_job* cj)` drains either one targeted job or the global calculation queue.
- `do_calc_job` creates a stack-allocated checksum job over a number of sectors, queues it, helps process it synchronously, and waits for completion.
- `add_calc_job_decomp` allocates a heap job for one zlib/lzo/zstd decompression operation.
- `add_calc_job_comp` allocates a heap job for one zlib/lzo/zstd compression operation.
- `calc_thread` is the system-thread routine that waits on `Vcb->calcthreads.event`, drains queued jobs, honors `thread->quit`, and signals `thread->finished`.

## Job Types

Checksum jobs:

- `calc_thread_crc32c`: stores bitwise-not CRC32C of one sector.
- `calc_thread_xxhash`: stores `XXH64` of one sector.
- `calc_thread_sha256`: calls `calc_sha256`.
- `calc_thread_blake2`: calls `blake2b` with `BLAKE2_HASH_SIZE`.

Compression jobs:

- Decompression: zlib, LZO, ZSTD.
- Compression: zlib, LZO, ZSTD, using mount-level compression options for levels.

## Synchronization

- The queue is protected by `Vcb->calcthreads.spinlock`.
- Each `calc_job` has `left` and `not_started` counters plus a completion event.
- Jobs are removed from the queue when `not_started` reaches zero.
- `InterlockedDecrement(&cj2->left)` signals the job event when all units finish.
- The caller can run `calc_thread_main` directly after enqueueing. This makes checksum jobs partly work-conserving: the submitting thread helps process its own work before blocking.

## Dependencies

- Includes `btrfs_drv.h`, ZSTD's `xxhash.h`, and `crc32c.h`.
- Calls codec functions declared in `btrfs_drv.h`: `zlib_decompress`, `lzo_decompress`, `zstd_decompress`, `zlib_compress`, `lzo_compress`, `zstd_compress`.
- Uses `Vcb->superblock.sector_size`, `Vcb->csum_size`, and `Vcb->options` for job sizing and compression levels.

## Research Notes

- Heap `calc_job` allocations are nonpaged and ownership is passed to the caller, which waits and frees them after completion.
- `calc_thread` pins each worker to an affinity bit derived from `thread->number`.
- The event is set and immediately cleared while holding the spinlock when jobs are enqueued; worker threads wait on that event and then drain all available work.
- Error paths record `cj2->Status` for compression/decompression jobs and log failures.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/calcthread.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/compress.c -->
# File Research: sources/windows/winbtrfs/src/compress.c

## Role

`compress.c` provides zlib, LZO, and ZSTD compression/decompression support plus the filesystem-level `write_compressed` path that turns file data into Btrfs compressed extents.

## Codec Support

- zlib:
  - `zlib_alloc`/`zlib_free` allocate from paged pool using `ALLOC_TAG_ZLIB`.
  - `zlib_compress` wraps `deflateInit`, `deflate(..., Z_FINISH)`, and `deflateEnd`.
  - `zlib_decompress` wraps `inflateInit`, `inflate(..., Z_NO_FLUSH)`, and `inflateEnd`.
- LZO:
  - Defines an `lzo_stream` cursor/error structure and LZO1X constants.
  - `do_lzo_decompress` implements bytecode-style LZO decompression with bounds checks on input, output, and backreferences.
  - `lzo_decompress` handles Btrfs' per-page LZO framing, page padding, and zero-fills short decompressed pages.
  - `lzo_do_compress`, `lzo1x_1_compress`, and `lzo_compress` implement old LGPL LZO compression and Btrfs page framing.
- ZSTD:
  - Uses `ZSTD_STATIC_LINKING_ONLY` and ZSTD custom memory callbacks backed by paged pool.
  - `zstd_decompress` uses a `ZSTD_DStream`.
  - `zstd_compress` uses a `ZSTD_CStream`, clamps `windowLog` to Btrfs' maximum of 17, and reports remaining output space.

## `write_compressed`

The filesystem integration path does the following:

- Chooses compression type from mount options, per-FCB compression property, and filesystem incompat flags.
- Calls `excise_extents` to remove the old data range.
- Splits the write into `COMPRESSED_EXTENT_SIZE` chunks, 128 KiB each.
- Queues one compression calculation job per chunk through `add_calc_job_comp`.
- Drains jobs, waits for each completion event, and propagates any codec failure.
- Keeps compressed output only if it saves at least one sector; otherwise stores that chunk uncompressed.
- Sets LZO/ZSTD incompat flags when those compression types are actually used.
- Sector-aligns compressed output buffers and zero-pads alignment slack.
- If the first 128 KiB of a file is incompressible and compression was not forced, marks the inode `BTRFS_INODE_NOCOMPRESS`.
- Concatenates all chosen parts into a contiguous buffer.
- Finds or allocates a suitable data chunk, reserves free space with `space_list_subtract`, and writes the buffer through `write_data_complete`.
- Calculates sector checksums with `do_calc_job` unless the inode has `BTRFS_INODE_NODATASUM`.
- Creates `EXTENT_DATA`/`EXTENT_DATA2` entries for each compressed or uncompressed part via `add_extent_to_fcb`.
- Adds delayed extent references with `add_changed_extent_ref`.
- Marks extents and inode state dirty and calls `mark_fcb_dirty`.

## Dependencies

- Includes `btrfs_drv.h`, `zlib/zlib.h`, and `zstd/lib/zstd.h`.
- Relies on driver allocation, write, checksum, chunk, space-list, rollback, and extent-ref APIs declared in `btrfs_drv.h`.
- Used by write and FSCTL code paths for compressed data writes; read and send paths use the decompression helpers.

## Research Notes

- The file contains third-party-derived codec code: LZO decompression notes credit libavcodec and LZO compression notes credit LZO 0.22.
- `write_compressed` mixes CPU work, allocation, chunk-space reservation, physical I/O, checksum generation, and metadata updates, so rollback and cleanup behavior is important.
- The compression decision is per 128 KiB part; a single logical write can produce a mix of compressed and uncompressed extents.
- ZSTD is constrained to Btrfs' expected window size, preventing creation of extents that Linux/Btrfs-compatible readers would reject.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/crc32c-aarch64.asm -->
# File Research: sources/windows/winbtrfs/src/crc32c-aarch64.asm

## Role

`crc32c-aarch64.asm` provides the ARM64 hardware CRC32C implementation of `calc_crc32c_hw`.

## Behavior

- Exports `calc_crc32c_hw`.
- Calling convention documented in comments:
  - `w0`: seed/current CRC.
  - `x1`: input buffer.
  - `w2`: input length.
  - `x3`: scratch.
- Processes 8-byte chunks with `crc32cx`.
- Processes remaining 4-byte, 2-byte, and 1-byte tail data with `crc32cw`, `crc32ch`, and `crc32cb`.
- Returns the updated CRC in `w0`.

## Dependencies

- Declared by `crc32c.h` when `_ARM64_` is defined.
- Selected at runtime by driver initialization when ARM64 CRC32 instructions are detected.

## Research Notes

- This file contains only the hardware path. The portable software fallback for ARM64 comes from `crc32c.c`.
- The file uses ARM assembler syntax with `AREA`, `GLOBAL`, and `END`.
- The loop branches back to `calc_crc32c_hw` for 8-byte chunks, then falls through the tail handlers.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/crc32c-aarch64.asm -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/crc32c-gas.S -->
# File Research: sources/windows/winbtrfs/src/crc32c-gas.S

## Role

`crc32c-gas.S` provides GNU assembler CRC32C implementations for x86-64 and x86 builds.

## x86-64 Path

- Exports `calc_crc32c_sw` and `calc_crc32c_hw`.
- Uses Windows x64 register arguments:
  - `rcx`: seed.
  - `rdx`: buffer.
  - `r8`: length.
- Software path:
  - Processes one byte at a time.
  - Uses external `crctable`.
  - Computes `crctable[(crc ^ byte) & 0xff] ^ (crc >> 8)`.
- Hardware path:
  - Uses SSE4.2 `crc32` instructions.
  - Processes 8-byte chunks, then 4-byte, 2-byte, and 1-byte tails.

## x86 Path

- Exports stdcall-decorated `_calc_crc32c_sw@12` and `_calc_crc32c_hw@12`.
- Reads seed, buffer, and length from stack.
- Software path mirrors the table-driven byte loop.
- Hardware path processes 4-byte chunks, then 2-byte and 1-byte tails with `crc32`.
- Returns with `ret 12`, matching stdcall cleanup.

## Dependencies

- Depends on external `crctable`/`_crctable` defined in `crc32c.c`.
- Declared by `crc32c.h` for `_X86_` and `_AMD64_`.
- Intended for non-MSVC toolchains using GAS-compatible assembly.

## Research Notes

- The file uses Intel syntax under GAS (`.intel_syntax noprefix`) to keep instruction bodies close to the MASM version.
- Hardware use must be gated by runtime CPU feature checks elsewhere; the assembly itself assumes the `crc32` instruction is available when called.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/crc32c-gas.S -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/crc32c-masm.asm -->
# File Research: sources/windows/winbtrfs/src/crc32c-masm.asm

## Role

`crc32c-masm.asm` provides MASM CRC32C implementations for MSVC x64 and x86 builds.

## x64 Path

- Chosen under `IFDEF RAX`.
- Declares `EXTERN crctable:qword`.
- Exports `calc_crc32c_sw` and `calc_crc32c_hw`.
- Uses Windows x64 calling convention with seed in `rcx`, buffer in `rdx`, and length in `r8`.
- Software path uses the table-driven byte loop.
- Hardware path uses `crc32` over 8-byte chunks, then 4-byte, 2-byte, and 1-byte tails.

## x86 Path

- Uses `.686P` when not assembling x64.
- Declares `EXTERN crctable:ABS`.
- Exports `calc_crc32c_sw@12` and `calc_crc32c_hw@12`.
- Preserves `esi` and `ebx` in the software path.
- Reads arguments from the stack and returns with `ret 12`.
- Hardware path uses `crc32` over 4-byte chunks, then 2-byte and 1-byte tails.

## Dependencies

- Depends on `crctable` from `crc32c.c`.
- Provides the x86/x64 symbols declared in `crc32c.h` when building with MSVC/MASM.

## Research Notes

- This is functionally parallel to `crc32c-gas.S`, with syntax and symbol decoration adapted for MASM.
- Hardware routines require external CPU feature selection before the function pointer is redirected to `calc_crc32c_hw`.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/crc32c-masm.asm -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/crc32c.c -->
# File Research: sources/windows/winbtrfs/src/crc32c.c

## Role

`crc32c.c` defines the CRC32C function pointer, lookup table, and portable software implementation used by WinBtrfs.

## Behavior

- Defines `crc_func calc_crc32c = calc_crc32c_sw`, so the default implementation is software.
- Defines the 256-entry CRC32C table `crctable`.
- For non-x86/non-amd64 builds, defines `calc_crc32c_sw` in C:
  - Starts with the supplied seed.
  - For each byte, updates `rem = crctable[(rem ^ msg[i]) & 0xff] ^ (rem >> 8)`.
  - Returns the non-finalized remainder.

## Architecture Interaction

- x86 and amd64 software implementations live in assembly files, so the C software function is excluded for `_X86_` and `_AMD64_`.
- ARM64 gets the C software fallback here and the hardware implementation from `crc32c-aarch64.asm`.
- Driver initialization elsewhere can replace `calc_crc32c` with `calc_crc32c_hw` after CPU feature detection.
- Callers perform Btrfs-specific final inversion where needed, for example `~calc_crc32c(0xffffffff, ...)`.

## Dependencies

- Includes `crc32c.h`, standard integer/bool headers, and SAL annotations.
- The assembly files depend on this file's exported `crctable`.

## Research Notes

- The function pointer design makes hardware acceleration transparent to checksum callers.
- The implementation returns an intermediate CRC state, not always the final Btrfs checksum value; callers decide seed and complement semantics.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/crc32c.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/crc32c.h -->
# File Research: sources/windows/winbtrfs/src/crc32c.h

## Role

`crc32c.h` is the small public declaration header for the WinBtrfs CRC32C implementation.

## API

- Declares `calc_crc32c_hw` only for `_X86_`, `_AMD64_`, or `_ARM64_`.
- Declares `calc_crc32c_sw` for all builds.
- Defines `crc_func` as a `__stdcall` function pointer taking seed, byte buffer, and length.
- Declares the global dispatch pointer `extern crc_func calc_crc32c`.
- Wraps declarations in `extern "C"` for C++ consumers.

## Dependencies

- Includes `<stdint.h>`.
- Implemented by `crc32c.c` and architecture assembly files.
- Included by `calcthread.c` and other checksum users.

## Research Notes

- This header deliberately exposes both direct implementations and the dispatch pointer. Normal callers use `calc_crc32c`; CPU feature setup code can assign it to the hardware implementation.
- The fixed `__stdcall` signature keeps x86 symbol decoration and cross-language linkage predictable.

<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/crc32c.h -->