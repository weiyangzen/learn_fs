<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ohci.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ohci.c

Purpose: Virtualizes the AMD CS5536 OHCI PCI function by translating 32-bit PCI config-space reads and writes into CS5536 model-specific register accesses. It lets generic PCI enumeration see OHCI as a normal PCI 2.2 device while the real state lives in USB, GLCP, GLIU, DIVIL, and southbridge MSRs.

Important APIs/types/functions: `pci_ohci_write_reg(int reg, u32 value)` handles command bits, status clearing, BAR programming, and interrupt routing. `pci_ohci_read_reg(int reg)` synthesizes vendor/device ID, command/status, class/revision, BAR sizing, subsystem IDs, ROM/capability pointers, interrupt line, and a CS5536-specific interrupt-enable register.

Control flow: Writes switch on config dword offset. `PCI_COMMAND` mirrors bus-master and memory-enable bits into `USB_MSR_REG(USB_OHCI)` high bits. `PCI_BAR0_REG` either returns range sizing via `SOFT_BAR_OHCI_FLAG` or stores the BAR and configures `GLIU_P2D_BM3`. Reads reverse that mapping and clear the soft BAR sizing flag after returning the mask.

State and persistence: State is persistent hardware/MSR state, not kernel heap state. The soft BAR flag in `GLCP_SOFT_COM` is a transient handshake for PCI sizing. Interrupt enable is encoded in `PIC_YSEL_LOW`.

Dependencies and integration: Depends on `cs5536.h` and `cs5536_pci.h` register constants and `_rdmsr/_wrmsr`. Called through the VSM dispatch table in `cs5536_pci.c` for function 4.

Risks: Incorrect BAR masking or GLIU window construction can make OHCI MMIO unreachable or overlap other devices. The status write path only clears parity when the southbridge error bit is present. Interrupt routing assumes `CS5536_USB_INTR` and PIC shift constants match board wiring.

Test signals: PCI enumeration should show the CS5536 OHCI vendor/device/class, BAR sizing should report `CS5536_OHCI_RANGE`, OHCI MMIO should probe after BAR assignment, and USB interrupts should appear only when `PCI_OHCI_INT_REG` enables the PIC route.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ohci.c -->
