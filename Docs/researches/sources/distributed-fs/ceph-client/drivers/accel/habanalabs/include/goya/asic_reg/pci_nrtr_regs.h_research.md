# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/pci_nrtr_regs.h

Purpose: maps the PCI north router register block to 102 MMIO offsets. The block covers HBW/LBW credit limits, debug arbiter slots, split coefficient and timeout controls, HBW/LBW address range hit/mask/base tables, regulator controls, and scrambling enable registers.

Important APIs/types/functions: no functions or structs are defined. The API is the `mmPCI_NRTR_*` macro namespace from `mmPCI_NRTR_HBW_MAX_CRED` at `0x100` through `mmPCI_NRTR_NON_LIN_SCRAMB` at `0x604`. Indexed tables include ten `SPLIT_COEF` registers, eight HBW range entries with low/high mask and base halves, and sixteen LBW range mask/base entries.

Control flow: users combine these offsets with the PCI_NRTR block base from `goya_blocks.h` or the driver configuration window, then access them through register helpers. The file itself is declarative; sequencing is imposed by callers configuring credits/ranges before enabling traffic or reading hit/status registers after traffic.

State and persistence: the header is stateless. Hardware register contents are persistent device state and may affect routing until reset.

Dependencies and integration: included by `goya_regs.h`; field definitions are in `pci_nrtr_masks.h`. It integrates with Goya host interface setup, address decoding, and PCI transaction routing even when references are indirect through aggregate headers.

Risks: offset drift is severe because routers are low-level address-decoding hardware. Indexed macro ordering must stay in lockstep with firmware/hardware tables. Some addresses are relative offsets rather than full physical MMIO addresses, so callers must use the correct base and not mix them with absolute PSOC addresses.

Test signals: compile checks against `goya_regs.h`, register read/write smoke tests, PCI BAR aperture tests, HBW/LBW DMA traffic, and negative tests that verify unsupported or unmapped windows do not produce silent routing.
