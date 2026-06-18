# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-orion.c

## Purpose
Marvell Orion/Armada/AC5 EHCI glue. It configures DMA masks, optional clocks, MBUS DRAM windows, Orion PHY errata registers, Armada 3700 SBUSCFG, and then registers a shared EHCI HCD with caps at `regs + 0x100`.

## Important APIs, types, and functions
`struct orion_ehci_hcd` stores the optional clock. `orion_usb_phy_v1_setup()` implements Orion USB controller guidelines and errata programming. `ehci_orion_conf_mbus_windows()` mirrors DRAM chip-select windows into USB address-decode registers. `ehci_orion_drv_reset()` calls `ehci_setup()` and applies the Armada 3700 SBUSCFG workaround. `ehci_orion_drv_probe()`, remove, suspend, and resume provide lifecycle. OF match data selects 32-bit or AC5 34-bit DMA masks.

## Control flow
Probe gets IRQ, coerces DMA mask from compatible data, maps MMIO, creates the HCD, sets caps/resource state and integrated TT, enables an optional clock, configures MBUS windows if present, applies legacy PHY setup for non-DT platform data, and calls `usb_add_hcd()`. Remove unregisters the HCD, disables the optional clock, and releases the HCD. PM routes to `ehci_suspend()`/`ehci_resume()`.

## State and persistence behavior
State lives in `struct orion_ehci_hcd`, HCD/EHCI core fields, and MMIO registers. MBUS windows, PHY tuning, SBUSCFG, interrupt masks, and host-mode bits persist until controller reset or driver teardown.

## Dependencies and integration points
Depends on Marvell MBUS helpers, platform data for legacy PHY version, OF match data, clock APIs, DMA mapping, and common EHCI code. Compatible strings include `marvell,orion-ehci`, `marvell,armada-3700-ehci`, and `marvell,ac5-ehci`.

## Risks and edge cases
`of_device_get_match_data()` must provide a valid DMA mask pointer for DT devices. Legacy non-DT `pd` is dereferenced when no OF node is present. PHY setup contains busy-wait reset loops with no timeout. MBUS windows are limited to four entries, matching the register block.

## Test signals
DT probe for all compatibles, AC5 memory above 4 GiB, optional clock absence/presence, MBUS window programming, Armada 3700 SBUSCFG after reset, suspend/resume, remove, and USB enumeration under DMA stress are key signals.
