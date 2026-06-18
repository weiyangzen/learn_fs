# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.h

## Purpose
Declares the WCN36xx power-management controller interface and the per-VIF power-state enum used by the driver.

## Important APIs, Types, and Functions
`enum wcn36xx_power_state` has `WCN36XX_FULL_POWER` and `WCN36XX_BMPS`, stored in `struct wcn36xx_vif`. The header declares `wcn36xx_pmc_enter_bmps_state()`, `wcn36xx_pmc_exit_bmps_state()`, and `wcn36xx_enable_keep_alive_null_packet()`.

## Control Flow and State
The header owns no runtime flow. Its enum values define the software power state that gates whether `pmc.c` sends BMPS exit requests and whether mac80211 beacon filtering is considered active for a VIF.

## Dependencies and Integration Points
Forward-declares `struct wcn36xx` and relies on including contexts for `struct ieee80211_vif`. Included through `wcn36xx.h`, making the PMC API available to `main.c` and other driver modules. The implementation delegates to SMD messages whose ABI is declared in `hal.h`.

## Risks and Test Signals
Prototype drift would break the power-save integration in `main.c`. Because only two software power states are modeled, additional firmware states such as IMPS, UAPSD, and WoWLAN are tracked elsewhere and must not be inferred from this enum. Test signals are compile coverage with mac80211 power-save code, BMPS enter/exit state transitions, and keepalive programming after association.
