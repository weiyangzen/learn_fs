# sources/distributed-fs/ceph-client/drivers/acpi/acpica/excreate.c

## Purpose
`excreate.c` creates named AML runtime objects: aliases, events, mutexes, operation regions, processors, power resources, and methods.

## Important APIs, Types, And Functions
Executor APIs are `acpi_ex_create_alias`, `acpi_ex_create_event`, `acpi_ex_create_mutex`, `acpi_ex_create_region`, `acpi_ex_create_processor`, `acpi_ex_create_power_resource`, and `acpi_ex_create_method`. It works with `struct acpi_walk_state`, namespace nodes, operand objects, OS semaphores/mutexes, method flags, and region secondary objects.

## Control Flow
Alias creation dereferences an alias target to avoid alias chains, then marks the alias node as method-alias or general alias pointing at the final namespace node. Event creation allocates an event object, creates an unsignaled OS semaphore, attaches it to the namespace node, and removes the local reference. Mutex creation allocates an object, creates an OS mutex, records sync level and node, attaches it, and drops the local reference. Region creation skips if an object is already attached, validates but does not fail on unknown space IDs, records AML operand location and scope in the secondary object, initializes address/length as unevaluated, clears setup/REG/initialized flags, and attaches the region. Processor, power resource, and method creation copy AML operands into typed objects and attach them to namespace nodes.

## State And Persistence
Created objects persist as namespace-attached operand objects. Region address and length are deliberately deferred until runtime and stored as AML pointers. Methods persist AML start/length, parameter count, serialization flag, and sync level. Local references are dropped after attach because namespace ownership remains.

## Dependencies And Integration Points
The file integrates parser/walk-state operands, namespace attach logic, object allocation, OS synchronization primitives, and later executor paths for region argument evaluation, method invocation, event signaling, and mutex acquisition.

## Risks
Deferred region evaluation means invalid region operands may surface much later at field access time. Invalid space IDs are logged but tolerated during table load. Semaphore/mutex creation failure paths rely on reference cleanup to delete partially created OS resources. Alias correctness depends on avoiding chains and preserving method alias type.

## Test Signals
Tests should cover alias-to-alias flattening, event initial semaphore count, mutex sync-level storage, region redefinition no-op, invalid space-id logging without load abort, scope capture for regions, serialized method flag decoding, and reference cleanup after attach failures.
