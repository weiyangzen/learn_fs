<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsobject.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsobject.c

## Purpose
Manages objects and caller data attached to namespace nodes. It attaches/detaches operand objects, retrieves primary/secondary objects, and stores opaque handler-keyed data objects.

## Important APIs, Types, And Functions
Provides `acpi_ns_attach_object`, `acpi_ns_detach_object`, `acpi_ns_get_attached_object`, `acpi_ns_get_secondary_object`, `acpi_ns_attach_data`, `acpi_ns_detach_data`, and `acpi_ns_get_attached_data`. It uses operand descriptor lists, node object pointers, node types, region address-range registration, and local data objects.

## Control Flow
Attach validates node/object parameters, resolves namespace-node inputs to their attached object, detaches any existing non-data object, increments the new object's reference count, chains multi-descriptor objects before data objects, updates node type, and stores the object. Detach ignores pure data lists, frees allocated method AML buffers when flagged, removes operation-region address ranges, unlinks primary/secondary descriptors while preserving data attachments, resets node type, and drops the object reference. Data attach scans for duplicate handlers, creates a local-data object, and appends it; detach and get scan the linked list by handler.

## State And Persistence
Mutates namespace node object pointers and types, operand reference counts, local data attachment lists, allocated method AML buffers, and global region address-range tracking.

## Dependencies And Integration Points
Used throughout namespace load, evaluation, deletion, and driver data attachment APIs. Depends on object allocation/reference utilities and region address range helpers.

## Risks And Edge Cases
Reference count ownership is subtle when attaching an object already referenced elsewhere. Multi-descriptor objects and data attachments share the same `next_object` chain, so detach must preserve data nodes. Region detach must unregister address ranges to avoid stale handlers.

## Test Signals
Attach/detach integers, methods with allocated AML, regions, data-only nodes, duplicate data handlers, secondary descriptor objects, namespace-node aliases as attach sources, and reference count/leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsobject.c -->
