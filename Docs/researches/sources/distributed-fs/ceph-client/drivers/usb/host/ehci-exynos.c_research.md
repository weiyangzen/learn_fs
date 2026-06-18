<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c` is the Samsung S5P/Exynos EHCI platform wrapper. It manages Exynos USB host clock, PHYs, optional VBUS GPIO, DMA-burst tuning, legacy PHY binding quirks, and system PM around the generic EHCI core. The source was read as a complete 323-line file.

## Important APIs, Types, and Functions

`struct exynos_ehci_hcd` stores the USB host clock, saved OF node, up to three PHY handles, and a `legacy_phy` flag. Important functions are `exynos_ehci_get_phy()`, `exynos_ehci_phy_enable()`, `exynos_ehci_phy_disable()`, `exynos_setup_vbus_gpio()`, `exynos_ehci_probe()`, `exynos_ehci_remove()`, `exynos_ehci_suspend()`, and `exynos_ehci_resume()`. `exynos_overrides` extends EHCI private storage.

## Control Flow

Probe coerces a 32-bit DMA mask, requests optional `"samsung,vbus"` GPIO high, creates the HCD, obtains PHYs through modern `phys` phandles or legacy child-node bindings, enables the `usbhost` clock, maps resources, gets the IRQ, powers PHYs, sets `ehci->caps`, temporarily clears `pdev->dev.of_node` for legacy PHY children to avoid generic USB device binding conflicts, enables DMA burst in instruction register 0, and calls `usb_add_hcd()`. Remove restores the OF node, removes the HCD, powers off PHYs, and releases the HCD. PM suspend calls `ehci_suspend()`, powers off PHYs, and disables the clock; resume reverses that and reapplies DMA burst tuning before `ehci_resume()`.

## State and Persistence Behavior

Runtime state is the HCD private Exynos structure, PHY power state, optional VBUS GPIO state, clock enable state, saved OF node pointer, and hardware DMA-burst register. No file-backed state is used.

## Dependencies and Integration Points

The driver depends on platform resources, OF matching `samsung,exynos4210-ehci`, generic PHY framework, clock framework, GPIO descriptors, and the common EHCI core. It bridges both modern and legacy Exynos PHY descriptions.

## Risks and Edge Cases

`exynos_ehci_get_phy()` counts `phys` phandles without bounding `num_phys` against `PHY_NUMBER`, so malformed DT with more than three PHYs risks array overrun. Legacy OF-node clearing is a fragile integration workaround and must be restored on every failure/remove path. PHY power-on rollback must match partial successes. DMA-burst tuning must be reprogrammed after resume.

## Test Signals

Test modern and legacy DT PHY bindings, absent optional VBUS GPIO, suspend/resume, PHY power-on failure rollback, high-speed transfer throughput with DMA burst enabled, and module remove after failed and successful probes. Static analysis should flag PHY array bounds if DT input is not constrained elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c -->
