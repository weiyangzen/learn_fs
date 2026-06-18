# Group Research: group_1700_reactos_sources_windows_reactos_drivers_filesystems_udfs_Include_ph_517115795342

Scope checked against `Docs/research_subset_a.md`: these files are under `sources/windows/reactos`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.cpp

## Purpose
Implements UDFS physical-device I/O for optical and disk media: low-level reads/writes, write preparation, retry/error recovery, track-map discovery, block-size detection, device-driver reset, speed control, caching mode setup, and unaligned data access.

## Main Responsibilities
- `UDFTRead` and `UDFTWrite` issue synchronous physical reads/writes through `UDFPhReadSynchronous` / `UDFPhWriteVerifySynchronous`, with optional relocation-map handling under `_BROWSE_UDF_`.
- `UDFPrepareForWriteOperation` configures optical write parameters, packet mode, random-access mode, OPC, MRW mode, and background-format continuation before writes.
- `UDFRecoverFromError` interprets low-level CDRW/SCSI sense data and decides whether to retry, sync cache, reset/reinitialize the lower driver, delay for in-progress operations, mark bad blocks, or fail.
- `UDFReadDiscTrackInfo`, `UDFReadAndProcessFullToc`, and `UDFUseStandard` populate `VCB` media layout fields from CDRW-specific IOCTLs, full TOC, or standard CDROM TOC fallback.
- `UDFGetBlockSize` and `UDFGetDiskInfo` establish block size, last LBA, media class, writable/read-only flags, compatibility flags, cache sizing, track map, and speed/caching policy.
- `UDFReadData`, `UDFWriteData`, `UDFReadInSector`, and `UDFWriteInSector` bridge byte-range requests to sector-aligned physical I/O and write-cache access.

## Important Data/State
The file mutates many `PVCB` fields defined in `udf_common.h`: block size, track map, media class, `LastLBA`, `LastPossibleLBA`, `NWA`, `VCBFlags`, `CompatFlags`, `BSBM_Bitmap`, write cache, speed buffers, OPC state, MRW state, and last-error buffers.

## Build Modes
Behavior is heavily conditional:
- `_BROWSE_UDF_` enables relocation, bad-block sparing, verify-cache recovery, write cache, raw UDF browsing, unaligned read/write helpers, and fixed-packet/MRW addressing workarounds.
- `UDF_FORMAT_MEDIA` adds formatter-specific media probing, output, and `fms` policy handling.
- `UDF_READ_ONLY_BUILD` disables physical write paths.
- `UDF_ASYNC_IO` contains an unused async read path.

## Notable Risks
- The code uses extensive stateful device heuristics and retry loops around optical media behavior; regressions can affect mounting, formatting, or data integrity.
- Several pointer increments cast `Buffer` through `uint32*`, reflecting old 32-bit assumptions.
- Many IOCTL buffers are reused through type punning.
- Error recovery can mark bad blocks and alter free/zero bitmaps, so call context and lock ownership matter.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.h

## Purpose
Public declarations and flags for the physical I/O layer implemented in `phys_lib.cpp`.

## Main Contents
- Declares low-level APIs: `UDFTRead`, `UDFTWrite`, verify wrappers, disk-info discovery, block-size detection, read/write preparation, NWA updates, and driver reset.
- Defines physical I/O flags such as `PH_TMP_BUFFER`, `PH_VCB_IN_RETLEN`, `PH_LOCK_CACHE`, `PH_EX_WRITE`, and `PH_IO_LOCKED`.
- Defines `UDFReadSectors` as a macro that prefers `WCacheReadBlocks__` when the fast cache is initialized and IRQL allows it, otherwise falls back to `UDFTRead`.
- Exposes unaligned read/write helpers and write-sector helpers, with write declarations gated by `UDF_READ_ONLY_BUILD`.

## Dependencies
Requires UDFS core types such as `PVCB`, `PDEVICE_OBJECT`, `OSSTATUS`, `PSIZE_T`, and write-cache functions/macros from the surrounding include set.

## Notes
This header is not standalone; it is meant to be included after the UDFS environment and common type headers are available.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/phys_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/platform.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/platform.h

## Purpose
Defines simple fixed-width integer aliases for the UDFS codebase.

## Main Contents
- Signed aliases: `int8`, `int16`, `int32`, `int64`.
- Unsigned aliases: `uint8`, `uint16`, `uint32`, `uint64`.
- Defines `lba_t` as `uint32`.

## Notes
The typedefs assume Windows-style C/C++ type sizes, especially `long == 32-bit`. `lba_t` is 32-bit, so callers needing larger block addresses must use other types.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/platform.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.cpp

