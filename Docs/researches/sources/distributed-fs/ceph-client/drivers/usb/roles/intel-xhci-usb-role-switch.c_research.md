<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/intel-xhci-usb-role-switch.c -->
# sources/distributed-fs/ceph-client/drivers/usb/roles/intel-xhci-usb-role-switch.c

Purpose: Intel xHCI OTG role-switch platform driver for Cherry Trail, Broxton, and similar SoCs; exposes hardware role selection as a generic USB role switch. The complete 227-line source was read.

Important APIs/types/functions: `struct intel_xhci_usb_data`, `intel_xhci_usb_probe()`, `intel_xhci_usb_remove()`, `intel_xhci_usb_set_role()`, `intel_xhci_usb_get_role()`, registers `DUAL_ROLE_CFG0/1`, bits `SW_IDPIN`, `SW_VBUS_VALID`, `SW_SWITCH_EN`, and `HOST_MODE`.

Control flow and state: probe maps MMIO, registers a software node, creates a userspace-controllable role switch, and enables runtime PM. Set-role takes the ACPI global lock, resumes the device, writes ID/VBUS/static-dynamic config bits, then polls `HOST_MODE` up to 1000 ms. Get-role reads CFG0 and derives host/device/none. State is devm driver data plus MMIO register state and the registered role switch.

Dependencies and integration points: ACPI global lock, x86 platform devices, runtime PM, software nodes, MMIO, and the role-switch class.

Risks and test signals: risks include AML races, unchecked `pm_runtime_get_sync()` failure, global software-node assumptions, `sw_switch_disable` quirks, and role-switch timeouts. Test sysfs role writes, CFG register traces, AML events, runtime suspend/resume, timeout injection, remove/reprobe, and ACPI x86 build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/roles/intel-xhci-usb-role-switch.c -->
