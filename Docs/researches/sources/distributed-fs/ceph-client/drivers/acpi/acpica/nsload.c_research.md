<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsload.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsload.c

## Purpose
Loads ACPI tables into the namespace and initializes table-owned objects. It also contains obsolete/future namespace unload helpers behind compile-time gates.

## Important APIs, Types, And Functions
Primary live API is `acpi_ns_load_table`. Gated routines include `acpi_ns_load_namespace`, `acpi_ns_delete_subtree`, and `acpi_ns_unload_namespace`. It coordinates table indices, owner IDs, namespace parse, loaded flags, and dispatcher object initialization.

## Control Flow
`acpi_ns_load_table` returns `AE_ALREADY_EXISTS` for already-loaded tables, allocates an owner ID, parses the table into the namespace, marks the table loaded on success, or deletes all namespace nodes owned by the table and releases the owner ID on parse failure. It then enters the interpreter and calls `acpi_ds_initialize_objects` to parse/initialize control methods and deferred objects. Gated legacy code loads DSDT/SSDT/PSDT by type; future unload code walks a subtree and deletes children.

## State And Persistence
Mutates table loaded flags, table owner IDs, namespace nodes and objects owned by loaded tables, and initialized method/object state. Failure paths remove partially loaded namespace content.

## Dependencies And Integration Points
Depends on table manager ownership, namespace parsing in `nsparse.c`, namespace owner deletion in `nsalloc.c`, dispatcher initialization, and interpreter locking.

## Risks And Edge Cases
Namespace collisions and missing `Scope` targets during parse are treated as severe load failures and trigger owner cleanup. The function returns `AE_ALREADY_EXISTS` for duplicate loads, which callers must treat appropriately. Partial cleanup correctness depends on accurate owner IDs.

## Test Signals
Load DSDT/SSDT-like tables, duplicate table loads, parse failures after some names are created, namespace collision cases, missing scope target cases, owner cleanup validation, and method-object initialization after successful load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsload.c -->
