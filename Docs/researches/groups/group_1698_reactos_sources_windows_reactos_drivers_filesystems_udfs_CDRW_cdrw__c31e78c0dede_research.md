# Group Research: group_1698_reactos_sources_windows_reactos_drivers_filesystems_udfs_CDRW_cdrw__c31e78c0dede

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`, and all files in this grouped work item are under that source tree.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_hw.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_hw.h

## Purpose

`cdrw_hw.h` is the packed low-level MMC/SCSI/ATAPI protocol definition header used by the UDFS CD/DVD writer support layer. It defines wire-format command descriptor blocks, response records, mode pages, event blocks, media feature descriptors, profile numbers, sense codes, and optical-disc metadata structures.

## Main Contents

- Defines the central packed `CDB` union for many 6, 10, and 12 byte commands:
  - inquiry, request sense, read/write, format unit, erase, mode sense/select, log sense, start/stop, media removal.
  - CD/DVD-specific commands including read TOC, read header, read CD/MSF, write CD, close track/session, blank, reserve track, set CD speed, synchronize cache, read DVD structure, get configuration, set streaming, send OPC, send cue sheet, report/send key.
  - vendor commands for Plextor and NEC CD-DA reads.
- Defines SCSI operation codes and bus/status constants:
  - `SCSIOP_*` command opcodes.
  - `SCSISTAT_*` status values.
  - `SCSI_SENSE_*`, `SCSI_ADSENSE_*`, and `SCSI_SENSEQ_*` sense key/additional sense mappings.
- Defines optical media response records:
  - inquiry and sense data.
  - read capacity.
  - TOC/session/full TOC/PMA/ATIP/CD-TEXT records.
  - disc info, track info, event status blocks, buffer capacity, mechanical status.
- Defines mode pages:
  - read/write recovery, read recovery, write parameters, caching, CD device params, CD audio, power condition, failure reporting, timeout/protect, Philips sector type, capabilities/mechanical status, MRW.
- Defines format and capacity structures:
  - `FORMAT_LIST_HEADER`, `CDRW_FORMAT_DESCRIPTOR`, `DVD_FORMAT_DESCRIPTOR`, `FORMAT_UNIT_PARAMETER_LIST`, format-capacity descriptors.
- Defines GET CONFIGURATION feature/profile structures:
  - profile list and profile descriptors.
  - removable media, multiread, CD read, formattable, MRW, DVD+RW/+R, DVD write, streaming, BD read/write descriptors.
- Defines DVD/CSS key exchange and structure records:
  - copyright, disk key, AGID, challenge key, title key, ASF records.

## Integration Notes

This file is included by `cdrw_usr.h` and likely by the CDRW implementation files to build SCSI CDBs and parse device responses. Its structures are packed with `#pragma pack(push, 1)`, so callers must treat them as on-the-wire byte layouts, not native host records.

## Risks And Edge Cases

- Heavy use of C bitfields in packed wire structures is compiler- and endian-sensitive. The code assumes the Windows/x86 layout used by the original driver.
- Many multi-byte SCSI/MMC fields are stored as byte arrays in big-endian order. Callers must byte-swap explicitly.
- The header carries old and newer MMC definitions together, including obsolete and vendor-specific commands, so consumers need feature/profile checks before issuing commands.
- Several names contain historical typos such as `FormatCapcity`, `REMOVALE`, `OWERWRITE`, and `BlueRay`; these are ABI/source compatibility names and should not be casually renamed.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_usr.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_usr.h

## Purpose

`cdrw_usr.h` defines the public ABI between the CD writer driver and user/kernel clients. It maps driver IOCTLs, aliases standard CDROM/DVD/storage IOCTLs, and defines packed user-facing input/output structures that convert the low-level `cdrw_hw.h` wire records into host-endian fields.

## Main Contents

- Includes `cdrw_hw.h`, `ntddcdrm.h`, `ntddcdvd.h`, `winioctl.h`, and optionally `mountmgr.h`.
- Defines `FILE_DEVICE_CDRW`, `CDRW_SIGNATURE_v1`, and `CDRW_CTL_CODE_*` helpers.
- Defines private IOCTLs for:
  - tray locking, speed control, synchronize cache, capability/media queries.
  - write mode get/set, reserve track, blank, close track/session, low-level read/write.
  - disc/track info, buffer capacity, signature, driver reset, format unit, random access mode.
  - mode sense/select, read-ahead, media-change notification, OPC, cue sheet, full TOC/PMA/session/ATIP/CD-TEXT reads.
  - device info, event status, MRW mode, read capacity, disc layout, set streaming.
