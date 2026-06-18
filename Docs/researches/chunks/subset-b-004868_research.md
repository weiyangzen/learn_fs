# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800lib.c lines 1-8256

## Scope

This chunk covers the first two thirds of `rt2800lib.c`, the shared Ralink/MediaTek RT2800 support library used by the bus-specific rt2x00 drivers. The range starts at module metadata and low-level register access helpers, then covers firmware validation/loading, TX/RX descriptor handling, TX completion, watchdog and beacon handling, key/WCID programming, mac80211 configuration handlers, RF channel programming for many RF families, transmit-power programming, link tuning, common MAC register initialization, BBP initialization, RX filter calibration, and RFCSR initialization through the beginning of the RT3883 RFCSR path.

The range ends inside `rt2800_init_rfcsr_3883()`, after many RT3883 RFCSR defaults and BBP writes but before that function and the full RFCSR dispatcher are complete. Later chunk research must reconcile the remainder of RT3883, newer RFCSR calibration paths, radio enable/disable, EEPROM validation, hardware mode probing, and remaining mac80211 callbacks.

## Purpose

The code provides the hardware-facing body of the RT2800 driver: it translates rt2x00/mac80211 operations into device register, BBP, RF, RFCSR, EEPROM, and firmware operations for RT2860/2872/2883/307x/3090/3290/3352/3390/3572/3593/3883/53xx/5592/6352 and related RF front ends. Its responsibilities in this range include:

- Serialize indirect BBP/RFCSR/RF/MCU accesses and handle busy-bit polling.
- Map logical EEPROM fields to chipset-specific physical EEPROM offsets.
- Validate and load device firmware, including RT3290 WLAN enable sequencing and USB MCU boot signaling.
- Populate TXWI descriptors, parse RXWI descriptors, and translate TX status FIFO reports into mac80211 txdone outcomes.
- Detect hung TX/RX queues and coherent DMA busy conditions, then request hardware restart.
- Program hardware beacon slots and global beacon offsets.
- Program shared/pairwise keys, WCID attributes, BSS indices, IV/EIV templates, and station WCID allocation.
- Apply interface, receive-filter, ERP, HT protection, antenna, power-save, retry, channel, transmit-power, and link-tuner settings.
- Initialize core MAC/ASIC registers, BBP defaults, GLRT/DCOC tables, RX filter calibration values, LED/open-drain behavior, and early RFCSR defaults.

This is not filesystem code despite the repository path. It is Linux wireless driver code vendored under the Ceph client source tree for research.

## Important APIs, Types, and Data

Primary state flows through `struct rt2x00_dev *rt2x00dev`. This object supplies bus type predicates, chip/RF IDs, current band/channel, antenna chain counts, EEPROM memory, device flags, register operations, mac80211 `hw`, queue state, survey accumulators, watchdog counters, LED configuration, and `struct rt2800_drv_data` private calibration/cache fields.

Important shared/exported functions in this range include:

- `rt2800_mcu_request()` writes host-to-MCU mailbox and command registers for non-SoC devices.
- `rt2800_wait_csr_ready()`, `rt2800_wait_wpdma_ready()`, and `rt2800_disable_wpdma()` are bring-up and reset helpers for stable CSR and DMA state.
- `rt2800_get_txwi_rxwi_size()` selects descriptor word counts by chipset.
- `rt2800_check_firmware()` and `rt2800_load_firmware()` validate firmware length/CRC, write firmware through the bus driver, and bootstrap the device.
- `rt2800_write_tx_data()` constructs TXWI words from `struct txentry_desc`.
- `rt2800_process_rxwi()` parses RXWI fields, computes RSSI from AGC/EEPROM/LNA offsets, and removes the RXWI from the skb.
- `rt2800_txdone_entry()`, `rt2800_txdone()`, `rt2800_txstatus_timeout()`, `rt2800_txstatus_pending()`, and `rt2800_txdone_nostatus()` reconcile TX status FIFO entries with queued frames.
- `rt2800_watchdog()` checks queue progress and DMA coherent interrupt/busy state, then calls `ieee80211_restart_hw()` on hangs.
- `rt2800_write_beacon()` and `rt2800_clear_beacon()` program or invalidate hardware beacon memory.
- `rt2800_config_shared_key()` and `rt2800_config_pairwise_key()` write hardware crypto tables and WCID cipher metadata.
- `rt2800_sta_add()`, `rt2800_sta_remove()`, and `rt2800_pre_reset_hw()` maintain WCID allocation and station pointers.
- `rt2800_config_filter()`, `rt2800_config_intf()`, `rt2800_config_erp()`, `rt2800_config_ant()`, and `rt2800_config()` implement mac80211 configuration changes.
- `rt2800_gain_calibration()` and `rt2800_vco_calibration()` expose periodic transmit-power/VCO recalibration.
- `rt2800_link_stats()`, `rt2800_reset_tuner()`, and `rt2800_link_tuner()` update FCS error stats and adjust VGC.

