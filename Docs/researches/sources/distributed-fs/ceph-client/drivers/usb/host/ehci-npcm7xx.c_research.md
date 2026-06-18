# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-npcm7xx.c

## Purpose
Nuvoton NPCM7xx EHCI platform glue. It provides a minimal OpenFirmware platform driver that sets a 32-bit DMA mask, maps EHCI registers starting at offset zero, registers the HCD, and wires suspend/resume to the common EHCI power-management helpers.

## Important APIs, types, and functions
The main entry points are `npcm7xx_ehci_hcd_drv_probe()`, `npcm7xx_ehci_hcd_drv_remove()`, `ehci_npcm7xx_drv_suspend()`, and `ehci_npcm7xx_drv_resume()`. `ehci_npcm7xx_hc_driver` is initialized by `ehci_init_driver()` without custom overrides. The OF match table accepts `nuvoton,npcm750-ehci`.

## Control flow
Probe rejects disabled USB, obtains IRQ 0, coerces a 32-bit coherent DMA mask, creates an HCD, maps the first memory resource, records resource bounds, points `hcd_to_ehci(hcd)->caps` at `hcd->regs`, then calls `usb_add_hcd()` with `IRQF_SHARED`. Remove calls `usb_remove_hcd()` and `usb_put_hcd()`. Suspend delegates to `ehci_suspend()` with wakeup policy; resume calls `ehci_resume(hcd, false)`.

## State and persistence behavior
There is no driver-private state. Runtime state is the HCD/EHCI core state plus mapped hardware registers. The DMA mask setting persists on the device object for allocations made by USB core/EHCI pools.

## Dependencies and integration points
Depends on platform resources, OF matching, DMA mapping, USB HCD core, and common EHCI implementation. It uses `usb_hcd_platform_shutdown` for platform shutdown.

## Risks and edge cases
The driver assumes capability registers begin at resource offset zero. It has no explicit clocks, resets, or PHY handling, so board firmware/SoC integration must leave the controller powered and clocked. Missing `platform_set_drvdata()` is covered by `usb_add_hcd()`/HCD platform behavior only if the core stores it as expected for remove.

## Test signals
NPCM750 DT probe, DMA mask setup, IRQ sharing, root-hub enumeration, system suspend/resume with and without wakeup, shutdown, and repeated module bind/unbind are the main signals.
