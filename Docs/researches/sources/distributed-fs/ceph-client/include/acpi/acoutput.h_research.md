<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acoutput.h -->
# sources/distributed-fs/ceph-client/include/acpi/acoutput.h

## Purpose
`acoutput.h` defines ACPICA debug component IDs, debug levels, trace flags, diagnostic macros, module/function tracing macros, and compile-time stubs for builds without debug or error output. It is the diagnostic policy and call-site instrumentation header for ACPICA.

## Important APIs, types, and functions
Important layer masks include `ACPI_UTILITIES`, `ACPI_HARDWARE`, `ACPI_EVENTS`, `ACPI_TABLES`, `ACPI_NAMESPACE`, `ACPI_PARSER`, `ACPI_DISPATCHER`, `ACPI_EXECUTER`, `ACPI_RESOURCES`, and tool/driver component masks. Debug levels range from exception levels (`ACPI_LV_INIT`, `ACPI_LV_INFO`, `ACPI_LV_REPAIR`) through tracing, allocation, parse-tree, mutex/thread/I/O/interrupt, AML disassembly, and full-table verbosity. Call-site macros include `ACPI_MODULE_NAME`, `AE_INFO`, `ACPI_INFO`, `ACPI_WARNING`, `ACPI_ERROR`, `ACPI_EXCEPTION`, `ACPI_DEBUG_PRINT`, `ACPI_FUNCTION_TRACE*`, `return_ACPI_STATUS`, `return_PTR`, and dump/trace helpers.

## Control flow
In debug builds, call sites first check `acpi_dbg_level` and `acpi_dbg_layer` via `ACPI_IS_DEBUG_ENABLED()` before calling `acpi_debug_print()` or raw print variants. Function trace macros emit entry records and return macros emit exit records before returning. In non-debug builds, tracing and debug print macros compile away; error-message macros also compile away when `ACPI_NO_ERROR_MESSAGES` is defined.

## State and persistence behavior
The header itself has no storage, but it depends on ACPICA globals `acpi_dbg_level`, `acpi_dbg_layer`, and trace globals declared in `acpixf.h`. These are runtime debug settings only and do not persist across boot.

## Dependencies and integration points
`acpixf.h` declares the actual diagnostic functions and globals. OS-specific printing is ultimately implemented through OSL functions from `acpiosxf.h`. Linux ACPI debugging, dynamic debug, firmware-bug reporting, and ACPICA interpreter traces all flow through these macros.

## Risks and test signals
Risks include side effects in macro arguments, return macros hiding control flow, debug builds changing stack usage, compiled-out diagnostics masking important failures, and inconsistent component IDs causing missing or excessive logs. Test signals include builds with `ACPI_DEBUG_OUTPUT` on/off, `ACPI_NO_ERROR_MESSAGES` on/off, variadic macro and non-variadic compiler modes, runtime toggling of debug layer/level, and trace return macros preserving return values exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acoutput.h -->