- Re-exports standard CDROM/DVD/disk/storage IOCTLs where platform headers may not define them.
- Provides fallback `STORAGE_MEDIA_TYPE` and media IOCTL definitions for older environments.
- Defines input/output structs for all private IOCTLs:
  - speed, streaming, sync cache, blank, reserve track, low-level read/write, format, close, media removal, read ahead.
  - track info, disc status/info, media type/class/capability, mode sense/select, write parameters, capabilities, OPC.
  - last error, raw read, audio, TOC/session/PMA/ATIP/CD-TEXT, init/deinit, geometry, device info, event, DVD structure/key/session, disk verify, layout.
- Defines capability flags:
  - media classes and extended classes.
  - `CDRW_FEATURE_*` device workaround/feature flags.
  - `CDRW_DEV_CAPABILITY_*` media support bitmasks.
- Defines driver error codes returned by last-error queries.
- Defines registry value names and policy constants for timeout, autorun/load mode, packet size, format workaround, split sizes, simulation, speed detection, sync packets, readiness, seek workarounds, packet-on-CD-R, retry limits, DVD quirks, and default last-LBA fallbacks.

## Integration Notes

This is the stable control-plane contract for CDRW operations. Kernel code handling device control requests should interpret input/output buffers using these structures, while user tools can include the same header for compatible IOCTL calls.

## Risks And Edge Cases

- The ABI is packed with `#pragma pack(push, 1)` and uses Windows types, so structure layout compatibility is critical.
- Some conditional macros are suspicious:
  - In `CDRW_RESTRICT_ACCESS`, `CDRW_CTL_CODE_W` is defined twice.
  - `REG_BAD_DVD_LAST_LBA_NAME_USER` is duplicated.
  - Several public field names preserve typos such as `VersiomMajor`.
- `GET_DISK_LAYOUT_USER_OUT` contains a raw pointer to `MediaTrackMap`, which is fragile across user/kernel address spaces unless the IOCTL handler marshals it carefully.
- Many structs mirror low-level SCSI records but convert fields to host-endian integers; handlers must avoid mixing raw and user versions.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CDRW/cdrw_usr.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CDRW/scsi_port.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/CDRW/scsi_port.h

## Purpose

`scsi_port.h` is a local SCSI port compatibility header. It defines SCSI port IOCTLs, pass-through structures, inquiry/capability/address records, and class-driver helper prototypes for environments that need these definitions in the CDRW/UDFS stack.

## Main Contents

- Includes `srb.h`.
- Defines `IOCTL_SCSI_BASE` and the `\\Device\\ScsiPort` name prefix.
- Defines SCSI port IOCTLs:
  - pass-through and direct pass-through.
  - miniport, inquiry data, capabilities, address, rescan bus, dump pointers.
- Defines structures:
  - `SCSI_PASS_THROUGH` and `SCSI_PASS_THROUGH_DIRECT`.
  - `SCSI_BUS_DATA`, `SCSI_ADAPTER_BUS_INFO`, `SCSI_INQUIRY_DATA`.
  - `SRB_IO_CONTROL`.
  - `IO_SCSI_CAPABILITIES`.
  - `SCSI_ADDRESS`.
  - `DUMP_POINTERS`.
- Defines pass-through direction values: data out, data in, unspecified.
- Declares SCSI class helper routines in kernel mode:
  - inquiry/capacity reads, capability/address queries, queue release, device claim/remove, internal IO control, completion, synchronous SRB send, SRB bus address initialization.
- Declares `DbgWaitForSingleObject_`.

## Integration Notes

The CDRW layer can use this header to submit SCSI pass-through requests or interact with class/port driver helpers without depending on a specific platform SDK version.

## Risks And Edge Cases

