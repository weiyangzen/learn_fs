<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_pci.c

Purpose: Implements TSI108 PCI host bridge config access and a cascaded PCI INTx interrupt router.

Important APIs/types/functions: Provides `tsi108_setup_pci()`, `tsi108_direct_read_config()`, `tsi108_direct_write_config()`, `tsi108_clear_pci_error()`, `tsi108_clear_pci_cfg_error()`, `tsi108_pci_int_init()`, and `tsi108_irq_cascade()`. Static router helpers include `get_pci_source()`, `tsi108_pci_int_mask()`, and `tsi108_pci_int_unmask()`.

Control flow: PCI setup maps the config window, allocates a PCI controller, sets bus range and direct config ops, logs the bridge, and processes OF ranges. Config reads use inline asm with exception-table fixup so absent devices return all ones; writes directly update little-endian config data. Error cleanup clears PB and PCI/X error status after failed config reads. Interrupt init creates a legacy irqdomain and enables the PCI block interrupt source. Cascade handling reads TSI108 PCI interrupt status, round-robins active INTA-D bits, disables the block source, dispatches the selected IRQ, then EOIs the parent.

State and persistence: Global state includes config virtual/physical base, CSR virtual base, PCI IRQ domain, static round-robin mask in `get_pci_source()`, and hardware IRP config/enable/status registers.

Dependencies and integration points: Depends on TSI108 CSR accessors, PowerPC PCI host bridge code, OF ranges, generic IRQ domain/chained IRQ, MPIC parent interrupt, and legacy IRQ numbering constants from `tsi108_irq.h`.

Risks: Several virtual addresses are stored in `u32`, which is unsafe on wider address builds. `pci_irq_host_map()` tests Linux virq values 1..4 and then configures fixed legacy IRQs instead of using the provided virq directly, which is unusual and tightly coupled to legacy numbering. Cascade disables PCI block interrupts until child unmask reenables them.

Test signals: PCI enumeration including absent-device reads, PB/PCI error clearing, INT A-D routing, chained parent IRQ behavior, OF bus ranges/ranges parsing, and 32-bit address assumptions.

Source read size: 426 lines, 10707 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_pci.c -->
