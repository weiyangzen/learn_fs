# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.c

## Purpose
This file implements MT7921 firmware command and event handling. It parses MCU responses, routes unsolicited events, loads CLC data from firmware, queries NIC capabilities, starts firmware, configures EDCA/ROC/channel/eeprom/power-save/beacon filtering/stations/sniffer/beacon offload/CLC/thermal/RF pin/RX filters/RSSI monitor, and provides suspend IPv6 offload glue.

## Important APIs, Types, And Functions
Key exports are `mt7921_mcu_parse_response()`, `mt7921_mcu_set_suspend_iter()`, `mt7921_mcu_rx_event()`, `mt7921_mcu_uni_tx_ba()`, `mt7921_mcu_uni_rx_ba()`, `mt7921_run_firmware()`, `mt7921_mcu_radio_led_ctrl()`, `mt7921_mcu_set_tx()`, `mt7921_mcu_set_roc()`, `mt7921_mcu_abort_roc()`, `mt7921_mcu_set_chan_info()`, `mt7921_mcu_set_eeprom()`, `mt7921_mcu_uni_bss_ps()`, `mt7921_mcu_set_bss_pm()`, `mt7921_mcu_sta_update()`, `mt7921_mcu_set_beacon_filter()`, `mt7921_get_txpwr_info()`, `mt7921_mcu_set_sniffer()`, `mt7921_mcu_config_sniffer()`, `mt7921_mcu_uni_add_beacon_offload()`, `mt7921_mcu_set_clc()`, `mt7921_mcu_get_temperature()`, `mt7921_mcu_wf_rf_pin_ctrl()`, `mt7921_mcu_set_rxfilter()`, and `mt7921_mcu_set_rssimonitor()`.

## Control Flow
Responses are parsed by command type; timeouts log and reset the device, sequence mismatches return `-EAGAIN`, and selected commands extract status fields. RX MCU events are separated into UNI unsolicited events, legacy unsolicited events, and normal command responses. Events trigger ROC grants, scan completion queueing, connection-loss notification, firmware debug logging, coredump collection, low-power trace events, TX done processing, and CQM RSSI notifications.

Firmware run loads firmware, queries NIC capabilities, loads CLC data from the firmware trailer, marks MCU running, and enables firmware logs. CLC loading scans non-download firmware regions, stores matching CLC blobs, and submits country/environment rules with fallback to alpha2 `00`. Channel, ROC, EDCA, beacon, station, and power-save helpers build packed MCU payloads from mac80211 vif/channel/station state.

## State And Persistence
The file mutates `dev->phy.clc[]`, `dev->phy.clc_chan_conf`, chip capability flags, chainmask/antenna capabilities, 6 GHz support, MAC address, SDIO scheduler quota, firmware logging state, `MT76_STATE_MCU_RUNNING`, ROC grant/timer state, coredump state, RSSI/CQM delivery, and firmware-side BSS/STA/channel/filter/offload state.

## Dependencies And Integration Points
It depends on mt76 MCU queues, connac/connac2 command formats, firmware trailer structures, cfg80211/mac80211 state, coredump support, tracepoints, ACPI/DT power-limit helpers, SDIO scheduler state, and helpers from `mac.c` and `main.c`.

## Risks
Firmware ABI packing is dense and command-specific; field or endian mistakes cause subtle firmware failures. Response parsing resets the device on timeout, so spurious timeout handling has high blast radius. CLC parsing trusts trailer region lengths after bounds checks and must avoid reinitializing buffers across chip reset. ROC grant handling assumes event TLV layout and request type. Beacon offload has a 512-byte payload limit. RX event routing must free or retain SKBs exactly once.

## Test Signals
Test firmware download, NIC capability parsing, CLC disabled/enabled/fallback flows, country updates, EDCA and MU EDCA, ROC grant/abort, channel switch reasons, eeprom mode, BSS PM and beacon filtering, station records, BA commands, TX power query, sniffer config, beacon offload size limits, thermal query, RF pin rfkill polling, RX filter changes, RSSI monitor events, coredump events, scan events, and command timeout recovery.
