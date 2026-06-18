# Group Research: group_1862_xfsdump_sources_local_fs_xfsdump_common_drive_scsitape_c_sources_lo_6c651da61335

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/drive_scsitape.c -->
# File Research: sources/local-fs/xfsdump/common/drive_scsitape.c

## Summary
Implements the `drive_strategy_scsitape` backend for SCSI tape, remote tape, TS/TMF tape drivers, and QIC-style fixed-block devices. It adapts xfsdump/xfsrestore’s generic `drive_ops_t` interface to Linux tape ioctls, remote tape protocol calls, record framing, media-file labels, file marks, and tape positioning.

## Main Responsibilities
- Matches tape devices by remote path syntax or character-device major number.
- Opens, prepares, sizes, reads, writes, rewinds, spaces, erases, and optionally unloads tape media.
- Encodes each tape media file as fixed-size tape records with an xfsdump global header in the first record and `rec_hdr_t` metadata in every record.
- Negotiates fixed or variable block size, command-line block size, QIC constraints, and Linux/TS driver quirks.
- Implements media marks as byte offsets into the framed tape stream and supports forward mark search/resynchronization.
- Converts global/media/content/record headers through `arch_xlate` so media format remains endian-aware.
- Tracks uncertainty after end-of-media write errors and commits or discards queued marks accordingly.

## Core State
`drive_context_t` stores operational mode, ring/buffer ownership, current record pointers, record and I/O counters, tape fd, remote/variable/QIC/capability flags, selected block and record size, lost-record margin, checksum mode, unload/overwrite flags, and requested media file size.

The file currently forces `dc_singlethreadedpr = BOOL_TRUE`, but retains full ring-buffer support through `ring_read()`, `ring_write()`, and `Ring_*()` wrappers.

## Important Behavior
`ds_match()` rejects `stdio`, gives remote `host:path` devices a high match only if `MTIOCGET` succeeds, and detects local tape devices by comparing character major numbers for `st`, `ts`, and `tmf`.

`do_begin_read()` allocates or acquires a record buffer, calls `prepare_drive()` on first open, reads and validates the media label, initializes read offsets, and enters `OM_READ`.

`prepare_drive()` is the central tape probing path. It retries open/status while the drive becomes ready, rejects write-protected media during dump, detects variable block mode, queries tape capabilities, handles `--overwrite`, chooses initial record/block sizes, disambiguates file-mark position, and loops through read/status outcomes to classify blank, foreign, corrupt, EOD, EOM, wrong block size, and valid xfsdump media.

`validate_media_file_hdr()` verifies the global header checksum, optional tape record checksum, xfsdump magic/version, drive strategy id, SCSI tape magic/version, and then converts the first record into native header structures.

`do_read()`, `do_return_read_buf()`, `getrec()`, and `read_record()` expose only payload bytes after `STAPE_HDR_SZ`, while maintaining record counters and detecting EOF/EOD/EOM/corruption from read size plus tape status.

`do_seek_mark()` treats marks as raw media-file offsets and advances only forward, using buffered reads, optional `MTFSR`, and dummy reads to reach a requested mark.

`do_next_mark()` finds the next record-level mark or, after corruption/read error, tries to resynchronize by reading records, validating headers, optionally hunting QIC 512-byte block boundaries, and forward-spacing past bad tape blocks.

`do_begin_write()` writes the media-file header record, initializes the next data record header, and enters write mode. `do_write()` writes full records, prepares the next record header, and commits marks only after subtracting `dc_lostrecmax`. `do_end_write()` writes the padded final record if needed, flushes pending ring writes, writes a tape file mark, computes committed bytes, commits/discards marks, and exits write mode.

Tape movement helpers (`do_fsf()`, `do_bsf()`, `rewind_and_verify()`, `fsf_and_verify()`, `bsf_and_verify()`) wrap Linux tape ioctls and include driver-specific status workarounds. `map_ts_status()` maps TS/SGI tape status bits into Linux `mtget.mt_gstat` style bits.

## Dependencies
Depends on xfsdump drive/media/global/content headers, `ring`, `rec_hdr`, `arch_xlate`, `ts_mtio`, logging/dialog/control helpers, remote tape functions, Linux tape ioctls, `/proc/devices`, and UUID APIs.

## Risks
Tape status semantics are highly driver-specific; much of the correctness depends on Linux ST versus TS behavior, especially EOF/EOD/EOT and file-mark positioning.

The block-size detection loop is heuristic and can classify media as blank, foreign, corrupt, or wrong-sized based on subtle combinations of `read()` length, `errno`, and tape status.

