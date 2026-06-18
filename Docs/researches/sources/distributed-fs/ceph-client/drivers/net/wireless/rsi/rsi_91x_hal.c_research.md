# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_hal.c

Purpose: RSI HAL transmit descriptor construction, bus packet dispatch, beacon/BT packet formatting, and firmware boot/loading for 9113/9116 devices.

Important APIs/functions: `rsi_prepare_mgmt_desc()` and `rsi_prepare_data_desc()` prepend device descriptors to mac80211 frames. `rsi_send_data_pkt()`, `rsi_send_mgmt_pkt()`, `rsi_send_bt_pkt()`, and `rsi_send_pkt_to_bus()` dispatch frames. `rsi_prepare_beacon()` builds firmware beacon descriptors. Firmware flow is handled by `rsi_hal_device_init()`, `rsi_hal_prepare_fwload()`, `rsi_load_9113_firmware()`, `rsi_load_9116_firmware()`, bootloader command helpers, ping-pong writes, and optional flash upgrade.

Control flow: TX descriptor functions reserve frame descriptor plus extended descriptor headroom, add alignment padding, populate queue/length/rate/security/sequence/VAP/retry fields, and special-case probe responses and EAPOL. Send functions validate interface/association state, write to bus, and return TX status. Firmware init waits for bootloader readiness, selects firmware metadata by coex mode/device model, loads from request_firmware, writes via bus master operations, validates CRC or burns flash for 9113, and jumps/TA-resets for 9116.

State and persistence: uses common FSM, coex mode, firmware version fields, EAPOL confirmation state, beacon count, adapter block size, host interface ops, flash capacity, bootloader timer state, and firmware filename.

Dependencies/integration: Linux firmware loader, mac80211 frame helpers, Bluetooth skb control, RSI host interface ops, SDIO/USB differences, management/core TX paths, and Kconfig-selected coex.

Risks: descriptor headroom/alignment mistakes corrupt frames. EAPOL/probe confirmation blocks queues until firmware confirms. Firmware loading depends on exact metadata offsets, bootloader register protocol, endian handling, and timers. 9113 flash upgrade validates image address/size but writes persistent flash.

Test signals: management/data/EAPOL/beacon TX, AP/STA/P2P modes, fixed-rate config, BT data, 9113 CRC-pass and CRC-upgrade paths, 9116 chunked bootload, USB/SDIO host ops, and firmware version debugfs output.