- This is a compatibility copy of sensitive kernel storage APIs. Divergence from the platform’s real SCSI headers can cause ABI mismatches.
- Direct pass-through contains a kernel pointer field, so it is only safe when used in the correct caller mode and IOCTL method context.
- Helper prototypes are suppressed for `USER_MODE` and partially for `CDRW_W32`; call sites must honor those build modes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CDRW/scsi_port.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/CMakeLists.txt

## Purpose

This CMake file builds the ReactOS UDFS filesystem driver module.

## Main Contents

- Adds `Include` to the include path.
- Builds a `udfs` module from UDF core files, UDF info/physical/remap files, cache/memory/debug helpers, dispatch handlers, and `udffs.h`.
- Adds `udffs.rc` as the resource file.
- Defines `_CRT_NON_CONFORMING_SWPRINTFS`.
- Suppresses selected GCC/Clang warnings for this legacy codebase.
- Configures the target as a kernel-mode driver with `set_module_type(udfs kernelmodedriver)`.
- Links `${PSEH_LIB}` and imports `ntoskrnl` and `hal`.
- Adds precompiled header `udffs.h`.
- Installs the driver to `reactos/system32/drivers`.
- Registers `udfs_reg.inf`.

## Integration Notes

This is the build entry point for the UDFS driver under ReactOS. It intentionally omits `pnp.cpp` via a commented source entry, so PnP behavior is either not built or handled elsewhere.

## Risks And Edge Cases

- The warning suppressions indicate legacy code patterns that may hide real portability problems.
- `udffs.h` is both listed as a source and used as PCH, so changes to it have broad rebuild impact.
- `pnp.cpp` being commented out is a functional build decision worth checking before adding PnP-related changes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtDecl.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtDecl.h

## Purpose

`CrNtDecl.h` is a macro-expansion helper used by CrossNt to declare, define, or initialize dynamically resolved NT kernel compatibility function pointers.

## Main Contents

- Clears prior `CROSSNT_DECL` and `CROSSNT_DECL_EX` definitions.
- Under `CROSSNT_DECL_API`, expands declarations into:
  - function pointer typedefs.
  - `extern "C"` function pointer globals named `CrNt<name>`.
  - fallback implementation prototypes named `CrNt<name>_impl`.
- Under `CROSSNT_DECL_STUB`, expands declarations into initialized `CrNt<name> = NULL` pointer globals.
- Under `CROSSNT_INIT_STUB`, expands declarations into runtime initialization code:
  - logs the current pointer.
  - resolves the symbol from `NTOSKRNL.EXE` or a specified module.
  - falls back to `CrNt<name>_impl` when resolution fails.

## Integration Notes

This file is not useful alone. It is included around `CrNtStubs.h` after defining one of the expansion modes. That allows a single symbol list to generate declarations, storage, and initialization code.

## Risks And Edge Cases

- The macro system is fragile: wrong include order or missing mode macro changes emitted code.
- The `CROSSNT_INIT_STUB` branch has a suspicious debug format string in the non-EX macro: `final %\n` appears malformed.
- The code assumes `CrNtGetProcAddress`, module handles, and fallback implementations exist in the including translation unit.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtDecl.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtStubs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtStubs.h

## Purpose

`CrNtStubs.h` is the CrossNt symbol table. It lists NT/HAL/NDIS routines that the portability layer can dynamically bind or emulate.

## Main Contents

Macro invocations declare entries for:

- Process/thread identity:
  - `PsGetCurrentProcessId`
  - `PsGetCurrentThreadId`
- Spin/interlocked operations:
  - `KeTestSpinLock`
  - `InterlockedIncrement`
  - `InterlockedDecrement`
  - `InterlockedExchangeAdd`
  - `InterlockedCompareExchange`
- HAL IRQL helpers:
  - `KeRaiseIrqlToDpcLevel`
  - `KeRaiseIrqlToSynchLevel`
- NDIS read/write locks:
  - `NdisInitializeReadWriteLock`
  - `NdisAcquireReadWriteLock`
  - `NdisReleaseReadWriteLock`

## Integration Notes

This file depends entirely on `CROSSNT_DECL` and `CROSSNT_DECL_EX` being defined before inclusion, normally by `CrNtDecl.h`. It enables the same list to produce typedefs, globals, and initialization code.

## Risks And Edge Cases

