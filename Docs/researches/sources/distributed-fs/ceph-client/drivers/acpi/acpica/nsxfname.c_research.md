# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsxfname.c

## Purpose
`nsxfname.c` provides public namespace name-oriented APIs: path-to-handle lookup, handle-to-name conversion, object/device information collection, and dynamic installation of a single control method from a DSDT/SSDT buffer.

## Important APIs, types, and functions
Exports include `acpi_get_handle()`, `acpi_get_name()`, `acpi_get_object_info()`, and `acpi_install_method()`. `acpi_ns_copy_device_id()` is a local helper that packs variable-length PNP ID strings into an allocated `struct acpi_device_info` buffer. The file uses `struct acpi_pnp_device_id`, `struct acpi_pnp_device_id_list`, `struct acpi_device_info`, `struct acpi_table_header`, parser state, namespace nodes, and method operand objects.

## Control flow
`acpi_get_handle()` validates output and path parameters, converts an optional parent handle to a prefix node, accepts fully qualified names without a parent, rejects relative names without a parent, special-cases the root path, then calls `acpi_ns_get_node()` with no upsearch. `acpi_get_name()` validates buffer and name type, locks the namespace, and calls either full-path or single-name conversion.

`acpi_get_object_info()` locks only long enough to validate the handle and snapshot node type/name/parameter count. For devices and processors it then executes selected simple methods (`_HID`, `_UID`, `_CID`, `_CLS`, `_ADR`, `_SxW`, `_SxD`) and uses success to size and populate one allocated `acpi_device_info` buffer. HID/CID values are also checked for PCI root bridge classification. `acpi_install_method()` validates a DSDT/SSDT buffer containing a MethodOp, parses the method namestring/package length/flags from raw AML, preallocates an AML copy and method object, creates or finds a method node, initializes method metadata, attaches the new object, and marks the node buffer as dynamically allocated.

## State and persistence behavior
Handle/name functions are read-only. `acpi_get_object_info()` allocates a caller-owned information buffer and frees temporary ID buffers before return. `acpi_install_method()` persists a new or replacement method object in the namespace and stores copied AML that must later be freed because `ANOBJ_ALLOCATED_BUFFER` is set.

## Dependencies and integration points
The file depends on namespace lookup and validation helpers, path conversion helpers, parser helpers (`acpi_ps_peek_opcode`, `acpi_ps_get_opcode_size`, `acpi_ps_get_next_package_end`, `acpi_ps_get_next_namestring`), namespace attachment, object construction, simple predefined-method execution, and exported ACPI symbols used by kernel drivers.

## Risks and edge cases
`acpi_get_object_info()` intentionally avoids complex methods such as `_SUB` and `_STA` because discovery-time evaluation can touch operation regions. Size calculation must match the later packed-copy layout for HID/UID/CID/CLS strings. `acpi_install_method()` assumes the input table contains exactly the expected single MethodOp shape and that raw AML package parsing cannot run past the buffer. Replacing an existing method must not leak the old attached method object.

## Test signals
Signals include fully qualified and parent-relative `acpi_get_handle()` lookups, root path lookup, invalid relative lookup, name buffer sizing, device info with each optional ID/method present or absent, PCI root bridge flag detection through HID and CID, method parameter count reporting, invalid table signatures, non-method AML rejection, existing non-method node rejection, and successful replacement of an existing method.
