# Group Research: group_1656_reactos_sources_windows_reactos_drivers_filesystems_btrfs_btrfs_drv_38a63bdd07fa

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`; all listed files are under that source tree and were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/btrfs_drv.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/btrfs_drv.h

## Purpose

Central private driver header for the ReactOS-imported WinBtrfs filesystem driver. It defines the driver-wide Windows/ReactOS compatibility layer, core in-memory Btrfs objects, synchronization conventions, helper inlines, debug/logging macros, and cross-module prototypes used by the Btrfs driver implementation.

## Main Contents

- Platform setup:
  - Handles `__REACTOS__`, `_MSC_VER`, GCC/Clang warning pragmas, Windows target macros, missing DDK declarations, SAL compatibility, `try/except/finally` compatibility, and ReactOS-specific includes.
  - Includes `btrfs.h` and `btrfsioctl.h`, making this the bridge between on-disk Btrfs structures, user IOCTL ABI, and driver-private state.
- Driver constants:
  - Node types, pool tags, UID/GID defaults, xattr names and CRC hashes, max extent sizes, compressed extent size, read-ahead granularity, reparse tags, device name prefix, FSCTL definitions not present in older headers, and POSIX mode macros.
- Core object model:
  - `fcb_nonpaged`, `fcb`, `file_ref`, `ccb`: file control block, per-open context, name/reference tracking, xattrs, ADS data, cached extents, security descriptor state, dirty flags, oplock and lock state.
  - `extent`, `hardlink`, `dir_child`, `xattr`: in-memory file metadata children and extent representation.
  - `tree`, `tree_data`, `tree_holder`, `traverse_ptr`, `root`: Btrfs tree/root cache structures and traversal state.
  - `device`, `chunk`, `space`, `range_lock`, `partial_stripe`, `changed_extent`, `changed_extent_ref`: physical devices, allocation chunks, free-space/range locking, RAID partial stripes, and delayed extent-ref accounting.
  - `device_extension`: main mounted filesystem VCB containing mount options, superblock, roots, chunks, global locks, FCB lists, dirty lists, flush thread state, checksum/compression worker threads, balance/scrub/send state, and lookaside lists.
  - `volume_device_extension`, `pdo_device_extension`, `volume_child`, `bus_device_extension`, `control_device_extension`: PnP/volume/bus/control device state for multi-device Btrfs volumes.
- Worker/job structures:
  - `calc_job`, `drv_calc_thread`, `drv_calc_threads` for checksum, hash, compression, and decompression work.
  - `balance_info`, `scrub_info`, `scrub_error`, `send_info` for long-running maintenance operations.
- Inline helpers:
  - FCB lock wrappers.
  - `map_user_buffer`.
  - Btrfs/Windows time conversion.
  - RAID0 offset calculation.
  - Btrfs key comparison.
  - Sector alignment.
  - Subvolume readonly checks.
  - Extent ref data sizing/refcount helpers.
  - File ID packing using subvolume and inode.
  - Oplock lookup and fast-IO feasibility.
  - Compression policy via `write_fcb_compressed`.
  - Allocation size calculation via `fcb_alloc_size`.
  - POSIX `makedev`, `major`, `minor` equivalents.
- Cross-module declarations:
  - Prototypes for create/open, read/write, flush, tree functions, cache manager callbacks, compression, checksum workers, free-space cache, extent tree, security, EA, reparse, PnP, volume management, registry, balance, scrub, send, RAID helpers, and boot helpers.

## Architecture Notes

This file is the coordination point for almost every Btrfs driver module. The important ownership boundaries are:

- `device_extension` is the mounted-volume aggregate and owns global structures such as roots, chunks, dirty lists, worker threads, and cache/thread state.
- `fcb` represents inode-backed file state; `file_ref` represents name/reference/open-parent relationships.
- `tree`/`root`/`traverse_ptr` model loaded Btrfs metadata trees and item traversal.
- `chunk`/`device`/`space` model logical-to-physical allocation and free-space accounting.
- `calc_job` connects checksum/hash/compression work in `calcthread.c` and codec routines in `compress.c`.

## Synchronization

The header documents and encodes several lock-order assumptions:

- `_Create_lock_level_` and `_Lock_level_order_(tree_lock, fcb_lock)` establish tree lock before FCB lock.
- `fcb_lock`, `tree_lock`, chunk locks, dirty-list locks, range locks, and partial-stripe locks are embedded in driver state.
- Some prototypes are annotated with `_Requires_lock_held_`, `_Requires_exclusive_lock_held_`, or `_Releases_lock_`, making lock requirements visible across modules.
- `acquire_chunk_lock`/`release_chunk_lock` optionally track held chunk locks under `DEBUG_CHUNK_LOCKS`.

## Dependencies

- Depends on Windows kernel APIs: NT I/O manager, cache manager, FsRtl, resources, spinlocks, events, MDLs, PnP, mount manager, VPB/device objects.
- Depends on Btrfs on-disk type definitions from `btrfs.h`.
- Imports public/private Btrfs control structures from `btrfsioctl.h`.
- Declares codec/checksum integration points used by `compress.c`, `calcthread.c`, `crc32c.c`, and `crc32c.S`.

## Research Notes

- Any change to structures in this header has wide blast radius because many C files include it and share these layouts.
- `btrfsioctl.h` structures are user-visible ABI, while most structures here are driver-private.
- Compression policy is centralized in `write_fcb_compressed`: it avoids compression for NODATACOW files, root/cache inodes, and paging files; it honors force-compress, inode flags, and mount options.
- File IDs are deliberately lossy because Windows exposes 64-bit file IDs while Btrfs uses separate 64-bit subvolume and inode identifiers.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/btrfs_drv.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/btrfsioctl.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/btrfsioctl.h

## Purpose

Public Btrfs IOCTL/FSCTL ABI header for user/kernel communication with the Btrfs driver. It defines Btrfs-specific control codes and the request/response structures used for subvolume management, inode metadata, device listing, usage reporting, balance, scrub, xattrs, send/receive, resize, and checksum queries.

## Main Contents

- Control codes:
  - `FSCTL_BTRFS_GET_FILE_IDS`
  - `FSCTL_BTRFS_CREATE_SUBVOL`
  - `FSCTL_BTRFS_CREATE_SNAPSHOT`
  - `FSCTL_BTRFS_GET_INODE_INFO`
  - `FSCTL_BTRFS_SET_INODE_INFO`
  - `FSCTL_BTRFS_GET_DEVICES`
  - `FSCTL_BTRFS_GET_USAGE`
  - Balance controls: start/query/pause/resume/stop.
  - Device controls: add/remove.
  - Filesystem enumeration/probing/unload controls.
  - Scrub controls: start/query/pause/resume/stop.
  - Stats reset, `mknod`, received subvolume, xattr get/set, reserve/find/send/read-send-buffer, resize, checksum info.
- Compression constants:
  - `BTRFS_COMPRESSION_ANY`
  - `BTRFS_COMPRESSION_ZLIB`
  - `BTRFS_COMPRESSION_LZO`
  - `BTRFS_COMPRESSION_ZSTD`
- User-visible structures:
  - File identity: `btrfs_get_file_ids`.
  - Snapshot/subvolume creation: `btrfs_create_snapshot`, `btrfs_create_snapshot32`, `btrfs_create_subvol`.
  - Inode metadata: `btrfs_inode_info`, `btrfs_set_inode_info`.
  - Device and filesystem enumeration: `btrfs_device`, `btrfs_usage_device`, `btrfs_usage`, `btrfs_filesystem_device`, `btrfs_filesystem`.
  - Balance: `btrfs_balance_opts`, `btrfs_start_balance`, `btrfs_query_balance`.
  - Scrub: `btrfs_scrub_error`, `btrfs_query_scrub`.
  - Unix node creation and receive metadata: `btrfs_mknod`, `btrfs_received_subvol`.
  - Xattrs: `btrfs_set_xattr`.
  - Send/receive: `btrfs_find_subvol`, `btrfs_send_subvol`, `btrfs_send_subvol32`.
  - Resize and checksum export: `btrfs_resize`, `btrfs_csum_info`.

## ABI Notes

- Several structures use trailing one-element arrays (`name[1]`, `devices[1]`, `errors`, `data[1]`) as variable-length payloads.
- 32-bit compatibility structures use `POINTER_32` for handles/pointers passed from WOW64-style callers.
- Uses Windows `BOOL`, `HANDLE`, `WCHAR`, `ULONG`, `USHORT`, `NTSTATUS`, and Btrfs fixed-width integer fields.
- Balance and scrub status constants are bit/status values consumed by management tools and `fsctl.c` handlers.

## Dependencies

- Includes `btrfs.h` for Btrfs UUID and on-disk-compatible types.
- Included by `btrfs_drv.h`, so all driver modules see these definitions.
- Control codes are handled primarily by filesystem/device-control code outside this file.

## Research Notes

- This file is ABI-sensitive. Field order, widths, alignment assumptions, control numbers, and variable-length buffer conventions must remain stable for user-mode tools.
- `btrfs_inode_info` includes per-compression disk usage fields for zlib, LZO, Zstd, sparse size, and extent count, making it a metadata reporting interface rather than just POSIX stat emulation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/btrfsioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/cache.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/cache.c

## Purpose

Initializes Windows cache manager callbacks for the Btrfs driver. These callbacks coordinate lazy writer and read-ahead access with the driver's FCB and tree locking rules.

## Main Contents

- Global:
  - `CACHE_MANAGER_CALLBACKS cache_callbacks`.
- Lazy writer callbacks:
  - `acquire_for_lazy_write`
  - `release_from_lazy_write`
- Read-ahead callbacks:
  - `acquire_for_read_ahead`
  - `release_from_read_ahead`
- Initialization:
  - `init_cache`

## Behavior

`acquire_for_lazy_write`:

- Extracts the `fcb` from `FileObject->FsContext`.
- Acquires `Vcb->tree_lock` shared.
- Acquires the file's `Header.Resource` exclusive.
- Records the current thread in `fcb->lazy_writer_thread`.
- Sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`.

