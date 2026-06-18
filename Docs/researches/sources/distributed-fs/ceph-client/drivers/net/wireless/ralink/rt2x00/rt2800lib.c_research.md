# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800lib.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004868`: lines 1-8256, `Docs/researches/chunks/subset-b-004868_research.md`
- `subset-b-004869`: lines 8257-12346, `Docs/researches/chunks/subset-b-004869_research.md`

## Chunk Research

### subset-b-004868: lines 1-8256

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

### subset-b-004869: lines 8257-12346

# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800lib.c lines 8257-12346

## Scope

This chunk is the tail of the Ralink/MediaTek `rt2800lib.c` shared driver library for the Linux `rt2x00` wireless stack. It starts at the end of a preceding RFCSR initialization helper, then covers the RT5390/RT5392/RT5592 RFCSR init routines, the RT6352 calibration and RFCSR bring-up sequence, EEPROM/efuse/nvmem loading and validation, RF channel tables, hardware-mode probing, final hardware probe, radio enable/disable, and exported mac80211 callbacks.

The code is not a standalone subsystem. It depends on earlier register access helpers in the same file (`rt2800_register_*`, `rt2800_bbp_*`, `rt2800_rfcsr_*`), chipset predicates from `rt2x00`, EEPROM field macros, and lower-level bus-specific implementations supplied by the PCI/USB/SoC rt2800 drivers.

## Purpose

This range turns a detected rt2800-family device into a registered, calibrated, and usable mac80211 radio. It has three broad responsibilities:

- Program RFCSR/BBP/MAC register defaults for several later rt2800 chips, especially RT5390, RT5392, RT5592, and RT6352.
- Load and normalize persistent board data from efuse, nvmem, or EEPROM, then derive RF type, antenna chains, PA/LNA capabilities, LED config, power tables, channel tables, and mac80211 hardware capabilities.
- Provide exported runtime entry points used by bus-specific rt2800 drivers and mac80211 for radio on/off, RTS threshold updates, TX queue contention parameters, TSF reads, AMPDU negotiation, TKIP sequence reads, and survey reporting.

The most hardware-sensitive parts are RT6352 calibration routines. They temporarily stop TX/RX, route RF loopback paths, run DC/IQ/filter searches, poll BBP/RF completion bits, compute correction values, write BBP DCOC/IQ compensation registers, and restore saved RF/MAC/BBP state.

## Important APIs, Types, and Data

Important exported functions in this chunk:

- `rt2800_enable_radio()` initializes MAC registers, wakes BBP/RF, sends firmware boot signals through the MCU mailbox, initializes BBP/RFCSR blocks, enables TX/RX DMA, enables MAC TX/RX, and programs LED MCU state from EEPROM.
- `rt2800_disable_radio()` disables WPDMA, waits for DMA readiness as best effort, then clears MAC TX/RX enable bits.
- `rt2800_efuse_detect()`, `rt2800_read_eeprom_efuse()`, and `rt2800_read_eeprom_nvmem()` provide persistent configuration loading from efuse or nvmem.
- `rt2800_probe_hw()` is the final shared probe path: detect RT chipset, validate/load EEPROM, initialize EEPROM-derived runtime fields, set GPIO rfkill direction, build `hw_mode_spec`, set capabilities/requirements, and initialize watchdog/RSSI defaults.
- `rt2800_get_key_seq()`, `rt2800_set_rts_threshold()`, `rt2800_conf_tx()`, `rt2800_get_tsf()`, `rt2800_ampdu_action()`, and `rt2800_get_survey()` are exported mac80211 callbacks.

Important static initialization and calibration functions:

