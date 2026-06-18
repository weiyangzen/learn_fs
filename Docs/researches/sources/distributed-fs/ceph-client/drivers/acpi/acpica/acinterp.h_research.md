# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acinterp.h

Purpose: declares ACPICA AML interpreter/executor interfaces for operand conversion, debug tracing, field I/O, object creation, dynamic table loading, mutex/event/system operations, opcode execution, operand resolution, object storage/copying, interpreter locking, default operation-region handlers, and debug dumps.

Important APIs/functions: includes `acpi_ex_convert_to_*`, `acpi_ex_read_data_from_field`, `acpi_ex_write_data_to_field`, region access, concatenate/logical/math helpers, object creation for Mutex/Processor/Power/Region/Event/Alias/Method, load/unload table operations, mutex acquire/release, serial bus/GPIO field access, OS service wrappers, `acpi_ex_opcode_*` groups, operand resolve/store/copy helpers, interpreter enter/exit, global-lock helpers, ID/string conversions, space-ID validation, and default region handlers.

Control flow: dispatcher code resolves operands, dispatches opcode handlers, converts values to target types, performs field/region access, stores results, and calls OS services for Notify/Sleep/Stall/events/synchronization. Region handlers route AML reads/writes to memory, I/O, PCI config, CMOS, PCI BAR, EC, SMBus, or data table backends.

State and persistence: interpreter state is in walk states, operand objects, namespace nodes, method/thread state, mutex lists, fields, regions, and global interpreter locks.

Dependencies and integration: depends on operand objects, parse objects, namespace nodes, ACPI types, and OS synchronization. It is the executor side of the parser/dispatcher/interpreter pipeline.

Risks: implicit conversion/store rules are compatibility-sensitive. Field I/O must preserve update rules, widths, alignment, and locking. Mutex acquisition must honor sync levels and release on errors. Default region handlers are hardware-facing and need strict validation.

Test signals: conversions, arithmetic/logical opcodes, stores to fields/indexes/buffers/nodes, packages/buffers/strings, dynamic table load/unload, mutex/event methods, Notify, Sleep/Stall, region I/O, GPIO/serial fields, and method error unwinding.