`release_from_lazy_write`:

- Clears `fcb->lazy_writer_thread`.
- Releases the file resource and tree lock.
- Clears top-level IRP if it is still the cache sentinel.

`acquire_for_read_ahead`:

- Acquires the file resource shared.
- Sets top-level IRP to the cache sentinel.

`release_from_read_ahead`:

- Releases the file resource.
- Clears top-level IRP if appropriate.

`init_cache` installs the four function pointers into `cache_callbacks`.

## Dependencies

- Uses `fcb`, `device_extension`, and tracing macros from `btrfs_drv.h`.
- Uses Windows cache manager callback ABI and resource locking primitives.
- `cache_callbacks` is declared extern in `btrfs_drv.h` for use when cache maps are initialized elsewhere.

## Research Notes

- Lazy-write locking follows the global tree-before-FCB ordering documented in `btrfs_drv.h`.
- Read-ahead does not take the tree lock, only the FCB resource shared.
- Top-level IRP handling is defensive: release callbacks clear only the sentinel value they set.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/calcthread.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/calcthread.c

## Purpose

Implements worker-thread execution for CPU-bound Btrfs jobs: sector checksums/hashes and compression/decompression tasks. It supports both background calc threads and synchronous caller-assisted execution.

## Main Functions

- `calc_thread_main(device_extension* Vcb, calc_job* cj)`
- `do_calc_job(device_extension* Vcb, uint8_t* data, uint32_t sectors, void* csum)`
- `add_calc_job_decomp(...)`
- `add_calc_job_comp(...)`
- `calc_thread(void* context)`

