# sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.h

## Purpose
This header declares the USB PCI quirk helpers implemented in `pci-quirks.c` and provides safe inline no-op or false-returning stubs when the relevant configuration options are disabled. It lets USB host-controller drivers call chipset and handoff helpers without scattering preprocessor conditionals through their own implementations.

## Important APIs, Types, and Functions
Under `CONFIG_USB_PCI_AMD`, the header declares AMD helpers: `usb_hcd_amd_remote_wakeup_quirk`, `usb_amd_hang_symptom_quirk`, `usb_amd_prefetch_quirk`, `usb_amd_dev_put`, `usb_amd_quirk_pll_check`, `usb_amd_quirk_pll_disable`, `usb_amd_quirk_pll_enable`, `sb800_prefetch`, and `usb_amd_pt_check_port`. When disabled, the stubs return `false` for boolean queries and do nothing for mutators.

Under `CONFIG_USB_PCI`, it declares UHCI reset helpers, ASMedia flow-control tuning, Intel xHCI routing enable, and xHCI port disable helpers. When disabled, only stubs for `usb_asmedia_modifyflowcontrol` and `usb_disable_xhci_ports` are provided; the UHCI and Intel enable declarations are absent because callers should only require them when PCI USB support is built.

## Control Flow
There is no runtime control flow beyond inline stub execution. The compile-time control flow is determined by `CONFIG_USB_PCI_AMD` and `CONFIG_USB_PCI`. Enabled configurations bind callers to exported symbols from `pci-quirks.c`; disabled configurations compile no-op paths directly into callers.

## State and Persistence Behavior
The header owns no state. Its stubs intentionally do not allocate, retain, or release anything. In enabled AMD builds, callers must still pair chipset initialization side effects with `usb_amd_dev_put` according to the implementation contract in `pci-quirks.c`.

## Dependencies and Integration Points
The declarations depend on Linux PCI and device model types (`struct pci_dev`, `struct device`) but forward-declare `struct pci_dev` in the non-PCI branch to avoid unnecessary include coupling. The header is consumed by USB host-controller drivers and the PCI quirks implementation itself.

## Risks
The main risk is configuration mismatch. A caller that assumes a helper has real behavior in a disabled configuration will silently get a no-op or `false`, so feature behavior must be guarded by the same configuration semantics. The absence of some stubs in the non-`CONFIG_USB_PCI` branch means misuse can surface as compile errors, which is preferable for helpers that are not meaningful without PCI support.

## Test Signals
Compile matrix testing is the key signal: build with AMD quirks enabled/disabled, PCI USB enabled/disabled, and with host drivers that include this header. Functional tests should confirm disabled configurations do not require unresolved symbols, while enabled configurations link to the `EXPORT_SYMBOL_GPL` definitions in `pci-quirks.c`.
