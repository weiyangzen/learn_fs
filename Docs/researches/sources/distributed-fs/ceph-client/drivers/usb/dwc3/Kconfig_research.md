# sources/distributed-fs/ceph-client/drivers/usb/dwc3/Kconfig

## Purpose
`drivers/usb/dwc3/Kconfig` defines the build-time configuration menu for the DesignWare USB3 DRD core and its platform glue drivers. It controls whether the DWC3 core is built, whether host/gadget/dual-role support is compiled, whether ULPI support is enabled, and which SoC or bus glue modules participate in the build.

## Important Symbols
- `USB_DWC3`: top-level tristate for the DWC3 core, depending on USB or USB_GADGET plus DMA support and compatible EXTCON state. It selects xHCI platform support when host xHCI is enabled and role-switch support for dual-role mode.
- `USB_DWC3_ULPI`: optional ULPI PHY interface registration when the ULPI bus is available.
- Mode choice: `USB_DWC3_HOST`, `USB_DWC3_GADGET`, and `USB_DWC3_DUAL_ROLE`, with defaults based on available USB host/gadget subsystems.
- Glue symbols: OMAP, Exynos, PCI, HAPS, Keystone, Meson G12A, OF Simple, ST, Qualcomm, i.MX8MP, i.MX, Xilinx, AM62, Octeon, Realtek, generic platform, Apple, and Google platform support.

## Control Flow
Kconfig has declarative control flow. Enabling `USB_DWC3` opens the mode choice and platform glue menu. The mode choice determines which core source files the Makefile includes. Glue options default to `USB_DWC3` where appropriate but are constrained by architecture, OF, ACPI, PCI, COMMON_CLK, EXTCON, and COMPILE_TEST availability.

## State And Persistence Behavior
Selected symbols are persisted in the kernel `.config`, not in runtime driver state. Those symbols control which objects compile into the kernel or modules and which runtime capabilities exist. For example, selecting host-only removes gadget objects from the DWC3 core build, while dual-role selects role-switch support.

## Dependencies And Integration Points
This file directly integrates with `drivers/usb/dwc3/Makefile`, which maps the symbols to objects. It also integrates with USB core, USB gadget, xHCI platform, role-switch, EXTCON, ULPI bus, OF, ACPI, architecture symbols, common clock, and regmap dependencies. The glue symbols correspond to source files such as `dwc3-pci.o`, `dwc3-qcom.o`, `dwc3-of-simple.o`, and related platform objects.

## Risks
- Incorrect dependencies can expose glue drivers on unsupported build combinations or hide them from valid COMPILE_TEST coverage.
- Mode choice dependencies must match Makefile conditions; otherwise a selected mode might omit required objects or include impossible code.
- Defaulting many glue drivers to `USB_DWC3` is convenient but can increase build coverage and module surface; dependency mistakes become broad.
- Role-switch selection is required for dual-role and some platform glues. Missing selects can cause link or runtime role-management failures.

## Test Signals
- Run `allmodconfig`, `allyesconfig`, and targeted host/gadget/dual-role configs to verify symbol dependency consistency.
- Confirm `USB_DWC3=m` builds `dwc3.ko` and selected glue modules as modules.
- Validate host-only excludes gadget/DRD objects, gadget-only excludes host/DRD objects, and dual-role includes host, gadget, and DRD.
- Build platform glue options under COMPILE_TEST where allowed.
