# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpidebug.h

## Purpose

`hpidebug.h` defines HPI debug levels, logging/assertion macros, debug function declarations, and a fallback compile-time assertion macro.

## Important APIs, types, and functions

The debug-level enum spans error, warning, notice, info, debug, and verbose. `HPI_DEBUG_LEVEL_DEFAULT` is notice. `FILE_LINE` is built from `SOURCEFILE_NAME` and `__LINE__` when the source defines a name. `HPI_DEBUG_ASSERT()` emits a kernel error if an expression is false. `HPI_DEBUG_LOG(level, ...)`, `HPI_DEBUG_DATA()`, `HPI_DEBUG_MESSAGE()`, and `HPI_DEBUG_RESPONSE()` filter against the global `hpi_debug_level` and use per-level kernel log flags. The header declares `hpi_debug_init()`, `hpi_debug_level_set()`, `hpi_debug_level_get()`, `hpi_debug_message()`, `hpi_debug_data()`, and extern `hpi_debug_level`.

## Control flow

The macros expand into conditional `do { ... } while (0)` blocks. Runtime control is a simple threshold check: messages at or below the current debug level print, with response logging also printing errors at debug level.

## State and persistence behavior

The header owns no storage except through the extern debug-level declaration. Its macros embed file/line strings at compile time and influence all call sites that include it.

## Dependencies and integration points

It includes `hpi_internal.h` for message/response types and uses kernel logging symbols plus `HPI_DEBUG_FLAG_*` definitions expected from OS-specific integration. It is included by the backend, common, and firmware-loader files.

## Risks and test signals

Risks include compile failures if `HPI_DEBUG_FLAG_*` macros are missing, log format drift, assertions that log but do not stop execution, verbose log flooding, and duplicate `compile_time_assert` definitions. Test signals include builds with and without `SOURCEFILE_NAME`, runtime level changes, error-path logging, response logging for DSP errors, and verbose data/message dumps.
