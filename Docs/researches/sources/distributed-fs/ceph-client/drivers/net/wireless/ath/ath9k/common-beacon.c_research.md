# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.c

Purpose: Provides shared ath9k/ath9k-common beacon timer calculations for station, IBSS, and AP modes.

Important APIs/functions: `ath9k_cmn_beacon_config_sta()` fills `struct ath9k_beacon_state` for station BMISS/sleep timers. `ath9k_cmn_beacon_config_adhoc()` prepares IBSS SWBA timing. `ath9k_cmn_beacon_config_ap()` prepares AP/mesh staggered SWBA timing. `ath9k_get_next_tbtt()` is the core helper that advances TSF by a fudge factor and software beacon response time, then rounds to the next beacon interval.

Control flow: STA configuration is skipped with `-EPERM` until `ATH_OP_PRIM_STA_VIF` is set. It computes next TBTT and DTIM from current TSF, clamps BMISS threshold to 1..15, selects a 100 ms sleep duration rounded to beacon/DTIM periods, and sets TSF out-of-range threshold. IBSS converts interval to usec, chooses first TBTT directly for creators or next TBTT for joiners, and toggles SWBA in `ah->imask`. AP divides the beacon interval by buffer count for staggered SWBA and toggles SWBA similarly.

State/persistence: Mutates `struct ath_beacon_config` (`intval`, `nexttbtt`) and `ah->imask`; station mode also fills a caller-supplied `struct ath9k_beacon_state` consumed by hardware timer programming.

Dependencies/integration: Used by `beacon.c`, depends on `common.h`, hardware TSF reads, `ATH_OP_PRIM_STA_VIF`, and ath debug logging.

Risks: Units differ by mode: `beacon_interval` is in TU, while `intval` and `nexttbtt` are programmed in usec. Incorrect `bc_buf` or zero intervals can break SWBA cadence. BMISS threshold clamping affects roaming and false disconnect behavior.

Test signals: Station association BMISS timers, DTIM sleep alignment, IBSS creator and joiner beacon start, AP multi-BSS staggered SWBA interval, and interrupt mask toggling when beacons are enabled/disabled.