- `rt2800_init_rfcsr_5390()`, `rt2800_init_rfcsr_5392()`, and `rt2800_init_rfcsr_5592()` write fixed RFCSR defaults for those chip families, with revision, USB, clock, and DC-filter variations.
- `rt2800_init_rfcsr_6352()` writes central RF registers, channel RF registers, DC calibration registers, DRQFN-specific overrides, and then calls `rt2800_calibration_rt6352()`.
- `rt2800_calibration_rt6352()` runs the high-level RT6352 calibration sequence: optional external PA/LNA restore baseline, R calibration, self TX DC calibration, RX DCOC, TX/RX bandwidth filter calibration, LOFT/IQ calibration, another RX DCOC pass, RXIQ calibration, and final external PA/LNA programming.
- `rt2800_init_rfcsr()` dispatches to the right RFCSR init routine based on SoC detection and `rt2x00dev->chip.rt`.
- `rt2800_validate_eeprom()` reads EEPROM through `rt2800_read_eeprom()`, validates and patches invalid words, sets the MAC address, normalizes RSSI/LNA/frequency/LED fields, and caches mixer gains.
- `rt2800_init_eeprom()` decodes RF type, default TX/RX chains, antenna diversity, external LNA/PA, hardware button, BT coexistence, frequency offset, LEDs, and EIRP power limit into `rt2x00dev` flags and fields.
- `rt2800_probe_hw_mode()` selects the channel table, supported bands/rates/HT capabilities, per-channel power arrays, and VCO recalibration capability.

Important local data structures and arrays:

- `struct rt2x00_dev` is the central state carrier. This chunk mutates `chip.rt`, `chip.rf`, `default_ant`, `freq_offset`, `cap_flags`, `flags`, `spec`, `chan_survey`, `rssi_offset`, `link.watchdog`, `link.watchdog_interval`, and EEPROM memory.
- `struct rt2800_drv_data` stores calibration and EEPROM-derived state such as `txmixer_gain_24g`, `txmixer_gain_5g`, `tx_calibration_bw20`, `tx_calibration_bw40`, `rx_calibration_bw20`, and `rx_calibration_bw40`.
- `struct rf_reg_pair rf_store[CHAIN_NUM][13]` snapshots RFCSR bank/register/value triples for two chains during LOFT/IQ calibration.
- `struct rf_channel` arrays (`rf_vals`, `rf_vals_3x`, `rf_vals_3x_xtal20`, `rf_vals_3853`, `rf_vals_5592_xtal20`, `rf_vals_5592_xtal40`, `rf_vals_7620`) map IEEE channels to chip-specific synthesizer values.
- `struct hw_mode_spec` and `struct channel_info` are filled for mac80211 registration and per-channel power data.

## Control Flow

RF initialization dispatch starts in `rt2800_enable_radio()`. After MAC and firmware/MCU setup, it calls `rt2800_init_bbp()` from earlier in the file and then `rt2800_init_rfcsr()`. `rt2800_init_rfcsr()` first special-cases RT305x SoCs, then dispatches by `rt2x00dev->chip.rt`. In this chunk the relevant cases are RT5390, RT5392, RT5592, and RT6352.

The RT5390 and RT5392 paths are mostly fixed RFCSR tables. RT5390 adjusts several values for RT5390F-or-newer revisions and USB devices, then calls `rt2800_normal_mode_setup_5xxx()` and enables LED open-drain mode. RT5392 uses its own table and the same normal-mode/LED tail. RT5592 runs RF init calibration with a different target, writes RFCSR defaults, kicks RFCSR2, calls `rt2800_freq_cal_mode1()`, conditionally enables a DC filter on RT5592C and newer, enters normal mode, applies an older-revision RFCSR27 value, and enables LED open-drain mode.

The RT6352 path is much more involved. `rt2800_init_rfcsr_6352()` writes central RF defaults, channel-bank defaults through `rt2800_rfcsr_write_chanreg()` for banks 4 and 6, DC calibration defaults through `rt2800_rfcsr_write_dccal()` for banks 5 and 7, and several late overrides for external front-end/DRQFN-style layouts. It then calls `rt2800_calibration_rt6352()`.

