# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmthdat.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmthdat.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmthdat.c

### Purpose
`dsmthdat.c` implements storage for AML control-method arguments and local variables. It models Args and Locals as pseudo namespace nodes so `RefOf`, `DerefOf`, and indirect stores can use normal namespace/object semantics.

### Important APIs, Types, And Functions
Public functions are `acpi_ds_method_data_init`, `acpi_ds_method_data_delete_all`, `acpi_ds_method_data_init_args`, `acpi_ds_method_data_get_node`, `acpi_ds_method_data_get_value`, and `acpi_ds_store_object_to_local`. Static helpers set and delete slot values. An obsolete type getter is conditionally compiled.

### Control Flow
Initialization fills fixed Arg and Local pseudo-nodes with names, descriptor type, flags, and type `ANY`. Argument initialization stores incoming operand pointers directly for call-by-reference semantics. Get-node validates class/index and returns a pseudo-node. Get-value reports uninitialized args/locals unless interpreter slack is enabled, in which case it installs an integer zero. Store-to-local copies shared objects when needed, handles indirect stores through Arg references created by `RefOf`, deletes existing values, and installs the new object with reference-count incrementing.

### State, Persistence, And Dependencies
All state lives in the current `struct acpi_walk_state`: `arguments[]` and `local_variables[]` pseudo-nodes plus attached objects. Reference counts are incremented on install and decremented on delete/detach. The module depends on namespace attach/detach helpers, object copying, interpreter store-to-node, and global interpreter-slack policy.

### Integration Points
`dsmethod.c` initializes and deletes method frames. `dsobject.c` creates local/arg reference objects using `acpi_ds_method_data_get_node`. `dbmethod.c` mutates live locals/args through `acpi_ds_store_object_to_local`.

### Risks
Call-by-reference means argument storage can alias caller-owned objects. Indirect Arg stores are subtle and intentionally differ from Local stores. Shared objects must be copied before overwrite, or unrelated references observe unintended mutation. Slack-mode zero initialization can hide firmware bugs.

### Test Signals
Signals include valid pseudo-node names/flags for all Args/Locals, correct uninitialized Arg/Local errors without slack, zero-object creation with slack, reference counts balanced across set/delete/all-delete, indirect `Store(..., ArgX)` through `RefOf` updating the target node, and Local overwrite not performing automatic dereference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsmthdat.c -->
