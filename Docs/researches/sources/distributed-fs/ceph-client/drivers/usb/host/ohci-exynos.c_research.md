# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-exynos.c

## Purpose
`ohci-exynos.c` is Samsung Exynos platform glue for the generic OHCI USB host driver. It handles DMA-mask setup, HCD allocation, PHY discovery using current or legacy device-tree bindings, USB host clock management, PHY power sequencing, legacy OF-node masking, suspend/resume, and platform-driver registration.

## Important APIs, types, and functions
`struct exynos_ohci_hcd` stores the USB host clock, original OF node, up to three PHY handles, and a `legacy_phy` flag. `PHY_NUMBER` caps supported PHYs at three. Main helpers are `exynos_ohci_get_phy()`, `exynos_ohci_phy_enable()`, `exynos_ohci_phy_disable()`, `exynos_ohci_probe()`, `exynos_ohci_remove()`, `exynos_ohci_shutdown()`, `exynos_ohci_suspend()`, and `exynos_ohci_resume()`. `exynos_overrides` only supplies OHCI private data size; core OHCI reset/setup behavior is otherwise generic.

## Control flow
Probe coerces a 32-bit DMA mask, allocates an HCD with `exynos_ohci_hc_driver`, gets PHYs, obtains and enables the `"usbhost"` clock via `devm_clk_get_enabled()`, maps the MMIO resource, retrieves the IRQ, stores the HCD in platform drvdata, powers on all PHYs, optionally hides `pdev->dev.of_node` for legacy PHY subnode bindings, calls `usb_add_hcd()` with `IRQF_SHARED`, and enables wakeup.

PHY discovery first counts `phys` phandles with `#phy-cells` and gets each by index. If no modern PHY phandles exist, it iterates available child nodes, reads each child `reg` as the PHY slot, gets an optional PHY from that child, and marks `legacy_phy = true`. PHY enable powers on each stored PHY in order and unwinds previously powered PHYs on failure. PHY disable powers off all slots.

Removal restores the original OF node, removes the HCD, powers off PHYs, and releases the HCD. Shutdown delegates to the HCD driver's shutdown callback. Suspend calls `ohci_suspend()`, disables PHYs, and disables the clock. Resume reenables the clock, powers PHYs, unwinds clock on PHY failure, and calls `ohci_resume()`.

## State and persistence behavior
State is per-HCD private data plus device-managed clock/PHY/MMIO resources. `of_node` stores the original platform OF node so the probe-time legacy workaround can be undone on remove or add failure. There is no persistent state. Wakeup enablement is set after successful add and consulted during suspend through `device_may_wakeup()`.

## Dependencies and integration points
The driver depends on the generic OHCI core, Linux platform device, OF, PHY, clock, DMA, and USB HCD APIs. It matches `samsung,exynos4210-ohci`. The legacy binding behavior is an integration point with older Exynos device trees where PHYs are child nodes that could otherwise be mistaken for generic USB device child nodes.

## Risks and edge cases
`exynos_ohci_get_phy()` does not explicitly bound `num_phys` from modern `phys` phandles against `PHY_NUMBER`, so a device tree with more than three PHYs could write past `phy[]`. The legacy path does validate child `reg` against `PHY_NUMBER`. `phy_power_on(NULL)` behavior depends on the PHY API tolerating optional NULL handles; the code assumes unused slots are safe. Suspend disables a clock acquired through `devm_clk_get_enabled()`, then resume manually prepares/enables it, which is valid but requires balanced PM paths. The temporary `of_node = NULL` legacy workaround must be restored on every failure/removal path; the code restores it after `usb_add_hcd()` failure and in remove.

## Test signals
Validate modern `phys` bindings with one to three PHYs, legacy child-node PHY bindings, and no optional legacy PHY for unused slots. Probe should map MMIO, share IRQ, enumerate USB devices, and not create bogus USB child devices from legacy PHY child nodes. Suspend/resume should power-cycle PHYs and clock cleanly while preserving enumeration after resume. A negative DT test with too many modern PHYs is valuable because the array bound is not guarded in that path.
