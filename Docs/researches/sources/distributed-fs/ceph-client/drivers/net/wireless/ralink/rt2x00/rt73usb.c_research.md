# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt73usb.c

## Purpose

`rt73usb.c` implements the Ralink RT2571W/RT2671 USB wireless driver on top of rt2x00usb and mac80211. It owns BBP/RF indirect register access, firmware validation/loading, EEPROM normalization, RF/channel setup, hardware crypto programming, LED/rfkill support, link tuning, TX/RX descriptor translation, queue sizing, mac80211 callbacks, and the USB device ID table.

## Important APIs, Types, and Functions

Driver entry is `module_usb_driver(rt73usb_driver)`, with `rt73usb_probe()` delegating allocation/binding to `rt2x00usb_probe()`. `rt73usb_rt2x00_ops` is the main integration table: it supplies firmware hooks, device-state transitions, queue operations, descriptor writers, RX completion parsing, crypto configuration, link tuning, and config handlers. `rt73usb_mac80211_ops` exposes mac80211 callbacks, mostly via rt2x00 generic helpers plus local `conf_tx()` and `get_tsf()`. Critical helpers include `rt73usb_bbp_read/write()`, `rt73usb_rf_write()`, `rt73usb_config_shared_key()`, `rt73usb_config_pairwise_key()`, `rt73usb_config_channel()`, `rt73usb_write_tx_desc()`, `rt73usb_fill_rxdone()`, `rt73usb_validate_eeprom()`, `rt73usb_init_eeprom()`, and `rt73usb_probe_hw_mode()`.

## Control Flow

Probe flows through rt2x00usb into `probe_hw`: EEPROM is read and repaired, chip/RF IDs are validated, GPIO7 is configured for rfkill polling, channel/rate specs are built from RF-specific tables, and firmware/hardware-crypto/link-tuning capabilities are advertised. Startup later loads `rt73.bin` after CRC/length checks, initializes MAC/BBP registers, wakes the device through `MAC_CSR12`, clears security/beacon state, and applies EEPROM BBP overrides. Configuration callbacks update filters, MAC/BSSID, ERP timing, antenna/LNA, channel, TX power, retry limits, and power-save autowake. TX pushes a six-word descriptor into skb data, writes optional IV/EIV words, and relies on rt2x00usb to submit URBs. RX copies the descriptor out before skb pointer movement, reports CRC/crypto status, RSSI, rate signal type, BSS match, and strips descriptor bytes.

## State and Persistence Behavior

Persistent state is the EEPROM image: MAC, antenna defaults, RF type, hardware radio flag, LED polarity/mode, frequency offset, RSSI offsets, BBP overrides, and per-channel TX power. Volatile state includes CSR/BBP/RF registers, hardware key tables, beacon SRAM, `led_mcu_reg`, `lna_gain`, `freq_offset`, rf capability bits, queue descriptors, TSF registers, and link-quality tuner state. The `nohwcrypt` module parameter disables hardware crypto even when supported.

## Dependencies and Integration Points

The file depends on `rt2x00.h`, `rt2x00usb.h`, `rt73usb.h`, Linux USB, firmware, LED, rfkill, CRC ITU-T, and mac80211. It integrates with rt2x00lib for generic mac80211 operations, queue management, EEPROM storage, debugfs dumps, PLCP/rate handling, and crypto framing conventions. Hardware-facing integration is through USB vendor requests and register/multiwrite helpers.

## Risks and Edge Cases

Indirect BBP/RF access relies on busy-bit polling and `csr_mutex`; timeout paths can silently leave old values in place. Key-slot allocation uses bitmaps and `ffz()` with BSS/key index arithmetic, so invalid key indices or full tables can break encryption. The device requires exactly 2048-byte firmware with trailing CRC; bad firmware blocks startup. Beacon writes temporarily disable generation and free the skb, so error paths must keep `entry->skb` ownership clear. RSSI/LNA math depends on RF type, external LNA flags, and sane EEPROM offsets. USB packet length padding deliberately avoids exact max-packet multiples.

## Test Signals

Test with RT73 devices using each RF table, firmware CRC failure/success, hardware crypto enable/disable, shared/pairwise key exhaustion, rfkill GPIO transitions, LED radio/assoc/quality operations, 2.4/5 GHz channel changes, power-save sleep/wakeup, beacon generation, WMM `conf_tx`, RX crypto errors, descriptor length trimming, and USB suspend/resume/reset-resume.
