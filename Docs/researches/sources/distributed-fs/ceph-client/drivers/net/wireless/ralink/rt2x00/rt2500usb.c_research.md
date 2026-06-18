# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500usb.c

## Purpose

`rt2500usb.c` is the device-specific Linux driver for Ralink RT2570 USB wireless adapters in the rt2x00 stack. It connects USB vendor requests and RT2570 register semantics to the generic rt2x00 queue, EEPROM, mac80211, LED, rfkill, crypto, link-quality, and device-state callbacks.

The driver handles register access, BBP/RF indirect programming, EEPROM validation, radio bring-up, RF channel tables, power management, beacon upload, descriptor formatting, RX completion parsing, and USB device binding for many vendor/product IDs. It supports legacy 802.11b/g and limited 5 GHz operation when the RF5222 radio is present.

## Important APIs, types, and functions

Register access is centralized in `rt2500usb_register_read()`, `rt2500usb_register_write()`, their `_lock` variants, and `rt2500usb_register_multiwrite()`. They issue rt2x00 USB vendor requests using little-endian 16-bit CSR values. `rt2500usb_regbusy_read()` polls busy bits and backs the `WAIT_FOR_BBP` and `WAIT_FOR_RF` macros.

Indirect PHY access is implemented by:

- `rt2500usb_bbp_write()` and `rt2500usb_bbp_read()`, which serialize through `rt2x00dev->csr_mutex`, poll `PHY_CSR8_BUSY`, and use `PHY_CSR7` for data/register/read-control fields.
- `rt2500usb_rf_write()`, which polls `PHY_CSR10_RF_BUSY`, writes low RF bits through `PHY_CSR9`, writes high RF bits and bit count through `PHY_CSR10`, then updates the rt2x00 RF cache.

Major configuration callbacks include `rt2500usb_config_key()`, `rt2500usb_config_filter()`, `rt2500usb_config_intf()`, `rt2500usb_config_erp()`, `rt2500usb_config_ant()`, `rt2500usb_config_channel()`, `rt2500usb_config_txpower()`, `rt2500usb_config_ps()`, and aggregate `rt2500usb_config()`.

Initialization and state callbacks include `rt2500usb_init_registers()`, `rt2500usb_wait_bbp_ready()`, `rt2500usb_init_bbp()`, `rt2500usb_enable_radio()`, `rt2500usb_disable_radio()`, `rt2500usb_set_state()`, and `rt2500usb_set_device_state()`.

Queue and frame handling includes `rt2500usb_start_queue()`, `rt2500usb_stop_queue()`, `rt2500usb_write_tx_desc()`, `rt2500usb_write_beacon()`, `rt2500usb_get_tx_data_len()`, `rt2500usb_fill_rxdone()`, and the beacon URB callback `rt2500usb_beacondone()`.

Probe-time functions include `rt2500usb_validate_eeprom()`, `rt2500usb_init_eeprom()`, `rt2500usb_probe_hw_mode()`, `rt2500usb_probe_hw()`, and USB module binding through `rt2500usb_probe()` and `rt2500usb_driver`.

The file exports integration tables: `rt2500usb_mac80211_ops`, `rt2500usb_rt2x00_ops`, `rt2500usb_ops`, and `rt2500usb_device_table`.

## Control flow

Probe begins when `module_usb_driver()` registers `rt2500usb_driver` and the USB core matches an ID from `rt2500usb_device_table`. `rt2500usb_probe()` calls `rt2x00usb_probe()` with `rt2500usb_ops`. The rt2x00 core later calls `rt2500usb_probe_hw()`.

Hardware probing first reads and normalizes EEPROM in `rt2500usb_validate_eeprom()`. Invalid words are replaced with defaults for antenna, NIC, RSSI offset, BBP tuning threshold, and BBP tuning values. `rt2500usb_init_eeprom()` reads RF type, revision, antenna defaults, LED mode, hardware radio-button capability, and RSSI offset. `rt2500usb_probe_hw_mode()` sets mac80211 feature bits, selects RF channel tables, allocates per-channel info, and imports 2.4 GHz transmit power values from EEPROM.

Radio enable flows through `rt2500usb_enable_radio()`. `rt2500usb_init_registers()` sends USB device-mode setup requests, disables RX, toggles `MAC_CSR1` soft/BBP reset bits, programs BBP-ID auto-write registers, disables beacon generation, transitions to `STATE_AWAKE`, sets host-ready, programs revision-specific `PHY_CSR2`, sets frame length, clears crypto key state, configures RF latch behavior, and enables hardware sequence numbers. `rt2500usb_init_bbp()` waits until BBP register 0 is readable, writes a fixed BBP initialization table, then applies EEPROM BBP overrides.

Runtime configuration is split by mac80211 change flags. Channel changes patch RF3 transmit power, optionally perform a half-band prewrite for RF2525E, then write RF1 through RF4. Power-only updates rewrite RF3. Power-save updates program `MAC_CSR18` autowake fields, then request sleep or awake state through the device-state callback. Interface and ERP updates program beacon timing, TSF sync, MAC/BSSID, preamble, basic rates, beacon interval, and slot/SIFS/EIFS timing. RX filter updates `TXRX_CSR2` drop bits based on monitor mode and filter flags.

TX flow builds the RT2570 five-word descriptor in the SKB headroom. The descriptor carries retry limit, fragmentation, ACK, timestamp, OFDM, sequence, IFS, byte count, cipher/key, IV offset, queue contention settings, and PLCP values. Beacon TX is special: the driver disables beacon generation, prepends a descriptor, fills a USB bulk URB for a one-byte guardian transfer, submits the guardian URB, and then the callback submits the real beacon URB before freeing the SKB. The driver toggles `TXRX_CSR19` several times to avoid initial beacon-generation failure.

