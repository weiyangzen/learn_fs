# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pcu.c

## Purpose
`pcu.c` controls ath5k Protocol Control Unit behavior: frame duration/ACK timing, MIB counter accumulation, station/BSSID/multicast/RX filters, TSF and beacon timers, coverage class timing, RX PCU enable/disable, operating mode, and PCU initialization. It bridges mac80211 state to hardware registers that implement 802.11 protocol behavior.

## Important APIs and Control Flow
Timing helpers include `ath5k_hw_get_frame_duration()`, which extends mac80211 duration calculation for turbo/half/quarter rate modes, `ath5k_hw_get_default_slottime()`, and `ath5k_hw_get_default_sifs()`. `ath5k_hw_write_rate_duration()` fills AR5212 rate-duration registers using either high ACK rates or base CCK/OFDM rates. ACK/CTS timeout setters validate against field width before writing `AR5K_TIME_OUT`.

Filter and identity APIs include `ath5k_hw_set_lladdr()`, `ath5k_hw_set_bssid()`, `ath5k_hw_set_bssid_mask()`, `ath5k_hw_set_mcast_filter()`, `ath5k_hw_get_rx_filter()`, and `ath5k_hw_set_rx_filter()`. RX filter setup handles AR5212 PHY error filters and AR5210 radar-by-promiscuous fallback.

Beacon/TSF control includes a careful `ath5k_hw_get_tsf64()` double-read under local IRQ disable, `ath5k_hw_set_tsf64()`, `ath5k_hw_reset_tsf()`, `ath5k_hw_init_beacon_timers()`, `ath5k_hw_check_beacon_timers()`, and `ath5k_hw_set_coverage_class()`. `ath5k_hw_set_opmode()` maps NL80211 AP/STA/adhoc/mesh/monitor modes to `AR5K_STA_ID1`, `AR5K_CFG`, and AR5210 beacon-control bits. `ath5k_hw_pcu_init()` restores BSSID, opmode, rate durations, RSSI/BMISS thresholds, MIC/QoS NOACK settings, coverage timing, and ACK bitrate policy.

## State, Dependencies, and Integration
Persistent state is split between registers and software fields: `ath_common` MAC/BSSID/AID/mask, `ah->stats`, `ah->survey`, `ah->ah_current_channel`, `ah->ah_bwmode`, `ah->ah_short_slot`, `ah->ah_coverage_class`, `ah->opmode`, `ah->nvifs`, `ah->ah_ack_bitrate_high`, and RX filter bits. Dependencies include mac80211 rates/channels, ath common cycle counters, unaligned helpers, register macros, and reset/beacon/config paths.

## Risks and Test Signals
Risks include TSF inconsistent reads, wrong beacon timer windows after IBSS TSF merges, RX filter mistakes affecting ACK/radar/PHY-error behavior, incorrect duration math for non-default bandwidths, and opmode bit drift across AR5210 versus AR5212. Test signals include stable IBSS without ramping latency, correct beacon timing in AP/mesh/STA modes, survey counters accumulating, ACK timeout/rate-duration sanity, BSSID mask behavior with multi-VIF, and RX filter changes matching monitor/AP/STA expectations.
