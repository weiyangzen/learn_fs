# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.h

## Purpose
`phy_ac.h` defines register constants and the private-state shell for b43 AC-PHY support. It also declares the AC-PHY operations table consumed by common PHY allocation.

## Important APIs, Types, and Data
- AC register macros cover baseband config, band control, table ID/offset/data registers, classifier control, bandwidth registers, RF control command, and per-core clip-disable registers.
- Bit masks include reset CCA, 5 GHz band select, CCK/OFDM/waited classifier enables, and clip disable bits for cores 1-3.
- `struct b43_phy_ac` is currently empty.
- `extern const struct b43_phy_operations b43_phyops_ac` exposes the implementation in `phy_ac.c`.

## Control Flow
The header has no executable flow. It provides constants and declarations used when common code dispatches into the AC-PHY vtable.

## State and Persistence
No state is owned in the header. The empty AC private struct creates a typed storage slot under `struct b43_phy`, and the register definitions name persistent AC PHY hardware state.

## Dependencies and Integration Points
- Includes `phy_common.h` for the vtable type and device declarations.
- Used by `phy_ac.c` and by common PHY selection when `CONFIG_B43_PHY_AC` is enabled.
- Register definitions are potential integration points for future AC init, channel, classifier, bandwidth, and RF-control code.

## Risks and Edge Cases
- The empty private state signals incomplete AC support; future code must add fields without assuming old instances carry calibration or channel state.
- Register macros are low-level and do not enforce valid sequencing; table access and RF-control changes should be wrapped by dedicated helpers before broader use.
- The operations declaration can make AC appear supported even while critical callbacks remain absent in the implementation.

## Test Signals
- Build tests with AC-PHY enabled catch declaration drift.
- Runtime AC hardware tests should verify classifier enablement, band switching, table access, RF control, and clipping behavior once implementation grows.