- The listed prototypes must exactly match the real exported routines and calling conventions.
- Some call-argument macro payloads include parameter declarations rather than plain arguments in interlocked entries, which is harmless only if the active macro ignores or tolerates that field.
- NDIS lock support depends on `NDIS.SYS` availability; fallback behavior depends on implementations elsewhere.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtStubs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrossNt.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrossNt.h

## Purpose

`CrossNt.h` is the public include for the CrossNt compatibility layer, providing NT-version probing, module/symbol lookup, runtime-resolved kernel helper pointers, and old-NT compatibility shims.

## Main Contents

- Includes NT kernel headers, `ntddk_ex.h`, `rwlock.h`, optionally `ilock.h`, plus `misc.h` and `tools.h`.
- Declares:
  - `CrNtInit`
  - `CrNtGetCPUGen`
  - `CrNtGetModuleBase`
  - `CrNtFindModuleBaseByPtr`
  - `CrNtGetProcAddress`
  - `CrNtSkipImportStub`
- Declares runtime-resolved pointers:
  - `CrNtPsGetVersion`
  - `CrNtNtQuerySystemInformation`
- Exposes global OS/module state:
  - `MajorVersion`, `MinorVersion`, `BuildNumber`, `SPVersion`
  - `g_hNtosKrnl`, `g_hHal`
  - `g_KeNumberProcessors`
- Defines Windows version predicates and numeric IDs.
- In debug builds, remaps `strlen` and `strcmp` to CrossNt implementations for NT 3.51 compatibility.
- Defines `CROSSNT_DECL_API` and includes `CrNtDecl.h` plus `CrNtStubs.h` to emit the external function pointer declarations.

## Integration Notes

This header centralizes the portability contract for code that must run across old NT versions and ReactOS-like environments. It must be included in C++ contexts but wraps exports in `extern "C"`.

## Risks And Edge Cases

- The header exposes global state and macro predicates instead of encapsulated helpers.
- Version predicates are exact comparisons and can misclassify newer systems unless `WinVer_IsdNETp` is used.
- Debug-only `strlen`/`strcmp` remapping can surprise code included after this header.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrossNt.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/ilock.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/ilock.h

## Purpose

`ilock.h` declares internal CrossNt fallback implementations for interlocked operations on i386/x86 systems.

## Main Contents

- Declares MP and UP variants for:
  - `CrNtInterlockedIncrement_impl_i386_*`
  - `CrNtInterlockedDecrement_impl_i386_*`
  - `CrNtInterlockedExchangeAdd_impl_i386_*`
  - `CrNtInterlockedCompareExchange_impl_i386_*`

## Integration Notes

This file is included only when `CROSS_NT_INTERNAL` is defined. It supplies prototypes for fallback routines used when the corresponding NT exports are missing or unsuitable.

## Risks And Edge Cases

- The declarations are x86-specific and use `__fastcall`.
- The include guard terminator is written as `#endif __CROSS_NT_INTERLOCKED__H__`, which is nonstandard but accepted by many preprocessors as trailing tokens after `#endif`.
- Correct UP/MP selection must be handled elsewhere based on CPU/system state.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/ilock.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/misc.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/misc.h

## Purpose

`misc.h` declares x86 CrossNt helper routines and macros for endian/byte-order transforms, MSF movement, and low-level value swapping.

## Main Contents

Under `_X86_`, it declares:

- Runtime-selected function pointers:
  - `_MOV_DD_SWP`
  - `_REVERSE_DD`
  - `_MOV_MSF_SWP`
- i386/i486 implementations for doubleword swap/reverse and MSF swap helpers.
- Direct helper routines:
  - `_MOV_DW_SWP`
  - `_REVERSE_DW`
  - `_MOV_DW2DD_SWP`
  - `_MOV_SWP_DW2DD`
  - `_MOV_MSF`
  - `_XCHG_DD`
- Macros wrapping each helper by passing addresses:
  - `MOV_DD_SWP`, `MOV_DW_SWP`, `REVERSE_DD`, `REVERSE_DW`, `MOV_DW2DD_SWP`, `MOV_SWP_DW2DD`, `MOV_MSF`, `MOV_MSF_SWP`, `XCHG_DD`.

## Integration Notes

