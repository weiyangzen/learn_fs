# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbinput.c

## Purpose
Implements the front end for the AML debugger: command tables, help text, tokenization, command matching, dispatch, command history integration, interactive command loop, and the debugger command execution thread.

## Important APIs And Functions
`enum acpi_ex_debugger_commands`, `acpi_gbl_db_commands[]`, and `acpi_gbl_db_command_help[]` define command names, minimum argument counts, and help output. `acpi_db_get_next_token` tokenizes integers, quoted strings, buffers `(...)`, field units `{...}`, and nested packages `[...]`, returning an ACPI object type for later conversion. `acpi_db_get_line` copies input into the parsed buffer, extracts up to `ACPI_DEBUGGER_MAX_ARGS`, and uppercases the command. `acpi_db_match_command` supports prefix matching against the command table. `acpi_db_command_dispatch` validates argument count, adds history, and routes each command to the corresponding debugger subsystem. `acpi_db_execute_thread` and `acpi_db_user_commands` run the interactive loop using OS command-ready/complete callbacks.

## Control Flow, State, And Persistence
Input dispatch flow is copy line, tokenize in place by inserting NUL terminators, uppercase command, match prefix, optionally record history, validate minimum args, switch on command ID, return an ACPICA control status. Single-step commands return `AE_OK` to resume execution or `AE_CTRL_TERMINATE` to stop. The user loop runs until `acpi_gbl_db_terminate_loop`, resetting method-execution and step-to-call flags before each command and notifying the OS layer when complete.

## Dependencies And Integration Points
This is the hub for debugger modules: namespace displays, object dumps, method execution, resource displays, statistics, tracing, file I/O, table load/unload, hardware simulation, predefined-name tests, and history. Build flags gate application-only commands and disassembler-dependent commands. It depends on global debugger buffers/argument arrays, OS command synchronization hooks, and status codes used by the AML interpreter single-step loop.

## Risks And Test Signals
Prefix matching can make ambiguous abbreviations order-dependent. Tokenization mutates the parsed buffer and does not report unmatched quote/paren/bracket errors explicitly, so later conversion may see malformed tokens. Several commands assume optional args may be NULL, while minimum-argument validation only checks required counts. Test signals include help output, abbreviated command matching, nested package argument parsing, history recall dispatch, single-step commands during method execution, application-only commands, command loop termination, and malformed input fuzzing.
