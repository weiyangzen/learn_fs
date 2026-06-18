# sources/distributed-fs/ceph-client/drivers/acpi/viot.c

### Purpose
`viot.c` implements support for the ACPI Virtual I/O Translation Table. It maps PCI and MMIO endpoints to para-virtual virtio-iommu nodes so DMA configuration can attach endpoints to the correct IOMMU before device drivers probe.

### Important APIs, Types, And Functions
Key types are `struct viot_iommu` and `struct viot_endpoint`. Initialization APIs are `acpi_viot_early_init()` and `acpi_viot_init()`. Runtime configuration enters through `viot_iommu_configure(struct device *dev)`, which dispatches to PCI alias handling or MMIO platform-device matching. Helpers include `viot_check_bounds()`, `viot_get_iommu()`, `viot_parse_node()`, and `viot_dev_iommu_init()`.

### Control Flow
Early init checks for a VIOT table and requests PCI ACS before bus scan. Main init fetches the table, iterates `node_count` nodes from `node_offset`, validates bounds and length, interns virtio-iommu nodes, and records endpoint ranges. During `dma_configure()`, PCI devices iterate DMA aliases against VIOT PCI ranges and calculate endpoint IDs from segment/BDF offsets; platform devices match their first MMIO resource base. Successful matches call `acpi_iommu_fwspec_init()`.

### State, Persistence, And Dependencies
Global state includes the ACPI table pointer and three lists: IOMMU nodes, PCI ranges, and MMIO endpoints. The table memory is obtained from ACPI; endpoint/IOMMU records are heap allocated and retained for the life of the boot. Dependencies include ACPI VIOT structs, PCI lookup, ACPI resource consumers, fwnode allocation, virtio-iommu configuration, and the IOMMU core.

### Integration Points
The file plugs into ACPI table initialization and generic DMA setup. It bridges firmware topology to `iommu_fwspec`, supports PCI aliases, and uses device fwnodes to identify virtio-iommu providers even when PCI IOMMU devices lack ACPI nodes.

### Risks
Malformed table bounds, short node lengths, stale output-node offsets, missing provider devices, or incorrect endpoint ID arithmetic can prevent endpoint probing or attach devices to the wrong IOMMU. `acpi_viot_init()` returns early on parse errors without freeing prior allocations, acceptable during init but important for fault interpretation.

### Test Signals
Test by booting with valid/invalid VIOT tables, confirming ACS request before PCI scan, verifying probe deferral until virtio-iommu exists, checking PCI alias endpoint IDs, MMIO resource matching, and DMA mappings flowing through virtio-iommu ops.
