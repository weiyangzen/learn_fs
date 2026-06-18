# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/msc01_pci.h

Purpose: Register offsets, field encodings, absolute address macros, and raw access helpers for the MIPS System Controller PCI host bridge.

Important APIs/types/functions: Defines offsets for ID, system-controller-to-PCI memory/I/O base/mask/map registers, PCI-to-system masks/maps, interrupt config/status, config address/data, IACK, header registers, BAR0, config, and swap control. Field macros cover hostbridge ID, mapping fields, interrupt bits, config-address bus/device/function/register fields, BAR sizing, enable bits, retry count, and endian swap modes. `_pcictrl_msc` supplies `MSC01_PCI_REG_BASE`; `MSC_WRITE` and `MSC_READ` dereference volatile `u32`.

Control flow, state, and persistence: No function bodies beyond MMIO access macros. Hardware state persists in mapping, config, interrupt, and swap registers that affect PCI enumeration and transactions.

Dependencies and integration: Used by Malta/SOC-it PCI host code, with fixed default bases `MIPS_MSC01_PCI_REG_BASE` and `MIPS_SOCITSC_PCI_REG_BASE`.

Risks and test signals: The header has suspicious aliases for `MSC01_PCI_HEAD12` through `HEAD15` all using `HEAD11_OFS`, which should be reviewed against hardware docs. Test PCI config cycles, BAR sizing, endian swap configuration, and error interrupts.