## Purpose
Provides registry helper routines usable in both kernel and Win32 builds.

## Main Responsibilities
- `RegTGetKeyHandle` opens a registry key using `ZwOpenKey` in kernel mode or `RegOpenKeyExW` in Win32 mode.
- `RegTCloseKeyHandle` closes the corresponding handle with `ZwClose` or `RegCloseKey`.
- `RegTGetDwordValue` reads a DWORD value from a root/path/name tuple.
- `RegTGetStringValue` reads a Unicode string value, zeroes the destination first, and attempts null termination.

## Build Modes
- Non-`WIN_32_MODE` uses NT native registry APIs, `OBJECT_ATTRIBUTES`, `UNICODE_STRING`, and pool allocation for `KEY_VALUE_PARTIAL_INFORMATION`.
- `WIN_32_MODE` defaults null roots to `HKEY_LOCAL_MACHINE` and uses Win32 registry APIs.

## Notable Risks
- Win32 string termination checks `pStr[len-1]` even though `len` is byte count from `RegQueryValueExW`, which is easy to misuse for WCHAR indexing.
- Kernel string copy clamps byte count to `MaxLen`, so callers must pass byte capacity, not character capacity.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.h

## Purpose
Declares the multi-environment registry helper API.

## Main Contents
- Includes `check_env.h`.
- Maps `HKEY` to `HANDLE` outside `WIN_32_MODE`.
- Declares `RegTGetKeyHandle`, `RegTCloseKeyHandle`, `RegTGetDwordValue`, and `RegTGetStringValue`.

## Notes
This header abstracts registry access enough for shared UDFS kernel/user support code, but still exposes Windows-specific types and calling conventions.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/string_lib.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/string_lib.cpp

## Purpose
Supplies small RTL/string compatibility functions for non-native or user-mode builds.

## Main Responsibilities
- `MyRtlCompareMemory` returns the count of equal bytes from two buffers.
- Non-`NT_NATIVE_MODE` provides `RtlCompareUnicodeString`, `RtlUpcaseUnicodeString`, and `RtlAppendUnicodeToString`.
- `CDRW_W32` provides `MyInitUnicodeString` to allocate and initialize a `UNICODE_STRING`.

## Implementation Notes
- Uses x86 inline assembly for some wide-string length scans when `_X86_` is set, otherwise C loops.
- `RtlAppendUnicodeToString` can grow the destination buffer with `ExAllocatePoolWithTag` and frees the old buffer with `ExFreePool`.
- Case-insensitive comparison is not actually implemented in `RtlCompareUnicodeString`; `UpCase` is ignored.

## Notable Risks
This is compatibility glue, not a complete RTL implementation. Callers expecting exact NT semantics may get simplified behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/string_lib.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.cpp

## Purpose
Implements x86 assembly helpers declared by `tools.h`.

## Main Contents
Under `_X86_`, defines naked `__fastcall` routines for:
- Moving 32-bit and 16-bit values with byte swapping.
- Reversing 32-bit and 16-bit values in place.
- Moving swapped 16-bit values into 32-bit storage.
- Copying MSF byte triplets with and without swapping.
- Exchanging DWORD values.

## Notes
For non-x86 builds, the equivalent behavior is macro-defined in `tools.h`; this `.cpp` contributes only the x86 optimized implementations.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.h

## Purpose
Provides byte-order, MSF/LBA, packet-addressing, min/max, and simple lock helper macros used across UDFS.

## Main Contents
- Defines `FOUR_BYTE`.
- Provides `AcquireXLock`, either x86 `xchg` based or simple assignment fallback.
- Declares x86 helper routines and maps macros such as `MOV_DD_SWP`, `MOV_DW_SWP`, `REVERSE_DD`, `REVERSE_DW`, `MOV_MSF`, `MOV_MSF_SWP`, and `XCHG_DD`.
- Provides generic C macro implementations when the x86 helper path is unavailable.
- Defines `MSF_TO_LBA`, `PacketFixed2Variable`, `PacketVariable2Fixed`, `WAIT_FOR_XXX_EMU_DELAY`, `max`, `min`, and a fallback `offsetof`.

## Notable Risks
- `AcquireXLock` is only atomic in the x86/CrossNT helper path; the generic fallback is not atomic.
- `CONV_TO_LL` appears suspicious because `Byte3` is shifted by 8 rather than 24.
- Generic macros evaluate arguments through address-taking and local pointer casts, so callers should avoid expressions with side effects.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/tools.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_common.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_common.h

## Purpose
Defines common UDFS media classes, the central `VCB` volume-control block, global driver data, and major VCB/global flags.

