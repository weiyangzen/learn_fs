# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.h

Purpose: defines the 88SE64xx hardware register map, PCI config offsets, vendor-specific phy registers, bit fields, scatter-gather limits, PRD layout, and SPI register constants used by `mv_64xx.c` and generic register helpers.

Important APIs/types/functions: `MAX_LINK_RATE` is 3.0 Gb/s. `enum hw_registers` names BAR4 enhanced-mode registers including global control, port control/status, command list, RX FIS, TX/RX rings, interrupt masks/status, per-port serial control, command indirect registers, config ports, and VSR ports. `enum pci_cfg_registers`, `enum sas_sata_vsp_regs`, and `enum chip_register_bits` describe PCI and phy programming. `struct mvs_prd` is a 64-bit address plus length descriptor. SPI constants select peripheral EEPROM access.

Control flow: no direct execution. Values are consumed by `mv_chips.h` inline accessors and `mv_64xx.c` initialization, interrupt, PRD, SPI, and phy-control paths.

State and persistence: describes runtime hardware registers only. SPI constants may be used for EEPROM reads/writes by common code, but this header itself stores no state.

Dependencies and integration points: includes `linux/types.h` and relies on shared bit definitions from `mv_defs.h` for many control bits. Included before `mv_chips.h` so generic helpers bind to this chip's offsets and PRD layout.

Risks and test signals: wrong offsets or bit masks can cause silent hardware malfunction. Compile tests catch structure visibility; hardware tests should verify MMIO access, PRD DMA, SPI command execution, link-rate reporting, and 64xx-specific interrupt paths.
