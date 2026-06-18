# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_cmn.c

## Purpose
`phy_cmn.c` is the common Broadcom `brcmsmac` PHY implementation used between the higher MAC/shim layer and PHY-type-specific backends. It owns shared attach/detach, register and table access helpers, radio identification, public PHY HAL entry points, channel metadata, transmit-power target calculation, RSSI/noise sampling, watchdog calibration scheduling, and dispatch into NPHY or LCNPHY callbacks through `struct phy_func_ptr`.

The file is hardware-facing. Most operations read or write D11 core registers, PHY registers, radio registers, or firmware shared memory, with MAC suspend/resume around operations that cannot run while MAC hardware is active.

## Important APIs, Types, and Functions
- Register access: `read_phy_reg()`, `write_phy_reg()`, `and_phy_reg()`, `or_phy_reg()`, `mod_phy_reg()`, `read_radio_reg()`, `write_radio_reg()`, and radio mask helpers wrap D11/PHY/radio MMIO and handle core-revision-specific register paths.
- Register wake/serialization: `wlc_phyreg_enter()` and `wlc_phyreg_exit()` use shim wake overrides around PHY register access.
- Attach/lifecycle: `wlc_phy_shared_attach()`, `wlc_phy_attach()`, `wlc_phy_detach()`, and `wlc_set_phy_uninitted()` allocate/copy chip state, discover PHY/radio identity, select NPHY/LCNPHY backends, and reset software sentinels.
- Public HAL state: `wlc_phy_get_phyversion()`, `wlc_phy_hw_clk_state_upd()`, `wlc_phy_hw_state_upd()`, `wlc_phy_por_inform()`, and `wlc_phy_initcal_enable()`.
- Init/shutdown: `wlc_phy_init()`, `wlc_phy_cal_init()`, and `wlc_phy_down()` coordinate MAC-disabled initialization, backend callbacks, timers, and calibration state.
- Channel/radio: `wlc_phy_chanspec_set()`, `wlc_phy_chanspec_get()`, `wlc_phy_chanspec_radio_set()`, `wlc_phy_bw_state_set()`, `wlc_phy_clk_bwbits()`, `wlc_phy_channel2freq()`, `wlc_phy_chanspec_band_validch()`, `wlc_phy_switch_radio()`, and `wlc_phy_anacore()`.
- Power: `wlc_phy_txpower_get()`, `wlc_phy_txpower_set()`, `wlc_phy_txpower_sromlimit()`, `wlc_phy_txpower_limit_set()`, `wlc_phy_txpower_recalc_target()`, `wlc_phy_txpower_update_shm()`, and `wlc_phy_txpower_get_current()`.
- Measurement/calibration: `wlc_phy_watchdog()`, `wlc_phy_noise_sample_intr()`, `wlc_phy_rssi_compute()`, `wlc_phy_compute_dB()`, `wlc_phy_cal_perical()`, and multi-phase NPHY timer helpers.
- Static metadata: `chan_info_all[]` maps supported channels to frequency; `ofdm_rate_lookup[]` maps OFDM power-order indices to Broadcom rates.

## Control Flow
Attach starts with `wlc_phy_shared_attach()` creating shared chip/board/timer state. `wlc_phy_attach()` validates band flags, resets the core, reads `phyversion`, normalizes LCNXN as NPHY, validates PHY/radio IDs, initializes defaults, selects min TX power, configures timer/noise state, then calls `wlc_phy_attach_nphy()` or `wlc_phy_attach_lcnphy()` to populate type-specific callbacks and state.

Initialization is driven by `wlc_phy_init()`. It rejects reentrant init, records the chanspec, verifies the MAC is disabled and fast clock is present, sets not-associated hold state when appropriate, powers analog and radio blocks, adjusts bandwidth, dispatches the backend `init`, clears POR state, optionally performs dummy TX, updates shared-memory TX power for non-NPHY, restores RX diversity, and clears `init_in_progress`.

Transmit-power recalculation computes a target channel from the chanspec, derives LCN MCS limits if needed, measures environment limits, then combines user target, board/SROM limits, regulatory limits, fixed margins, percentage scaling, min power, and environment limits for every supported rate. It stores per-rate targets, min/max target, max-rate index, and offsets before calling the backend `txpwrrecalc` callback.

Noise sampling can be interrupt-driven through `MCMD_BG_NOISE` or direct polling. NPHY polling disables classifiers and collects IQ estimates; LCN polling enters receiver measurement mode and calls `wlc_lcnphy_rx_signal_power()`. Results update monitor/external state through `wlc_phy_noise_cb()`.

The watchdog increments `sh->now`, samples noise when not scanning/RM/PLT, clears stale noise state, optionally recalculates software TX power, skips calibration during scan/RM/PLT/association, and dispatches NPHY or LCNPHY periodic calibration paths.

## State and Persistence Behavior
All state is runtime-only. `struct shared_phy` persists while attached and holds shim, chip/board IDs, timers, clock/up state, chain masks, antenna diversity, and shared noise windows. `struct brcms_phy` persists per PHY and caches public identity, D11 core, chanspec/bandwidth, hold flags, TX power arrays, SROM limits, calibration fields, NPHY state, and the LCN private pointer.

No disk persistence exists. Hardware state is reconstructed from registers, SPROM/SROM, and static tables at attach/init/channel/calibration time.

## Dependencies and Integration Points
- Kernel helpers for allocation, delays, warnings, bit operations, and integer math.
- Broadcom headers for chip IDs, chipcommon, AI utilities, D11 registers, radio constants, NPHY registers, and Wi-Fi/rate/channel helpers.
- Shim calls `wlapi_*` for core reset, MAC suspend/resume, timers, shared memory, template RAM, bandwidth, MHF bits, and ucode wake overrides.
- Backend integration with NPHY helpers from other files and LCNPHY helpers in `phy_lcn.c`.
- Public declarations are in `phy_hal.h`; private structures and callbacks are in `phy_int.h`.

## Risks and Edge Cases
- Several early returns in `wlc_phy_init()` occur after `pi->init_in_progress = true`, which can leave later init attempts blocked.
- Register access is core-revision-sensitive; wrong radio offsets or missed flushes can produce stale or invalid hardware state.
- `wlc_phy_txpower_sromlimit()` can index a 5 GHz hardware-power array with the loop index even if the channel was not found.
- LCN packet RSSI correction indexes a gain-offset table from hardware status without a local bounds check.
- Hold flags must be balanced by callers; stale scan/mute/association holds can suppress measurements or calibration indefinitely.
- `wlc_phy_cal_txpower_recalc_sw()` and `wlc_phy_ldpc_override_set()` are stubs, so callers should not assume behavior beyond current no-op semantics.

## Test Signals
- Build with NPHY and LCNPHY enabled across representative D11 core revisions.
- Attach tests: invalid band, invalid radio, dual-band reference count, timer failure, NPHY attach, LCN attach.
- Init tests: MAC-disabled precondition, fast-clock precondition, bandwidth transition, backend callback, dummy TX, RX diversity restoration.
- Channel tests: SHM `M_CURCHANNEL`, valid-channel bit vectors, channel-to-frequency, high-5G disable.
- TX power tests: user/regulatory/SROM/env limits, LCN MCS offsets, NPHY OFDM/MCS conversion, SHM updates.
- Noise/RSSI/watchdog tests: background interrupt, polling paths, fixed-noise mode, stale noise timeout, scan/association hold behavior, and calibration skip/run decisions.
