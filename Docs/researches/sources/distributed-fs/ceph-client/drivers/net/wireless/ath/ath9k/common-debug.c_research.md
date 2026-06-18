# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.c

Purpose: Implements common debugfs readers and RX statistic accounting shared by ath9k components.

Important APIs/functions: Exported functions are `ath9k_cmn_debug_modal_eeprom()`, `ath9k_cmn_debug_base_eeprom()`, `ath9k_cmn_debug_stat_rx()`, `ath9k_cmn_debug_recv()`, and `ath9k_cmn_debug_phy_err()`. File operations expose `modal_eeprom`, `base_eeprom`, `recv`, and `phy_err`.

Control flow: EEPROM readers allocate fixed buffers, call `ah->eep_ops->dump_eeprom()` with base/modal selection, copy data to user, and free. RX stat accounting increments all-packet/byte counts, descriptor error counts, and per-PHY-error buckets when `rs_phyerr` is in range. Debugfs read paths format accumulated common RX counters or named PHY error counters into temporary buffers and return them through `simple_read_from_buffer()`.

State/persistence: Persistent stats live in caller-owned `struct ath_rx_stats`. Debugfs files hold private data pointers to `ath_hw` or `ath_rx_stats`; buffers are per-read allocations only.

Dependencies/integration: Depends on debugfs, EEPROM ops, `struct ath_rx_status`, PHY error enum values, and exported common debug declarations. `debug.c` registers these files under the ath9k debugfs directory.

Risks: Fixed output buffers can truncate future expanded counter sets. Stat increments are not locked here, so readers can observe racing updates. EEPROM dump size assumptions must match hardware implementation.

Test signals: Read debugfs EEPROM files on supported cards, inject RX statuses for CRC/decrypt/MIC/PHY errors, verify per-PHY counters, and confirm disabled common-debug builds compile to inline no-ops.