## Main Contents
- `UDFFSD_MEDIA_TYPE` classifies media such as HDD, CDR, CDRW, CDROM, ZIP, floppy, DVDR, and DVDRW.
- `VCB` combines kernel FCB-compatible fields, mounted-volume state, physical media geometry, track/write-cache state, UDF logical-volume metadata, bitmaps, sparing/VAT information, registry/config-derived policy, and compatibility flags.
- `UDFData` stores global driver objects, recognizer/device objects, zones/lookaside-like storage, delayed-close queues, global strings, cache defaults, and flags.
- Defines `UDF_VCB_FLAGS_*` for mount/read-only/raw/device/cache/eject/dead state.
- Defines `UDF_VCB_IC_*` compatibility and policy flags for timestamps, write behavior, sync-cache quirks, bad seek/MRW/FP addressing workarounds, dirty/read-only handling, and blank-CD display.

## Build Modes
Large portions of `VCB` and `UDFData` exist only with `_UDF_STRUCTURES_H_`; `_BROWSE_UDF_` adds logical UDF metadata, allocation maps, sparing, VAT, and verifier state. Formatter/user builds use reduced structures.

## Architectural Role
This header is the shared state contract for files like `phys_lib.cpp`; most physical I/O decisions mutate fields declared here.

## Notable Risks
Because `VCB` is broad and conditional, structure layout depends strongly on compile-time defines. Code sharing between kernel, formatter, and browse builds must use matching defines.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_common.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_lib_common.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_lib_common.h

## Purpose
Defines a small user/library status and callback interface for UDF library operations.

## Main Contents
- Includes `udferr_usr.h` unless `WITHOUT_FORMATTER` is set.
- Defines `UDF_STATUS` as `LONG` and `UDF_SUCCESS(x)` as non-negative status.
- Defines callback signatures for read, write, ioctl, reopen, get-size, and flush operations.

## Architectural Role
This is a thin abstraction layer for user-mode formatter/library code to operate over a caller-provided device/image backend.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_lib_common.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_reg.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_reg.h

## Purpose
Centralizes UDFS service names, registry paths, object names, filesystem titles, defaults, tunable registry value names, and companion executable names.

## Main Contents
- Defines service names such as `DwUdf`, `DwCdrw`, and `DwUdfMgr`.
- Defines service/parameter registry paths and CDROM class filter location.
- Defines NT object names for UDF filesystem devices, recognizers, DOS device link, and CDFS/UDFS recognizer names.
- Defines media-specific filesystem title strings, with `PRETEND_NTFS` overriding titles to `NTFS`.
- Defines defaults such as volume label, blank media label, max shell label length, and per-media default registry subkeys.
- Defines many registry tunables: allocation mode, UID/GID, packing thresholds, flush periods, delayed update/eject periods, FSP threads, readahead, sparse threshold, verify-on-write, timestamp/attribute update policies, read-only handling, compatibility flags, cache behavior, forced mount, autoformat, and mount filters.
- Defines formatter/register executable names.

## Notes
Some names preserve historical misspellings such as `ReadAheadGranlarity`, `IgnoreSequantialIo`, and `PartitialDamagedVolumeAction`; changing them would break registry compatibility.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udf_reg.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.cpp

## Purpose
Defines the formatter/checker error-code-to-message table.

## Main Contents
- `mkudf_err_msg[]` maps `MKUDF_*` and `CHKUDF_*` codes to user-facing English messages.
- Includes generated/adjacent entries from `udferr_usr_cpp.h`.
- Ends with sentinel `{0xffffffff, "Unknown error"}`.

## Coverage
Messages cover format success, invalid parameters, hardware layout/read/write failures, descriptor write failures, VAT/session constraints, blank/format requirements, ISO image errors, bad-block/system-area failures, privilege issues, user abort, and checker mount failure.

## Notes
The table contains historical spelling mistakes in messages, which may be user-visible compatibility artifacts.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.h

## Purpose
Declares formatter/checker error codes, the error-message table shape, and fallback NT-like status constants for non-native builds.

## Main Contents
- Defines `MKUDF_OK`, a large range of failing `MKUDF_*` status values, `MKUDF_PENDING`, and `CHKUDF_CANT_MOUNT`.
- Includes `udferr_usr_h.h` for additional generated/adjacent error definitions.
- Defines `struct err_msg_item` and declares `mkudf_err_msg[]`.
- If `STATUS_SUCCESS` is not already defined, supplies many NTSTATUS-style constants used by shared user/kernel code.

## Notes
`STATUS_SUCCESS` is defined as `1` in the fallback block, unlike normal NTSTATUS `0`. Code using this fallback should rely on local success macros/semantics rather than assuming Windows kernel values.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.h -->