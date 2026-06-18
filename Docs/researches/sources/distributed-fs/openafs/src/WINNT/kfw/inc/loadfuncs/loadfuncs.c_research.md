# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.c

## Purpose

This file implements the generic Windows DLL dynamic loader helper used by the KFW loadfuncs headers. It provides `LoadFuncs()` to populate function-pointer variables from named exports and `UnloadFuncs()` to clear those pointers and release a DLL handle.

## Important APIs, Types, and Functions

- `UnloadFuncs(FUNC_INFO fi[], HINSTANCE h)` iterates the function table, sets every target pointer to NULL, and calls `FreeLibrary(h)` if a module handle was supplied.
- `LoadFuncs(const char *dll_name, FUNC_INFO fi[], HINSTANCE *ph, int *pindex, int cleanup, int go_on, int silent)` loads the named DLL and resolves each export listed in `fi`.
- `LoadLibrary`, `GetProcAddress`, `FreeLibrary`, and `SetErrorMode(SEM_FAILCRITICALERRORS)` are the Windows APIs used for loading and error-dialog suppression.

## Control Flow

`LoadFuncs()` initializes optional outputs (`*ph = 0`, `*pindex = -1`) and clears all pointer variables in the `FUNC_INFO` array. If `silent` is true, it temporarily changes the process error mode before `LoadLibrary()` to suppress critical-error UI. It then resolves functions in order. If `go_on` is false, lookup stops at the first missing symbol; if true, lookup continues and records any missing-symbol error. On error with `cleanup` and not `go_on`, it clears all function pointers, frees the library, and returns 0. Otherwise it stores the module handle if requested and returns 0 for any missing symbol or 1 for complete success.

`UnloadFuncs()` is simpler: clear every pointer and free the module if non-NULL.

## State and Persistence Behavior

The functions mutate caller-provided function-pointer storage. They do not keep their own registry of loaded libraries, so callers are responsible for holding `HINSTANCE` values and calling `UnloadFuncs()` at the right time. `LoadFuncs()` can leave partially populated pointer tables when `go_on` is true or when `cleanup` is false.

## Dependencies and Integration Points

Includes `<windows.h>` and `loadfuncs.h`. It is the implementation backend for all `loadfuncs-*.h` dynamic wrappers. It integrates with the process module loader and process error mode.

## Risks

- `fi` is assumed non-NULL and terminated by `END_FUNC_INFO`; a malformed table can overrun.
- `SetErrorMode` changes process-global state temporarily and is not thread-isolated.
- If `go_on` is true, the function can return failure while still leaving successfully resolved pointers and a loaded module handle.
- If `cleanup` is false and a required symbol is missing, callers must understand that partial pointer state remains.
- Function pointer variables are not synchronized; concurrent load/unload around active calls can race.

## Test Signals

Unit tests can load a known system DLL with known exports, verify `pindex`, success status, and pointer population, then unload and confirm pointers are cleared. Negative tests should cover missing DLL, missing export with `cleanup` true/false, `go_on` true/false, and `silent` behavior.
