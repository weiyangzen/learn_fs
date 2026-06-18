<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig` defines the kernel configuration surface for USB host-controller drivers. It gates xHCI, EHCI, OHCI, UHCI, platform-specific glue, SPI/PCMCIA/SoC controllers, debug/test features, and virtualized Xen USB host support. The source was read as a complete 728-line file.

## Important APIs, Types, and Functions

This is Kconfig metadata rather than C code. Important symbols include `USB_XHCI_HCD`, `USB_XHCI_PLATFORM`, `USB_XHCI_*` SoC options, `USB_EHCI_HCD`, `USB_EHCI_ROOT_HUB_TT`, `USB_EHCI_TT_NEWSCHED`, `USB_EHCI_FSL`, `USB_EHCI_EXYNOS`, `USB_EHCI_HCD_AT91`, `USB_EHCI_HCD_PLATFORM`, `USB_BRCMSTB`, `USB_OHCI_HCD`, `USB_UHCI_HCD`, `USB_HCD_BCMA`, `USB_HCD_SSB`, `USB_HCD_TEST_MODE`, and individual non-EHCI host controllers. Dependencies and selects encode architecture, bus, PHY, DMA, I/O-memory, and companion-controller relationships.

## Control Flow

Menu flow is declarative. Top-level options expose host-controller families. Nested `if USB_XHCI_HCD`, `if USB_EHCI_HCD`, and `if USB_OHCI_HCD` blocks reveal family-specific platform drivers only when the family core is enabled. `select` statements pull in required common platform HCDs, root-hub TT support, generic PHY, firmware loader, or companion-controller glue. Deprecated symbols remain as compatibility prompts and redirect users to replacement drivers.

## State and Persistence Behavior

Kconfig selections persist in `.config` and determine which objects are compiled, built as modules, or omitted. No runtime state is stored here, but bad dependency/select relationships can create invalid builds or missing runtime drivers.

## Dependencies and Integration Points

The file integrates with `drivers/usb/host/Makefile`, architecture symbols, bus support (`USB_PCI`, `BCMA`, `SSB`, `SPI`, `PCMCIA`, `XEN`), PHY/reset frameworks, and common USB core options. It also documents module names and user-facing hardware support descriptions.

## Risks and Edge Cases

Incorrect dependencies can expose drivers on architectures without required MMIO/DMA/IOPORT/PHY support. Missing `select` links can build platform wrappers without their generic HCD backend. Overly broad `default y` values can unexpectedly increase kernel footprint on matching SoCs. Deprecated entries must continue to avoid selecting removed code. Typos in help text mention OCHI instead of OHCI in BCMA/SSB descriptions but do not affect builds.

## Test Signals

Validation should include `allmodconfig`, `allyesconfig`, `randconfig`, and architecture-focused configs for ARM, MIPS, PowerPC, SPARC/LEON, x86 PCI, and COMPILE_TEST. Confirm that enabled Kconfig symbols produce the expected Makefile objects and module names, and that deprecated options do not reference removed object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig -->
