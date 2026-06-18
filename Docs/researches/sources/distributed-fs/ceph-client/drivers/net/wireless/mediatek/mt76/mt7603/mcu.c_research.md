# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mcu.c

## Purpose
MT7603 MCU protocol implementation: command framing, response parsing, firmware selection/download/start, MCU teardown, EEPROM/calibration upload, channel switch commands, and transmit-power control commands.

## Important APIs, Types, And Functions
- `struct mt7603_fw_trailer` describes firmware version/build date/download length trailer.
- `mt7603_mcu_parse_response()` validates response sequence, reports timeouts, and feeds watchdog MCU-hang state.
- `mt7603_mcu_skb_send_msg()` prepends an MCU TXD, assigns nonzero 4-bit sequence numbers, selects firmware or normal port queue, handles legacy negative command IDs vs extended commands, and queues raw SKBs on `MT_MCUQ_WM`.
- `mt7603_mcu_init_download()`, `mt7603_mcu_start_firmware()`, and `mt7603_mcu_restart()` wrap ROM/firmware commands.
- `mt7603_load_firmware()` selects firmware by chip/revision, requests it, logs version/build time, switches scheduler bypass mode, downloads if ROM is ready and firmware is not already running, starts firmware, waits for ready bit, and records wiphy firmware version.
- `mt7603_mcu_init()` installs `mt76_mcu_ops` and loads firmware; `mt7603_mcu_exit()` requests restart download mode and purges responses.
- `mt7603_mcu_set_eeprom()` builds an efuse buffer-mode request from selected EEPROM offsets and sends it to firmware.
- `mt7603_mcu_set_tx_power()` sends EEPROM-derived target/rate/channel/temp compensation power fields.
- `mt7603_mcu_set_channel()` sends control/center channel, bandwidth, streams, SAR-limited txpower array, then sends txpower control.

## Control Flow
Hardware init calls `mt7603_mcu_init()` after DMA queues exist. Firmware load may skip download if a running bit is already set; otherwise it initializes target address/length, streams firmware chunks through common mt76 MCU helpers, starts firmware, and waits for initialization. Later init uploads EEPROM fields. Channel changes call `mt7603_mcu_set_channel()` and then `mt7603_mcu_set_tx_power()`. Exit sends restart-download and clears queued responses.

## State And Persistence
State includes `dev->mcu_running`, `dev->mcu_hang`, `dev->mt76.mcu_ops`, `dev->mt76.mcu.msg_seq`, `dev->mphy.txpower_cur`, and `hw->wiphy->fw_version`. Firmware is requested from the filesystem but not modified. EEPROM bytes are copied into request buffers and sent to firmware.

## Dependencies And Integration Points
Depends on Linux firmware loader, common mt76 MCU helpers, mt7603 firmware names/revision helpers, EEPROM offsets, DMA MCU queue allocation, and SAR/txpower helpers from mt76 core. RX event dispatch in `dma.c` must deliver MCU responses to common queues.

## Risks
Firmware selection by chip/revision must match available firmware files. The response parser only checks sequence, so command-specific status interpretation is minimal. Sequence space is 4 bits and skips zero; stale responses can cause `-EAGAIN` loops until timeout. EEPROM upload uses a fixed 0xff-entry request buffer and selected offsets, including unknown fields, so offset mistakes affect firmware calibration. Channel txpower subtracts 6 half-dBm for 2-chain operation and clamps to EEPROM limit; incorrect units break regulatory power.

## Test Signals
Probe all supported chip revisions with correct/missing/invalid firmware, verify firmware version string, command timeout behavior, MCU hang reset counter, channel switch across 20/40 MHz, SAR changes, txpower limits, and EEPROM upload success. Confirm teardown purges response queues and restart command does not hang remove.