Remote tape lacks capability and block-size ioctls, so the code falls back to conservative assumptions.

Record checksum use is optional and only checked when the on-media header says a checksum is present and checksum mode is enabled.

`do_quit()` unloads when requested but does not visibly close/free all context resources in the same way `drive_simple` does; lifecycle appears owned by broader drive shutdown assumptions.

The file contains old TS/APD and Linux ST workaround logic that is hard to validate without real tape hardware.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/drive_scsitape.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/drive_simple.c -->
# File Research: sources/local-fs/xfsdump/common/drive_simple.c

## Summary
Implements `drive_strategy_simple`, the backend for dump/restore streams stored in ordinary files, stdio, FIFOs, raw/block devices, and remote ordinary files through the rmt protocol. It supports exactly one media file and uses a simple page-aligned memory buffer instead of tape record framing.

## Main Responsibilities
- Matches fallback non-directory paths, `stdio`, and weakly matches remote `host:path` names.
- Opens stdio, local files/devices/FIFOs, or remote files with dump/restore-appropriate flags.
- Reads and writes the xfsdump global/media/content header.
- Buffers stream I/O in a 64-page page-aligned buffer.
- Maintains simple byte-offset marks for restore positioning.
- Supports rewind and erase when the backing object is seekable/truncatable.

## Important Behavior
`ds_instantiate()` allocates a page-aligned `drive_context_t`, records whether the path is remote, opens the path, and sets capabilities based on build mode and file type. Regular files can read, rewind, and erase; FIFOs generally cannot rewind; stdio maps to fd 1 for dump and fd 0 for restore.

`do_begin_read()` allows only one media file, initializes the read buffer, reads `GLOBAL_HDR_SZ` through the drive read callbacks, verifies the global checksum, translates headers, checks magic/version/strategy id, stores the first mark from `dh_specific`, and enables `DRIVE_CAP_NEXTMARK` if that mark exists.

`do_read()` refills the buffer with `read()` when empty and returns slices to the caller. Zero bytes from the backing fd maps to `DRIVE_ERROR_EOD`.

`do_seek_mark()` only seeks forward by consuming bytes through `read_buf()`. `do_next_mark()` only knows the first mark recorded in the media header.

`do_begin_write()` truncates readable destinations, initializes write buffering, writes a translated/checksummed global header through `write_buf()`, and records no first mark initially.

`do_set_mark()` records each mark offset. For the first mark, it either patches the still-buffered header or, for random-access outputs, seeks back to rewrite the on-media header and checksum. If the mark is already committed it calls the callback immediately; otherwise it queues the mark.

`do_write()` accepts ownership of a buffer slice and flushes the full buffer when filled, committing marks up to the flushed offset. `do_end_write()` flushes remaining bytes, rounds raw device output to `BBSIZE`, commits marks, bumps the single file-mark count, and reports committed bytes.

`do_rewind()` seeks to offset zero. `do_erase()` seeks to zero and truncates to zero length.

## Dependencies
Depends on xfsdump drive/global/media/content structures, `util` buffered I/O helpers, `arch_xlate`, rmt operations, logging, and build-time `DUMP`/`RESTORE` modes.

## Risks
The strategy intentionally supports only one media file; after one successful read or write, later begin operations return EOM.

First-mark persistence depends on either the mark being set before the initial buffer flush or the destination being randomly seekable.

Short writes on full-buffer flush map to EOM after committing only the bytes written; callers rely on mark commit/discard behavior to stay consistent.

The rmt macro remapping makes ordinary file access go through remote-tape wrappers, which can hide normal POSIX behavior behind rmt semantics.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/drive_simple.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/exit.h -->
# File Research: sources/local-fs/xfsdump/common/exit.h

## Summary
Defines process exit codes and a small string conversion helper for xfsdump/xfsrestore main and child processes.

## Main Contents
- `EXIT_NORMAL` = `0`, for successful completion or “do not exit”.
- `EXIT_ERROR` = `1`, for resource errors or exhaustion.
- `EXIT_INTERRUPT` = `2`, for operator or device interruptions.
- `EXIT_FAULT` = `4`, for internal code faults.
- `exit_codestring()` maps those constants to stable labels.

## Risks
The constants are public process status semantics. Scripts and supervisor code may depend on these exact values.

`EXIT_NORMAL` is documented as both normal completion and “don’t exit”, so callers must preserve contextual meaning.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/exit.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/fs.c -->
# File Research: sources/local-fs/xfsdump/common/fs.c