These helpers are relevant to CDRW/UDF parsing because SCSI/MMC and UDF structures contain big-endian byte arrays and MSF time/address fields.

## Risks And Edge Cases

- Entirely x86-oriented and calling-convention-sensitive.
- Macros take lvalue expressions and pass their addresses; side effects in macro arguments would be unsafe.
- Runtime function pointers must be initialized before use.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/rwlock.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/rwlock.h

## Purpose

`rwlock.h` defines local NDIS-compatible read/write lock structures and constants for CrossNt.

## Main Contents

- Defines `MAXIMUM_PROCESSORS` as 32 if absent.
- Defines `NDIS_RW_LOCK_REFCOUNT`, padding each refcount to a 16-byte cache-line-sized slot.
- Defines `NDIS_RW_LOCK` with a spin lock/context area and per-processor refcounts.
- Defines `LOCK_STATE` containing lock state and old IRQL.
- Defines lock-state constants:
  - free, read acquired, write acquired, recursive, released.
- Defines acquisition mode constants:
  - `RWLOCK_FOR_WRITE`
  - `RWLOCK_FOR_READ`

## Integration Notes

This supports the dynamically resolved NDIS lock routines listed in `CrNtStubs.h`, and provides layout definitions when platform headers do not.

## Risks And Edge Cases

- The NDIS lock layout must match the expected implementation. If NDIS uses a different layout on a target OS, this compatibility definition can break.
- `MAXIMUM_PROCESSORS` fixed at 32 reflects old NT-era assumptions.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/rwlock.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.cpp

## Purpose

`Sys_spec_lib.cpp` implements UDF-to-NT conversion and OS-specific helper logic shared by the UDFS driver support code. It translates timestamps, attributes, directory records, names, Unicode strings, cache state, and delete/rename policy between UDF metadata and NT filesystem structures.

## Main Functions

- `UDFTimeToNT`
  - Converts a UDF timestamp into NT system time.
  - Builds `TIME_FIELDS`, clamps pre-1601 years, converts local time to system time.
- `UDFTimeToUDF`
  - Converts NT time to a UDF local timestamp.
  - Fills microsecond, hundred-microsecond, centisecond, date/time, and timezone fields.
- `UDFAttributesToNT`
  - Converts UDF file-entry flags, permissions, file type, and directory-index characteristics to NT file attributes.
  - Sets system, archive, directory, hidden, readonly.
  - Caches attributes in `DIR_INDEX_ITEM`.
- `UDFAttributesToUDF`
  - Converts NT file attributes back to UDF permissions, file type, ICB flags, and file-characteristic bits.
  - Marks file entry and directory index as modified.
- `UDFFileDirInfoToNT`
  - Fills `FILE_BOTH_DIR_INFORMATION` from a `DIR_INDEX_ITEM`.
  - Uses cached `FileInfo`/FCB state when present.
  - Reads the file entry from disk when attributes or linked state require it.
  - Converts times, sizes, attributes, long name, and DOS short name.
  - Reports zero EOF/allocation size for directories.
- `UDFSetFileXTime`
  - Writes NT times into regular or extended UDF file entries and updates directory-index cached times.
- `UDFGetFileXTime`
  - Reads UDF entry times as NT times, with fallback to current system time.
- `UDFNormalizeFileName`
  - Trims trailing nulls, trailing periods, and trailing spaces except for `.` and `..`.
- `UDFDOSNameOsNative`
  - Uses `RtlGenerate8dot3Name` to generate a DOS short name, with special handling for `.` and `..`.
- Unicode string helpers:
  - `MyAppendUnicodeStringToString_`
  - `MyAppendUnicodeToString_`
  - `MyInitUnicodeString`
  - `MyCloneUnicodeString`
  - These allocate/reallocate kernel buffers and keep strings null-terminated.
- `UDFIsDirInfoCached`
  - Checks whether all directory-index entries already have usable cached attributes and are not unresolved linked entries.
- Delete/rename policy helpers:
  - `UDFDoesOSAllowFileToBeTargetForRename__`
  - `UDFDoesOSAllowFileToBeUnlinked__`
  - `UDFDoesOSAllowFilePretendDeleted__`

## Integration Notes

