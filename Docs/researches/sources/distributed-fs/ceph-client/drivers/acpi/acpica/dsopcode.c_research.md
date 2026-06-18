# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsopcode.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsopcode.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsopcode.c

### Purpose
`dsopcode.c` evaluates operands for region, table-region, buffer-field, data-object, and bank-field opcodes after parse nodes and namespace objects already exist. It turns deferred operand expressions into concrete addresses, lengths, buffers, packages, and field parameters.

### Important APIs, Types, And Functions
Entry points include `acpi_ds_initialize_region`, `acpi_ds_eval_buffer_field_operands`, `acpi_ds_eval_region_operands`, `acpi_ds_eval_table_region_operands`, `acpi_ds_eval_data_object_operands`, and `acpi_ds_eval_bank_field_operands`. Static `acpi_ds_init_buffer_field` performs common buffer-field setup.

### Control Flow
Buffer-field evaluation creates operands from the create-field parse args, resolves them, retrieves the attached buffer-field object, computes bit offset/count based on create opcode, validates target buffer size, prepares common field metadata, links the host buffer, adjusts reference count inheritance, and marks the field data-valid. Region evaluation resolves address/length operands, stores them on the region object, warns for zero-length predefined spaces, registers the address range, and marks data-valid. Table-region evaluation resolves signature/OEM strings, finds the matching ACPI table, stores its physical address/length/pointer, and marks valid. Data-object evaluation resolves length then builds buffer or package objects. Bank-field evaluation resolves the bank value and stores it into every named bank-field object in the field list.

### State, Persistence, And Dependencies
The file persists object fields: buffer-field common metadata and buffer link, operation-region address/length/pointer, data-valid flags, package/buffer payloads, and bank-field selector values. It removes operand references after use. Dependencies include operand creation/resolution, field preparation, table lookup, event region initialization, namespace attachment, and address-range tracking.

### Integration Points
`dsargs.c` triggers deferred evaluation using saved AML spans. `dsfield.c` creates field objects and parse-node node pointers consumed here. `dsobject.c` builds data object descriptors. Event code initializes operation regions.

### Risks
Bounds checking is essential for buffer fields; overflow or wrong unit conversion can expose memory outside the buffer. Region address/length evaluation can register invalid firmware ranges. Table-region lookup depends on exact string operands. Reference cleanup must match operand stack ownership, especially on failure paths.

### Test Signals
Signals include buffer-field creation failing on non-buffer targets and out-of-bounds bit ranges, all create-field opcode widths producing correct bit counts, operation regions receiving correct address/length and data-valid flag, table regions pointing at the selected ACPI table, buffer/package objects materialized from deferred AML, and bank fields receiving evaluated bank values across all named fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dsopcode.c -->
