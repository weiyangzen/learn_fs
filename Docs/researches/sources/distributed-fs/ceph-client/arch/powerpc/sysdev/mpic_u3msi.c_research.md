<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_u3msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_u3msi.c

Purpose: Provides legacy U3/U4 PowerMac MPIC MSI setup using HyperTransport MSI mapping or U4 bridge magic addresses.

Important APIs/types/functions: Entry point is `mpic_u3msi_init()`. MSI hooks are `u3msi_setup_msi_irqs()` and `u3msi_teardown_msi_irqs()`. IRQ chip is `mpic_u3msi_chip`; address helpers are `find_ht_magic_addr()` and `find_u4_magic_addr()`.

Control flow: Init creates the MPIC MSI allocator, stores the global MPIC pointer, and installs MSI setup/teardown callbacks on every PCI host bridge. Setup verifies a usable magic MSI address, allocates one MPIC hwirq per MSI descriptor, creates an irqdomain mapping, attaches the MSI descriptor, overrides the chip/type, writes the MSI address/data, and leaves MPIC/pci MSI mask handling to the chip callbacks. Teardown clears descriptors, disposes mappings, zeros descriptor IRQs, and frees hwirqs.

State and persistence: Uses global `msi_mpic`, MPIC MSI bitmap allocations, per-MSI Linux IRQ mappings, and PCI device MSI messages. Hardware address selection persists in device MSI capability/programming.

Dependencies and integration points: Depends on MPIC core, `msi_bitmap`, PCI MSI descriptor iteration, HT MSI mapping capability, U4 PCIe bridge compatibility strings, and global `hose_list`.

Risks: The implementation is explicitly U3/U4-specific and relies on magic bridge addresses. MSI-X is marked untested. `u3msi_setup_msi_irqs()` increments a local `hwirq` after writing each message even though each loop allocates a fresh hwirq, which is harmless locally but confusing. Partial setup failure can leave prior descriptors allocated until teardown.

Test signals: U3/U4 PowerMac MSI-capable PCI devices, MSI mask/unmask order, teardown after partial allocation, MSI-X smoke tests if used, and hwirq reservation collision checks.

Source read size: 196 lines, 5180 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_u3msi.c -->
