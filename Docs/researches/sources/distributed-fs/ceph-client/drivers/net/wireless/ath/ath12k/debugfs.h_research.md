# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.h

## Purpose
Declares the debugfs integration points and TPC formatting constants/enums. It also provides no-op stubs when debugfs is disabled.

## Important APIs, Types, And Functions
Enabled declarations include SOC create/destroy, radio register/unregister, vif debugfs add, pdev debugfs create, and inline accessors for extended RX stats state/filter. Constants define CCK/OFDM/HT/VHT/HE/EHT rate counts, NSS values, TPC wait time, invalid/max TPC values, table dimensions, modulation limit, and buffer size. Enums define WMI TPC preamble/bandwidth values, control-mode indices, and supported mode bits.

## Control Flow
No direct runtime flow. Compile-time `CONFIG_ATH12K_DEBUGFS` selects real functions and state accessors or no-op/false/zero stubs, allowing callers to avoid preprocessor branches.

## State And Persistence
The header does not store state; it exposes access to `ar->debug.extd_rx_stats` and `ar->debug.rx_filter` when debugfs exists. TPC constants determine allocation and formatting sizes in `debugfs.c`.

## Dependencies And Integration Points
References `ath12k_base`, `ath12k`, and mac80211 `ieee80211_hw`/`ieee80211_vif` types through declarations. Integrated with core startup, mac80211 vif creation, DP monitor filtering, and WMI TPC stats.

## Risks
`TPC_STATS_WAIT_TIME` is defined twice with the same value, which is benign but noisy. Rate and mode enum values must match firmware TPC data layout; mismatches lead to misleading debug output. Disabled stubs return false/zero, so production code must not depend on debugfs side effects.

## Test Signals
Build with `CONFIG_ATH12K_DEBUGFS=y` and disabled. Runtime TPC stats should fit the declared buffer and reflect expected preamble/mode mappings for 2/5/6 GHz and EHT puncturing cases.
