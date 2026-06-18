# sources/distributed-fs/ceph-client/include/linux/phy/phy-sun4i-usb.h

## Purpose
Allwinner sun4i USB PHY helper header for squelch-detect control.

## Important APIs, Types, and Functions
Declares `sun4i_usb_phy_set_squelch_detect(struct phy *phy, bool enabled)` and includes the generic PHY header.

## Control Flow
Consumers call the helper to enable or disable squelch detect on a sun4i USB PHY. Implementation-specific register programming lives outside this header.

## State and Persistence
No local state. The enabled setting persists in sun4i USB PHY hardware until changed or reset.

## Dependencies and Integration Points
Integrates Allwinner USB PHY drivers with generic `struct phy` consumers, likely USB controller glue that needs analog squelch behavior.

## Risks
Incorrect squelch settings can affect USB line-state detection and link reliability. There is no compile-time stub, so builds require the provider symbol when referenced.

## Test Signals
Allwinner USB host/device enumeration tests and suspend/resume or cable attach/detach tests with squelch toggling.
