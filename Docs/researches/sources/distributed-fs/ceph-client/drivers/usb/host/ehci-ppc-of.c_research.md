# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ppc-of.c

## Purpose
PowerPC OpenFirmware EHCI glue, especially for AMCC PPC 440EPx. It defines a complete `hc_driver`, maps OF resources/IRQs, supports big-endian MMIO/descriptors, enables a 440EPx Break Memory Transfer erratum bit, and coordinates with a companion OHCI controller for the AMCC USB23 erratum.

## Important APIs, types, and functions
`ehci_ppc_of_hc_driver` directly lists EHCI callbacks. `ppc44x_enable_bmt()` maps the second resource and writes `PPC440EPX_EHCI0_INSREG_BMT`. `ehci_hcd_ppc_of_probe()` and remove manage resources. `set_ohci_hcfs()` from `ehci.h` is used on removal when `has_amcc_usb23` is set.

## Control flow
Probe resolves OF memory resource and IRQ mapping, creates an HCD, maps registers, finds an IBM OHCI companion node, maps its control register if present, parses endian properties, sets caps, applies the 440EPx BMT workaround when compatible, calls `usb_add_hcd()`, and enables wakeup. Remove unregisters the HCD, disposes IRQ mapping, conditionally restores OHCI operational state if the companion appears loaded, and releases the HCD.

## State and persistence behavior
EHCI state lives in the HCD plus `ehci->has_amcc_usb23`, endian flags, and `ohci_hcctrl_reg`. Hardware state includes BMT and companion OHCI HCFS bits.

## Dependencies and integration points
Depends on OF address/IRQ APIs, PPC endian IO helpers, shared EHCI core, and optional IBM OHCI companion nodes. It matches compatible `usb-ehci`.

## Risks and edge cases
The direct `hc_driver` must remain synchronized with shared EHCI callback expectations. IRQ mappings are manually disposed. Companion OHCI coordination relies on probing resource ownership with `request_mem_region()`, which is indirect. Big-endian properties require Kconfig support in the shared helpers.

## Test signals
PPC OF probe/remove, 440EPx BMT register programming, big-endian descriptor/register operation, OHCI companion present/absent, IRQ mapping failure, and suspend/resume through bus callbacks are key signals.
