## sources/distributed-fs/ceph-client/drivers/acpi/resource.c

### Purpose
`resource.c` translates ACPI resource descriptors from methods such as `_CRS` and `_DMA` into Linux `struct resource` lists. It handles memory, I/O, address windows, IRQs, DMA filtering, resource consumers, and platform-specific IRQ override quirks.

### Important APIs, Types, And Functions
Exports include `acpi_dev_resource_memory()`, `acpi_dev_resource_io()`, `acpi_dev_resource_address_space()`, `acpi_dev_resource_ext_address_space()`, `acpi_dev_irq_flags()`, `acpi_dev_get_irq_type()`, `acpi_dev_resource_interrupt()`, `acpi_dev_get_resources()`, `acpi_dev_get_dma_resources()`, `acpi_dev_get_memory_resources()`, `acpi_dev_filter_resource_type()`, `acpi_dev_free_resource_list()`, and `acpi_resource_consumer()`.

### Control Flow
Memory and I/O helpers identify descriptor types, compute start/end ranges, validate length and architecture constraints, and set Linux resource flags. Address-space decoding applies producer translation offsets, detects CPU-address truncation, marks windows, and handles memory/I/O/bus ranges. IRQ decoding converts ACPI trigger/polarity/share/wake fields, applies x86 and DMI override policy for legacy IRQ descriptors, registers GSIs, and marks failed mappings disabled. `acpi_dev_get_resources()` walks `_CRS`, optionally lets callers preprocess each ACPI resource, converts recognized descriptors to `resource_entry` objects, and returns a count. DMA and memory helpers are filters over the same walker.

### State, Persistence, And Dependencies
State is mostly transient resource lists allocated for callers. Static DMI tables encode IRQ override quirks for known machines. Dependencies include ACPICA resource walking, Linux resource lists, IRQ/GSI registration, DMI, architecture IRQ override data, and x86 CPU-feature checks.

### Integration Points
ACPI-enumerated platform, PCI, serial, GPIO, I2C, SPI, and other drivers use these helpers to obtain resources. `acpi_resource_consumer()` scans the ACPI namespace to find which device consumes a given resource.

### Risks
Firmware often reports invalid lengths or IRQ polarity; the code contains compatibility behavior and DMI exceptions. Legacy IRQ overrides differ from extended IRQ descriptors. Resource-window arithmetic can overflow smaller `resource_size_t` architectures and is rejected. Callers must pass an empty list and free it. GSI registration failures still produce a disabled resource entry.

### Test Signals
Exercise all memory/I/O descriptor forms, address16/32/64 and extended address spaces, producer windows with translation offsets, invalid/unassigned resources, x86 I/O range limits, IRQ and extended IRQ descriptors, DMI override systems, `_DMA` filtering, preprocessor skip/abort paths, and resource-consumer namespace scans.
