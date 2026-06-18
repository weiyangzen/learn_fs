# sources/distributed-fs/ceph-client/drivers/acpi/acpica/extrace.c

## Purpose
`extrace.c` implements interpreter tracing for AML methods, opcodes, and regions, including filtered and one-shot method tracing.

## Important APIs, Types, and Functions
Exports include `acpi_ex_trace_point()`, `acpi_ex_trace_args()`, `acpi_ex_start_trace_method()`, `acpi_ex_stop_trace_method()`, `acpi_ex_start_trace_opcode()`, and `acpi_ex_stop_trace_opcode()`. Local state is `acpi_gbl_trace_method_object`. Global controls include `acpi_gbl_trace_flags`, `acpi_gbl_trace_method_name`, `acpi_gbl_trace_dbg_level`, `acpi_gbl_trace_dbg_layer`, `acpi_dbg_level`, and `acpi_dbg_layer`.

## Control Flow, State, and Persistence
`acpi_ex_interpreter_trace_enabled()` checks global enable, method-name filters, active traced method object, and one-shot state. Method start obtains the normalized path, decides whether tracing is enabled, records the method object, saves original debug level/layer, installs trace debug settings, and emits a begin trace point. Method stop emits the end trace point, clears one-shot filter state when appropriate, restores original debug settings, and clears the active method object. Opcode start/stop trace only when opcode tracing is enabled. Argument tracing prints integer and string arguments to the trace stream.

## Dependencies and Integration Points
This file is used by dispatcher/executor trace hooks and by ACPICA debug output macros. It integrates namespace pathname formatting, parser opcode names, debug level/layer globals, and method argument object formatting.

## Risks and Test Signals
Risks include global debug settings not being restored after abnormal method exit, one-shot filters being cleared too early or late, NULL/empty string argument handling, nested traced method behavior, and tracing overhead when disabled. Tests should cover unfiltered, filtered, and one-shot tracing; nested methods; opcode trace flags; integer/string/empty-string arguments; method-not-found path handling; and failure paths that still call the stop hook.
