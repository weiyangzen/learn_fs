# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsobject.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsobject.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsobject.c

### Purpose
`dsobject.c` translates parser ops into compact ACPICA operand objects and attaches them to namespace nodes. It handles constants, literals, strings, deferred buffers/packages, namespace references, method arguments/locals, and named object creation.

### Important APIs, Types, And Functions
Entry points are `acpi_ds_build_internal_object`, `acpi_ds_build_internal_buffer_obj`, `acpi_ds_create_node`, and `acpi_ds_init_object_from_op`. Key types include `union acpi_parse_object`, `union acpi_operand_object`, `struct acpi_walk_state`, opcode metadata, namespace nodes, and method pseudo-nodes.

### Control Flow
For namepath ops, object building reuses a resolved node, resolves it immediately unless it is a package element, or records unresolved package references for later resolution. It creates an object based on opcode object type and initializes it from opcode-specific data. Buffer creation chooses the larger of declared length and byte-list initializer length, allocates zeroed storage, copies byte-list data, and marks the buffer data-valid. Named node creation builds the first argument object, retypes the namespace node, attaches the object, and drops the local reference.

### State, Persistence, And Dependencies
The file persists object payloads and node attachments. Buffers/packages store node backpointers and deferred AML ranges. Strings point into the ACPI table and are marked static. Integer constants are marked `AOPOBJ_AML_CONSTANT`, with table-width truncation for 32-bit AML. Local/Arg references store pseudo-node pointers.

### Integration Points
`dsopcode.c` completes deferred data objects. `dsargs.c` evaluates deferred AML ranges. `dsmthdat.c` provides Local/Arg pseudo-nodes. Namespace attach/detach code owns lifetime once objects are attached.

### Risks
Package namepaths intentionally defer resolution to support forward/external references; resolving too early breaks compatibility. Static string pointers must never be freed. Buffer allocation failure must delete the object descriptor correctly. Reference objects must distinguish namespace names, debug object, Args, and Locals.

### Test Signals
Signals include correct integer values for Zero/One/Ones/Revision, 64-bit literal truncation warnings for 32-bit tables, buffer length selection from declared versus initializer lengths, package forward references marked unresolved, node type retyping on attach, and no freeing of table-backed string storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsobject.c -->
