# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.h

## Purpose
Declares the small RTL8192DE RF helper interface used by PHY and hardware initialization code.

## Important APIs, Types, And Functions
Exports `rtl92d_phy_rf6052_config()` for RF table programming, `rtl92d_phy_enable_anotherphy()` for temporary peer-PHY enablement, and `rtl92d_phy_powerdown_anotherphy()` for restoring the peer-PHY power state.

## Control Flow
The header has no executable flow. Its prototypes support the flow where `phy.c` calls RF6052 configuration and the RF/channel code temporarily enables the other PHY before DBI-based operations.

## State And Persistence
No state is owned here. The declared functions mutate `rtl_hal` flags and hardware RF power/register state in their implementations.

## Dependencies And Integration Points
Requires `struct ieee80211_hw` and bool definitions from included users. It is consumed by `phy.c` and `rf.c` and complements `phy.h`.

## Risks
The API exposes low-level dual-PHY power controls without ownership annotations; callers must pair temporary enablement and powerdown correctly.

## Test Signals
Compilation and successful RF initialization are the primary signals. Dual-MAC bring-up exercises all three declarations.
