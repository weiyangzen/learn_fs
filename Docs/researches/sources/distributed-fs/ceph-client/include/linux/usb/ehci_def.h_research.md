<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_def.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ehci_def.h

Purpose: defines EHCI host-controller capability and operational register layouts plus bitfield macros.

Important APIs and types: `struct ehci_caps` maps capability registers (`hc_capbase`, `hcs_params`, `hcc_params`, `portroute`) and macros decode cap length, version, debug port, companion controllers, port counts, PPC, LPM, prefetch, periodic size, 64-bit addressing, and extended caps. `struct ehci_regs` maps command, status, interrupt enable, frame index, segment, periodic/async list pointers, TX tuning, config flag, port status/control, USBMODE, HOSTPC/Broadcom extension registers, and USBMODE_EX. Macros define command/status, port, mode, and hostpc bits including write-clear port change bits.

Control flow: EHCI HCDs ioremap controller registers, decode caps, reset/start the controller via command bits, configure schedules and port ownership/power/reset/suspend, service status interrupts, and apply platform-specific register extensions.

State and persistence: all state is hardware MMIO state plus DMA schedule pointers programmed by the HCD. The header only defines layouts and bit masks.

Dependencies and integration points: includes EHCI debug-port definitions and relies on HCD helpers such as `ehci_big_endian_capbase()` supplied by implementation code. It integrates generic EHCI core with PCI/platform/SoC HCDs.

Risks and test signals: risks include endian/capbase decoding errors, write-one-to-clear mishandling of port bits, invalid port count assumptions, 64-bit DMA segment setup bugs, and extension register conflicts. Test EHCI on big/little-endian systems, port reset/suspend/resume, interrupt status handling, companion-controller handoff, and SoC-specific HOSTPC/Broadcom paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ehci_def.h -->
