<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/Kconfig

## Purpose
This Kconfig file defines build-time selection for the Synopsys DesignWare USB2 DRD core driver. It controls whether the common DWC2 module is built, whether it supports host, peripheral, or dual-role operation, whether the PCI glue is available, and whether debug or SOF tracking diagnostics are compiled.

## Important APIs, types, and functions
The central symbol is `USB_DWC2`, a tristate depending on DMA, USB or USB_GADGET, and MMIO support, and selecting `USB_ROLE_SWITCH`. The mode choice selects one of `USB_DWC2_HOST`, `USB_DWC2_PERIPHERAL`, or `USB_DWC2_DUAL_ROLE` with defaults based on enabled USB host and gadget subsystems. Additional symbols are `USB_DWC2_PCI`, `USB_DWC2_DEBUG`, `USB_DWC2_VERBOSE`, `USB_DWC2_TRACK_MISSED_SOFS`, and `USB_DWC2_DEBUG_PERIODIC`.

## Control flow
The `if USB_DWC2` block presents a mutually exclusive mode choice. Host mode requires host USB availability and handles built-in/module constraints. Peripheral and dual-role mode require gadget support. PCI glue is independently selectable when USB PCI support is present. Debug and verbose options feed compiler flags in the Makefile, while missed SOF tracking enables extra host state in `core.h`.

## State and persistence behavior
No runtime state is stored here. The selected symbols persist in the kernel configuration and determine which objects, fields, stubs, debug prints, and host/gadget code paths exist in the compiled driver.

## Dependencies and integration points
This file integrates Kconfig with the DWC2 Makefile, USB host core, USB gadget core, USB role-switch framework, PCI bus glue, debugfs-dependent debug output, and host scheduler diagnostics. Its defaults are important because the source uses `IS_ENABLED(CONFIG_USB_DWC2_...)` to compile host/gadget structures and fallback stubs.

## Risks
Misconfigured dependencies can produce a DWC2 build with unavailable host or gadget APIs. The dual-role option requires both host and gadget support, so distribution configs must ensure all dependency combinations are covered. Verbose debug can flood logs. The missed-SOF option is explicitly experimental and may impose memory/logging overhead.

## Test signals
Build coverage should include built-in and module `USB_DWC2`, host-only, peripheral-only, dual-role, PCI enabled/disabled, debug/verbose, debugfs on/off, and missed-SOF tracking. Runtime smoke tests should confirm that expected modules (`dwc2`, platform glue, optional PCI glue) appear and that role-switch support is present for dual-role-capable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/Kconfig -->
