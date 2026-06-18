# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbnames.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbnames.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbnames.c

### Purpose
`dbnames.c` implements AML debugger commands for inspecting and validating the ACPI namespace. It changes the debugger current scope, dumps namespace subtrees and full paths, searches names with wildcard support, reports object counts and field values, checks predefined-name compliance, performs namespace integrity checks, finds direct references, and reports bus/device information around `_PRT` providers.

### Important APIs, Types, And Functions
Entry points include `acpi_db_set_scope`, `acpi_db_dump_namespace`, `acpi_db_dump_namespace_paths`, `acpi_db_dump_namespace_by_owner`, `acpi_db_find_name_in_namespace`, `acpi_db_check_predefined_names`, `acpi_db_display_objects`, `acpi_db_display_fields`, `acpi_db_check_integrity`, `acpi_db_find_references`, and `acpi_db_get_bus_info`. Static walk callbacks implement matching, predefined-name validation, object counting, field display, integrity validation, reference finding, and bus reporting.

### Control Flow
Most commands normalize or resolve an input path, then call `acpi_walk_namespace`/`acpi_ns_dump_*` with a focused callback. Scope setting validates either root-relative or current-scope-relative paths before appending to `acpi_gbl_db_scope_buf`. Name search uppercases and pads to a four-character nameseg, supports `?` wildcards, then prints full path plus summary object data. Object display either counts all types or walks only the requested type. Field display filters region fields by address-space ID and evaluates each matching field for readable output.

### State, Persistence, And Dependencies
Persistent debugger state is limited to `acpi_gbl_db_scope_buf`, `acpi_gbl_db_scope_node`, and output redirection flags. The code reads live namespace nodes, attached objects, object info, predefined method metadata, region field descriptors, and device info returned by `acpi_get_object_info`. It depends on namespace locks handled by the walker/evaluator APIs.

### Integration Points
The file integrates with `dbutils.c` for argument matching, namestring preparation, and output routing. It uses predefined-name validation from `acpredef`, interpreter field evaluation via `acpi_evaluate_object`, and namespace dumping/integrity helpers from `acnamesp`.

### Risks
Field display and bus reporting can execute firmware objects, so debugger inspection may have side effects. Integrity and reference searches only check direct node/object relationships, not every nested subobject. Scope buffer concatenation is guarded, but a failed relative scope update leaves the prior scope intact. Field walks assume valid field object chains, so corrupt namespace state can still produce null dereference risk if invariants are already broken.

### Test Signals
Signals include correct namespace dumps from root and subtrees, wildcard name matches, predefined-name counts matching firmware contents, object-type summaries matching raw namespace walks, field display only for the requested address space, integrity checks reporting invalid descriptors/names, and bus info listing devices/processors with `_PRT` plus `_ADR`, `_HID`, `_UID`, and `_CID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbnames.c -->