## Summary
Provides filesystem discovery helpers for xfsdump. It resolves a user-supplied source string into filesystem type, block device, mount point, and XFS UUID by reading the mounted-filesystem table and querying XFS geometry.

## Main Responsibilities
- Build an in-memory list from `setmntent(MOUNTED, "r")`.
- Resolve block-device paths directly or by matching `st_rdev`.
- Resolve mount-point paths by exact mount-table match.
- Fill output buffers for fs type, block device, mount point, and UUID.
- Query XFS UUID with `XFS_IOC_FSGEOMETRY_V1`.
- Estimate in-use inode count via `statvfs()`.

## Important Behavior
`fs_info()` first checks whether the user string is a block device. If so, it looks up the corresponding mount-table entry by block path or device number. Otherwise it treats the string as a mount point and looks that up directly.

If the mount-table entry lacks a type, `fs_info()` falls back to the caller-provided default type. On success it calls `fs_getid()` for the mount point and logs the UUID.

`fs_mounted()` is intentionally shallow: it returns true if the mount-point string is non-empty.

`fs_getid()` opens the mount point and issues `XFS_IOC_FSGEOMETRY_V1`; failures clear the UUID and return `-1`.

`fs_getinocnt()` returns `f_files - f_ffree` when `statvfs()` succeeds and the values are sane.

## Dependencies
Depends on mount table APIs, `stat64`, `statvfs`, Linux/XFS ioctl definitions, UUID APIs, and xfsdump logging/types.

## Risks
Mount-point lookup is exact-string only; it does not canonicalize paths or handle bind mounts beyond what appears in the mount table.

`fs_mounted()` does not verify live mount state or UUID/type consistency.

Output copying relies on `assert(strlen(...) < bufsz)` rather than runtime bounds handling, so production builds without assertions may not guard against unexpectedly long mount-table fields.

`fs_getid()` is XFS-specific; non-XFS sources will fail UUID lookup even if mount-table resolution succeeds.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/fs.h -->
# File Research: sources/local-fs/xfsdump/common/fs.h

## Summary
Declares filesystem utility interfaces used to identify dump sources and query basic XFS filesystem properties.

## Main Contents
- Default name/path limits: `FS_MAXNAMELEN_DEFAULT` and `FS_MAXPATHLEN_DEFAULT`.
- `fs_info()` for resolving source name to type, device, mount point, and UUID.
- `fs_mounted()` for checking mounted status.
- `fs_getid()` for retrieving filesystem UUID.
- `fs_getinocnt()` for counting in-use inodes.

## Risks
The header describes generic filesystem utilities, but the implementation’s UUID lookup is XFS ioctl based.

Callers must provide correctly sized writable buffers for `fs_info()` outputs.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/getdents.c -->
# File Research: sources/local-fs/xfsdump/common/getdents.c

## Summary
Wraps the Linux `getdents64` syscall behind a `struct dirent`-oriented interface, based on glibc getdents conversion logic.

## Main Responsibilities
- Define a local `kernel_dirent64` layout matching the Linux syscall record format.
- Optionally allocate a slightly larger temporary buffer if kernel and libc `d_name` offsets differ.
- Call `syscall(SYS_getdents64, ...)`.
- Convert kernel records into libc `struct dirent` records when layouts differ.
- Detect inode/offset overflow and return already converted entries when possible.

## Important Behavior
The conversion logic computes the kernel/libc header-size difference, adjusts record lengths to libc alignment, copies inode/offset/type/name fields, and uses `lseek64()` to roll back to the last safe offset if an overflow occurs after at least one entry.

## Dependencies
Depends on Linux syscall numbers, `dirent`, `alloca`, `offsetof`, `lseek64`, and libc/kernel dirent layout assumptions.

## Risks
The implementation returns immediately when `retval != -1`, which is the successful syscall path. That makes the subsequent conversion loop unreachable on successful reads. If libc `struct dirent` differs from the kernel layout on a target platform, callers may receive unconverted kernel records.

The loop condition after the early return also depends on `retval` being a positive byte count; as written, the only fallthrough path is syscall failure, where `retval == -1`.

The fixed `d_name[256]` in the local kernel struct is a layout stand-in, not a flexible array, so correctness depends on offset and reclen use rather than the declared array capacity.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/getdents.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/getdents.h -->
# File Research: sources/local-fs/xfsdump/common/getdents.h

## Summary
Declares `getdents_wrap()`, the local wrapper for reading directory entries through Linux `getdents64`.

## Interface
`int getdents_wrap(int fd, char *buf, size_t nbytes);`

