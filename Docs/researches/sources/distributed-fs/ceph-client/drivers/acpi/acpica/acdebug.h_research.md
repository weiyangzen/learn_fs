# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdebug.h

Purpose: declares ACPICA AML debugger command, conversion, namespace, method-execution, display, file I/O, history, statistics, and utility interfaces.

Important APIs/types/functions: defines debugger buffer size, command/help/argument structs, execution walk state, and stepping flags. Declarations cover single-step and breakpoints, table display/unload, notify injection, locks/resources/GPE/handler display, object conversions, method breakpoints and locals/args mutation, namespace dumps/searches, method execution threads, debug table/file loading, command history, object dumps, statistics, output redirection, namespace lookup, and interrupt generation.

Control flow: debugger input is tokenized and dispatched to command handlers, which can inspect/mutate namespace state, execute AML methods, display objects, load/unload tables, or spawn execution threads. Conditional macros provide stubs in non-debugger or reduced-hardware builds.

State and persistence: uses debugger globals from `acglobal.h`, walk states, parse objects, namespace nodes, tables, output files, and history buffers. The header owns declarations only.

Dependencies and integration: includes disassembler declarations when `ACPI_DISASSEMBLER` is enabled and integrates debugger code with interpreter, namespace, event/GPE, table, and disassembler subsystems.

Risks: debugger commands are powerful and can mutate method data, inject events, or load tables. Conditional stubs must match signatures. Display paths must tolerate partially invalid state during failure debugging.

Test signals: debugger-enabled builds, command parser coverage, single-step method execution, namespace/object display, table load/unload, GPE/SCI generation on hardware builds, and output redirection/history behavior.