Important internal helpers include the indirect access helpers `rt2800_bbp_read/write()`, `rt2800_rfcsr_read/write()`, banked RFCSR helpers, DCOC/GLRT BBP indexed writes, and `rt2800_rf_write()`. EEPROM access is normalized by `rt2800_eeprom_word_index()`, `rt2800_eeprom_read()`, `rt2800_eeprom_write()`, `rt2800_eeprom_addr()`, and `rt2800_eeprom_read_from_array()`, using either `rt2800_eeprom_map` or `rt2800_eeprom_map_ext` for RT3593/RT3883 extended layouts.

The chunk uses many rt2x00 queue and descriptor types: `struct queue_entry`, `struct data_queue`, `struct txentry_desc`, `struct rxdone_entry_desc`, `struct skb_frame_desc`, `struct rt2x00lib_crypto`, `struct ieee80211_key_conf`, `struct ieee80211_sta`, `struct rt2x00_sta`, `struct rt2x00lib_conf`, `struct rt2x00lib_erp`, `struct rf_channel`, `struct channel_info`, `struct antenna_setup`, and `struct link_qual`.

Persistent constants and tables in this chunk include logical EEPROM maps, the `watchdog` module parameter, TX power register index enum values, chipset-specific BBP/GLRT/DCOC programming sequences, and many literal RFCSR register-value tables embedded in the per-chip initialization functions.

## Control Flow

Indirect hardware access is the base layer. BBP, RFCSR, RF, and MCU accesses poll busy/owner bits using `WAIT_FOR_*` macros under `rt2x00dev->csr_mutex` where needed. MT7620/RT6352 RFCSR layout is handled separately from older RFCSR layouts. Failed waits generally leave reads returning `0xff`/busy-derived values and log through lower layers.

Firmware flow starts with `rt2800_check_firmware()`. It selects 4 KiB firmware blocks for USB and RT3290, 8 KiB blocks for PCI/SoC, validates total size and multi-block USB firmware expectations, and checks each block with CCITT CRC over all but the final two bytes. `rt2800_load_firmware()` optionally enables RT3290 WLAN clocks, clears autowakeup, waits for CSR readiness, adjusts PCIe power/clock registers, disables WPDMA, writes firmware through the bus driver, waits for `PBF_SYS_CTRL_READY`, disables WPDMA again, clears MCU/BBP mailbox registers, and sends USB boot signal.

TX flow builds a TXWI in `rt2800_write_tx_data()` using frame flags, HT metadata, key/WCID, length, queue id, and entry id. TX completion reads status FIFO entries in `rt2800_txdone()`, locates the queue by encoded PID queue, verifies the next done entry is status-pending, and checks WCID/ACK/PID fields in `rt2800_txdone_entry_check()`. `rt2800_txdone_entry()` derives success/failure, retry count, fallback, AMPDU, no-ack, and actual rate metadata. When status does not match the queued frame, it uses status-derived rate and tries to recover a station pointer by WCID under RCU before calling the no-match txdone path.

RX flow is compact. `rt2800_process_rxwi()` reads RXWI word 0 for cipher and size, word 1 for SGI/bandwidth/MCS/PHY mode, strips the CCK short-preamble bit from signal, reads word 2 for AGC/RSSI fields, computes the best-chain RSSI using `rt2800_agc_to_rssi()`, and removes the RXWI descriptor from skb data.

Watchdog flow has two independent detectors selected by `rt2x00dev->link.watchdog`. The queue hang detector samples each queue's DMA-done index and increments per-queue `wd_count` if it stops moving, treating TX queues and STA-mode RX queue differently. The DMA-busy detector tracks repeated `WPDMA_GLO_CFG_*_DMA_BUSY` plus coherent interrupt bits. Either detector can trigger `ieee80211_restart_hw()` unless scanning is active.