This file depends on core UDFS structures and helpers such as `PVCB`, `PUDF_FILE_INFO`, `PDIR_INDEX_ITEM`, `UDFReadFileEntry`, `ValidateFileInfo`, `UDFDirIndex`, `UDFGetDirIndexByFileInfo`, cache helpers, memory wrappers, and NT runtime routines.

## Risks And Edge Cases

- `UDFTimeToUDF` computes `LocalTime` but uses `NtTime % 100` for sub-centisecond fields after conversion, which is worth verifying for precision correctness.
- Unicode append helpers reallocate manually and update `MaximumLength`; the `MyAppendUnicodeToString_` path sets `MaximumLength` based on only appended length in one branch, which may be fragile.
- `UDFFileDirInfoToNT` copies `UdfName.MaximumLength` into `FileName` while setting `FileNameLength` from `Length`; callers must ensure the output buffer is large enough.
- File deletion policy is conservative: directory targets, parentless files, stream dirs, open children, readonly attributes, and active FCB state can block operations.
- Several blocks are compiled out for `_CONSOLE` or `UDF_READ_ONLY_BUILD`, so behavior differs by build mode.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.h

## Purpose

`Sys_spec_lib.h` declares the UDFS system-specific helper interface implemented by `Sys_spec_lib.cpp` and provides macros for timestamp updates, cache checks, file ID creation, allocation rounding, and device-object classification.

## Main Contents

Inside `_BROWSE_UDF_`, it declares:

- Timestamp conversion:
  - `UDFTimeToNT`
  - `UDFTimeToUDF`
- Attribute conversion:
  - `UDFAttributesToNT`
  - `UDFAttributesToUDF`
- Directory info conversion:
  - `UDFFileDirInfoToNT`
- File-entry time mutation/access:
  - `UDFSetFileXTime`
  - `UDFGetFileXTime`
- Timestamp update macros:
  - access, modify, attribute, create time updates based on VCB compatibility flags.
- Name/string helpers:
  - `UDFDOSNameOsNative`
  - `UDFNormalizeFileName`
  - `MyAppendUnicodeStringToString_`
  - `MyAppendUnicodeToString_`
  - `MyInitUnicodeString`
  - `MyCloneUnicodeString`
- Cache helpers:
  - `UDFIsDataCached`
  - `UDFIsDirInfoCached`
- File operation policy helpers:
  - rename/hardlink target checks.
  - unlink/move checks.
  - pretend-delete and OS-reference removal checks.
- Utility macros:
  - `UDFGetNTFileId`
  - `UnicodeIsPrint`
  - `UDFSysGetAllocSize`
  - `UDFIsFSDevObj`

## Integration Notes

The header is gated by `_BROWSE_UDF_`, so consumers must define that build symbol to see the main declarations. It assumes many UDFS internal types are already visible.

## Risks And Edge Cases

- Update macros evaluate arguments multiple times and embed multi-statement logic; they should be used with simple variables.
- `UDFGetNTFileId` mixes disk location, filename checksum, and VCB pointer bits, making it process/address-space dependent.
- `UDFIsDataCached` requires low IRQL and initialized write cache; callers should not assume it is purely a metadata check.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/Sys_spec_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/check_env.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/check_env.h

## Purpose

`check_env.h` detects and validates the execution environment for shared UDFS/CDRW code: NT kernel mode, NT native mode, or Win32 mode.

## Main Contents

- Contains an older, fully commented environment-selection block showing intended include policy for kernel/native/Win32 builds.
- Defines `NT_KERNEL_MODE` when `NT_INCLUDED` is already set.
- Leaves `USER_MODE` definitions commented out for NT native and Win32 cases.
- Defaults to `WIN_32_MODE` when neither NT kernel nor NT native mode is selected, or when `WIN_32_MODE` is explicitly defined.
- Emits preprocessor errors if:
  - `NT_KERNEL_MODE` is combined with `NT_NATIVE_MODE` or `WIN_32_MODE`.
  - `NT_NATIVE_MODE` is combined with `WIN_32_MODE`.

## Integration Notes

This header should be included before environment-specific headers to prevent conflicting build-mode definitions.

## Risks And Edge Cases

- Much of the original include logic is commented out, so this file now mostly validates macros rather than including the right platform headers.
- Defaulting to Win32 mode can hide missing mode definitions unless build scripts set explicit symbols.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/check_env.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.cpp

