# sources/distributed-fs/ceph-client/tools/objtool/signal.c

Purpose: Installs objtool signal handling so interrupted runs can clean up or report consistently.

Important APIs/types/functions: `is_stack_overflow`, `signal_handler`, `read_stack_limit`, `init_signal_handler`.

Control flow: Initialization registers handlers for fatal/interruption signals used by the command-line tool.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Uses POSIX signal APIs and objtool process state.

Risks: Handlers must remain async-signal-safe and not corrupt partially written ELF output.

Test signals: Interrupt objtool during long analysis and verify exit status/temp-file cleanup.

Source coverage: researched from the complete local file (136 lines, 2865 bytes).
