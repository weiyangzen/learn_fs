<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_gige.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_gige.h

Purpose: Defines the SSB Gigabit Ethernet pseudo-PCI bridge/core interface and helper queries used by Ethernet drivers on Broadcom SSB SoCs.

Important APIs/types/functions: GigE register offsets and flags, `struct ssb_gige`, `pdev_is_ssb_gige_core()`, `pdev_to_ssb_gige()`, `ssb_gige_is_rgmii()`, `ssb_gige_have_roboswitch()`, DMA/posted-write quirk helpers, MAC/PHY address helpers, `ssb_gige_pcibios_plat_dev_init()`, `ssb_gige_map_irq()`, `ssb_gige_init()`, and `ssb_gige_exit()`.

Control flow: With `CONFIG_SSB_DRIVER_GIGE`, a PCI device can be identified as the SSB GigE core, converted to `struct ssb_gige` through the PCI ops container, and queried for board/SoC quirks and SPROM-provided MAC/PHY data. Without the config, helpers return disabled/error values.

State and persistence behavior: Runtime state includes SSB device pointer, spinlock, RGMII/GMII mode, PCI controller/ops, and I/O/memory resources. Board state comes from `bus->sprom`.

Dependencies: `ssb.h`, PCI core, spinlocks, resource management, and board flags from SPROM.

Integration points: MIPS/BCM47xx PCI platform initialization and Ethernet MAC drivers that query PHY mode, MAC address, DMA limitations, posted-write flushing, and IRQ mapping.

Risks: `ssb_gige_exit()` deliberately calls `BUG()` when enabled because the bridge cannot be unregistered, so it must not be used as a normal unload path. Wrong `pdev_to_ssb_gige()` assumptions can return `NULL`.

Test signals: Enabled/disabled build coverage, PCI platform-device initialization, IRQ mapping, MAC/PHY SPROM data tests, and hardware-specific DMA/posted-write quirk validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_gige.h -->