RT6352 calibration uses several nested flows:

- `rt2800_r_calibration()` saves RF/BBP/MAC state, disables TX and RX through `MAC_SYS_CTRL`, waits for BBP/RF idle, sets bypass/control and RF bank values, measures two BBP readings (`d1`, `d2`), computes a rounded calibration code with `rt2800_calcrcalibrationcode()`, writes RF bank 0 register 7, toggles BBP reset, then restores all saved state.
- `rt2800_rf_self_txdc_cal()` saves RF control/bypass registers, routes bypass/control paths for self TX DC calibration, toggles bank 5 and bank 7 register 1 calibration bits with up to 100 polls per chain, and restores original MAC registers.
- `rt2800_rxdcoc_calibration()` enables RX DCOC state, forces MAC RX mode, waits for TX idle, sets DCCAL bank values, starts BBP DCOC, polls BBP159 until bit 0x40 clears or 10000 iterations expire, then restores MAC, BBP selector, and RF bank 0 register 2.
- `rt2800_bw_filter_calibration()` saves a large RF/BBP/MAC register set, calibrates both 20 MHz and 40 MHz modes for either TX or RX, repeatedly adjusts AGC filter codes until measured calibration delta crosses the target, persists the selected code in `rt2800_drv_data`, then restores RF/BBP/MAC state and the active bandwidth.
- `rt2800_loft_iq_calibration()` has two phases. First it calibrates LO feedthrough DC offsets for both chains and three ALC levels using RF loopback, tone generation, FFT power accumulation, and binary-style DC search. Then it calibrates IQ gain/phase error for both chains using VGA gain selection and coarse/fine searches. It writes resulting DC/IQ compensation into BBP indirect registers and restores RF/MAC/BBP snapshots.
- `rt2800_rxiq_calibration()` calibrates RX IQ imbalance. It saves many RF/MAC/BBP registers, configures RF loopback and DCOC, searches a VGA table until sufficient signal variance is measured, computes sigma/correlation values, derives gain imbalance and phase correction with range checks, writes BBP correction registers for chain 0 and chain 1, and restores state even on fatal calibration timeout via `goto restore_value`.

Probe control flow begins in `rt2800_probe_hw()`. It calls `rt2800_probe_rt()` to read `MAC_CSR0` or `MAC_CSR0_3290`, validate the chipset ID, remap RT5390 SoC devices to RT6352, and set `rt2x00dev->chip.rt`. It then calls `rt2800_validate_eeprom()` and `rt2800_init_eeprom()`. Only after EEPROM-derived RF/chains/capabilities are known does it configure GPIO rfkill polling and call `rt2800_probe_hw_mode()`.

`rt2800_probe_hw_mode()` sets default wiphy retry and power-save behavior, mac80211 hardware flags, permanent MAC address, rate-report limits, supported rates, RF channel table, supported bands, HT capabilities/MCS masks, per-channel survey storage, per-channel TX power defaults from EEPROM, and VCO recalibration capability. `rt2800_probe_hw()` then sets shared driver capability and requirement bits, applies watchdog policy from the module parameter, and initializes the RSSI offset.

The mac80211 callback flow is direct: key sequence reads are limited to TKIP and read a `mac_iveiv_entry`; RTS threshold updates program the base RTS register plus CCK/OFDM/MM/GF protection enables; TX queue configuration first delegates validation/state update to `rt2x00mac_conf_tx()` and then writes WMM/EDCA registers for queues 0-3; TSF reads combine high and low timer registers; AMPDU actions enforce known WCID before allowing aggregation; survey reads refresh counters on index 0 and convert stored microsecond-ish counters to milliseconds.

## State and Persistence

Most register writes in this chunk persist in device hardware until later radio disable, reset, channel change, recalibration, or RFCSR initialization. RFCSR init routines program baseline chip state. Calibration routines temporarily overwrite many registers but generally save and restore original values, while persisting only the intended correction values or driver-side calibration fields.

