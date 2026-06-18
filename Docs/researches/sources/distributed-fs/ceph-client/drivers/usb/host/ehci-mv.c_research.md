# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mv.c

## Purpose
Marvell/PXA EHCI platform glue. It allocates an EHCI HCD, maps the Marvell register layout with capability registers at `0x100`, handles optional OTG host registration, enables clocks/PHYs, drives VBUS for host mode, and applies HSIC-specific port setup before delegating transfers to the shared EHCI core.

## Important APIs, types, and functions
`struct ehci_hcd_mv` stores mode, mapped base/cap/op register pointers, OTG/PHY/clock handles, and a platform `set_vbus` callback. `mv_ehci_enable()` and `mv_ehci_disable()` sequence clock and PHY lifetime. `mv_ehci_reset()` sets `hcd->has_tt`, calls `ehci_setup()`, and toggles `PORT_TEST_FORCE` for HSIC. `mv_ehci_probe()`, `mv_ehci_remove()`, and `mv_ehci_shutdown()` provide platform-driver lifecycle. `platform_overrides` supplies the reset hook and private size to `ehci_init_driver()`.

## Control flow
Probe checks `usb_disabled()`, creates the HCD, pulls platform data, gets an optional generic PHY plus a required clock, maps MMIO, enables hardware, computes caps/op register pointers, gets IRQ, and sets `ehci->caps`. OTG mode registers the host with the transceiver and disables local power until OTG activates it. Host mode asserts VBUS, calls `usb_add_hcd()`, and enables wakeup. Remove unregisters the HCD if present, detaches OTG host state, clears VBUS, disables PHY/clock for host mode, and releases the HCD.

## State and persistence behavior
Software state lives in `ehci_hcd_mv` under `ehci->priv` and in USB core HCD state. Hardware state persists in Marvell EHCI/PHY registers, port status bits, VBUS, clock gating, and OTG host binding until remove, reset, or power loss.

## Dependencies and integration points
Depends on platform device resources, clocks, generic PHY, legacy USB PHY/OTG, `mv_usb_platform_data`, device-tree PHY mode, and shared EHCI symbols from `ehci.h`. It matches `marvell,pxau2o-ehci` and legacy platform IDs `pxa-u2oehci`/`pxa-sph`.

## Risks and edge cases
The register offset assumptions are Marvell-specific. OTG mode intentionally disables local clock/PHY after `otg_set_host()`, so host-mode and OTG-mode teardown differ. HSIC setup writes reserved-looking port bits and depends on accurate DT PHY mode. Error paths must undo VBUS, clock, PHY, and HCD ownership in the right order.

## Test signals
Probe/remove in host and OTG modes, deferred PHY probing, clock failure, IRQ absence, HSIC DT mode, VBUS callback behavior, root-hub registration, suspend wakeup capability, and module unload are the useful signals.
