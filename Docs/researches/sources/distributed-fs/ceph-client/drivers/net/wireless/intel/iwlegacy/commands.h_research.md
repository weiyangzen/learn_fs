# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/commands.h

## Purpose

`commands.h` is the firmware command and notification ABI contract for the `iwlegacy` Intel 3945/4965 wireless driver. It assigns uCode command IDs, sequence-number helpers, status bits, endian-annotated packed command layouts, notification/response layouts, rate/antenna/security bitfields, and shared constants used by `common.c`, `3945.c`, `4965.c`, rate scaling, scan, station, calibration, and interrupt/Rx handlers.

This header is not algorithmic code. Its main job is to make host memory and firmware DMA buffers match the legacy microcode wire format exactly. The ABI covers RXON channel state, QoS, stations, WEP/CCMP/TKIP keys, RX metadata, TX descriptors and completion status, link-quality retry tables, Bluetooth coexistence, spectrum measurement, power-save, scan requests/results, beaconing, statistics, sensitivity, PHY calibration, LEDs, and the top-level `struct il_rx_pkt` union used to decode all inbound firmware packets.

## Important APIs, Types, and Constants

The leading command enum maps host-visible command IDs such as `N_ALIVE`, `N_ERROR`, `C_RXON`, `C_ADD_STA`, `C_TX`, `C_SCAN`, `C_STATS`, `C_SENSITIVITY`, `N_RX_PHY`, `N_RX_MPDU`, `N_RX`, and `N_COMPRESSED_BA`. `IL_CN_MAX` marks the command namespace boundary. `il_get_cmd_string()` in `common.c` depends on this enum staying in sync.

Common framing types and helpers include `struct il_cmd_header`, `IL_CMD_FAILED_MSK`, `SEQ_TO_QUEUE()`, `QUEUE_TO_SEQ()`, `SEQ_TO_IDX()`, `IDX_TO_SEQ()`, `SEQ_HUGE_FRAME`, and `SEQ_RX_FRAME`. These encode the command queue ID, queue slot, huge command flag, and unsolicited firmware notification bit that `il_enqueue_hcmd()` and `il_tx_cmd_complete()` use to route responses.

Radio/rate/power ABI definitions include `IL_CCK_RATES`, `IL_OFDM_RATES`, `IL_MAX_RATES`, `RATE_MCS_*` flags, `RATE_MCS_ANT_*` masks, `struct il3945_tx_power`, `struct il3945_power_per_rate`, `union il4965_tx_power_dual_stream`, `struct tx_power_dual_stream`, and `struct il4965_tx_power_db`. These are consumed by transmit power table commands, channel switch commands, rate control, and Tx command setup.

Lifecycle and control command layouts include `struct il_init_alive_resp`, `struct il_alive_resp`, `struct il_error_resp`, `struct il3945_rxon_cmd`, `struct il4965_rxon_cmd`, `struct il_rxon_cmd`, `struct il3945_rxon_assoc_cmd`, `struct il4965_rxon_assoc_cmd`, `struct il_rxon_time_cmd`, 3945/4965 channel switch commands, and `struct il_csa_notification`.

Station/security structures include station table IDs (`IL_AP_ID`, `IL_STA_ID`, `IL3945_BROADCAST_ID`, `IL4965_BROADCAST_ID`, `IL_INVALID_STATION`), station flags (`STA_FLG_*`, `STA_MODIFY_*`), `struct il4965_keyinfo`, `struct sta_id_modify`, 3945/4965/common add-station commands, add/remove station responses, `struct il_rem_sta_cmd`, `struct il_wep_key`, and `struct il_wep_cmd`.

RX/TX data plane structures include 3945 RX frame stats/header/end layouts with `static_assert()` offset checks, 4965 PHY metadata (`struct il4965_rx_non_cfg_phy`, `struct il_rx_phy_res`, `struct il_rx_mpdu_res_start`), 3945 and 4965 Tx command layouts (`struct il3945_tx_cmd`, `struct il_tx_cmd`), Tx response/status enums, aggregation status records, `struct il4965_tx_resp`, and `struct il_compressed_ba_resp`.

Management and background operation structures include `struct il_link_quality_cmd`, `struct il_bt_cmd`, spectrum measurement command/response/notification types, power table/sleep/card-state/thermal-kill types, scan channel/scan command/result/complete types, beacon command/notification types, 3945/4965 statistics trees, missed beacon notification, sensitivity command, PHY calibration command, LED command, and final `struct il_rx_pkt`.

## Control Flow and Data Flow

Host-to-firmware traffic normally starts in driver code that populates one of this header's packed command structs, wraps it in `struct il_host_cmd`, and calls `il_send_cmd*()` from `common.c`. `il_enqueue_hcmd()` then copies the command payload into a DMA command queue buffer, prepends `struct il_cmd_header`, encodes queue/slot/huge state into `sequence`, maps it for DMA, attaches it to a TFD, and advances the command queue write pointer.

