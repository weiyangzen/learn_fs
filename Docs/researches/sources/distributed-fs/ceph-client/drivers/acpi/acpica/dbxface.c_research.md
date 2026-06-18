# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbxface.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbxface.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbxface.c

### Purpose
`dbxface.c` is the external interface between the AML interpreter and the AML debugger. It initializes/terminates debugger state, manages single-step and breakpoint entry into the command loop, filters debugger handling to the configured thread, and exports debugger setup symbols.

### Important APIs, Types, And Functions
Public functions include `acpi_db_signal_break_point`, `acpi_db_single_step`, `acpi_initialize_debugger`, `acpi_terminate_debugger`, and `acpi_set_debugger_thread_id`. Static helpers are `acpi_db_start_command` and, with the disassembler, `acpi_db_get_display_op`. The code uses parse ops, walk states, debugger globals, OSL debugger hooks, and interpreter enter/exit wrappers.

### Control Flow
Breakpoint opcode handling sets `acpi_gbl_cm_single_step` for the debugger thread. `acpi_db_single_step` first handles abort requests, method/user breakpoints, opcode filtering, optional disassembly/logging, step-to-call semantics, and step-over behavior for method calls. When it must stop, it exits the interpreter, runs the command loop until dispatch no longer returns `AE_CTRL_TRUE`, then re-enters the interpreter. Initialization allocates the debugger buffer, resets scope/output options, and optionally starts a separate debugger execution thread.

### State, Persistence, And Dependencies
Persistent state includes `acpi_gbl_db_buffer`, output flags, debug levels, scope state, terminate flags, debugger thread id, single-step flags, and debugger-thread termination flags. The file depends on OSL debugger synchronization (`acpi_os_notify_command_complete`, `acpi_os_wait_command_ready`, `acpi_os_initialize_debugger`), command dispatch, disassembler support, and interpreter lock transitions.

### Integration Points
`dscontrol.c` calls `acpi_db_signal_break_point` for AML breakpoint opcodes. `dbmethod.c` writes breakpoint/step globals that `acpi_db_single_step` consumes. `acdebug` command dispatch implements the interactive commands.

### Risks
Entering the command loop while interpreter state is paused is sensitive to locking; comments note namespace locking concerns. Thread filtering is required in kernel-style builds. Step-over uses a synthetic nonzero method breakpoint and must not collide with user breakpoints. Multi-threaded debugger shutdown spins until worker threads terminate.

### Test Signals
Signals include clean initialization/termination, debugger buffer allocation/free, single-step stopping only on the configured thread, AML breakpoint opcodes producing `ACPI_SIGNAL_BREAKPOINT`, step-to-call stopping at method calls, step-over resuming after nested methods, and no interpreter lock imbalance around command dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbxface.c -->
