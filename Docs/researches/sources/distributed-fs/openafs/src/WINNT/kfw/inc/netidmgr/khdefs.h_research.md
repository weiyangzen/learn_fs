# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khdefs.h

## Purpose

`khdefs.h` is the core portability and ABI definition header for NetIDMgr. It defines fixed-width integer aliases, generic handles, booleans, size types, calling/export conventions, common permission and creation flags, pointer/math macros, and version records used by every other public NetIDMgr header.

## Important APIs, Types, and Functions

- Integer aliases: `khm_octet`, `khm_int16`, `khm_ui_2`, `khm_int32`, `khm_ui_4`, `khm_int64`, and `khm_ui_8`.
- Numeric limits: `KHM_UINT32_MAX`, `KHM_INT32_MAX`, `KHM_INT32_MIN`, `KHM_UINT16_MAX`, `KHM_INT16_MAX`, `KHM_INT16_MIN`.
- `khm_handle` is an opaque `void *`; `KHM_INVALID_HANDLE` is `NULL`.
- `khm_boolean` is `khm_int32`, `khm_size` is `size_t`, and `khm_ssize` is a Windows-width signed size.
- `khm_wparm` and `khm_lparm` mirror Windows parameter widths, with `_WIN64` and `_WIN32` branches.
- `KHMAPI` is `__stdcall`; `KHMEXP`, `KHMEXP_EXP`, and `KHMEXP_IMP` select DLL export/import decoration.
- Generic flags include `KHM_PERM_READ`, `KHM_PERM_WRITE`, and `KHM_FLAG_CREATE`.
- Utility macros include `UBOUND32`, `BYTEOFFSET`, `IS_POW2`, `UBOUNDSS`, and `ARRAYLENGTH`.
- `khm_version` carries four 16-bit fields: major, minor, patch, and auxiliary/build.

## Control Flow

There is no executable control flow. The header controls compile-time ABI shape and calling convention. Any exported API declared with `KHMEXP khm_int32 KHMAPI` uses the same stdcall/dll decoration defined here, which is essential because plugin callbacks and import libraries are shared across binaries.

## State and Persistence Behavior

The values are compile-time contracts. `khm_handle` values represent runtime-owned objects in other subsystems but this header intentionally hides structure layout. `khm_version` is used for compatibility checks, including `khm_get_lib_version()` in `khuidefs.h` and plugin/module compatibility in `kmm.h`/`kplugin.h`.

## Dependencies and Integration Points

`khdefs.h` includes standard C headers `<stddef.h>`, `<limits.h>`, and `<wchar.h>`. Every listed header directly or indirectly depends on it. It assumes Microsoft C integer spelling (`__int32`, `_W64`, `__declspec`) and Windows build macros; non-Windows builds trigger an error for parameter-width types.

## Risks and Edge Cases

- `KHM_UINT32_MAX` lacks an unsigned suffix; comparisons in strict code should avoid signed conversion surprises.
- `IS_POW2(d)` treats zero as true by design; callers looking for positive powers must add their own nonzero check.
- `UBOUND32(d)` is documented only for positive integers and underflows for `d == 0`.
- `KHMEXP` is always `dllexport` in this snapshot; consumers may need a separate import build define or import library conventions.
- `khm_lparm` is defined as 64-bit even on `_WIN32`, which may be intentional for data transport but differs from Win32 `LPARAM` width.

## Test Signals

- Compile representative plugin and core headers for x86 and x64 to catch calling-convention and typedef drift.
- Assert fixed-width typedef sizes and `khm_version` layout in ABI tests.
- Exercise utility macros with boundary values, including zero and already aligned inputs.
- Validate exported symbols in import libraries match `KHMAPI` name decoration.
