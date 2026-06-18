# Group Research: group_1699_reactos_sources_windows_reactos_drivers_filesystems_udfs_Include_en_d917d68286e8

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/reactos`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.cpp

Win32/native-mode implementation side of the UDF environment shim used by user-mode formatter/browser/library builds.

Key responsibilities:
- Defines global Win32-side open/lock state when not building the formatter state object: `LockMode`, `open_as_device`, and `opt_invalidate_volume`.
- Routes physical device control through `UDFPhSendIOCTL()`, either to Win32 `DeviceIoControl()` or to LIBUDF/LIBUDFFMT callback tables.
- Implements synchronous physical reads and writes through Win32 file handles or callback hooks.
- Implements `my_open()` for opening a target as a volume/device first, locking it, enabling extended DASD I/O, and falling back to an image file.
- Provides volume lock/unlock helpers using UDF private lock IOCTLs where available and standard `FSCTL_LOCK_VOLUME` / `FSCTL_UNLOCK_VOLUME` otherwise.
- Provides file/image helpers, debug console output, time conversion wrappers, pool allocation wrappers, and `ProbeMemory()`.

Important behavior:
- `UDFPhWriteSynchronous()` aligns writes through a temporary 64 KiB-aligned buffer before `WriteFile()` in the non-library Win32 path.
- `my_open()` retries locking and can issue `FSCTL_INVALIDATE_VOLUMES` or `IOCTL_UDF_INVALIDATE_VOLUMES` after enabling `SE_TCB_NAME`.
- If direct volume opening or locking fails in Win32 mode, `my_open()` falls back to creating/opening the provided name as a plain image file.
- `ProbeMemory()` touches the last byte and every page under SEH to validate user pointers.

Dependencies:
- Uses Win32 APIs such as `CreateFileW`, `DeviceIoControl`, `SetFilePointer`, `ReadFile`, `WriteFile`, `GetVolumeInformationW`, and `GetDriveTypeW`.
- Depends on UDF-specific structures/callbacks including `PVCB`, `UDFWriteData`, `PUDF_VOL_HANDLE_I`, `_UDF_FMT_PARAMETERS`, and private UDF IOCTL values.

Notable risks:
- Several paths cast pointers and offsets through `ULONG`, so the code is effectively 32-bit-oriented.
- Volume open/lock behavior differs substantially across normal tools, LIBUDF, LIBUDFFMT, CDRW_W32, and NT native builds.
- Thread heap free paths return without releasing `MemLock` if the current thread pool is not found.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.h

User-mode and NT-native compatibility header that lets shared UDF code build outside the real kernel DDK environment.

Key responsibilities:
- Selects either `nt_native.h` or Win32 headers depending on `NT_NATIVE_MODE`.
- Defines NT-like primitive types, constants, status helpers, pool types, IRQL values, events, resources, spin locks, device objects, packets, FCB headers, section object pointers, time fields, and I/O status blocks.
- Provides debug, user-print, timing, performance, allocation, dump, assertion, breakpoint, and validation macros.
- Maps `ExAllocatePool`, `ExAllocatePoolWithTag`, and `ExFreePool` either to Win32 `GlobalAlloc`/`GlobalFree` or local implementations.
- Declares physical I/O functions, image helpers, open/exit helpers, volume locking helpers, device type lookup, and memory probing.
- Provides fallback list-manipulation macros if platform headers do not define them.

Important behavior:
- Debug and user output behavior changes under `DBG`, `PRINT_ALWAYS`, `PRINT_TO_DBG_LOG`, `CDRW_W32`, `LIBUDFFMT`, and `LIBUDF`.
- Resource acquisition macros spin around `AcquireXLock()` and treat shared and exclusive acquisition the same way.
- `DEVICE_OBJECT` is a local substitute whose fields differ depending on LIBUDF/LIBUDFFMT/non-library builds.
- `UDFPhWriteVerifySynchronous` is currently aliased to `UDFPhWriteSynchronous`.

Dependencies:
- Includes `platform.h`, `udferr_usr.h`, and `env_spec_nt.h` in native mode.
- Expects shared UDF code to provide `AcquireXLock`, `MyRtlCompareMemory`, string helpers, and UDF structures.

Notable risks:
- This header intentionally redefines or substitutes many kernel APIs; incorrect build flags can silently select very different semantics.
- Several macros evaluate arguments more than once or expand to statement blocks without `do { } while (0)`.
- Pointer arithmetic macros and structure substitutions assume 32-bit pointer sizes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_w32.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.cpp

Common formatter-side Win32 helpers for optical drive discovery, capability classification, and formatter drive locking.

Key responsibilities:
- Defines initial drive selection `szDisc` and changer flag `bChanger`.
- Implements `CheckCDType()` to open a CD/DVD volume, query cdrw.sys signature/device information/capabilities, and classify writer type.
- Implements `InitDeviceList()` to enumerate logical drives, filter CD-ROM drives, classify each one, and pass display data to a callback.
- Implements formatter drive acquisition/release/query using named public events as per-drive/per-level locks.

Important behavior:
- `CheckCDType()` returns `BUSY` if the target cannot be opened, `OTHER` for unsupported/unknown media, and specific writer types for CD/DVD formats.
- Device capabilities come from both capability bitmasks and GET CONFIGURATION feature flags.
- Formatter acquisition creates `DwFmtLock_<Drive><Level>` events; an existing event means the drive is already acquired.

Dependencies:
- Uses Win32 drive APIs, `OpenOurVolume()`, `UDFPhSendIOCTL()`, cdrw.sys private IOCTLs, capability output structures, and `MediaTypeStrings`.

Notable risks:
- The code is ANSI-oriented and casts buffers through `LPTSTR`, so Unicode/MBCS build settings matter.
- Drive lock names only use the first drive character and a single level byte.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.h

Public declarations for common UDF formatter UI/device helpers.

Key responsibilities:
- Declares `CheckCDType()` for optical writer/media capability classification.
- Defines the `PADD_DEVICE` callback signature used by device-list population.
- Declares `InitDeviceList()` for enumerating candidate optical drives.
- Exposes global formatter selection/state variables `szDisc` and `bChanger`.
- Declares formatter drive acquisition, release, and query helpers.

Dependencies:
- Requires prior definitions of `JS_DEVICE_TYPE`, Win32 `HWND`, `HANDLE`, `BOOL`, `PCHAR`, and related formatter types.
- Implemented by `format_common.cpp`.

Notable risks:
- `FmtAcquireDriveW` is only a pointer cast rather than a true wide-character implementation.
- The visible header has no include guard, so it relies on surrounding include discipline.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.cpp

Wide-character, context-based GNU getopt implementation for UDF command-line tools.

Key responsibilities:
- Implements `getopt_init()` to initialize caller-owned `optarg_ctx`.
- Maintains option ordering mode: require-order, permute, or return-nonoptions-in-order.
- Implements argument permutation through `exchange()`.
- Implements `_getopt_internal()` for short options, long options, optional/required arguments, abbreviation matching, ambiguity detection, `--` termination, and long-only fallback behavior.
- Exposes `getopt()` and `getopt_long()` wrappers.

Important behavior:
- Uses wide-character string primitives.
- `optind == 0` is the initialization signal; scanning starts at argv index 1.
- `optstring` prefix `-` selects return-in-order mode; prefix `+` selects require-order mode; otherwise default is permutation.
- Long option abbreviation is accepted only if unique or exact.

Dependencies:
- Includes `getopt.h`.
- Uses `UDFPrint()` for diagnostics.
- Mutates `argv` order in permutation mode.

Notable risks:
- `ordering` is file-static global state, shared across contexts.
- `getopt_long_only()` is declared in the header but not implemented in this file.
- Error format strings mix wide and narrow specifiers in a few places.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.h

Header for the UDF wide-character getopt implementation.

Key responsibilities:
- Defines `BAD_OPTION`.
- Defines `optarg_ctx`, the caller-owned state object for reentrant option parsing.
- Defines `struct option` for long-option declarations.
- Defines `no_argument`, `required_argument`, and `optional_argument`.
- Declares `getopt_init()`, `getopt()`, `getopt_long()`, `getopt_long_only()`, and `_getopt_internal()`.

Important behavior:
- `optarg_ctx` stores parser outputs and internal scan/permutation state.
- All parser strings are `WCHAR` based; this is not byte-string POSIX getopt.
- Comments document GNU-style argument permutation and long-option semantics.

Dependencies:
- Requires `WCHAR` and C linkage support from surrounding includes.
- Implemented mostly by `getopt.cpp`.

Notable risks:
- Consumers expecting standard global `optarg`/`optind` variables must use `optarg_ctx` fields instead.
- `BAD_OPTION` is `'\0'`, unusual compared with standard `'?'` behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/getopt.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.cpp

Optional internal heap manager implementation enabled by `MY_USE_INTERNAL_MEMMANAGER`.

Key responsibilities:
- Maintains global fixed-size heap frame metadata in `FrameList`, protected by either a spin lock or an `ERESOURCE` wrapper.
- Implements debug dumping and integrity checking for frames and allocation descriptors under `UDF_DBG`.
- Implements best-fit allocation within a frame.
- Implements address-to-descriptor/frame lookup.
- Implements free/coalescing and whole-frame reclamation.
- Implements in-place shrink/grow where possible and fallback allocate/copy/free reallocation.
- Initializes and releases the allocator through `MyAllocInit()` and `MyAllocRelease()`.

Important behavior:
- Frames are `MY_HEAP_FRAME_SIZE` bytes, descriptor arrays have `MY_HEAP_MAX_BLOCKS` entries, and descriptors store address plus length/used-bit.
- Freeing clears the used bit, optionally stamps the freed block with `0xDEADDA7A`, checks optional bounds sentinels, and coalesces adjacent free descriptors.
- Frame descriptors are kept sorted by address, allowing binary-search-like lookup.

Dependencies:
- Depends on constants, structures, alignment macros, and tracking flags from `mem_tools.h`.
- Uses `DbgAllocatePool`, `DbgFreePool`, `RtlMoveMemory`, `RtlZeroMemory`, `RtlCopyMemory`, `UDFPrint`, `ASSERT`, and `BrutePoint`.

Notable risks:
- The allocator stores addresses in `ULONG`, making it 32-bit-specific.
- `MyReallocPool()` calls `MyAllocatePool()` while already holding the allocator lock; this depends on lock semantics and can deadlock if the lock is not recursively compatible.
- Debug accounting in the grow path appears suspicious.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.h

Memory allocation abstraction for shared UDF code, selecting either the optional internal frame allocator or system/debug pool wrappers.

Key responsibilities:
- Defines allocation descriptor and frame descriptor structures used by the internal allocator.
- Defines heap constants: used flag, length mask, frame size, maximum frames, maximum blocks, alignment, and page alignment.
- Declares internal allocator APIs when enabled.
- Defines public macros `MyAllocatePool__`, `MyAllocatePoolTag__`, `MyFreePool__`, `MyReallocPool__`, `MyFreeMemoryAndPointer`, and `MyCheckArray`.
- Supports optional owner tracking, reference/tag tracking, forced nonpaged allocation, internal allocator use, caller tracking, and sentinel checking.

Important behavior:
- Allocation sizes are normally rounded by `MyAlignSize__()` to a 64-byte boundary.
- Without the internal allocator, allocations route to debug/system pool wrappers.
- With `MY_MEM_BOUNDS_CHECK`, extra bytes are appended and filled with sentinels.

Dependencies:
- Requires DDK-like pool types/macros and debug allocation wrappers from the UDF environment.
- Internal allocator implementation is in `mem_tools.cpp`.

Notable risks:
- Inline bounds-checking code uses x86 `__asm int 3` in places.
- Several macros force `NonPagedPool` regardless of incoming type.
- Because much of the API is macro-based, behavior changes significantly with compile-time flags.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/mem_tools.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/misc_common.cpp -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/misc_common.cpp

Tiny shared helper module for UDF volume modified-state bookkeeping.

Key responsibilities:
- Implements `UDFSetModified()` to increment `Vcb->Modified` and normalize overflow/sign-bit cases back to `2`.
- Implements `UDFPreClrModified()` to set `Vcb->Modified` to `1` before clearing.
- Implements `UDFClrModified()` to log the clear operation and decrement `Vcb->Modified`.

Important behavior:
- Uses `UDFInterlockedIncrement()` and `UDFInterlockedDecrement()` wrappers.
- The modified state is counter-like rather than a simple boolean.

Dependencies:
- Depends on `PVCB` containing a `Modified` field.
- Uses `UDFPrint()` and environment interlocked macros.

Notable risks:
- In user-mode shim builds, the interlocked macros are simple non-atomic increments/decrements.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/misc_common.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/nt_native.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/nt_native.h

Large native NT API compatibility header used when building UDF tools for `NT_NATIVE_MODE`.

Key responsibilities:
- Includes low-level NT/storage/device IOCTL headers, then fills in many NT declarations normally provided by Win32/DDK headers.
- Defines access masks, generic rights, file rights, file attributes, share modes, create dispositions, create/open options, file status return values, alignment constants, device characteristics, and FSCTL values.
- Declares RTL registry/string/integer conversion routines and memory helpers.
- Defines `TIME_FIELDS`, generic mapping, `CTL_CODE`, I/O status/APC types, file information classes/structures, filesystem information classes, and registry key/value structures.
- Declares native registry APIs, heap APIs, process/thread/display APIs, and native file/control/read/write/query/close/wait/delay APIs.
- Defines object-manager, section, memory protection/allocation, process, thread, client ID, floating-save-area, x86 context, environment/startup, and heap structures/constants.

Important behavior:
- The file is declaration-only; it makes native-mode code compile without the normal Win32 process environment.
- It targets x86 context layout explicitly.
- Some definitions are guarded for ReactOS or existing header symbols, but many constants are unconditional compatibility copies.

Dependencies:
- Includes `<excpt.h>`, `<ntdef.h>`, `<ntstatus.h>`, `<string.h>`, `<DEVIOCTL.H>`, `<NTDDSTOR.H>`, and `<NTDDDISK.H>`.
- Used by `env_spec_w32.h` and `env_spec_w32.cpp` when `NT_NATIVE_MODE` is set.

Notable risks:
- This header duplicates many platform definitions; conflicts are likely if included alongside newer/full SDK or DDK headers.
- The context and pointer-related declarations are 32-bit/x86-centric.
- Several declarations are historical and may not match modern NT header signatures exactly.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/nt_native.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/ntddk_ex.h -->
# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/ntddk_ex.h

Supplemental DDK compatibility header for system information, module/image structures, and storage IOCTL constants.

Key responsibilities:
- Defines `SYSTEM_INFORMATION_CLASS` values used with `ZwQuerySystemInformation()`.
- Declares `ZwQuerySystemInformation()`.
- Defines `SYSTEM_MODULE_ENTRY` and `SYSTEM_MODULE_INFORMATION`.
- Provides basic `WORD`, `BOOL`, `DWORD`, and `BYTE` aliases.
- When not building ReactOS, defines PE/COFF image structures needed for export parsing.
- Defines missing disk/storage IOCTL constants such as partition info, drive layout, geometry, load media, media types, and verify checks.

Important behavior:
- PE image declarations are skipped under `__REACTOS__`, relying on ReactOS headers there.
- `SystemPowerInformation` is conditionally renamed when `PO_CB_SYSTEM_POWER_POLICY` is already present.

Dependencies:
- Intended to be included after base NT/DDK definitions that provide `NTSYSAPI`, `NTSTATUS`, `NTAPI`, pointer/integer types, and IOCTL macros.

Notable risks:
- This is a compatibility patch header; duplicate definitions can conflict with modern SDK/DDK headers.
- The `SYSTEM_MODULE_ENTRY` layout is historical and version-sensitive.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/udfs/Include/ntddk_ex.h -->