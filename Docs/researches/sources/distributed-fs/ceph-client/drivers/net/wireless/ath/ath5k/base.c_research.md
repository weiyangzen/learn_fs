# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/base.c

## Purpose
`base.c` is the main mac80211-facing ath5k driver implementation. It registers hardware capabilities, builds channel/rate tables, allocates DMA descriptors and software buffers, manages RX/TX queues, handles interrupts and tasklets, performs reset/start/stop/deinit, configures beaconing, exposes regulatory integration, and converts hardware descriptor status into mac80211 RX/TX status.

## Important APIs, functions, and data
- Module parameters: `nohwcrypt`, `fastchanswitch`, and `no_hw_rfkill_switch`.
- Static data: `srev_names` for chip naming and `ath5k_rates` for CCK/OFDM rate mappings.
- mac80211 lifecycle: `ath5k_init_ah`, `ath5k_deinit_ah`, `ath5k_start`, `ath5k_stop`, internal `ath5k_init`, `ath5k_reset`, `ath5k_stop_locked`, and `ath5k_reset_work`.
- Channel/rate setup: `ath5k_setup_channels`, `ath5k_setup_bands`, `ath5k_setup_rate_idx`, `ath5k_chan_set`.
- Interface state: `ath5k_vif_iter`, `ath5k_update_bssid_mask_and_opmode`, `ath5k_any_vif_assoc`, `ath5k_set_beacon_filter`.
- DMA and buffers: `ath5k_desc_alloc/free`, `ath5k_rx_skb_alloc`, `ath5k_rxbuf_setup`, `ath5k_txbuf_setup`, `ath5k_txbuf_free_skb`, `ath5k_rxbuf_free_skb`.
- RX/TX processing: `ath5k_tasklet_rx`, `ath5k_receive_frame_ok`, `ath5k_receive_frame`, `ath5k_tx_queue`, `ath5k_tx_processq`, `ath5k_tasklet_tx`, `ath5k_tx_frame_completed`.
- Beaconing: `ath5k_beacon_setup`, `ath5k_beacon_update`, `ath5k_beacon_send`, `ath5k_beacon_update_timers`, `ath5k_beacon_config`, `ath5k_tasklet_beacon`.
- Interrupt/calibration: `ath5k_intr`, `ath5k_intr_calibration_poll`, `ath5k_calibrate_work`, `ath5k_tasklet_ani`, `ath5k_tx_complete_poll_work`.

## Control flow
Attach starts in `ath5k_init_ah`: it sets mac80211 feature flags, supported interface combinations, antenna masks, IRQ handler, bus/common operations, cache line size, calls `ath5k_hw_init`, configures MRR limits, then calls internal `ath5k_init`. `ath5k_init` builds supported bands from capability bits and regulatory-compatible channel checks, allocates descriptor DMA memory and buffer objects, sets up beacon/CAB/data queues, initializes tasklets/work items, reads the permanent MAC from EEPROM, initializes regulatory state, registers the hw with mac80211, then initializes LEDs and sysfs.

Runtime start is `ath5k_start`: stop any old state, set the current channel and interrupt mask, call `ath5k_reset`, start hardware rfkill if enabled, clear key cache, reset beacon slots, mark started, and queue TX completion polling. `ath5k_reset` disables interrupts, kills tasklets, disables ANI, drains TX, stops RX PCU/DMA, optionally fast-switches channel, calls `ath5k_hw_reset`, rebuilds RX descriptors, restores ANI, schedules calibration deadlines, clears survey/cycle counters, configures beacons and wakes mac80211 queues.

TX flow starts at `ath5k_tx_queue`: add 4-byte MAC header padding if needed, stop queues on high-water marks or no buffers, pull a free `ath5k_buf`, and call `ath5k_txbuf_setup`. That maps the skb for DMA, merges station rate tables or asks mac80211 for rates, resolves key index, RTS/CTS/CTS-to-self settings, fills the version-specific descriptor through `ah_setup_tx_desc`, optionally fills MRR, links the descriptor to the hardware queue, and starts TX DMA. Completion arrives through interrupts into `ath5k_tasklet_tx`, which processes queues selected by ISR bits, converts status into `ieee80211_tx_status_skb`, unmaps DMA, and recycles buffers while avoiding a hardware race on the last descriptor.

RX flow is descriptor-ring based. `ath5k_rx_start` creates a self-linked tail ring and starts RX DMA/PCU. `ath5k_tasklet_rx` walks descriptors until the hardware-owned descriptor or in-progress status, filters acceptable frames, replaces the SKB before handing the old one up, unmaps DMA, sets `ieee80211_rx_status`, extends timestamps, tracks beacon RSSI/IBSS TSF, and calls `ieee80211_rx`.

Interrupt flow loops over ISR status until no PCI interrupt remains or a safety counter expires. Fatal and older RX overrun conditions schedule reset work. RX/TX statuses schedule tasklets, SWBA schedules beacon work, TX underrun raises trigger level, MIB updates counters and ANI, and GPIO schedules rfkill. RX/TX interrupts are temporarily masked while tasklets are pending.

## State and persistence behavior
All runtime state lives in `ath5k_hw`, `ath_common`, DMA-coherent descriptor memory, SKBs, work/tasklet state, and hardware registers. The file tracks queue lengths, buffer pools, BSSID masks, current opmode/channel, beacons, calibration deadlines, survey counters, and error statistics. It reads EEPROM MAC/regdomain through bus ops. No persistent file state is written. Hardware state persists only until reset, stop, suspend, or module unload.

## Dependencies and integration points
The file depends heavily on mac80211/cfg80211 APIs, Linux DMA mapping, IRQ/tasklet/workqueue primitives, list/spinlock/mutex primitives, shared ath helpers for crypto/regulatory/cycle counters, ath5k hardware helpers from `ath5k.h`, register definitions, ANI, descriptor functions, LED/sysfs/rfkill helpers, and tracepoints. It bridges bus-specific probe code with mac80211 registration and the lower hardware files.

## Risks and edge cases
- DMA and descriptor ownership are race-prone; the code intentionally keeps the last TX descriptor and uses self-linked RX descriptors to avoid hardware races.
- Reset ordering is critical: interrupts/tasklets, ANI, TX drain, PCU/DMA stop, hardware reset, RX restart, beacon config, and queue wake must remain synchronized under `ah->lock`.
- `ath5k_start` sets `ATH_STAT_STARTED` and schedules polling after `done` even if reset returned an error, which is worth scrutiny when changing start error handling.
- Header padding mutates SKBs before DMA and must be removed on TX completion/RX receive paths.
- `ath5k_extend_tsf` depends on timely RX processing of 15-bit timestamps.
- Multi-vif BSSID mask and opmode logic has special promiscuous behavior for multiple STA interfaces and limited mixed-mode assumptions.

## Test signals
Important signals include successful `ieee80211_register_hw`, visible 2 GHz/5 GHz bands and rate maps, stable `ip link set up/down`, scanning and channel switching, AP/IBSS beacon generation, TX status ACK/retry reporting, RX FCS/decrypt/MIC behavior, rfkill GPIO toggles, debugfs queue/frameerror counters, no stuck TX queue resets during normal load, no interrupt storms, and clean module unload after active traffic.