## Behavior

`calc_thread_main`:

- Acquires `Vcb->calcthreads.spinlock`.
- Selects either a caller-supplied job or the head of the queued job list.
- For checksum/hash jobs, advances `in` by one sector and `out` by checksum size for each work unit.
- Decrements `not_started`, removes the job from the queue when no units remain, and releases the spinlock.
- Executes the selected work:
  - CRC32C via `calc_crc32c`.
  - XXH64 via `XXH64`.
  - SHA-256 via `calc_sha256`.
  - BLAKE2 via `blake2b`.
  - Zlib/LZO/Zstd decompression via codec functions.
  - Zlib/LZO/Zstd compression via codec functions.
- Decrements `left` atomically and signals the job event when all work units complete.

`do_calc_job`:

- Builds a stack-local `calc_job` for checksum generation across multiple sectors.
- Selects checksum type from `Vcb->superblock.csum_type`.
- Inserts the job into the calc queue.
- Signals calc threads, runs `calc_thread_main` itself to help drain the job, then waits for completion.

`add_calc_job_decomp` and `add_calc_job_comp`:

- Allocate a nonpaged `calc_job`.
- Initialize input/output buffers, lengths, status, event, and type.
- Validate the Btrfs compression type.
- Queue the job and return it to the caller for waiting/freeing.

`calc_thread`:

- References the device object.
- Pins the system thread to `1 << thread->number`.
- Waits on `Vcb->calcthreads.event`, drains queued jobs, and exits when `thread->quit` is set.
- Signals `thread->finished` and terminates.

## Dependencies

- Includes `xxhash.h` and `crc32c.h`.
- Calls compression functions declared in `btrfs_drv.h` and implemented in `compress.c`.
- Calls SHA-256 and BLAKE2 functions declared in `btrfs_drv.h`.
- Uses Windows kernel spinlocks, events, interlocked operations, system threads, and object references.

## Research Notes

