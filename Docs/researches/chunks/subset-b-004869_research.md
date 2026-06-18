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
