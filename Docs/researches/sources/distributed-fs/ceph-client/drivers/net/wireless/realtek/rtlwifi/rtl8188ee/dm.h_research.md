# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.h

## Purpose

`dm.h` is the RTL8188EE dynamic-management contract. It defines antenna identifiers, DM-specific RF/BB/MAC register aliases, threshold constants, rate-adaptive and antenna-diversity enums, the software antenna-try state structure, and the functions exported by `dm.c`.

## Important APIs, Types, And Constants

The register macros map dynamic-management names to hardware offsets used by DIG, antenna diversity, false-alarm accounting, EDCA tuning, TX-power tracking, and IQK matrix updates. Thresholds such as `DM_DIG_FA_TH0/1/2`, `DM_DIG_FA_UPPER/LOWER`, `TX_POWER_NEAR_FIELD_THRESH_LVL1/2`, and `TXPWRTRACK_MAX_IDX` encode the main DM heuristics. `enum pwr_track_control_method` selects between baseband swing and TXAGC power tracking. `enum _ANT_DIV_TYPE` is in `phy.h`, while `dm.h` defines the concrete main/aux mapping values consumed by `dm.c`.

The exported functions connect `dm.c` to hardware initialization, periodic watchdog work, TX descriptor construction, RX statistics collection, thermal tracking, EDCA setup, and rate-adaptive-mask initialization.

## Control Flow And Integration

The header itself contains no executable control flow. Its declarations are consumed by `hw.c` during initialization and network-state changes, by TX/RX paths through antenna-selection helpers, and by timer setup through `rtl88e_dm_fast_antenna_training_callback()`. The constants are also tightly coupled to `reg.h` because many values are raw hardware offsets.

## State And Persistence Behavior

`struct swat_t` carries software antenna-try counters and RSSI history, but most active DM state lives in shared driver structures declared elsewhere. The header’s state impact is mostly ABI-like: changing constants or enum values directly changes how `dm.c` writes registers and interprets antenna modes.

## Dependencies, Risks, And Test Signals

`dm.h` assumes Linux kernel integer types, `struct ieee80211_hw`, `struct timer_list`, and rtlwifi shared enums such as `enum rtl_led_pin` are already visible through including translation units. Risks are primarily semantic: duplicated or stale register aliases can cause silent hardware misconfiguration. Tests should compile all RTL8188EE objects, verify that public prototypes match `dm.c`, and exercise each antenna-diversity mode and TX-power tracking mode that relies on these constants.