- The design lets submitters participate in execution, reducing latency for synchronous checksum/compression work.
- `calc_job` ownership is split: stack-owned for `do_calc_job`, heap-owned for compression/decompression helper APIs.
- The queue counters are protected by spinlock, while completion uses `InterlockedDecrement` plus an event.
- The event is set and immediately cleared when jobs are queued; calc threads wake on the set edge while the job list remains authoritative.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/calcthread.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/compress.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/compress.c

## Purpose

Implements Btrfs compression and decompression support for zlib, LZO, and Zstd, plus the `write_compressed` path that converts file data into compressed Btrfs extents and updates allocation/checksum/extent state.

## Main Components

- Codec setup:
  - zlib included through ReactOS/system or local zlib headers.
  - Zstd included with `ZSTD_STATIC_LINKING_ONLY`.
  - Custom zlib and Zstd allocators backed by kernel pool allocation.
- LZO implementation:
  - `lzo_stream` state.
  - Byte/length/copy/copyback helpers.
  - `do_lzo_decompress`.
  - `lzo_decompress`.
  - LZO 1x-style compressor helpers: `lzo_do_compress`, `lzo1x_1_compress`, `lzo_max_outlen`, `lzo_compress`.
- zlib:
  - `zlib_compress`
  - `zlib_decompress`
- Zstd:
  - `zstd_compress`
  - `zstd_decompress`
- Compressed write path:
  - `comp_part`
  - `write_compressed`

## Codec Behavior

LZO decompression:

- Reads Btrfs LZO page chunks, each prefixed by a 32-bit compressed length.
- Decompresses into 4 KiB pages.
- Zero-fills the remainder of a page if the decompressed output is short.
- Handles Btrfs page-boundary padding before the next page chunk.

zlib compression/decompression:

- Uses zlib stream APIs with kernel-pool custom allocation.
- Compression sets `space_left` to zero when output did not fit, otherwise to remaining output capacity.
- Decompression inflates until stream end or output buffer full.

Zstd compression/decompression:

- Uses advanced stream creation with custom memory callbacks.
- Compression clamps `windowLog` to `ZSTD_BTRFS_MAX_WINDOWLOG` to match Linux Btrfs behavior.
- Reports no space left if input was not fully consumed.

LZO compression:

- Compresses data page-by-page.
- Builds the Btrfs LZO wire format with an overall size header and per-page size headers.
- Copies compressed data to the caller only when it is smaller than the allowed output size.

## `write_compressed` Flow

1. Chooses compression type from mount options, inode property compression, and superblock incompat feature flags.
2. Removes replaced extents with `excise_extents`.
3. Splits the write range into `COMPRESSED_EXTENT_SIZE` parts, normally 128 KiB each.
4. Queues a compression calc job for each part.
5. Helps execute jobs via `calc_thread_main`, waits for completion, and checks job statuses.
6. Marks a part compressed only if at least one filesystem sector is saved; otherwise stores it uncompressed.
7. Sets LZO/Zstd incompat feature flags when those compression formats are actually used.
8. Sector-aligns compressed output and zero-pads the tail.
9. If the first 128 KiB is incompressible and compression was not forced, marks the inode `BTRFS_INODE_NOCOMPRESS`.
10. Concatenates all compressed/uncompressed parts into one write buffer.
11. Finds or allocates a data chunk with enough free space.
12. Reserves logical space with `space_list_subtract`.
13. Writes the data with `write_data_complete`.
14. Calculates checksums unless `BTRFS_INODE_NODATASUM` is set.
15. Adds one `EXTENT_DATA` item per part to the FCB.
16. Copies per-part checksums into extent state.
17. Updates changed extent refs under `changed_extents_lock`.
18. Marks extents and inode dirty.

## Dependencies

- Includes `btrfs_drv.h`.
- Uses `calcthread.c` through `add_calc_job_comp`, `calc_thread_main`, and `do_calc_job`.
- Uses allocation/free-space helpers from write/free-space modules: `find_data_address_in_chunk`, `alloc_chunk`, `space_list_subtract`.
- Uses extent and dirty-state helpers: `add_extent_to_fcb`, `add_changed_extent_ref`, `mark_fcb_dirty`.
- Uses physical/logical write path through `write_data_complete`.

## Research Notes

- This is both codec code and filesystem mutation code; `write_compressed` touches allocation, checksums, extent items, incompat flags, and dirty tracking.
- The compressed-write success criterion is conservative: if compression saves less than one sector, the part is stored uncompressed.
- Zstd feature compatibility is controlled here by setting `BTRFS_INCOMPAT_FLAGS_COMPRESS_ZSTD` once Zstd extents are emitted.
- Notable edge cases to preserve during future work:
  - LZO page framing includes padding logic tied to `LZO_PAGE_SIZE` and `inpageoff`.
  - `write_compressed` assumes rollback-aware free-space and extent updates.
  - Small LZO input handling and LZO input-length calculations are sensitive paths and should be tested if touched.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.S -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.S

