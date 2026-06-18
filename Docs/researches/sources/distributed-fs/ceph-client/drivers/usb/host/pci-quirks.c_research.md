# sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.c

## Purpose
This file provides early and runtime USB PCI host-controller quirks for Linux. It resets or hands off UHCI, OHCI, EHCI, and xHCI controllers from firmware to the OS, handles Intel xHCI port routing, applies ASMedia flow-control tuning, and exposes AMD chipset helpers used by USB HCDs to avoid known power-management, prefetch, PLL, and disabled-port issues.

## Important APIs, Types, and Functions
The AMD-specific section, gated by `CONFIG_USB_PCI_AMD`, defines `enum amd_chipset_gen`, `struct amd_chipset_type`, and the global `amd_chipset` cache protected by `amd_lock`. Exported AMD helpers include `sb800_prefetch`, `usb_hcd_amd_remote_wakeup_quirk`, `usb_amd_hang_symptom_quirk`, `usb_amd_prefetch_quirk`, `usb_amd_quirk_pll_check`, `usb_amd_quirk_pll_disable`, `usb_amd_quirk_pll_enable`, `usb_amd_dev_put`, and `usb_amd_pt_check_port`.

Generic exported helpers include `usb_asmedia_modifyflowcontrol`, `uhci_reset_hc`, `uhci_check_and_reset_hc`, `usb_enable_intel_xhci_ports`, and `usb_disable_xhci_ports`. Internal handoff paths include `quirk_usb_handoff_uhci`, `quirk_usb_handoff_ohci`, `ehci_bios_handoff`, `quirk_usb_disable_ehci`, `handshake`, `quirk_usb_handoff_xhci`, and `quirk_usb_early_handoff`.

## Control Flow
The early handoff path is registered with `DECLARE_PCI_FIXUP_CLASS_FINAL` for USB-class PCI devices. `quirk_usb_early_handoff` filters unsupported devices, skips special Netlogic and Raspberry Pi 4 xHCI cases, enables the PCI device, dispatches by controller class, then disables the PCI device again.

UHCI handoff checks I/O BAR availability and resets legacy support, interrupts, and command state. OHCI handoff ioremaps BAR0, optionally requests ownership from firmware, disables interrupts, preserves `HcFmInterval` except for a known ULi lockup device, resets, and unmaps. EHCI handoff walks extended capabilities, performs BIOS semaphore handoff with DMI skip rules for broken systems, disables legacy SMIs, clears CONFIGFLAG when firmware previously owned the controller, then halts the controller and disables interrupts. xHCI handoff locates the xHCI legacy support extended capability, requests OS ownership, disables legacy SMIs, applies Intel port routing if appropriate, waits for controller readiness, and halts the controller with interrupts disabled.

AMD helper flow lazily initializes chipset identity with `usb_amd_find_chipset_info`. It probes SMBus and northbridge devices, records generation/revision, decides whether PLL quirks are needed, and holds PCI device references until `usb_amd_dev_put`. PLL disable/enable is reference-counted through `amd_chipset.isoc_reqs`, so multiple isochronous users keep the workaround active until the last release.

## State and Persistence Behavior
The only durable in-kernel state is the static `amd_chipset` cache. It stores referenced PCI devices, chipset generation/revision, northbridge type, `probe_count`, `isoc_reqs`, and whether the PLL quirk is required. `amd_lock` protects updates and reference-count transitions, while `pci_dev_put` is intentionally performed outside the spinlock.

Controller handoff functions persist changes in PCI config space and MMIO registers, including firmware ownership semaphores, interrupt masks, port-routing registers, and controller run/reset bits. There is no filesystem persistence.

## Dependencies and Integration Points
This code depends on PCI config access, I/O port access when UHCI is enabled, MMIO mapping, DMI, ACPI/OF device data, xHCI extended-capability definitions from `xhci-ext-caps.h`, and Linux PCI fixup infrastructure. It integrates with UHCI/OHCI/EHCI/xHCI host drivers by preparing controllers before normal probing and by exporting helper symbols that those drivers can call for chipset-specific behavior.

Intel routing uses PCI config registers `USB_INTEL_XUSB2PR`, `USB_INTEL_USB2PRM`, `USB_INTEL_USB3_PSSEN`, and `USB_INTEL_USB3PRM`. ASMedia flow control writes vendor-specific registers `ASMT_DATA_WRITE0/1`, `ASMT_CONTROL_REG`, and command/data constants.

## Risks
This file writes low-level chipset registers very early in boot, so bad detection can hang hardware, break firmware handoff, or disconnect boot-critical USB devices. Many paths are hardware-specific and depend on vendor/device/revision IDs and DMI strings staying accurate. The AMD PLL path manipulates southbridge and northbridge registers under a spinlock and uses I/O port cycles; incorrect reference counting could leave power management disabled or re-enable it while isochronous transfers are active.

The EHCI capability walker bounds the loop, but malformed config-space capabilities can still produce warnings or incomplete handoff. xHCI handoff assumes BAR0 length is sufficient before reading ext-cap registers and includes force-handoff exceptions for known devices. Intel port switchover must not run when xHCI support is missing, or USB ports may become unusable; the code explicitly disables xHCI routing in that configuration.

## Test Signals
Build signals should cover combinations of `CONFIG_USB_PCI`, `CONFIG_USB_PCI_AMD`, `CONFIG_USB_UHCI_HCD`, `CONFIG_HAS_IOPORT`, `CONFIG_USB_XHCI_HCD`, DMI, OF, and ACPI. Runtime validation includes early boot logs for BIOS handoff failures, no hangs on known DMI skip systems, successful UHCI/OHCI/EHCI/xHCI probing after fixups, Intel switchable USB2/USB3 ports routing to xHCI only when supported, and ASMedia writes completing without timeout.

AMD-specific tests should verify chipset detection reference counts, `usb_amd_dev_put` cleanup, PLL disable/enable nesting under concurrent isochronous streams, SB800 prefetch toggling, Promontory disabled-port detection for supported device IDs, and remote-wakeup/hang/prefetch quirk decisions on matching revisions.
