# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/stats.h

## Purpose
Defines firmware statistics command and notification ABI. It includes older monolithic statistics notifications and newer typed system-statistics notifications for operational, PHY, MAC, RX, TX, duration, and HE counters.

## Important APIs, Types, And Functions
Core legacy structures include `iwl_notif_statistics_v10`, `iwl_notif_statistics_v11`, `iwl_notif_statistics`, `iwl_statistics_cmd`, and their nested RX/TX/general/load structs. Newer system-statistics APIs include `iwl_system_statistics_cmd`, `iwl_statistics_ntfy_hdr`, `iwl_system_statistics_notif_oper`, `iwl_system_statistics_part1_notif_oper`, `iwl_statistics_operational_ntfy`, `iwl_statistics_phy_ntfy`, `iwl_statistics_mac_ntfy`, `iwl_statistics_rx_ntfy`, `iwl_statistics_tx_ntfy`, `iwl_statistics_duration_ntfy`, and `iwl_statistics_he_ntfy`.

## Control Flow
The driver can request statistics, clear counters, disable unsolicited notifications, or configure system-statistics notification cadence and type masks. Firmware emits either legacy aggregate notifications or typed notifications with a common header identifying type, version, and size. Consumers parse nested per-MAC, per-link, per-PHY, and per-station arrays to update debugfs, survey, telemetry, and rate/control diagnostics.

## State And Persistence
No state is stored in this header, but firmware counters persist between reports until reset/clear semantics request clearing. Fields track beacon counts, missed beacons, channel load, RX/TX time, BT coexistence deferrals, aggregation outcomes, PHY errors, CCA, power/temperature, HE trigger/MU activity, and station energy. Some structures differ by MAC/link capacity constants.

## Dependencies And Integration Points
Includes `mac.h` and `mac-cfg.h` for MAC/link/station limits. Integrates with iwlwifi debugfs statistics, mac80211 survey/station reporting, firmware health monitoring, beacon filtering, BT coexistence diagnostics, MLO/link accounting, and channel-load based policy decisions.

## Risks
Versioned structures differ in array dimensions and field availability; parsing by the wrong notification version can shift every following counter. Many counters are firmware-defined diagnostic values with sparse comments, so higher-level policy must avoid overinterpreting them. Reset/disable flags can unintentionally suppress periodic diagnostics or clear evidence needed for debugging.

## Test Signals
Issue on-demand and periodic stats commands, verify notification type/version/size handling, compare legacy and typed reports on supported firmware, validate channel load and beacon counters during association, force missed beacons and TX failures, and inspect HE counters during HE trigger/MU traffic. Sparse endian checks help catch missing `le32_to_cpu()` conversions.
