## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utobject.c

Purpose: `utobject.c` creates, validates, deletes, and sizes ACPICA internal operand objects. It is central to converting AML/interpreter objects into external `union acpi_object` buffers for public APIs.

Important APIs and functions: `acpi_ut_create_internal_object_dbg` allocates a cached operand descriptor, creates secondary `LOCAL_EXTRA` descriptors for region/buffer-field/bank-field objects, sets the object type, and initializes the reference count. `acpi_ut_create_package_object`, `acpi_ut_create_integer_object`, `acpi_ut_create_buffer_object`, and `acpi_ut_create_string_object` allocate typed objects and backing storage. `acpi_ut_valid_internal_object`, `acpi_ut_allocate_object_desc_dbg`, and `acpi_ut_delete_object_desc` validate and manage descriptors through `acpi_gbl_operand_cache`. `acpi_ut_get_object_size` dispatches to simple or package sizing.

Control flow: object creation consistently allocates the descriptor first, then type-specific backing memory, and removes/releases the descriptor on allocation failure. Package sizing walks nested package elements with `acpi_ut_walk_package_tree`, sums rounded simple element sizes, counts package headers, and returns the external buffer length.

State and dependencies: persistent state lives in object descriptors, reference counts, `next_object` chains, package element arrays, and backing buffers. The module depends on operand descriptor caches, namespace pathname helpers for name references, and Linux kmemleak annotation.

Integration points: AML execution, namespace object attachment, public evaluation APIs, package copying, and reference-count deletion paths all rely on these constructors and size calculators.

Risks: sizing supports only specific reference classes and object types; unsupported reference classes return `AE_TYPE`. Alignment and packed string/buffer layout are deliberate, so external-object conversion code must use bytewise access where required.

Test signals: zero-length strings/buffers, package arrays with null elements, nested packages, name references requiring pathname sizing, unsupported local references, and allocation-failure cleanup paths should be exercised.