Beacon flow temporarily disables beacon generation, pushes a TXWI into the beacon skb, writes the padded beacon image to the hardware beacon slot, marks `ENTRY_BCN_ENABLED`, recomputes active beacon offsets in `BCN_OFFSET0/1`, updates `MAC_BSSID_DW1_BSS_BCN_NUM`, restores beaconing, and frees the skb. Clearing a beacon zeroes only the TXWI area to invalidate that slot and recomputes the global offsets.

Key and station flow programs hardware crypto state around WCIDs. Shared keys compute `hw_key_idx = 4 * bssidx + keyidx`, write `SHARED_KEY_ENTRY`, update `SHARED_KEY_MODE_ENTRY`, write WCID MAC address, BSS index, cipher attributes, and IV/EIV template. Pairwise keys use the station WCID if within hardware range and write `PAIRWISE_KEY_ENTRY`. Station add/remove maintains `drv_data->sta_ids`, `drv_data->wcid_to_sta`, station-private WCID, and global maximum PSDU length based on the smallest associated AMPDU factor.

Configuration flow is mac80211-driven. `rt2800_config()` always recalculates LNA gain, then on channel change saves survey counters, dispatches to `rt2800_config_channel()`, and reprograms transmit power. It separately handles power, retry limit, and power-save changes. Interface and ERP functions update TSF sync, MAC/BSSID registers, beacon contention, receive filters, basic rates, slot/EIFS timing, beacon interval, and HT protection registers.

Channel flow first clamps EEPROM channel powers to hardware-accepted ranges, then dispatches by RF chipset to one of the `rt2800_config_channel_rf*()` functions. Those functions program synthesizer values, TX power fields, chain power-down bits, frequency offsets, band-specific RFCSR tables, calibration bandwidths, and VCO/RF tuning triggers for RF2xxx, RF3xxx, RF3052/3053, RF3290, RF3322, RF3853, RF53xx, RF55xx, and RF7620. After RF-specific programming, common channel code updates BBP LNA/VGC and CCK behavior, `TX_BAND_CFG`, `TX_PIN_CFG` PA/LNA enables, GPIO band/LNA selection for some parts, RT5592/RT6352 GLRT and IQ settings, BBP bandwidth/HT40-minus fields, legacy RT2860C BBP timing, survey counter clearing, and BBP update flags.

Transmit power flow uses EEPROM rate-power tables plus compensation. `rt2800_get_gain_calibration_delta()` reads TSSI bounds and BBP49 to compute temperature compensation when external TX ALC is supported. `rt2800_get_txpower_bw_comp()` reads 20/40 MHz EEPROM deltas, and `rt2800_get_txpower_reg_delta()` derives reductions for devices without explicit power-limit capability. `rt2800_compensate_txpower()` clamps per-rate values and enforces EIRP power limits where available. RT3593/RT3883 use extended TX power registers for up to three chains; RT6352 copies 8-bit by-rate EEPROM values and fills missing high-rate registers in vendor-driver style before configuring internal ALC; older RT28xx parts use TX power CFG0-4 plus BBP R1 coarse reductions.

Initialization flow in `rt2800_init_registers()` disables WPDMA, calls the bus-specific init hook, applies RT6352 BBP reset, writes baseline rates, beacon timing, filters, slot timing, chip-specific TX switch/ALC/AMPDU/BT/coexistence values, TX link/timeout/retry/protection registers, USB WPDMA defaults, RTS/ACK/XIFS timing, power pins, key/WCID/IVEIV cleanup, beacon memory cleanup, cycle counters by bus clock, fallback tables, BA window policy, counter clearing, pre-TBTT lead time, and channel-stat timer setup.

BBP initialization is chipset-dispatched by `rt2800_init_bbp()`. The per-chip functions write long register sequences for receive gain, MLD, ADC/DAC, in-band RXWI mapping, antenna diversity, GLRT tables, frequency calibration, DCOC, and beamforming timeout. After most per-chip setup paths, EEPROM BBP override words from `EEPROM_BBP_START` are applied. Some chips return early and intentionally skip generic EEPROM BBP overrides.

