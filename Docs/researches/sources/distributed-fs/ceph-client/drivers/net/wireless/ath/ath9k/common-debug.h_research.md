# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.h

Purpose: Defines shared RX statistics and conditional debug helper prototypes/no-op stubs for ath9k common debug support.

Important APIs/types: `struct ath_rx_stats` records aggregate RX packets/bytes, CRC/decrypt/MIC/PHY errors, delimiter/decrypt-busy errors, per-PHY-error counters, length/OOM/rate/fragment drops, beacon/fragments, and spectral sample counters. Under `CONFIG_ATH9K_COMMON_DEBUG`, prototypes expose EEPROM and RX debugfs helpers; otherwise static inline no-ops preserve call sites.

Control flow: RX paths update `ath_rx_stats` directly or through `ath9k_cmn_debug_stat_rx()`. Debug initialization registers files only when common debug is built.

State/persistence: This header defines the persistent RX stats structure embedded in ath9k debug stats. It does not synchronize updates.

Dependencies/integration: Requires PHY error constants and `struct ath_rx_status` from ath9k hardware headers; included by `common.h` and `debug.h`.

Risks: Counter width is `u32`, so long-lived systems can wrap. No-op stubs mean tests must cover both debug-enabled and debug-disabled builds.

Test signals: Compile matrix with and without `CONFIG_ATH9K_COMMON_DEBUG`, RX counter increments, spectral sample good/error accounting, and debugfs output consistency with structure fields.
