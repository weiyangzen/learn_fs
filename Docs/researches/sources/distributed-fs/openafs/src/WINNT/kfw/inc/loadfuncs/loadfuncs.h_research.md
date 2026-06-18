# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.h

## Purpose

This header defines the small dynamic-loader abstraction shared by the KFW loadfuncs wrappers. It describes how named DLL exports map to caller-owned function-pointer variables and declares the loader/unloader functions implemented in `loadfuncs.c`.

## Important APIs, Types, and Functions

- `FUNC_INFO` contains `void **func_ptr_var` and `char *func_name`, pairing storage for a function pointer with the export name to resolve.
- `DECL_FUNC_PTR(x)` declares a function pointer variable named `p<x>` using typedef `FP_<x>`.
- `MAKE_FUNC_INFO(x)` creates a `FUNC_INFO` entry for variable `p<x>` and export name `x`.
- `END_FUNC_INFO` terminates a `FUNC_INFO` array.
- `TYPEDEF_FUNC(ret, call, name, args)` defines function pointer type `FP_<name>`.
- `LoadFuncs()` and `UnloadFuncs()` are declared for runtime loading and cleanup.

## Control Flow

Consumer headers use `TYPEDEF_FUNC` to declare pointer types for each external symbol. Consumer source files use `DECL_FUNC_PTR` to define storage and `MAKE_FUNC_INFO` rows to form a NULL-terminated table. `LoadFuncs()` populates the table, and `UnloadFuncs()` clears it.

## State and Persistence Behavior

This header does not store state. It standardizes process-global or module-global pointer variables in consumers and an external DLL handle passed to the loader/unloader. Loaded state persists until the caller invokes `UnloadFuncs()` or the process exits.

## Dependencies and Integration Points

Includes `<windows.h>` and wraps declarations in `extern "C"` for C++ compatibility. It is used by KRB4, KRB5, KRB524, Leash, LSA, profile, and wshelper dynamic-binding headers.

## Risks

- `char *func_name` is not `const char *`, although macro-generated names are string literals.
- The macros assume a strict naming convention (`FP_name` and `pname`), which makes generated declarations easy to misuse if a symbol is renamed.
- Storing function pointers through `void **` is common for this Windows pattern but not strictly portable C.
- The API leaves thread-safety and lifetime discipline to callers.

## Test Signals

Compile tests should instantiate a small typedef/pointer/table using all macros. Runtime tests belong with `loadfuncs.c` and should verify pointer clearing and export lookup behavior.
