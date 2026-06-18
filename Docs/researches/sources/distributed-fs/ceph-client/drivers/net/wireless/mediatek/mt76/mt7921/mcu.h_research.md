# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.h

## Purpose
This header defines MT7921-specific MCU event, command, testmode, CLC, TX power, and RF-pin payload structures and constants used by `mcu.c`, `debugfs.c`, and testmode code.

## Important APIs, Types, And Functions
Important structures include `mt7921_mcu_tx_done_event`, `mt7921_mcu_eeprom_info`, `mt7921_mcu_ant_id_config`, `mt7921_txpwr_req`, `mt7921_txpwr_event`, `mt7921_wf_rf_pin_ctrl_event`, `mt7921_rftest_cmd`, `mt7921_rftest_evt`, and `mt7921_clc_info_tlv`. Constants define the rate encoding masks (`MT_RA_RATE_*`), beamforming flags, rate report event id, RF test modes, and CLC channel-conf bitmap meaning.

## Control Flow
There is no executable flow. `mcu.c` casts firmware SKB data to these structures while parsing TX done, EEPROM, TX power, RF pin, RF test, and CLC response/event payloads.

## State And Persistence
All structures are transient host-side views of firmware messages. Persistent effects are held in firmware and driver fields updated from those messages, such as TX power tables, CLC channel configuration, RF pin result, and TX status.

## Dependencies And Integration Points
The header includes `mt76_connac_mcu.h` and references `MT7921_EEPROM_BLOCK_SIZE`, `struct mt7921_txpwr`, and common connac MCU formats. It is included by MT7921 common MCU/debug/test paths.

## Risks
Packed layout mismatches break firmware communication. The TX done event includes fixed-size reserved and TXS regions; consumers assume `txs` starts at the expected offset. CLC channel-conf comments are the contract used by regulatory channel disabling, so bit interpretation must stay synchronized with firmware.

## Test Signals
Signals include successful TX done parsing, EEPROM block reads, TX power debugfs dumps, RF pin ctrl responses, RF test commands, and CLC event parsing on firmware revisions that report UNII channel configuration.