Persistent software state includes:

- EEPROM memory in `rt2x00dev->eeprom`, filled by bus/chip-specific `rt2800_read_eeprom()`, efuse, or nvmem, then patched in memory by `rt2800_validate_eeprom()` for invalid defaults.
- The device MAC address, set from EEPROM through `rt2x00lib_set_mac_address()` and later exposed to mac80211 through `SET_IEEE80211_PERM_ADDR()`.
- Chip identity in `rt2x00dev->chip.rt` and `rt2x00dev->chip.rf`.
- Default antennas and chain counts in `rt2x00dev->default_ant`, including hardware diversity for certain RT5390/RT5370 revisions.
- Capability flags for external LNA, external PA TX0/TX1, hardware radio button, Bluetooth coexistence, power limits, hardware crypto, filter control, pre-TBTT interrupt, restart capability, link tuning, VCO recalibration, and DMA/tasklet/firmware requirements.
- `rt2800_drv_data` mixer gains and RT6352 bandwidth calibration codes.
- `rt2x00dev->spec` channel/rate/HT metadata and dynamically allocated `channels_info`.
- `rt2x00dev->chan_survey`, allocated in `rt2800_probe_hw_mode()` and read later by `rt2800_get_survey()`.
- LED MCU configuration read from EEPROM and sent on radio enable.

The calibration functions are deliberately state-preserving around destructive measurement setups. They save MAC control/bypass registers, RFCSR banks, BBP indirect registers, power pin config, TX pin config, and bandwidth bits before forcing loopback, tone generation, or RF bypass state. The main exceptions are explicitly persisted calibration outputs: BBP DCOC/IQ/LOFT compensation registers and `drv_data` bandwidth filter calibration values.

## Dependencies and Integration Points

This chunk integrates with several layers:

- The `rt2x00` core supplies `struct rt2x00_dev`, capability flags, chipset/RF predicates (`rt2x00_rt`, `rt2x00_rf`, revision helpers), queue helpers, EEPROM accessors, MAC address validation, logging, and mac80211 glue.
- Earlier code in `rt2800lib.c` supplies register, BBP, RFCSR, MCU, WPDMA, survey, and initialization helpers used throughout this chunk.
- Register and field macros from `rt2800.h` define MAC/BBP/RFCSR offsets and bit layouts such as `MAC_SYS_CTRL`, `WPDMA_GLO_CFG`, `EFUSE_CTRL_*`, `EEPROM_*`, `TX_RTS_CFG`, protection config registers, WMM/EDCA registers, and TSF timer fields.
- Linux mac80211/cfg80211 types and callbacks are used through `struct ieee80211_hw`, `struct ieee80211_vif`, `struct ieee80211_key_conf`, `struct ieee80211_ampdu_params`, `struct survey_info`, `ieee80211_hw_set()`, `ieee80211_stop_tx_ba_cb_irqsafe()`, and channel/band constants.
- The nvmem framework is used by `rt2800_read_eeprom_nvmem()` through `nvmem_cell_get()`, `nvmem_cell_read()`, and `nvmem_cell_put()`.
- Bus-specific rt2800 drivers call the exported shared functions and provide lower-level register transport and EEPROM-read implementations. Non-SoC devices require firmware; USB devices have special MCU/current handling and watchdog restrictions.

## Risks

