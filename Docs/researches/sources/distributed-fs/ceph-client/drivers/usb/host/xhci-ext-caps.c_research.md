# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.c

Purpose: handles vendor-specific xHCI extended capabilities at controller initialization. In this file, the implemented behavior is Intel USB role-switch companion device creation for controllers advertising a vendor capability and the matching quirk.

Important APIs and functions: `xhci_ext_cap_init()` walks all extended capabilities with `xhci_find_next_ext_cap()`. `xhci_create_intel_xhci_sw_pdev()` creates an `intel_xhci_usb_sw` platform device with a memory resource mapped onto the vendor capability window. `xhci_intel_unregister_pdev()` is registered as a devm cleanup action. Cherryview additionally gets a managed software node property `sw_switch_disable`.

Control flow: init begins at the first extended capability, loops through each capability, reads the capability ID, and on Intel vendor capability checks `XHCI_INTEL_USB_ROLE_SW`. If set, it allocates the platform device, adds a 0x400-byte MMIO resource, optionally installs software node properties, parents it to the xHCI PCI device, registers it, and attaches a devm unregister action to the controller device.

State and persistence: no long-lived private state is kept in this file. The child platform device and its resource persist until the parent device is removed or devm cleanup runs.

Dependencies and integration points: depends on PCI device identity, platform device APIs, property/software-node APIs, xHCI quirk flags, and extended capability parsing from `xhci-ext-caps.h`. Exported `xhci_ext_cap_init()` is called by core xHCI initialization and exported GPL for host glue.

Risks: assumes the controller device is PCI when the Intel role switch quirk is active (`to_pci_dev(dev)`). Resource sizing is fixed at 0x400 bytes and must match the companion driver expectation. Returning an error aborts init on role-switch pdev failures, so device-property or platform registration regressions can block host setup for affected hardware.

Test signals: Intel role-switch hardware or emulated capability; Cherryview property attachment; failure paths for platform allocation/resource/property/add/devm action; non-Intel or no-quirk controllers should no-op; verify companion driver binds to `intel_xhci_usb_sw`.