## Purpose

Assembly implementations of CRC32C for x86 and x86-64 builds. Provides both software table-driven CRC32C and hardware-accelerated CRC32C using the CPU `crc32` instruction.

## Main Contents

- Includes `asm.inc`.
- x86-64 section under `__x86_64__`:
  - Extern `crctable`.
  - Exports `calc_crc32c_sw`.
  - Exports `calc_crc32c_hw`.
- x86 section under `_X86_`:
  - Extern `_crctable`.
  - Exports `_calc_crc32c_sw@12`.
  - Exports `_calc_crc32c_hw@12`.

## Behavior

Software implementation:

- Starts with caller-provided seed.
- For each byte:
  - Shifts current CRC right by 8.
  - XORs low CRC byte with input byte.
  - Uses the result as an index into `crctable`.
  - XORs table value with shifted CRC.
- Returns the updated CRC.

Hardware implementation:

- Starts with caller-provided seed.
- Processes the buffer in the widest supported chunks:
  - x86-64: 8-byte chunks, then 4-byte, 2-byte, and 1-byte stragglers.
  - x86: 4-byte chunks, then 2-byte and 1-byte stragglers.
- Uses the SSE4.2 `crc32` instruction.
- Returns the updated CRC.

## Dependencies

- The CRC table is defined in `crc32c.c`.
- Function declarations are in `crc32c.h`.
- The active function pointer `calc_crc32c` is defined in `crc32c.c` and consumed by checksum code such as `calcthread.c`.

## Research Notes

- This file supplies x86/x64 implementations only. Non-x86 architectures use the C fallback in `crc32c.c`.
- Hardware acceleration is implemented here but selection of `calc_crc32c_hw` is not performed in this file.
- Calling conventions are explicitly handled: Windows x64 register convention and x86 stdcall decorated exports.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.S -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.c

## Purpose

Defines CRC32C shared state for the Btrfs driver: the exported function pointer, the 256-entry CRC32C table, and the portable C software fallback for non-x86 architectures.

## Main Contents

- Includes:
  - `crc32c.h`
  - `<stdint.h>`
  - `<stdbool.h>`
  - `<sal.h>`
- Global function pointer:
  - `crc_func calc_crc32c = calc_crc32c_sw;`
- Constant table:
  - `const uint32_t crctable[]` with 256 CRC32C values.
- Portable fallback:
  - `calc_crc32c_sw` is compiled only when neither `_X86_` nor `_AMD64_` is defined.

## Behavior

The C fallback:

- Initializes remainder from the seed.
- Iterates every byte in the input buffer.
- Updates the remainder using `crctable[(rem ^ msg[i]) & 0xff] ^ (rem >> 8)`.
- Returns the unfinalized CRC remainder.

Callers perform Btrfs-specific finalization/inversion where needed; for example `calcthread.c` stores `~calc_crc32c(0xffffffff, sector, sector_size)`.

## Dependencies

- `crc32c.S` provides x86/x64 implementations for `calc_crc32c_sw` and `calc_crc32c_hw`.
- `crc32c.h` exposes the function pointer and declarations.
- Consumers use `calc_crc32c` instead of calling a specific implementation directly.

## Research Notes

- Default implementation is software CRC32C. Hardware selection, if enabled, must occur elsewhere by assigning `calc_crc32c = calc_crc32c_hw`.
- The table is shared by the C fallback and assembly software implementation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.h

## Purpose

Public internal header for CRC32C checksum routines used by the Btrfs driver.

## Main Contents

- Includes `<stdint.h>`.
- Provides C++ linkage guards with `extern "C"`.
- Declares `calc_crc32c_hw` on x86/x64 builds.
- Declares `calc_crc32c_sw`.
- Defines:
  - `typedef uint32_t (__stdcall *crc_func)(uint32_t seed, uint8_t* msg, uint32_t msglen);`
- Declares:
  - `extern crc_func calc_crc32c;`

## Dependencies

- Implemented by `crc32c.c` and `crc32c.S`.
- Included by `calcthread.c` for checksum job execution.

## Research Notes

- Consumers call through `calc_crc32c`, allowing runtime or initialization-time selection between software and hardware implementations.
- Hardware implementation is intentionally architecture-gated.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.h -->