Firmware-to-host traffic arrives as `struct il_rx_pkt`. The RX interrupt/tasklet path uses the packet header's command ID and sequence fields to distinguish command completions from unsolicited notifications. Command completions flow to `il_tx_cmd_complete()`, which uses the sequence helpers from this header to find the original command metadata and wake synchronous waiters or invoke callbacks. Unsolicited notifications are dispatched through per-command handlers registered in driver state.

RXON flow uses `struct il_rxon_cmd` as a common superset that can be converted by chip-specific code into 3945 or 4965 command layouts. A full `C_RXON` retunes channel and clears firmware station/Tx-power state; lighter association changes may use `C_RXON_ASSOC` when `il_full_rxon_required()` says the change is allowed. `C_RXON_TIMING` carries TSF/beacon timing separately.

Station flow uses `C_ADD_STA` to create or modify firmware station table entries. The `sta_id`, station flags, encryption key fields, TID disable mask, BA add/remove fields, and HT aggregation density/factor fields are shared with `common.c` station setup and 4965 link-quality commands. `C_REM_STA` removes entries by MAC address.

Scan flow builds either `struct il3945_scan_cmd` or `struct il_scan_cmd`: a fixed scan header, an embedded Tx probe command header, directed SSID entries, a probe request frame, and a trailing per-channel table. Firmware then emits `N_SCAN_START`, `N_SCAN_RESULTS`, and `N_SCAN_COMPLETE`, decoded with the scan notification structures.

## State and Persistence Behavior

The header itself stores no runtime state, but nearly every definition describes persistent firmware or driver state. RXON commands mutate firmware channel/filter/association/rate state and may clear station and Tx-power tables. Station commands mutate the microcode station table and key table. Power commands configure sleep policy. Scan commands temporarily move firmware off-channel and produce stateful notifications. Statistics notifications report counters that firmware accumulates and sometimes clears. Sensitivity and calibration commands update firmware DSP/PHY working tables.

Because these structures are DMA-visible ABI, field order, packing, fixed endianness, and flexible-array placement are persistent compatibility constraints. The `__packed`, `__le*`, `DECLARE_FLEX_ARRAY`, and `static_assert(offsetof(...))` usage is part of that contract.

## Dependencies and Integration Points

`commands.h` includes `<linux/ieee80211.h>` and relies on Linux kernel types, endian annotations, `BIT()`, Ethernet address sizes, and flexible array helpers. `common.h` includes and republishes many of these types through driver APIs. `common.c` uses the command IDs, sequence helpers, RXON/station/power/scan/QoS/TX/RX/security/statistics structs, and notification union. Chip-specific 3945 and 4965 files translate the common forms into device-specific layouts and provide operation callbacks for command sizing, RXON commit, scanning, Tx power, and LED behavior.

mac80211 integration depends on this ABI through TX/RX flags, `struct ieee80211_hdr` flexible arrays in Tx and beacon commands, scan request construction, QoS EDCA parameters, HT capabilities/rate tables, and RX status flags derived from firmware decrypt and PHY status fields.

## Risks and Edge Cases

ABI drift is the main risk. Any field reorder, type-width change, missing `__packed`, wrong `__le*` conversion, or incorrect flexible-array offset can corrupt firmware command or notification parsing.

The header contains parallel 3945 and 4965 layouts with subtly different field widths and extra fields. Callers must route commands through chip-specific size/build helpers; using `struct il_rxon_cmd` or `struct il_addsta_cmd` directly with the wrong command size can send garbage or omit required fields.

Many bit masks are defined as already endian-converted constants, while some status masks are host-endian. Call sites must avoid double conversion and compare in the same endian domain.

Full `C_RXON` is destructive to station and Tx-power firmware state. Code that changes RXON fields must follow up by restoring stations and power tables or use `C_RXON_ASSOC` when safe.

Scan command construction is size-sensitive: `IL_MAX_SCAN_SIZE`, `IL_MAX_CMD_SIZE`, probe request length, direct SSID count, and channel-table length must fit the command queue's huge slot rules.

Security status handling must distinguish TKIP bad TTAK, bad ICV/MIC, and successful hardware decrypt. Incorrect interpretation can either drop recoverable packets or mark corrupted plaintext as decrypted.

## Test Signals

Strong signals include `W=1`/sparse builds that validate endian annotations and packed struct usage, allmodconfig-style builds with `CONFIG_IWLEGACY`, `CONFIG_IWL3945`, `CONFIG_IWL4965`, debugfs, and PM enabled, and compile coverage after any command layout edit.

Runtime signals include successful firmware boot with both initialize and runtime `N_ALIVE`, successful command completion matching through `sequence`, association requiring full RXON plus station restore, RXON_ASSOC-only changes, station add/remove with key and HT flags, active/passive scan completion, Tx status and compressed BA handling, RX decrypt flag handling, statistics/sensitivity notifications, channel switch notifications, and RF-kill/card-state transitions.

Fault-oriented tests should cover command queue timeout, command failure flag handling, scan abort, firmware error notification decoding, command-size assertions for huge scan commands, and chip-specific 3945 versus 4965 command sizing.