## Purpose

`env_spec_nt.cpp` implements NT-native-mode wrappers that emulate a subset of Win32-style APIs on top of NT system calls. It is compiled only under `NT_NATIVE_MODE`.

## Main Functions

- `GetOsVersion`
  - Reads `CurrentVersion` and `CurrentBuildNumber` from the Windows NT registry path.
  - Fills optional major, minor, and build outputs.
- `MyDeviceIoControl`
  - Routes control codes to `NtDeviceIoControlFile` or `NtFsControlFile` based on device type.
  - Waits for pending completion and reports returned byte count.
- `Sleep`
  - Implements millisecond sleep via `NtDelayExecution`.
- `MyGlobalAlloc` / `MyGlobalFree`
  - Lazily creates an RTL heap and allocates/frees from it.
- `PrintNtConsole`
  - Formats an ANSI debug message, prefixes line starts, converts to Unicode, and calls `NtDisplayString`.
- File wrappers:
  - `EnvFileOpenW`
  - `EnvFileOpenA`
  - `EnvFileClose`
  - `EnvFileGetSizeByHandle`
  - `EnvFileGetSizeA`
  - `EnvFileGetSizeW`
  - `EnvFileExistsA`
  - `EnvFileExistsW`
  - `EnvFileWrite`
  - `EnvFileRead`
  - `EnvFileSetPointer`
  - `EnvFileDeleteW`

## Integration Notes

This file pairs with `env_spec_nt.h`, which maps Win32-like names such as `DeviceIoControl`, `Sleep`, `GlobalAlloc`, and `ExitProcess` to these NT-native implementations.

## Risks And Edge Cases

- `GetOsVersion` parses the major/minor version as hexadecimal-style accumulation (`*16`) instead of decimal, which may be intentional for version IDs but is unusual.
- `MyDeviceIoControl` writes `*lpBytesReturned` without checking for null on success or warning paths.
- `EnvFileSetPointer` returns the existing `Status` when the computed position is negative; that value may be stale from a previous branch.
- `PrintNtConsole` uses static buffers and a global `was_enter`, so it is not thread-safe.
- `EnvFileOpenW` always requests read/write/synchronize access, so it is not suitable for read-only opens.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.h

## Purpose

`env_spec_nt.h` declares the NT-native environment abstraction and maps selected Win32-like APIs to NT-native helper implementations when `NT_NATIVE_MODE` is defined.

## Main Contents

- Includes `zw_2_nt.h` under `NT_NATIVE_MODE`.
- Defines `MAX_PATH` if missing.
- Declares `GetOsVersion` and maps `PsGetVersion` to it.
- Provides simple inline/macro versions of interlocked increment, decrement, and exchange-add.
- Maps `DeviceIoControl` to `MyDeviceIoControl`.
- Maps character conversion helpers to `swprintf`-based conversions.
- Declares `Sleep`.
- Maps `GlobalAlloc`/`GlobalFree` to `MyGlobalAlloc`/`MyGlobalFree`.
- Maps `ExitProcess` to `NtTerminateProcess`.
- Declares console and file helper functions:
  - `PrintNtConsole`
  - `EnvFileOpenW/A`
  - `EnvFileClose`
  - `EnvFileGetSizeByHandle`
  - `EnvFileGetSizeA/W`
  - `EnvFileExistsA/W`
  - `EnvFileWrite`
  - `EnvFileRead`
  - `EnvFileSetPointer`
  - `EnvFileDeleteW`
- Defines file seek mode constants:
  - `ENV_FILE_CURRENT`
  - `ENV_FILE_END`
  - `ENV_FILE_BEGIN`
- Maps `PrintDbgConsole` to `PrintNtConsole`.

## Integration Notes

This header allows shared formatter/tools code to compile in NT native mode without including Win32 user-mode APIs.

## Risks And Edge Cases

- The interlocked macros are not atomic; they are only safe in single-threaded or otherwise serialized native-mode utility contexts.
- `OemToCharW` and `MultiByteToWideChar` mappings ignore code page semantics and buffer size correctness.
- Macro replacements for common APIs can affect included code unexpectedly.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.h -->