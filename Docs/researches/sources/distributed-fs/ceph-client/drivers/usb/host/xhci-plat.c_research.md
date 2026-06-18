# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.c

## Purpose
Implements generic platform-device bus glue for xHCI controllers. It handles MMIO mapping, DMA mask setup, clocks, resets, optional USB PHYs, firmware/DT/ACPI quirk discovery, dual-root-hub creation, sideband-aware suspend, runtime PM, and exported probe/remove/PM hooks used by SoC-specific wrappers.

## Important APIs, Types, And Functions
Exported APIs are `xhci_plat_probe()`, `xhci_plat_remove()`, and `xhci_plat_pm_ops`. Internal callbacks include `xhci_plat_setup()`, `xhci_plat_start()`, `xhci_generic_plat_probe()`, `xhci_plat_suspend_common()`, `xhci_plat_resume_common()`, runtime PM callbacks, and quirk dispatchers `xhci_priv_init_quirk()`, `xhci_priv_suspend_quirk()`, `xhci_priv_resume_quirk()`, and `xhci_priv_post_resume_quirk()`. Match data uses `struct xhci_plat_priv`.

## Control Flow
Module init initializes the platform HCD driver and registers `xhci-hcd`. Probe chooses a firmware-visible `sysdev`, configures a 64-bit DMA mask, enables runtime PM, creates the primary HCD, maps resource 0, gets optional `reg` and core clocks plus shared reset array, deasserts reset, enables clocks, copies match-data quirks, parses parent-chain properties, initializes optional USB PHYs, adds the primary HCD, creates/adds a shared HCD when needed, enables streams, then forbids runtime PM by default. Suspend can skip work when an xHCI sideband instance is active; otherwise it calls private suspend quirks, `xhci_suspend()`, and optional clock gating. Resume re-enables clocks, runs private resume/post-resume hooks, calls `xhci_resume()`, and refreshes runtime PM state.

## State And Persistence
Runtime state lives in `struct xhci_hcd`, HCD private `struct xhci_plat_priv`, clocks, reset controls, USB PHY handles, runtime PM state, and quirk flags. The `sideband_at_suspend` and `power_lost` fields affect PM recovery but are not persistent beyond the bound device.

## Dependencies And Integration Points
Depends on platform bus, OF/ACPI properties, DMA mapping, clock/reset/USB PHY APIs, generic xHCI core, `xhci-mvebu.h`, and `xhci-sideband`. Renesas and other wrappers call its exported probe/remove/PM operations with custom `struct xhci_plat_priv`.

## Risks And Test Signals
Risks include incorrect `sysdev` selection for DMA, clock/reset unwind bugs, PHY ownership conflicts with DWC3, shared-HCD lifetime errors, sideband suspend mismatches, and parent-property quirks unexpectedly applying to child controllers. Test signals include generic OF and ACPI probing, DWC3 child platform cases, PCI-parent child cases, USB2/USB3 enumeration, suspend/resume/runtime PM with wake and no-wake, sideband active suspend, missing optional PHYs/clocks, and reset/clock failure injection.
