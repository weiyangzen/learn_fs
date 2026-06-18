## sources/distributed-fs/ceph-client/drivers/acpi/property.c

### Purpose
`property.c` implements ACPI device-specific properties and ACPI firmware-node operations. It parses `_DSD` property packages, non-device data subnodes, buffer properties, references, graph endpoints, child traversal, DMA metadata, and IRQ lookup through the generic `fwnode` abstraction.

### Important APIs, Types, And Functions
Key public APIs include `acpi_init_properties()`, `acpi_free_properties()`, `acpi_dev_get_property()`, `acpi_node_prop_get()`, `__acpi_node_get_property_reference()`, `is_acpi_device_node()`, and `is_acpi_data_node()`. Important internals include `acpi_extract_properties()`, `acpi_enumerate_nondev_subnodes()`, `acpi_data_get_property_array()`, `acpi_fwnode_get_reference_args()`, `acpi_data_prop_read()`, ACPI graph helpers, and the exported `acpi_device_fwnode_ops` and `acpi_data_fwnode_ops`.

### Control Flow
Initialization creates property/subnode lists, detects ACPI Device Tree namespace compatibility, evaluates `_DSD`, extracts GUID-matched property packages, converts referenced buffer properties, builds non-device subnode trees, tags namespace handles with data nodes, initializes `compatible`, and falls back to Apple property extraction if `_DSD` is unusable. Read paths search property lists by name, validate requested ACPI object types, convert integer/string/buffer arrays into generic device-property values, and resolve references either from local references or string paths. Fwnode operations expose child iteration, named child lookup, property reads, graph endpoint traversal, remote endpoint resolution, DMA attributes, and IRQ access.

### State, Persistence, And Dependencies
Parsed state is retained in `struct acpi_device_data`, `struct acpi_device_properties`, and `struct acpi_data_node` until `acpi_free_properties()`. Buffer property conversion owns separate ACPICA buffers. Dependencies include ACPICA object evaluation and handle tagging, Linux fwnode APIs, GUID helpers, ACPI graph conventions, DMA helpers, ACPI IRQ helpers, and optional Apple property support.

### Integration Points
This file lets drivers use generic firmware-property APIs with ACPI devices and data nodes, mirroring Device Tree-style property and graph access. It is used by driver core property reads, media graph consumers, GPIO/reference consumers, DMA setup, and IRQ lookup.

### Risks
Firmware package shape is complex and partially permissive across multiple equivalent GUIDs. Embedded reference packages can lose namespace scope, making string path references invalid. Lifetime management must not free ACPICA buffers while fwnode users retain references. Graph-node recognition accepts both `reg` plus `port@`/`endpoint@` and compatibility properties. Reference parsing intentionally supports holes and mixed string/reference forms.

### Test Signals
Test valid and malformed `_DSD`, multiple property GUIDs, buffer property GUID evaluation, nested data subnodes, direct and string references with arguments, holes in reference arrays, integer overflow in property reads, string-array reads, ACPI graph endpoint parsing and remote endpoints, property cleanup with tagged subnodes, and Apple fallback.