RFCSR initialization in this range covers 305x SoC, 30xx, 3352, 3390, 3572, 3593, 5350, and the beginning of 3883. These functions write reset/default RFCSR tables, perform RF init calibration, run RX filter calibration where supported, save calibration values in `drv_data`, set LED open-drain behavior, and switch RF blocks into normal mode by disabling LO paths and powering required RF blocks. The RT3883 function is incomplete at the chunk boundary.

## State and Persistence

Hardware register writes persist until later channel changes, resets, radio disable/enable paths, watchdog restart, or another calibration sequence overwrites them. State is split between device registers and driver caches.

Driver-persistent state in `struct rt2x00_dev` includes current band/channel, `freq_offset`, `lna_gain`, default antenna setup, `tx_power`, watchdog mode/counters, per-channel survey accumulators, queue watchdog indices/counts, and device flags such as scanning/reset/flushing/monitoring. `curr_band`, channel, antenna chain counts, and capabilities influence almost every RF/BBP path.

`struct rt2800_drv_data` persists calibration and association metadata, including `calibration_bw20`, `calibration_bw40`, RT6352 RX/TX calibration bandwidth fields, saved BBP25/BBP26, tx mixer gains, maximum PSDU setting and per-AMPDU-factor station counts, WCID allocation bitmap, and WCID-to-station lookup table.

EEPROM state is read frequently and sometimes addressed as arrays. It drives RSSI offsets, LNA gains, TX power by channel/rate, TSSI bounds, NIC chain/path config, antenna diversity, LED mode/polarity, external PA/LNA capability, calibration bytes, and BBP override entries. The logical-to-physical EEPROM map differs for RT3593/RT3883.

Queue state persists through TX/RX/beacon operations. TX entries use flags such as `ENTRY_DATA_STATUS_PENDING`, `ENTRY_OWNER_DEVICE_DATA`, `ENTRY_DATA_IO_FAILED`, and beacon entries use `ENTRY_BCN_ENABLED`/`ENTRY_BCN_ASSIGNED`. TX status timeout behavior depends on `entry->last_action` and the global flushing state.

Security state persists in hardware key tables, WCID MAC entries, WCID attributes, shared-key mode registers, and MAC IV/EIV entries. `rt2800_init_registers()` clears key/WCID state at startup and avoids clearing IV/EIV during reset to preserve connections across watchdog recovery.

Survey state is accumulated by reading clear-on-read or accumulating hardware channel idle/busy counters before channel changes and during watchdog checks. Link-quality state persists current VGC level in `struct link_qual`.

## Dependencies and Integration Points

The code depends on the rt2x00 core for queue management, EEPROM access, debugfs frame dumps, common register helpers, field extraction/setters, hardware restart, device state changes, crypto glue, BSS index lookup, and bus predicates. Bus-specific rt2800 drivers provide operations such as `rt2800_register_read/write`, `rt2800_register_write_lock`, `rt2800_register_multiwrite`, `rt2800_drv_write_firmware()`, `rt2800_drv_get_txwi()`, `rt2800_drv_get_dma_done()`, and `rt2800_drv_init_registers()`.

It integrates with mac80211 through `struct ieee80211_hw`, `ieee80211_vif`, `ieee80211_sta`, `ieee80211_conf`, channel definitions, key configuration, TX status reporting, RX rate/RSSI metadata, power-save flags, retry limits, ERP/HT BSS change flags, station add/remove callbacks, and hardware restart.

Linux kernel dependencies include module parameters, CRC-CCITT, endian helpers, skb manipulation, kfifo, RCU, LED class device support, mutexes, clock APIs for SoC/RT6352 timing, sleep/delay primitives, bit operations, warnings/logging, and optional debugfs support.

Hardware dependencies are extensive. The code writes MAC CSR registers, WPDMA registers, PBF/MCU mailbox registers, BBP registers, RFCSR registers, old RF registers, GPIO/LED/clock/LDO/coexistence registers, key tables, beacon memory, and per-rate power registers. Register layout is selected by chip ID, RF ID, bus type, revision, current band, channel, HT40 state, antenna chain count, and board capabilities.

## Risks