- Register ordering risk is high in RT6352 calibration. The routines depend on exact MAC disable/idle waits, RF bypass setup, BBP indirect register selection, delays, and restoration order. Small changes can leave TX/RX disabled, loopback active, or compensation registers invalid.
- Polling loops have weak failure handling. Several loops cap out after 20, 40, 100, or 10000 iterations, but many paths continue with the latest sampled value rather than returning an error. This makes hardware timing failures visible mainly through WARN/debug messages or degraded RF behavior.
- `rt2800_r_calibration()` writes `RF_CONTROL0` using `MAC_RF_CONTROL0 | (~0x3002)`, which sets many bits because of bitwise complement promotion. This appears inherited from vendor-style code and is risky if register definitions or compiler assumptions change.
- EEPROM validation silently rewrites in-memory invalid fields. This prevents obvious probe failure for bad EEPROMs but can mask board-specific configuration errors, especially antenna paths, external LNA/PA flags, RSSI offsets, LNA gains, LED settings, and power tables.
- RF type/channel table selection must match both RT and RF identity. A wrong EEPROM chip ID or `MAC_DEBUG_INDEX_XTAL` value can choose an incompatible synthesizer table, causing bad channel programming or missing 5 GHz support.
- RT6352 external PA/LNA handling is split between EEPROM-derived capability bits, `rt2800_restore_rf_bbp_rt6352()`, calibration, and final post-calibration register values. Incorrect capability detection can program the wrong front-end path.
- `rt2800_probe_hw_mode()` allocates `channels_info` and `chan_survey`; errors clean up `info` if `chan_survey` allocation fails, but later ownership/lifetime must be handled by the broader driver teardown.
- `rt2800_get_survey()` takes `chan_survey = &rt2x00dev->chan_survey[idx]` before validating `idx` against band channel counts. If mac80211 ever supplies an out-of-range index beyond the allocated total, this computes an out-of-bounds pointer before returning `-ENOENT`.
- AMPDU support depends on valid station WCID assignment. Unknown WCIDs are rejected to avoid ambiguous TX status, but bugs in station setup can surface as aggregation refusal rather than a direct station-management error.
- The final module metadata means this file exports shared symbols to GPL-only bus drivers; changing function names or signatures affects rt2800pci/rt2800usb/SoC integration.

## Test and Validation Signals

Useful validation is mostly hardware and integration oriented:

- Probe supported RT2860/2872/3070/3071/3090/3290/3352/3390/3572/3593/3883/5350/5390/5392/5592 and RT6352/MT7620-style SoC devices and check for successful `rt2800_probe_hw()` without invalid RT/RF chipset errors.
- Test EEPROM backends separately: efuse present detection, efuse reads on RT3290 and non-RT3290 register layouts, nvmem cell size validation, and fallback/default patching for invalid EEPROM words.
- Bring radio up/down repeatedly and watch for failures from `rt2800_wait_wpdma_ready()`, `rt2800_wait_bbp_rf_ready()`, `rt2800_wait_bbp_ready()`, MCU boot/current requests, and DMA/MAC enable sequencing.
- On RT5390/RT5392/RT5592 hardware, verify RFCSR initialization by association, TX/RX throughput, LED behavior, frequency offset stability, and absence of calibration-related warnings.
- On RT6352 hardware, validate all calibration stages by watching `rt2x00_warn()`/`rt2x00_dbg()` output for RXIQ, LOFT/IQ, RXDCOC, and filter calibration, then measuring link sensitivity, EVM, TX power, and throughput on both chains.
- Exercise internal and external PA/LNA RT6352 boards because the register sequences and capability flags differ materially.
- Test 20 MHz and 40 MHz operation after bandwidth filter calibration and confirm `drv_data` TX/RX calibration codes are populated and reused correctly.
- Exercise 2.4 GHz and 5 GHz channel tables where supported, including RF5592 20 MHz vs 40 MHz crystal paths and RF7620 2.4 GHz-only paths.
- Verify mac80211 callbacks: TKIP replay counters from `rt2800_get_key_seq()`, RTS threshold enabling/disabling across all protection registers, WMM/EDCA register programming for queues 0-3, TSF monotonicity, AMPDU negotiation with valid/invalid WCIDs, and survey time/busy/ext-busy reporting.
- Watch module parameter `watchdog` behavior, especially USB devices where DMA watchdog is masked because `INT_SOURCE_CSR` is invalid.
