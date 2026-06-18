# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/debugfs.c

## Purpose
Debugfs diagnostics and knobs for MT7603 aggregation statistics, transmit queues, EDCCA behavior, watchdog reset testing, reset causes, radio sensitivity, and dynamic sensitivity control.

## Important APIs, Types, And Functions
- `mt7603_reset_read()` reports reset-cause counters by human-readable reason.
- `mt7603_radio_read()` reports current sensitivity and false CCA counts.
- `mt7603_edcca_set()` and `mt7603_edcca_get()` back the writable `edcca` debugfs attribute and reinitialize EDCCA under `dev->mt76.mutex`.
- `mt7603_ampdu_stat_show()` displays aggregation length bucket boundaries and counters from `dev->mphy.aggr_stats`.
- `mt7603_init_debugfs()` registers the mt76 debugfs root plus `ampdu_stat`, `xmit-queues`, `edcca`, `reset_test`, `reset`, `radio`, `sensitivity_limit`, and `dynamic_sensitivity`.

## Control Flow
Device registration calls `mt7603_init_debugfs()` after mac80211 registration. Reads format live driver state through seq_file helpers. Writes to `edcca` alter `ed_monitor_enabled`, derive active `ed_monitor` from ETSI region, and call `mt7603_init_edcca()`.

## State And Persistence
Debugfs exposes mutable runtime fields: `ed_monitor_enabled`, `reset_test`, `sensitivity_limit`, and `dynamic_sensitivity`. Other files read counters and sensitivity state. Debugfs settings are not persistent across driver reload.

## Dependencies And Integration Points
Depends on mt76 debugfs registration, seq_file, debugfs attribute helpers, and runtime state updated by `mac.c` watchdog/sensitivity logic and `main.c` regulatory notifier.

## Risks
Debugfs writes can affect radio behavior and trigger watchdog test resets. Values are lightly constrained because debugfs is for privileged diagnostics. EDCCA changes depend on mutex serialization with channel/MAC work.

## Test Signals
Mount debugfs, read each file after probe and under traffic, toggle `edcca`, adjust `dynamic_sensitivity` and `sensitivity_limit`, and set `reset_test` to force each reset cause. Confirm no use-after-free during device removal while debugfs entries exist.
