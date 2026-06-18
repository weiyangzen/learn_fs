# sources/distributed-fs/openafs/src/WINNT/talocale/talocale.h

## Purpose

`talocale.h` is the umbrella public header for the TaLocale Windows localization helper library. It normalizes Unicode macros, includes Windows/common-control/TCHAR support, defines the string-resource table shape, includes the string/dialog/allocation sub-APIs, and declares the core module/language/resource-loading API.

## Important APIs, Types, and Functions

- Synchronizes `UNICODE` and `_UNICODE` definitions.
- Defines `STRINGTEMPLATE`, the length-prefixed string-table entry format used by Win32 `RT_STRING` resources.
- Includes `tal_string.h`, `tal_dialog.h`, and `tal_alloc.h`.
- Defines the `REALLOC` macro over `TaLocaleReallocFunction()`.
- Module priorities include highest, boosted, normal, lowest, and remove.
- Declares module management (`TaLocale_SpecifyModule`, `TaLocale_EnumModule`), locale DLL loading, language get/set/override APIs, generic resource lookup, string/dialog resource lookup, and menu/image/icon/accelerator loading wrappers.

## Control Flow

The header provides the API shape; implementations lazily initialize TaLocale state, build a module search chain, select a language, then retrieve resources in priority and language-fallback order. The `REALLOC` macro is used internally and by consumers that need growable arrays allocated through TaLocale allocation policy.

## State and Persistence

The header itself has no state. Declared APIs manage process-local module/language state and a registry-backed language override in `tal_main.cpp`.

## Dependencies and Integration Points

This is the main integration point for Win32 UI modules using localized resources. It depends on `windows.h`, `commctrl.h`, and `tchar.h`, and exports functions suitable for DLL boundaries through `EXPORTED`.

## Risks and Edge Cases

- The umbrella include order pulls in `winsock2.h` indirectly through `tal_string.h`; consumers that already included `windows.h` with older Winsock headers may see include-order conflicts in some environments.
- `REALLOC(_a,_c,_r,_i)` evaluates `_a` and `_c` by address and expects `_c` to be a `size_t`-like variable matching the target element count.
- Default arguments in exported C++ declarations require consumers to compile with compatible C++ settings.

## Test Signals

Header-level tests should compile representative Unicode/non-Unicode modules, DLL import/export configurations, and callers of each resource wrapper. Runtime signals come from `tal_main.cpp`, `tal_string.cpp`, and `tal_dialog.cpp` tests.