RX flow receives the hardware RX descriptor at the end of the USB buffer. `rt2500usb_fill_rxdone()` copies it to stable SKB descriptor storage, parses CRC/PLCP/cipher status, extracts IV/EIV when present, computes RSSI by subtracting `rt2x00dev->rssi_offset`, maps signal as PLCP or bitrate, marks same-BSS frames, and trims the SKB to the reported MPDU length.

## State and persistence behavior

The module parameter `nohwcrypt` disables hardware crypto capability at probe. EEPROM contents are read into `rt2x00dev->eeprom`; the driver mutates invalid values in that in-memory copy and uses those synthesized values for later setup. `rt2x00dev->rssi_offset`, `rt2x00dev->default_ant`, capability flags, and per-channel `channels_info` persist for the device lifetime.

The RF cache is updated by `rt2500usb_rf_write()` after each successful RF write, making later power-only updates possible through `rt2x00_rf_read()`. BBP tuning state persists in BBP registers and is reset by `rt2500usb_reset_tuner()` from EEPROM tuning words.

Hardware crypto state persists in key registers `SEC_CSR*` and key-valid bits in `TXRX_CSR0`. The driver enforces a single cipher algorithm across active hardware keys and only supports WEP key index 0 for WEP, otherwise falling back to software crypto.

Power state is requested through `MAC_CSR17` desired/current fields and polled until BBP/RF current state matches. Beacon generator state persists in `TXRX_CSR19`; RX enable state persists in `TXRX_CSR2`.

## Dependencies and integration points

This file depends on Linux USB, mac80211, LED class, module infrastructure, and rt2x00 core headers. It uses `rt2x00usb_vendor_request_buff()`, `rt2x00usb_vendor_req_buff_lock()`, `rt2x00usb_initialize()`, `rt2x00usb_uninitialize()`, `rt2x00usb_kick_queue()`, `rt2x00usb_flush_queue()`, `rt2x00usb_watchdog()`, `rt2x00usb_disable_radio()`, suspend/resume/disconnect helpers, and EEPROM USB reads.

It integrates with mac80211 through `struct ieee80211_ops`, mostly delegating generic operations to `rt2x00mac_*` wrappers. It integrates with rt2x00lib through `struct rt2x00lib_ops`, where the device-specific callbacks are registered. Queue sizing is provided through `rt2500usb_queue_init()`, including RX, four AC queues, beacon queue, and required ATIM queue.

RF channel tables are local static data keyed by RF type. Hardware capability export depends on those tables, EEPROM TX power bytes, and the RF5222 dual-band case.

## Risks

- USB register access is mostly fire-and-forget. Basic read/write helpers ignore vendor request status, so failures can surface later as bad register values or busy-loop errors.
- BBP/RF indirect access relies on `csr_mutex` and bounded polling. Calling unlocked variants while already serialized is intentional; mixing variants incorrectly risks deadlock or register races.
- `rt2500usb_config_key()` has strict hardware limits: all active hardware keys must use the same cipher, WEP is restricted to key index 0, and pairwise/shared key index collisions can return `-ENOSPC`.
- EEPROM validation reads BBP register 17 before the full radio initialization path. If BBP access is not ready, the derived VGC lower bound can be wrong.
- `rt2500usb_probe_hw()` reads calibrated RSSI offset in `rt2500usb_init_eeprom()` but then sets `rt2x00dev->rssi_offset = DEFAULT_RSSI_OFFSET` at the end, overriding EEPROM calibration. This is intentional or legacy behavior but is a strong audit point for RSSI accuracy.
- Beacon upload depends on guardian URB ordering and repeated `TXRX_CSR19` toggles. URB submission failure is not checked in this path, so beacon loss may be silent.
- RX descriptor location is computed from `actual_length - desc_size`; malformed short USB transfers would underflow without prior core validation.
- Power-save autowake programs `beacon_int - 20`; unexpectedly low beacon intervals could underflow the field.
- RF tables are hand-coded constants. Incorrect RF type detection or channel index assumptions can program invalid synthesizer values.

## Test signals

- Build coverage for `CONFIG_RT2X00_LIB_LEDS`, `CONFIG_RT2X00_LIB_DEBUGFS`, and normal builds should cover optional callback tables.
- Probe tests on RT2570 devices should validate EEPROM defaults, RF detection, channel table selection, LED registration, hardware button capability, and queue setup.
- USB fault-injection or tracing should confirm vendor request failures, BBP/RF busy timeouts, and register read/write ordering are observable.
- Radio bring-up should reach `STATE_AWAKE`, set `MAC_CSR1_HOST_READY`, complete BBP initialization, and avoid "BBP register access failed" and "Indirect register access failed" logs.
- Channel tests should cover all supported RF chip table paths, including RF2525E half-band prewrite and RF5222 5 GHz channels.
- Crypto tests should verify hardware crypto success for supported single-cipher cases and software fallback for mixed cipher, WEP nonzero index, and full key mask cases.
- TX/RX tests should inspect descriptor fields, USB packet length padding rules, RSSI offset application, FCS/PLCP reporting, and encrypted RX IV/EIV propagation.
- Beacon/AP tests should verify guardian URB behavior, TSF/beacon enable toggling, DTIM/multicast behavior, and AP interface limit handling.
- Power-save and rfkill tests should exercise GPIO polling, autowake, sleep/awake transitions, and failure logging from `rt2500usb_set_device_state()`.
