# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.h

## Purpose
Defines the private platform xHCI extension structure and exported platform glue interfaces used by generic and SoC-specific xHCI platform drivers.

## Important APIs, Types, And Functions
`struct xhci_plat_priv` contains an optional firmware name, xHCI quirk bitmask, `power_lost`, `sideband_at_suspend`, and hook pointers for platform start, init, suspend, resume, and post-resume quirks. Helpers `hcd_to_xhci_priv()` and `xhci_to_priv()` cast the generic xHCI private area. Exported declarations are `xhci_plat_probe()`, `xhci_plat_remove()`, and `xhci_plat_pm_ops`.

## Control Flow
No code runs here. Match data in generic or SoC-specific drivers is copied into the HCD private area by `xhci_plat_probe()`, then the hooks are called during setup, start, suspend, resume, and post-resume paths.

## State And Persistence
The structure is runtime-only and stored in the extra private bytes requested by `xhci-plat.c` overrides. It persists for the lifetime of the HCD and carries platform-specific recovery decisions, but has no stable userspace or disk representation.

## Dependencies And Integration Points
The header is included by `xhci-plat.c`, `xhci-rcar.c`, and RZ helper code. It forms the callback contract that keeps SoC-specific register and firmware operations outside the generic platform wrapper.

## Risks And Test Signals
Risks include private-size mismatches, callbacks being called with uninitialized private data, and hook ordering assumptions across setup/start/PM. Test signals include builds of generic platform, Renesas R-Car/RZ, MVEBU, and Broadcom variants, plus PM tests that exercise every hook slot.
