# sources/distributed-fs/ceph-client/drivers/acpi/acpica/aclocal.h

Purpose: defines ACPICA internal data types and constants shared across the subsystem. It is the state-schema header for mutexes, namespace nodes, table lists, predefined-name validation, events/GPEs, parser state, AML parse objects, hardware register metadata, resource descriptors, disassembler/debugger structs, and debug memory tracking.

Important APIs/types: key types include `acpi_rw_lock`, `acpi_mutex_info`, `acpi_namespace_node`, `acpi_table_list`, `acpi_create_field_info`, predefined package-info unions, repair callbacks, GPE handler/notify/dispatch/event/register/block/interrupt structs, fixed-event structs, generic state unions, `acpi_opcode_info`, parse value/object/state structs, `acpi_bit_register_info`, `_OSI` and port validation structs, external/disassembler file lists, debugger method/integrity/object info, and debug allocation headers.

Control flow: the header models ACPICA flow through data structures. Interpreter modes distinguish load pass 1, load pass 2, and execute; generic states form parser/scope/control/thread/result/notify stacks; parse objects form AML trees; GPE dispatch unions select method, handler, or notify processing; namespace nodes form the loaded object tree.

State and persistence: namespace nodes, table lists, GPE blocks, and register metadata persist while tables/events are active. Generic states and parser states are transient and often cache-backed. The header owns no storage but defines most storage layouts.

Dependencies and integration: included through `accommon.h` by namespace, parser, dispatcher, interpreter, event, resource, table, debugger, disassembler, and compiler code.

Risks: layout is high risk: namespace descriptor fields must align with operand objects, predefined info is packed, GPE structs are memory-sensitive, and some flags have runtime versus iASL-only meanings. Changes can cascade through caches, locks, parser walks, and table unload.

Test signals: full ACPICA builds, namespace load/unload, AML parse/execute, GPE dispatch, predefined validation/repair, resource parsing, debugger/disassembler/compiler builds, memory-debug builds, and layout/alignment checks.