- Register sequencing is fragile. Many functions rely on exact order, busy-bit polling, and `udelay`/`msleep`/`usleep_range` delays. Reordering or removing waits can break BBP/RF access, VCO calibration, firmware boot, or DMA recovery.
- Chipset gating is high risk. Similar operations use different RFCSR bit layouts for RT6352/MT7620, RT3593/RT3883, RF7620, RF55xx, RF53xx, and older RF2xxx/3xxx families. Wrong `rt2x00_rt()` or `rt2x00_rf()` gating can program unrelated registers.
- TX power code affects regulatory behavior. EEPROM by-rate power, TSSI compensation, HT40 deltas, EIRP limits, user power, BBP R1 coarse control, internal ALC, and chain-specific registers interact. Bad compensation can cause underpowered links or excessive transmit power.
- TX status matching is lossy under aggregation and no-match cases. The code intentionally substitutes status-derived rates when aggregation changes the actual MCS or when no matching entry is found, and retry counts are known imprecise in no-match cases.
- WCID and station-pointer handling depends on RCU and bitmap consistency. Incorrect add/remove/reset sequencing can leave stale station pointers or hardware WCID entries.
- Beacon writes mutate skb layout and then free the skb. Padding failure sets `entry->skb = NULL`; callers must tolerate this and not reuse the skb.
- Watchdog false positives can restart hardware during slow queue progress. RX hang detection is explicitly STA-oriented and not robust for AP mode.
- EEPROM map warnings indicate invalid logical accesses, but callers often continue with index zero behavior after warnings. This is especially risky for fields that overlap across old and extended layouts.
- Some comments document unresolved or suspicious vendor-driver behavior: ignored RT6352 HT40 power deltas, `0x20` by-rate replacement with `0x21`, incomplete TX beamforming support, hard-coded RT3883 ECO value, missing RT3883 RX filter calibration, possible BBP105 overwrites, and TODOs around RX IQ calibration.
- The chunk boundary cuts through `rt2800_init_rfcsr_3883()`. Any final file-level conclusion about RT3883 RFCSR initialization must combine the next chunk.

## Test and Validation Signals

Validation is mostly hardware and integration oriented:

- Probe and firmware-load tests should confirm firmware length/CRC handling, RT3290 WLAN enablement, CSR readiness, PBF readiness, and USB MCU boot signaling without `Unstable hardware` or `PBF system register not ready` errors.
- DMA/reset tests should verify WPDMA busy waits, watchdog DMA-busy detection, queue hang detection, and restart recovery without losing IV/EIV state after watchdog reset.
- TX/RX data-path tests should exercise legacy, HT20, HT40, SGI, AMPDU, encrypted, no-ack, and failed transmissions while checking TXWI fields, TX status matching, retry/fallback reporting, RXWI parsing, RSSI values, and skb descriptor stripping.
- AP and STA beacon tests should verify beacon slot writes, beacon clearing, offset register updates, BSSID beacon-count programming, and safe behavior on skb padding failure.
- Crypto tests should cover shared WEP/TKIP/CCMP keys, pairwise keys, key deletion, multiple BSS indices, WCID reuse, reset behavior, and RX WI UDF/cipher reporting.
- Station scaling tests should add/remove HT stations with different AMPDU factors and verify `MAX_LEN_CFG_MAX_PSDU` follows the smallest active factor and returns after removal.
- Channel-change tests should cover 2.4 GHz, low/mid/high 5 GHz, HT20/HT40 plus/minus, external LNA/PA boards, Bluetooth coexistence parts, one/two/three chain hardware, and RF families RF2xxx, RF3xxx, RF3052/3053, RF3290, RF3322, RF3853, RF53xx, RF55xx, RF7620, RT3593, RT3883, RT5592, and RT6352.
- Transmit-power tests should compare requested power, regulatory limits, EEPROM by-rate values, TSSI compensation, HT40 deltas, ALC programming, and measured conducted power across temperature and band changes.
- Link-tuner tests should verify VGC updates at RSSI thresholds and that per-chain BBP66 writes are used on multi-chain parts.
- Initialization tests should check that MAC/BBP/RFCSR defaults, fallback tables, protection registers, timing registers, key table clearing, beacon clearing, and channel-stat timers are programmed as expected after cold boot and watchdog reset.
- Built-in log signals include warnings/errors for BBP/RF register access failure, WPDMA busy, TX/RX watchdog detection, unsupported RF chipset for VCO calibration, invalid EEPROM word access, invalid RT6352 channel assumptions, and TX status reports for empty or unexpected queues.
