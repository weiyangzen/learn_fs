# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acnamesp.h

Purpose: declares ACPICA namespace management interfaces for initialization, loading, parsing, walking, lookup, node allocation/deletion, object conversion, dumping, evaluation, predefined argument/return validation and repair, pathname conversion, object/data attachment, searching, and termination.

Important APIs/functions: defines namespace property, lookup, walk, package-element, and warning flags. Declares `acpi_ns_load_namespace`, `acpi_ns_load_table`, `acpi_ns_walk_namespace`, `acpi_ns_parse_table`, `acpi_ns_execute_table`, `acpi_ns_lookup`, node create/delete/remove helpers, conversion helpers, dump functions, `acpi_ns_evaluate`, predefined check/repair functions, pathname builders/internalizers/externalizers, object/data attach/get/detach functions, search/install helpers, and `acpi_ns_terminate`.

Control flow: table loading parses AML into namespace nodes; runtime evaluation resolves handles/pathnames, checks predefined arguments, invokes methods or returns objects, validates/repairs returns, and attaches operand objects to nodes. Walks support initialization, dumps, unload, and discovery.

State and persistence: state is the namespace tree, attached operand objects, owner IDs, and optional per-node data.

Dependencies and integration: depends on walk callbacks, evaluate info, predefined info, operand objects, and name/path conversion structs. It integrates parser/dispatcher table load, interpreter evaluation, predefined validation, dynamic unload, events, debugger commands, and handle/path APIs.

Risks: lookup flags are subtle around parent search, temporary nodes, external declarations, and scope opening. Dynamic unload depends on owner IDs and object lifetimes. Predefined repair must not corrupt caller-owned objects. Namespace locking must be correct during walks.

Test signals: AML namespace load, external declarations, dynamic table load/unload, path round trips, handle lookup failures, predefined validation/repair, namespace walks with unlock flags, node deletion by owner, and debugger dumps.
