# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmethod.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmethod.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmethod.c

### Purpose
`dsmethod.c` manages control-method lifecycle: auto-serialization scanning, method error handling, serialized method mutex acquisition, nested method invocation, restart after callee return, and teardown of method-created namespace state.

### Important APIs, Types, And Functions
Entry points include `acpi_ds_auto_serialize_method`, `acpi_ds_method_error`, `acpi_ds_begin_method_execution`, `acpi_ds_call_control_method`, `acpi_ds_restart_control_method`, and `acpi_ds_terminate_control_method`. Static helpers are `acpi_ds_detect_named_opcodes` and `acpi_ds_create_method_mutex`.

### Control Flow
Auto-serialization creates a temporary parse root/walk state, scans method AML, and marks methods serialized when named/create/field opcodes appear. Begin execution starts trace, enforces reentrancy limit, lazily creates/acquires method mutexes, checks sync level unless ignored, allocates owner IDs, and increments thread counts. Method calls validate argument counts, begin callee execution, create a nested walk state, initialize it with copied arguments, clear caller operands, and dispatch internal methods if needed. Termination deletes locals/args, removes temporary namespace objects when the last thread exits, releases method mutex depth, decrements thread count, applies pending serialization, and releases owner IDs.

### State, Persistence, And Dependencies
Persistent method state includes flags, mutex object, sync level, owner ID, thread count, AML pointers, and modified-namespace flags. Walk state carries nesting depth, method pathname, return descriptors, and thread sync level. The file depends on parser, namespace cleanup, mutex/OS wait APIs, trace hooks, and exception handler callbacks.

### Integration Points
`dsinit.c` calls auto-serialization. `dscontrol.c` creates method return descriptors. `dsmthdat.c` initializes/deletes arguments and locals. Namespace and interpreter subsystems use method owner IDs for temporary object cleanup.

### Risks
Reference, mutex, and owner-ID balancing are critical. Recursive serialized calls rely on acquisition depth. Failure paths must terminate partially started methods. Dynamic serialization after `AE_ALREADY_EXISTS` intentionally changes future behavior. Exception handlers run outside the interpreter and can remap failures.

### Test Signals
Signals include serialized methods acquiring/releasing mutexes correctly, sync-level order errors detected, nested method calls returning values to caller result stacks, temporary namespace objects deleted after method exit, owner IDs released when no threads remain, pending serialization applied only after the last active thread, and method errors invoking stack/local diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmethod.c -->
