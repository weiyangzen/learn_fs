# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.h

Purpose: Declares common ath9k initialization helpers for channel/rate tables and HT capability setup.

Important APIs: `ath9k_cmn_init_channels_rates()`, `ath9k_cmn_setup_ht_cap()`, and `ath9k_cmn_reload_chainmask()`.

Control flow: Driver probe code initializes supported bands, then HT capability setup is run per supported band and can be re-run when chainmasks change.

State/persistence: No direct state; callers pass `ath_common`, `ath_hw`, and mac80211 HT capability structures mutated by the implementation.

Dependencies/integration: Included by `common.h`, used by ath9k and ath9k_htc style common initialization.

Risks: Header is minimal and has no explicit include guard in this snapshot; duplicate inclusion is expected through controlled includes.

Test signals: Build coverage and device registration checks for visible channels/rates/HT capabilities.
