<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb.h

Purpose: Defines the Sonics Silicon Backplane core bus model, device/driver abstractions, SPROM board data, bus registration APIs, MMIO access wrappers, power management hooks, DMA translation, and host-bus integration.

Important APIs/types/functions: `struct ssb_sprom`, `struct ssb_boardinfo`, `struct ssb_bus_ops`, core/vendor/board constants, `struct ssb_device`, `dev_to_ssb_dev()`, drvdata helpers, `struct ssb_driver`, `ssb_driver_register/unregister()`, `enum ssb_bustype`, `struct ssb_bus`, `struct ssb_init_invariants`, bus registration functions for SoC/PCI/PCMCIA/SDIO, suspend/resume, `ssb_device_enable/disable/is_enabled()`, `ssb_read*/write*()`, block I/O helpers, `ssb_dma_translation()`, powerup/powerdown, `ssb_commit_settings()`, and address-match helpers.

Control flow: Host-specific registration fills an `ssb_bus`, enumerates cores into `ssb_device` entries, populates invariant board/SPROM data, and registers devices with the driver model. Per-device MMIO operations dispatch through `ssb_bus_ops`. Device drivers bind via `ssb_driver` probe/remove/suspend/resume hooks. Power helpers coordinate bus-level power state around device activity.

State and persistence behavior: Runtime bus state includes MMIO base, mapped core/window state, BAR lock, host-bus pointer, quirks, chip ID/revision/package, device array, board/SPROM data, optional GPIO/watchdog state, list linkage, and power flags. SPROM contents represent persistent board configuration read into memory.

Dependencies: Linux device model, lists, spinlocks, PCI, GPIO, DMA mapping, platform devices, SSB register constants, and companion SSB core headers.

Integration points: Broadcom SSB-based wireless, Ethernet, MIPS SoC, PCI bridge, PCMCIA, SDIO, GPIO, watchdog, and architecture pcibios fixups.

Risks: Incorrect core window switching under `bar_lock`, stale SPROM fallback data, wrong host-bus union use, and DMA translation mistakes can break device access. The fixed `SSB_MAX_NR_CORES` device array depends on register-map constants.

Test signals: Enumeration on each host bus, SPROM parse/fallback tests, read/write/block I/O traces, suspend/resume and powerdown tests, DMA mapping tests, and SSB driver probe/remove coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb.h -->
