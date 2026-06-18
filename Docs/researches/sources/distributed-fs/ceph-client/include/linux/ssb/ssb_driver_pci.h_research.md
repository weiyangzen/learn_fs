<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_pci.h

Purpose: Defines SSB PCI core registers, translation settings, state flags, and helpers for PCI host/core initialization and IRQ routing.

Important APIs/types/functions: `SSB_PCICORE_*` register/bit constants, SB-to-PCI translation constants, `SSB_PCICORE_BFL_NOPCI`, `struct ssb_pcicore`, `ssb_pcicore_init()`, `ssb_pcicore_dev_irqvecs_enable()`, `ssb_pcicore_plat_dev_init()`, and `ssb_pcicore_pcibios_map_irq()`.

Control flow: Enabled builds expose real initialization and IRQ-vector helpers. Disabled builds provide an empty type and stubs returning success for init/IRQ-vector enable or `-ENODEV` for platform PCI init/map IRQ.

State and persistence behavior: Runtime state includes SSB PCI device pointer and bit flags recording setup, host mode, and cardbus mode. Hardware state includes PCI control, arbiter, interrupt, GPIO, translation, config, and SPROM shadow registers.

Dependencies: PCI types, SSB device definitions, board flags, and architecture pcibios integration.

Integration points: SSB-as-PCI-host support, PCI client configuration, IRQ routing, SPROM shadow access, and embedded platform PCI setup.

Risks: Translation window programming and IRQ routing are chip-revision sensitive. Disabled stubs may compile users but leave platform PCI unsupported at runtime.

Test signals: PCI host and client mode enumeration, IRQ vector enable tests, config-space access, SPROM shadow access, and disabled-config compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_pci.h -->