The caller supplies a directory fd, output buffer, and byte capacity. Return semantics follow getdents-style conventions: positive byte count, zero at end, or `-1` with `errno`.

## Risks
The header exposes only a raw byte-buffer API, so callers must know the expected record layout and iterate entries correctly.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/getdents.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/global.c -->
# File Research: sources/local-fs/xfsdump/common/global.c

## Summary
Builds, frees, checksums, and validates version numbers for the xfsdump global media-file header. During dump builds it creates the dump session identity; during restore builds it can parse a requested session UUID.

## Main Responsibilities
- Allocate and initialize `global_hdr_t`.
- Fill global magic, version, timestamp, host id, dump UUID, hostname, and dump label.
- Parse relevant command-line options for dump label, dump time, format compatibility, and restore session id.
- Optionally prompt interactively for a dump label.
- Compute and verify the 32-bit additive-inverse header checksum.
- Accept known global header versions.

## Important Behavior
`global_hdr_alloc()` sets `GLOBAL_HDR_VERSION` by default. Dump builds generate a new UUID; restore builds clear it unless `GETOPT_SESSIONID` provides one.

`GETOPT_DUMPTIME` uses a specified file’s `st_mtime` as the dump timestamp. `GETOPT_FMT2COMPAT` downgrades the global header version to version 2 for compatibility.

If no dump label is supplied and dialogs are allowed, `prompt_label()` displays an interactive dialog with a timeout. If still empty, the label is stored as an empty string.

`global_hdr_checksum_set()` zeroes `gh_checksum`, sums the full header as converted 32-bit words, and writes the two’s-complement additive inverse. `global_hdr_checksum_check()` succeeds when the converted 32-bit sum of the whole header is zero.

`global_version_check()` accepts versions 0 through 3.

## Dependencies
Depends on command-line option definitions, logging/dialog helpers, UUID APIs, hostname/hostid/time/stat calls, `strncpyterm`, and `ARCH_CONVERT` integer helpers.

## Risks
`global_hdr_alloc()` returns `NULL` on several validation errors after allocating `ghdrp`, without freeing that allocation.

The checksum is over the entire fixed-size global header and assumes 32-bit word alignment and stable serialized conversion behavior.

Dump label and restore session parsing reuse global `getopt` state by resetting `optind`; this requires callers to tolerate repeated option scans.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/global.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/global.h -->
# File Research: sources/local-fs/xfsdump/common/global.h

## Summary
Defines the fixed first-page global media-file header and declares helpers for allocation, checksum, and version validation.

## Main Contents
`global_hdr_t` is exactly one page (`GLOBAL_HDR_SZ = PGSZ`) and begins every media file. It contains:
- xfsdump magic `xFSdump0`.
- Header version, currently `GLOBAL_HDR_VERSION_3`.
- Header checksum.
- Dump timestamp.
- Host id.
- Dump session UUID.
- Hostname.
- Dump label.
- `gh_upper`, reserved for upper-layer headers.

Version notes:
- Version 1 adds extended file attribute dumping.
- Version 2 adds hole encoding and inventory format changes.
- Version 3 uses the full 32-bit inode generation number in directory entry headers.

## Exposed APIs
- `global_hdr_alloc()`.
- `global_hdr_free()`.
- `global_hdr_checksum_set()`.
- `global_hdr_checksum_check()`.
- `global_version_check()`.

## Risks
The layout is on-media format. Field sizes, offsets, and `GLOBAL_HDR_SZ` are compatibility-sensitive and are assumed by drive backends.

`gh_upper` embeds higher-layer headers by convention, so users must preserve layering and size assumptions.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/global.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/hsmapi.c -->
# File Research: sources/local-fs/xfsdump/common/hsmapi.c

## Summary
Implements xfsdump/xfsrestore support for SGI DMF/HSM metadata. It detects DMF-managed XFS files, treats dual-state/offline/partial files as offline for dump purposes, rewrites DMF attributes to a safe offline form, and protects files during restore with temporary `NOMIGR` attributes.

## Main Responsibilities
- Manage opaque filesystem and per-file HSM contexts.
- Interpret DMF root extended attribute `SGI_DMI_DMFATTR`.
- Read DMF attributes via `jdm_attr_multi()` using XFS/JDM file handles.
- Estimate dump size/offset for files whose online bytes should be represented as holes.
- Modify `xfs_bstat` and `getbmapx` data to make selected HSM files appear offline.
- Filter original DMF attributes and add replacement offline attributes to the dump stream.
- Add/remove temporary restore-time DMF attributes to prevent migration interference.

