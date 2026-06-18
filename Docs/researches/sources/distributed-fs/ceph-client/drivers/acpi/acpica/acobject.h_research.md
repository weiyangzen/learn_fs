# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acobject.h

Purpose: defines `union acpi_operand_object`, ACPICA's internal descriptor for AML operands, namespace-attached objects, operation regions, fields, methods, synchronization objects, handlers, references, and cache entries.

Important APIs/types: defines common object headers/flags; integer/string/buffer/package objects; event/mutex/region/method objects; notify-capable device/power/processor/thermal objects; common field, region, bank, index, and buffer fields; notify and address-space handlers; reference objects and classes; extra/data/cache objects; descriptor-type constants; `union acpi_operand_object`; and `union acpi_descriptor`.

Control flow: interpreter code allocates operand objects, attaches them to namespace nodes, pushes them through operand/result stacks, reads/writes fields and regions, manages references, dispatches methods/handlers, and releases them through reference counting and caches. Descriptor type fields let common code distinguish object families.

State and persistence: objects can be transient operands, persistent namespace attachments, active synchronization/region/handler state, or cache-list entries. Common headers include `reference_count`; several variants link back to namespace nodes or handlers.

Dependencies and integration: used by interpreter, namespace, event, region, and handler code. Descriptor and type field positions must match `struct acpi_namespace_node`.

Risks: layout changes are high risk. String and buffer common fields must stay identical. Operand and namespace descriptor fields must align. Ownership flags and reference counts drive deletion. Handler/region lists are lifetime-sensitive during detach and table unload.

Test signals: object allocation/cache tests, reference-count leak detection, namespace attach/detach, method execution, region/field I/O, handler install/remove, package traversal, reference opcodes, table unload, and 32-bit/64-bit layout checks.
