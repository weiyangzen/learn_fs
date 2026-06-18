## sources/distributed-fs/ceph-client/drivers/acpi/riscv/rimt.c

### Purpose
`riscv/rimt.c` implements RISC-V IOMMU Mapping Table support. It associates RIMT IOMMU nodes with Linux fwnodes and configures PCI or platform devices with ACPI IOMMU fwspecs by walking RIMT ID-mapping chains.

### Important APIs, Types, And Functions
Public hooks include `riscv_acpi_rimt_init()`, `rimt_iommu_register()`, and, under `CONFIG_IOMMU_API`, `rimt_iommu_configure_id()`. Key internals include `rimt_scan_node()`, `rimt_match_node_callback()`, `rimt_set_fwnode()`, `rimt_get_fwnode()`, `rimt_node_map_id()`, `rimt_node_map_platform_id()`, and `rimt_iommu_xlate()`.

### Control Flow
Initialization caches the RIMT table mapping for runtime use. IOMMU drivers register themselves by finding their RIMT IOMMU node via PCI segment/BDF or platform MMIO base, creating a static fwnode for PCI IOMMUs if needed, and storing the node-to-fwnode association in a locked list. Device configuration scans the RIMT for the device's PCI root complex or platform-device node, walks ID mapping entries toward an IOMMU node, translates request IDs to destination IDs, defers probing if the target IOMMU fwnode is not registered, adds a device link to enforce removal ordering, and initializes the ACPI IOMMU fwspec. PCI root-complex ATS support is propagated to the fwspec flag.

### State, Persistence, And Dependencies
State includes the cached `rimt_table` pointer and the spinlock-protected `rimt_fwnode_list`. Dependencies include ACPI RIMT table structures, PCI and platform device APIs, IOMMU fwspec helpers, device links, ACPI full-path lookup, and optional `CONFIG_IOMMU_API`.

### Integration Points
RISC-V IOMMU drivers call `rimt_iommu_register()`. ACPI/IOMMU core code calls `rimt_iommu_configure_id()` to attach devices to the correct IOMMU. `init.c` calls `riscv_acpi_rimt_init()` when enabled.

### Risks
Firmware-provided RIMT offsets and ID ranges are trusted with bounds checks limited to scan end and null-destination warnings. `rimt_id_map()` treats `source_id_base + num_ids` as inclusive, which is worth validating against the table spec. `rimt_pci_iommu_init()` maps the same PCI alias twice before translation, likely redundant. Probe deferral is expected until IOMMU drivers register fwnodes.

### Test Signals
Test absent and malformed RIMT, PCI IOMMU registration, platform IOMMU registration, PCI root-complex mapping with DMA aliases, platform devices with explicit and implicit IDs, missing IOMMU fwnode deferral, ATS flag propagation, invalid/null destination offsets, and shutdown ordering via device links.