## Important Behavior
`HsmInitFsysContext()` supports only `HSM_API_VERSION_1`, allocates a DMF filesystem context, and stores a JDM filesystem handle for the mount point.

`HsmInitFileContext()` quickly rejects non-regular files, files without XFS attrs, and files without interesting DMAPI event bits. For candidates, it fetches `SGI_DMI_DMFATTR`, validates filesystem type, validates format 0 or format 1 length, reads the DMF state in big-endian form, and marks files in dualstate, unmigrating, partial, or offline states as dump candidates.

`HsmEstimateFileSpace()` returns zero bytes for candidate files when dumping dual-residency data as holes. It can use an existing file context, build a temporary accurate context, or use a cheaper bstat/event-bit heuristic.

`HsmEstimateFileOffset()` maps any requested byte quantity for a candidate file to EOF, because physical data is treated as absent.

`HsmModifyInode()` sets `bs_dmevmask` to the DMF event mask for candidate files. `HsmModifyExtentMap()` turns the remaining file range into one hole extent or indicates EOF.

`HsmFilterExistingAttribute()` skips the original DMF root attribute for candidate files so it can be replaced.

`HsmAddNewAttribute()` emits one replacement `SGI_DMI_DMFATTR`. It preserves format 1 only when a nonzero site tag requires it, otherwise writes format 0, and sets global state to offline. Format 1 output is reduced to one offline region spanning the whole file.

Restore helpers:
- `HsmBeginRestoreFile()` sets a temporary root DMF `NOMIGR` attr if the restored bstat appears DMF-managed.
- `HsmRestoreAttribute()` clears the temporary-removal flag when a real DMF attr is restored.
- `HsmEndRestoreFile()` removes the temporary attr if no real DMF attr replaced it.

## Dependencies
Depends on XFS bstat/getbmapx structures, XFS/JDM handles and attribute APIs, Linux attr APIs, UUID headers, and DMF attribute format knowledge copied into this file to avoid a DMAPI dependency.

## Risks
DMF attributes are parsed with fixed local structures and big-endian field helpers; incompatible future DMF formats are silently ignored.

`dmf_f_ctxt_t.attrval` is a fixed 5000-byte buffer assumed to exceed any possible DMF attribute value.

`HsmDeleteFsysContext()` frees only the context pointer; the JDM filesystem handle lifetime is not explicitly released in this file.

The cheap estimator assumes there are no MIG files and may under-estimate non-directory dump size when that assumption fails.

`HsmModifyInode()` returns success even for non-candidates, but only modifies candidates.

Restore protection is intentionally crude and state is carried by one integer flag, so correctness depends on the caller invoking begin/attribute/end hooks in order.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/hsmapi.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/hsmapi.h -->
# File Research: sources/local-fs/xfsdump/common/hsmapi.h

## Summary
Declares the opaque HSM API used by xfsdump and xfsrestore to integrate with DMF-managed XFS files.

## Main Contents
- `HSM_API_VERSION_1`, the only supported API version.
- Opaque `hsm_fs_ctxt_t` and `hsm_f_ctxt_t` typedefs.
- Filesystem context lifecycle: `HsmInitFsysContext()`, `HsmDeleteFsysContext()`.
- File context lifecycle: `HsmAllocateFileContext()`, `HsmDeleteFileContext()`, `HsmInitFileContext()`.
- Dump-side estimators/modifiers: `HsmEstimateFileSpace()`, `HsmEstimateFileOffset()`, `HsmModifyInode()`, `HsmModifyExtentMap()`.
- Attribute filtering/addition hooks: `HsmFilterExistingAttribute()`, `HsmAddNewAttribute()`.
- Restore hooks: `HsmBeginRestoreFile()`, `HsmRestoreAttribute()`, `HsmEndRestoreFile()`.

## Intended Contract
Dump code can initialize one read-only filesystem context per mounted filesystem and one read-write file context per dump stream. Restore code does not need those contexts and uses only the restore hook trio.

The API lets xfsdump represent dual-residency HSM files as offline files with replacement HSM metadata, avoiding forced staging of file data during dump.

## Risks
The `HsmInitFileContext()` return-value comment in this header contradicts both `hsmapi.c` and callers: the implementation uses `0` for successful initialization and nonzero for “do not dump”.

The header intentionally hides context internals, so all callers must respect lifecycle and avoid stack assumptions except where implementation explicitly uses temporary internal contexts.

The API is versioned but only version 1 is supported.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/hsmapi.h -->