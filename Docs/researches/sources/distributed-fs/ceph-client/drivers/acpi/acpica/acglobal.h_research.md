# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acglobal.h

Purpose: declares ACPICA global variables shared by table management, namespace, interpreter, hardware, event, debugger, disassembler, compiler, and application builds.

Important state declarations: root table list, DSDT/FACS/FADT indexes and pointers, FADT-derived PM/GPE addresses, integer width globals, mutex/spinlock objects, global lock state, caches, startup/shutdown flags, global handlers, owner ID masks, namespace root/predefined names, parser/interpreter globals, hardware sleep values, GPE/fixed-event globals, debug counters, dynamic tracing levels, debugger buffers/state, disassembler options, ASL converter globals, and application print/output buffers.

Control flow: no direct functions. Initialization fills these globals, runtime subsystems consume and mutate them, and termination releases them. `ACPI_GLOBAL` and `ACPI_INIT_GLOBAL` determine declaration versus definition depending on compilation context.

State and persistence: this is the central ACPICA state map; most entries persist for subsystem or tool-process lifetime.

Dependencies and integration: depends on table, namespace, operand, mutex, GPE, handler, debugger, and disassembler types. Included through `accommon.h` by nearly every ACPICA implementation file.

Risks: global state makes initialization order, locking, and teardown order critical. Misusing `ACPI_GLOBAL` can create duplicate or missing storage. Config-gated debugger/disassembler/compiler sections must not leak into normal builds.

Test signals: ACPI boot, table load/unload, namespace init, method execution, GPE dispatch, sleep/wake, debugger/disassembler/compiler builds, and subsystem shutdown/leak tests.
