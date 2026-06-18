# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsdebug.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsdebug.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsdebug.c

### Purpose
`dsdebug.c` provides dispatcher-side debug printing for failed method execution. It reports the exception, current method path, active method-call stack, and optionally the failed ASL statement when disassembler support is compiled in.

### Important APIs, Types, And Functions
The exported function is `acpi_ds_dump_method_stack`; under debug/debugger builds it uses static `acpi_ds_print_node_pathname`. A no-op implementation is compiled when neither debug output nor debugger support is enabled.

### Control Flow
The dump routine ignores ACPICA control exceptions and deferred opcode subtrees. It also returns when no thread state exists, such as compiler constant folding. Otherwise it prints the exception and current method path, walks `thread->walk_state_list`, stops method tracing for each method descriptor, displays the current failed opcode by temporarily severing `op->common.next`, and labels older stack entries as callers of the previous method.

### State, Persistence, And Dependencies
The function is diagnostic and only transiently modifies `op->common.next`, restoring it before returning. It depends on walk-state linkage, method descriptors, namespace pathname allocation, optional disassembler support, and tracing hooks.

### Integration Points
`dsmethod.c` calls this after method errors and before optional debugger local/argument dumps. It complements `dbobject.c` by showing call stack and failed statement rather than frame variables.

### Risks
Because it runs after errors, it must tolerate partial method state and null nodes. The temporary parse-op link modification must always be restored to avoid corrupting parse traversal. Without disassembler support, diagnostics are less specific.

### Test Signals
Useful checks are no output for control exceptions, clear stack output for nested method failures, correct path allocation/free behavior, failed opcode display when disassembler is enabled, and a no-op build result when debug output is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsdebug.c -->
