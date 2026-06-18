## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qtn_hw_ids.h

### Purpose
`qtn_hw_ids.h` centralizes Quantenna PCI identifiers, chip ID masks, control-register offsets, and firmware image names for qtnfmac PCI hardware.

### Important APIs, Types, And Functions
It defines `PCIE_VENDOR_ID_QUANTENNA`, `PCIE_DEVICE_ID_QSR`, chip ID constants for Topaz and Pearl revisions, firmware file names for PCI Pearl/Topaz, and `qtnf_chip_id_get()`, which reads `QTN_REG_SYS_CTRL_CSR` and masks `QTN_CHIP_ID_MASK`.

### Control Flow
PCI probe code can match vendor/device IDs, map the device registers, call `qtnf_chip_id_get()` to classify the chipset, and choose firmware names and driver behavior based on the returned chip family.

### State, Persistence, And Dependencies
There is no local state. The only persistent contract is the register layout and firmware pathname expected by request-firmware paths. It depends on PCI ID definitions, MMIO `readl()`, and the caller passing a valid mapped register base.

### Integration Points
PCI bus code and utility stringification use the chip IDs. Firmware loading and board-specific setup depend on these constants to select the right image.

### Risks
Bad register mapping or unsupported chip IDs lead to unknown classification. Firmware names are ABI-like user-space paths under `/lib/firmware`, so renames break loading. New hardware revisions require updates to both ID constants and user-facing string conversion.

### Test Signals
Validate PCI ID matching, register reads on supported boards, firmware image selection for Topaz and Pearl variants, unknown-chip logging, and request-firmware failures for missing images.
