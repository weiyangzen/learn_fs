# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherror.h

## Purpose

`kherror.h` defines the common NetIDMgr integer error-code space and success/failure predicates. It is the lightweight return-code companion to the richer contextual reporting in `kherr.h`.

## Important APIs, Types, and Functions

- `KHM_ERROR_BASE` is `0x40000000L`; NetIDMgr-specific failures occupy `KHM_ERROR_BASE` through `KHM_ERROR_BASE + KHM_ERROR_RANGE`.
- `KHM_ERROR_RANGE` is 256.
- `KHM_ERROR_NONE` and `KHM_ERROR_SUCCESS` are both zero.
- Defined errors cover invalid name, too long/insufficient buffer, invalid parameter, duplicate, not found, not ready, no resources, type mismatch, already exists, timeout, exit, unknown/general, out of bounds, deleted, invalid operation, invalid signature, not implemented, equivalent, no provider, partial success, and incompatible.
- `KHM_SUCCEEDED(rv)` tests equality with success, and `KHM_FAILED(rv)` tests nonzero.

## Control Flow

APIs throughout NetIDMgr return `khm_int32` values from this space. A zero return continues normal flow. Nonzero values are treated as failures, with `KHM_ERROR_PARTIAL` representing a completed operation with some subscriber or component errors. `KHM_ERROR_EXIT` is also used by KMQ dispatch loops to signal thread quit messages.

## State and Persistence Behavior

The header has no runtime state. Error codes can be persisted in configuration or failure-count records, such as KMM module/plugin failure reasons. They are also often paired with a `kherr` context for user-visible diagnostics.

## Dependencies and Integration Points

It is included directly by `kplugin.h` and indirectly by `khuidefs.h`. It is referenced broadly by `kconfig.h`, `kcreddb.h`, `kmq.h`, `kmm.h`, `khconfigui.h`, and plugin callbacks as the common return-code vocabulary.

## Risks and Edge Cases

- Success is exactly zero; any warning-like nonzero value is a failure to `KHM_FAILED()`.
- The range is small and manually allocated. New error codes must not collide or exceed the documented range without auditing callers.
- `KHM_ERROR_PARTIAL` is nonzero, so callers that only check `KHM_FAILED()` will treat partial success as hard failure.
- The values are not HRESULTs even though the high bit pattern resembles Windows-style codes; callers should not pass them to HRESULT-only APIs without conversion.

## Test Signals

- Compile all public headers and assert each documented code is unique.
- Unit-test APIs that intentionally return `KHM_ERROR_TOO_LONG` with required-size out parameters.
- Verify KMQ synchronous calls return `KHM_ERROR_PARTIAL` when any subscriber fails.
- Confirm module/plugin failure records store and display these codes correctly.
