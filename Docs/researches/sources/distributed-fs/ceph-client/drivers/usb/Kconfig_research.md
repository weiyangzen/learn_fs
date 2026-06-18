# sources/distributed-fs/ceph-client/drivers/usb/Kconfig

## Purpose
`drivers/usb/Kconfig` is the top-level USB configuration menu. It defines foundational endianness symbols, the `USB_SUPPORT` and `USB` core options, PCI host support toggles, and includes submenus for common USB code, core, monitors, HCDs, class/storage/image/USBIP drivers, dual-mode controllers, serial/misc/ATM peripheral drivers, PHY, gadget, Type-C, and role-switch support.

## Important APIs, Types, And Functions
- `USB_SUPPORT` gates the entire USB menu and depends on `HAS_IOMEM`.
- `USB` builds host-side USB core support and selects `GENERIC_ALLOCATOR`, `USB_COMMON`, and `NLS`.
- `USB_PCI` and `USB_PCI_AMD` control PCI-specific host integration and AMD quirk support.
- Endianness booleans such as `USB_OHCI_BIG_ENDIAN_DESC` and `USB_EHCI_BIG_ENDIAN_MMIO` are selected by lower-level host drivers.
- `source` directives include all child Kconfig files in a deliberate dependency order.

## Control Flow
Kconfig evaluation starts with low-level helper symbols, then displays `USB_SUPPORT`. If enabled, common USB code and host-side USB become available. If `USB` is selected, host core, monitor, HCD, class, storage, image, and USBIP menus are included. Dual-mode controller menus are included under USB support even outside the `if USB` block where appropriate. USB serial, misc, and ATM drivers are included only when host USB is enabled. PHY, gadget, Type-C, and role-switch menus are then sourced before closing `USB_SUPPORT`.

## State And Persistence Behavior
The file contributes build-time `.config` state only. It does not define runtime state, but selected symbols determine which USB subsystems and modules exist in the built kernel.

## Dependencies And Integration Points
This file integrates with the kernel Kconfig system and child USB subsystem Kconfigs. It coordinates dependencies for the Makefile paths in `drivers/usb/Makefile`, including `drivers/usb/atm/Kconfig` for the DSL modem files in this work item.

## Risks And Edge Cases
Misplaced `source` directives can expose options without required host support or hide drivers unexpectedly. `USB_PCI` defaults to yes on PCI systems but can be disabled for SoCs with non-PCI USB. Endianness helper symbols are invisible and rely on child drivers selecting them correctly. The `USB` tristate controls `usbcore` module availability and can ripple widely.

## Test Signals
Run `make menuconfig` or `scripts/kconfig/conf` for configs with `USB_SUPPORT=n`, `USB_SUPPORT=y USB=n`, and `USB=m/y`. Confirm USB ATM appears only under host USB. Verify generated `.config` drives expected object directories in `drivers/usb/Makefile`.
