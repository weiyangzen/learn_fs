# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utdebug.c

Purpose: `utdebug.c` implements ACPICA debug printing, function trace entry/exit helpers, stack-depth tracking, and interpreter trace point forwarding when `ACPI_DEBUG_OUTPUT` is enabled.

Important APIs/types/functions: `acpi_debug_print()` and `acpi_debug_print_raw()` are exported variadic debug sinks. `acpi_ut_trace*()` helpers log function entry with optional pointer/string/u32 payloads. `acpi_ut_exit*()` helpers log function exits with status/value/pointer/string payloads. `acpi_ut_init_stack_ptr_trace()` and `acpi_ut_track_stack_ptr()` maintain stack tracking globals. `acpi_trace_point()` forwards interpreter trace points to `acpi_ex_trace_point()` and optionally `acpi_os_trace_point()`.

Control flow: Debug output first checks `ACPI_IS_DEBUG_ENABLED()` against requested level and component. `acpi_debug_print()` tracks thread ID changes, optionally prints thread/nesting metadata in application builds, trims `Acpi`/`acpi_` prefixes from function names, and formats via `acpi_os_vprintf()`. Trace entry increments nesting and tracks stack before optional logging; exit logs and decrements nesting.

State and persistence behavior: Debug-only globals include previous thread ID, nesting/deepest nesting, entry/lowest stack pointers, and debug level/layer globals. It emits logs but does not affect core ACPI behavior when debug is disabled.

Dependencies and integration points: It depends on ACPICA debug macros, OSL thread/printf/tracing hooks, interpreter trace support, and exception formatting. Many ACPICA files call these helpers through trace macros, so correctness affects observability across the subsystem.

Risks and test signals: Risks include non-thread-safe nesting display across multiple threads, compiler warnings around storing stack addresses intentionally for diagnostics, log flooding, and format-string misuse by callers. Tests should verify debug gating, thread switch messages, function-name trimming for original and linuxized symbols, nesting under balanced trace/exit macros, stack-depth updates, and system tracer forwarding.
