# Research: subset-b-004800

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/main.c

## Purpose

`main.c` is the central common/BMAC implementation for the Broadcom `brcmsmac`
soft-MAC driver. It owns attachment, initialization, bring-up, shutdown,
interrupt dispatch, DMA ring integration, D11 core programming, microcode
loading, channel and band changes, rate/PLCP duration calculations, TX header
construction, TX completion feedback, RX status conversion, beacon/probe
template programming, WME parameter programming, radio-disable monitoring, and
the watchdog loop.

The file bridges three major boundaries:

- Linux/mac80211: `ieee80211_hw`, `ieee80211_tx_info`,
  `ieee80211_rx_status`, queue stop/wake, TX status, RX delivery, channel and
  vif state.
- Broadcom bus/core access: BCMA, chipcommon, AI/SI helpers, SPROM, D11 core
  registers, shared memory, template RAM, and object memory.
- Driver-local subsystems: PHY HAL, channel manager, antenna selection, STF,
  AMPDU, DMA, ucode loader, debug/trace, and public `brcms_pub` state.

The source is not a thin wrapper. It is the state-machine center of the driver:
it maintains software shadows for hardware state, sequences clocks/resets
around D11 access, translates mac80211 packet metadata into Broadcom TX
descriptors, and translates hardware RX/TX status back to mac80211.

## Important Constants And Tables

The local constants define timing, default QoS, retry, FIFO, PLCP, and hardware
limits used throughout the D11 control path:

- Timer intervals: `TIMER_INTERVAL_WATCHDOG` is 1000 ms and
  `TIMER_INTERVAL_RADIOCHK` is 800 ms.
- Beacon and template sizes: `BEACON_INTERVAL_DEFAULT` is 100 TU and
  `BCN_TMPL_LEN` caps beacon/probe templates at 512 bytes.
- D11 queue sizing: `NTXD`, `NRXD`, `TX_HEADROOM`, `NRXBUFPOST`, `RXBND`, and
  `TXSBND` bound descriptor rings and deferred processing.
- 802.11 duration helpers: CCK/OFDM/MIMO preamble, SIFS, slot, ACK/CTS/RTS,
  BA, and fragment-size constants feed the frame-duration calculations.
- WME/EDCF defaults: `default_edcf_acparams` and related masks encode default
  AC BE/BK/VI/VO contention and TXOP parameters.
- `wme_fifo2ac`, `wme_ac2fifo`, `ac_to_fifo_mapping`, and
  `fifo_to_ac_mapping` translate between mac80211 access categories and the
  Broadcom TX FIFOs.
- `xmtfifo_sz` contains per-core-revision FIFO block allocations. The driver
  writes these sizes into D11 FIFO registers and corresponding ucode SHM.

These constants are tightly coupled to hardware and ucode expectations. A wrong
value does not usually fail at compile time; it can cause frame underruns, bad
duration fields, unusable TX status, or firmware/hardware queue mismatch.

## Main Public Entry Points

The file exposes the common driver operations used by the mac80211 interface
layer and sibling modules:

- Lifecycle: `brcms_c_attach`, `brcms_c_detach`, `brcms_c_up`,
  `brcms_c_down`, `brcms_c_init`, `brcms_c_reset`, `brcms_c_pub`.
- Interrupt and DPC: `brcms_c_isr`, `brcms_c_intrsupd`, `brcms_c_dpc`,
  `brcms_c_intrson`, `brcms_c_intrsoff`, `brcms_c_intrsrestore`.
- TX path: `brcms_c_sendpkt_mac80211`, `brcms_c_txfifo`,
  `brcms_c_tx_flush_completed`, `brcms_c_inval_dma_pkts`,
  `brcms_c_get_header_len`.
- RX path support is mostly private, but ends in mac80211 delivery through
  `ieee80211_rx_irqsafe`.
- Configuration: `brcms_c_set_channel`, `brcms_c_set_gmode`,
  `brcms_c_set_nmode`, `brcms_c_set_rateset`,
  `brcms_c_get_current_rateset`, `brcms_c_set_rate_limit`,
  `brcms_c_set_beacon_period`, `brcms_c_set_shortslot_override`,
  `brcms_c_set_tx_power`, `brcms_c_get_tx_power`,
  `brcms_c_set_beacon_listen_interval`, `brcms_c_tsf_get`,
  `brcms_c_tsf_set`, `brcms_c_mac_promisc`.
- AP/STA/IBSS state: `brcms_c_start_station`, `brcms_c_start_ap`,
  `brcms_c_start_adhoc`, `brcms_c_set_ssid`,
  `brcms_c_associate_upd`, `brcms_c_scan_start`, `brcms_c_scan_stop`.
- Beacon/probe response: `brcms_c_set_new_beacon`,
  `brcms_c_update_beacon`, `brcms_c_set_new_probe_resp`,
  `brcms_c_update_probe_resp`, `brcms_c_enable_probe_resp`.
- Low-level BMAC helpers exported to other driver files:
  `brcms_b_set_chanspec`, `brcms_b_write_shm`, `brcms_b_read_shm`,
  `brcms_b_mhf`, `brcms_b_mctrl`, `brcms_b_corereset`,
  `brcms_b_phy_reset`, `brcms_b_bw_set`, `brcms_b_core_phypll_reset`,
  `brcms_b_write_template_ram`, `brcms_b_rate_shm_offset`,
  `brcms_b_copyto_objmem`, `brcms_b_copyfrom_objmem`,
  `brcms_b_switch_macfreq`, `brcms_b_get_txant`, `brcms_b_txant_set`,
  `brcms_b_band_stf_ss_set`, `brcms_b_xmtfifo_sz_get`, and PHY clock helpers.

## Attach And Allocation Flow

`brcms_c_attach` is the high-level constructor. It allocates the common state
with `brcms_c_attach_malloc`, wires public and private pointers, initializes
defaults with `brcms_c_info_init` and `brcms_c_ap_upd`, then delegates hardware
probing to `brcms_b_attach`.

`brcms_c_attach_malloc` allocates a `struct brcms_c_info` and its owned
subobjects: `brcms_pub`, `brcms_hardware`, hardware band array, module callback
array, default BSS, BSS config/current BSS, protection state, STF state, common
band array, core state, and MAC-stat snapshot. Allocation uses `GFP_ATOMIC`.
Every allocation failure assigns a unique-ish error number and funnels through
`brcms_c_detach_mfree`.

`brcms_b_attach` performs hardware discovery and low-level state setup:

- Logs PCI or SoC identity and initializes `struct brcms_hardware` defaults.
- Attaches AI/SI state with `ai_attach` and checks device support through
  `brcms_c_chipmatch`.
- Records vendor/device/core revision, validates D11 core revision with
  `brcms_c_isgoodchip`, initializes clock control, forces fast clock, resets
  the D11 core, and verifies register access through
  `brcms_b_validate_chip_access`.
- Reads SPROM board revision, SROM revision, board flags, and MAC address.
- Determines single-band versus dual-band capability from device IDs.
- Attaches the PHY shim and shared PHY state, then loops over each band,
  assigning band unit/type, reading MAC capabilities, selecting TX FIFO sizing,
  attaching a per-band PHY, validating PHY type/revision, copying PHY/radio
  metadata into both hardware and common band state, and attaching DMA.
- Leaves hardware in the driver-down state: D11 core disabled, PCI host down,
  PLL/xtal off where possible.

Back in `brcms_c_attach`, the file computes STF chain setup, initializes
per-band antenna and rateset state, attaches module subsystems
(`antsel`, `ampdu`, `stf`), initializes timers, attaches the channel manager,
initializes the default BSS, configures MIMO bandwidth capability and SGI state,
and returns the ready `brcms_c_info`.

Failure paths are deliberately centralized. `brcms_c_attach` calls
`brcms_c_detach` on partial state. `brcms_c_detach` tears down BMAC, radio
monitoring, channel manager, timers, modules, and memory. The code assumes
detach should generally not touch D11 registers because the core may be reset
or clock-gated.

## Hardware Bring-Up, Init, And Shutdown

The bring-up path is staged:

1. `brcms_c_up` rejects removed or hardware-off devices. If hardware has not
   been powered after POR/S3/S5, it calls `brcms_b_hw_up`.
2. It applies board-specific FEM host flags, runs `brcms_b_up_prep` if the
   radio is not already disabled, and handles hardware rfkill by starting the
   radio monitor timer rather than fully starting the device.
3. It marks the common clock state, stops radio monitoring, enables EDCF host
   flags, calls the outer `brcms_init(wlc->wl)` hook, handles pending band init
   and channel switch, finishes BMAC bring-up with `brcms_b_up_finish`, writes
   WME retry limits, arms the watchdog, updates TX antenna and LDPC state.

`brcms_b_up_prep` powers xtal/PLL, initializes clock control, forces fast
clock, enables PCI IRQ routing, checks hardware radio-disable state, brings PCI
host up, and resets the D11 core. `brcms_b_up_finish` marks hardware up,
updates PHY state, returns dynamic clock control, and enables interrupts.

`brcms_c_init` is the full D11 initialization path after reset. It:

- Computes the current mac80211 channel's 20 MHz chanspec and calls
  `brcms_b_init`.
- Updates beacon listen interval, MAC address, and BSSID registers.
- Restores TSF beacon-period related values if already associated.
- Initializes per-band rate state and selected channel through
  `brcms_c_bandinit_ordered`.
- Programs probe-response timeout, max burst TXOP, duty-cycle SHM, AMPDU SHM,
  band-specific rate tables and antenna state, EDCF, ucode version reporting,
  and RF-disable delay.
- Enables MAC execution via `brcms_c_enable_mac`.
- Optionally mutes TX.
- Reads WME retries from SHM if not already initialized.

`brcms_b_init` sequences low-level init: force fast clock, disable interrupts,
select band, set PHY radio channel, run PHY calibration, run `brcms_b_coreinit`,
run band-specific `brcms_b_bsinit`, restore interrupts, seed MAC suspend state,
and return to dynamic clocking.

`brcms_b_coreinit` is the core D11 programming sequence. It resets the PSM,
downloads ucode once, starts PSM until it self-suspends, initializes GPIOs,
writes core-revision/PHY-specific init tables, fixes TX FIFO sizing, verifies
SHM FIFO sizes against driver expectations, programs frameburst/antenna
defaults, RX interrupt laziness, station-mode maccontrol, beacon interval
registers, RX FIFO interrupt mask, dynamic PHY clock control, fast power-up
delay, hardware revision/capability SHM values, retry limits, fallback retry
limits, EDCF defaults, TX DMA engines, RX DMA engine, and RX buffers.

Shutdown is also staged:

- `brcms_c_down` guards against reentry with `going_down`, calls
  `brcms_b_bmac_down_prep`, invokes registered module down callbacks, stops the
  watchdog, marks public state down, unmutes PHY, calls `brcms_b_down_finish`,
  clears common clock state, and releases the reentry guard.
- `brcms_b_bmac_down_prep` disables interrupts and forces fast clock unless the
  device is gone, then brings PHY down.
- `brcms_b_down_finish` marks hardware down, updates PHY state, reclaims queues
  if the device is gone, or suspends MAC, resets, disables D11, powers PCI and
  xtal down if safe.

## Clock, Reset, And MAC Control State

This file keeps software shadows for D11 state that must survive optimized
register writes:

- `wlc_hw->maccontrol` is the cached MAC control value.
- `wake_override`, `mute_override`, and `suspended_fifos` are software
  overlays applied by `brcms_c_mctrl_write`.
- `mac_suspend_depth` tracks nested MAC suspend callers.
- `clk`, `sbclk`, `phyclk`, `forcefastclk`, `pllreq`, and `ucode_loaded`
  describe hardware power/clock/microcode state.

`brcms_b_mctrl` applies masked updates to the cached maccontrol and writes the
composed value only when it changes. `brcms_c_ucode_wake_override_set` and
`brcms_c_ucode_wake_override_clear` force or release ucode wake. Setting a
first wake override writes `MCTL_WAKE` and waits for ucode wake with
`brcms_b_wait_for_wake`. Mute override forces a non-beaconing STA-like
maccontrol shape by clearing AP and setting INFRA.

`brcms_c_suspend_mac_and_wait` and `brcms_c_enable_mac` are the main safe
windows around register/SHM changes that require a suspended PSM. They use
`mac_suspend_depth` to coalesce nested callers, set a wake override, clear
`MCTL_EN_MAC`, wait for `MI_MACSSPNDD`, and re-enable MAC later while clearing
the suspend interrupt and wake override. Failures to read valid registers call
`brcms_down`.

Clock and reset helpers include:

- `brcms_b_clkctl_clk`: switches PMU or legacy clock control between fast and
  dynamic modes and synchronizes `forcefastclk` plus wake overrides.
- `brcms_b_xtal`: records external oscillator/backplane clock state and avoids
  power-down while PLL requests exist.
- `brcms_b_corereset`: forces fast clock, resets DMA rings, enables D11 core,
  resets MAC control state, resets PHY, enables PHY PLL, clears software
  interrupt status, and restores clock mode.
- `brcms_b_phy_reset`, `brcms_b_core_phypll_reset`, and
  `brcms_b_core_phypll_ctl`: handle PHY reset and PLL sequences, including
  revision-specific NPHY handling.
- `brcms_c_coredisable`: turns radio/analog/PHY PLL off and disables D11 core
  unless the device is removed or `noreset` is set.

The risk is that these state shadows and register writes are order-dependent.
Callers that touch D11 registers without ensuring clock/MAC state can race
hardware sleep or PSM execution.

## Interrupt And Deferred Processing Flow

The first-level path is `brcms_c_isr`. It exits when hardware is not up or the
software interrupt mask is zero. Otherwise it calls `wlc_intstatus` in ISR mode.
`wlc_intstatus` reads `macintstatus`, traces it, detects device removal, masks
unrequested bits, disables further MAC interrupts, clears handled bits in
hardware, clears RX FIFO interrupt status when `MI_DMAINT` is present, and
returns the pending masked status. `brcms_c_isr` stores that status in
`wlc->macintstatus` and asks the caller to schedule deferred work.

`brcms_c_intrsupd` performs a similar status update outside the ISR path, ORing
new bits into `wlc->macintstatus`.

`brcms_c_dpc` is the second-level dispatcher. It first detects device removal,
then consumes and clears `wlc->macintstatus`. It handles:

- `MI_TFS`: drain TX status through `brcms_b_txstatus`, possibly setting
  `MI_TFS` again if bounded processing stopped early.
- `MI_TBTT`/`MI_DTIM_TBTT`: call `brcms_c_tbtt` to mark direct frame queue
  valid for adhoc mode.
- `MI_ATIMWINEND`: push queued valid bits to `maccommand`.
- `MI_DMAINT`: receive frames through `brcms_b_recv`, possibly requeueing
  `MI_DMAINT` if bounded processing has more work.
- `MI_BG_NOISE`: notify PHY noise-sample interrupt.
- `MI_GP0`: report PSM watchdog and call `brcms_fatal_error`.
- `MI_TO`: clear general purpose timer.
- `MI_RFDISABLE`: notify rfkill state change.
- `MI_BCNTPL`: update beacon template.

The function returns whether `wlc->macintstatus` still has work and therefore
whether DPC should be rescheduled. Fatal TX status or PSM watchdog paths call
the driver's fatal-error hook.

## DMA, TX Status, And Queue Flow Control

`brcms_b_attach_dmapio` creates DMA handles for FIFO 0 through 3. FIFO 0 is
both background TX and RX; FIFOs 1, 2, and 3 are BE, VI, and VO TX. It records
each DMA engine's `txavail` pointer for later queue flow control. Detach and
reset paths use `brcms_b_detach_dmapio`, `brcms_c_flushqueues`, DMA reset,
reclaim, and fill helpers.

The transmit enqueue path is:

1. `brcms_c_sendpkt_mac80211` maps mac80211 queue to Broadcom FIFO and calls
   `brcms_c_d11hdrs_mac80211`.
2. `brcms_c_d11hdrs_mac80211` prepends PLCP and D11 TX header, fills rate,
   duration, protection, antenna, and FIFO metadata.
3. `brcms_c_tx` verifies DMA availability, commits BCMC frame ID to SHM when
   needed, then calls `brcms_c_txfifo`.
4. `brcms_c_txfifo` calls `dma_txfast` and stops the corresponding mac80211
   queue when `txavail <= TX_HEADROOM`.

TX completion runs through `brcms_b_txstatus`, which reads hardware TX status
registers until empty or bounded by `TXSBND`, then calls
`brcms_c_dotxstatus`. `brcms_c_dotxstatus` validates the queue and frame ID,
retrieves the transmitted SKB from the DMA engine, handles AMPDU status through
`brcms_c_ampdu_dotxstatus`, reconstructs mac80211 rate counts for Minstrel,
sets `IEEE80211_TX_STAT_ACK` when appropriate, strips PLCP and D11 TX headers,
and calls `ieee80211_tx_status_irqsafe`. Fatal mismatches free the SKB. After
status handling, it wakes a stopped mac80211 queue when DMA space is above
`TX_HEADROOM` and kicks DMA.

Important edge conditions:

- Intermediate non-AMPDU status is ignored as nonfatal.
- Frame ID mismatch, missing DMA packet, invalid queue, or invalid status path
  is treated as fatal for the packet and may trigger larger recovery.
- Queue stop/wake assumes the same mapping between FIFO and mac80211 ACs used
  in TX construction.

## TX Descriptor, Rate, PLCP, And Duration Logic

`brcms_c_d11hdrs_mac80211` is the largest single function because it constructs
the exact Broadcom D11 transmit descriptor. Its inputs are a packet whose data
starts at the 802.11 MAC header, the selected mac80211 rates, the target FIFO,
fragment metadata, and a station control block. It:

- Pushes D11 PHY and TX headers using `skb_push`.
- Handles sequence assignment and frame ID construction, including multicast
  frame IDs through `bcmc_fid_generate`.
- Extracts primary/fallback mac80211 rates and converts them to Broadcom
  ratespec values. MCS conversion is delegated to `mac80211_wlc_set_nrate`.
- Determines RTS/CTS protection, short preamble, CCK/OFDM/MCS frame types,
  20/40 MHz width, STBC/SISO/CDD/SDM mode, and antenna configuration.
- Builds PLCP headers for main and fallback rates through
  `brcms_c_compute_plcp`.
- Calculates MPDU duration fields, fallback duration, RTS/CTS duration, and
  WME TXOP durations.
- Fills D11 `d11txh` fields such as `MacTxControlLow`,
  `MacTxControlHigh`, `MacFrameControl`, `TxFrameRA`, `TxFrameID`,
  `MainRates`, `XtraFrameTypes`, `PhyTxControlWord`,
  `PhyTxControlWord_1`, fallback PHY controls, mixed-mode length fields,
  RTS frame, RTS PLCP, and fallback RTS duration.
- Updates per-FIFO fragmentation thresholds when WME TXOP budget implies a
  smaller threshold.

Duration and PLCP helpers include:

- `brcms_c_calc_frame_time`: computes airtime for MCS, OFDM, or CCK frames.
- `brcms_c_calc_frame_len`: inverse of duration to length.
- `brcms_c_compute_frame_dur`: computes MAC duration including ACK/SIFS and
  optional next-fragment time.
- `brcms_c_compute_rtscts_dur`: computes RTS/CTS or CTS-to-self duration.
- `brcms_c_calc_lsig_len`: computes HT mixed-mode L-SIG spoof length.
- `brcms_c_compute_mimo_plcp`, `brcms_c_compute_ofdm_plcp`, and
  `brcms_c_compute_cck_plcp`: encode PHY headers for the selected modulation.
- `brcms_c_phytxctl1_calc`: calculates PHY TX control word 1 from ratespec.
- `brcms_c_rspec_to_rts_rspec`: selects a basic/protection rate for RTS/CTS.

The code deliberately disables short GI in TX descriptor construction. MCS32 is
handled specially because it requires 40 MHz duplicate mode. Unsupported rates
fall back to 1 Mbps or are rejected by `brcms_c_valid_rate`.

## RX Flow And Status Conversion

RX is initiated by `brcms_b_recv` from the DPC `MI_DMAINT` path. It drains DMA
RX frames into a temporary SKB queue bounded by `RXBND` when requested, refills
RX buffers, converts the little-endian D11 RX header fields in place, and calls
`brcms_c_recv` for each frame.

`brcms_c_recv` strips the hardware RX offset (`BRCMS_HWRXOFF`), removes padding
when `RXS_PBPRES` is set, filters FCS failures unless `FIF_FCSFAIL` is enabled,
rejects runt frames and A-MSDU frames, and passes the packet to
`brcms_c_recvctl`.

`brcms_c_recvctl` prepares a mac80211 RX status structure with
`prep_mac80211_status`, strips PLCP and FCS from the SKB, unmutes TX after a
beacon if FIFOs were suspended, copies the status into `IEEE80211_SKB_RXCB`,
and delivers the packet through `ieee80211_rx_irqsafe`.

`prep_mac80211_status` reconstructs RX metadata:

- TSF is recovered from the 16-bit RX header TSF plus current 64-bit TSF via
  `brcms_c_recover_tsf64`.
- Channel, band, frequency, RSSI, antenna, rate/MCS index, HT encoding, 40 MHz
  bandwidth, short preamble, short GI, PLCP CRC, and FCS CRC flags are mapped
  into mac80211 fields.
- Legacy 5 GHz rate indexes are adjusted by `BRCMS_LEGACY_5G_RATE_OFFSET`.

The RX path does not support A-MSDU here and silently drops those frames. That
is an important behavioral limitation.

## Beacon And Probe Response Handling

Beacon and probe response state is cached as SKBs in `wlc->beacon` and
`wlc->probe_resp`. `brcms_c_set_new_beacon` and
`brcms_c_set_new_probe_resp` replace the cached SKBs, push PLCP headroom, and
immediately try to update hardware if the interface is up and in AP or adhoc
mode.

`brcms_c_update_beacon` clears the beacon-template interrupt bit in the default
interrupt mask and calls `brcms_c_update_beacon_hw` for AP/adhoc modes.
`brcms_c_update_beacon_hw` manages the dual D11 beacon templates. On a virgin
template it writes both and marks beacon0 valid. Later it waits if both
templates are busy, enabling `MI_BCNTPL` so DPC can retry when one is free, or
writes whichever template is not valid.

`brcms_c_beacon_write` calculates beacon PLCP, updates beacon PHY TX antenna
control, writes template RAM at `T_BCN0_TPL_BASE` and/or `T_BCN1_TPL_BASE`,
updates beacon length SHM, and programs TIM offset/DTIM period.

Probe responses are handled by `brcms_c_update_probe_resp` and
`brcms_c_bss_update_probe_resp`. The latter can suspend MAC, writes probe
response template RAM, records frame length, writes SSID/SSID length to SHM,
and updates per-rate probe-response PLCP/duration entries with
`brcms_c_mod_prb_rsp_rate_table`. `brcms_c_enable_probe_resp` controls ucode
probe response by programming `M_PRS_MAXTIME`; disabling sets timeout to 1 so
ucode effectively cannot respond in time.

## Channel, Band, Rate, Protection, And WME Configuration

Channel handling occurs at both BMAC and common layers:

- `brcms_b_set_chanspec` updates the hardware chanspec shadow, changes bands
  if needed, initializes or sets PHY chanspec, applies TX power limits, and
  mutes/unmutes TX according to channel muting.
- `brcms_c_set_chanspec` validates the chanspec, handles multi-band switching
  unless band-locked, calls `brcms_c_set_phy_chanspec`, updates antenna
  selection and MCS filtering on bandwidth changes, and updates ucode MAC
  state.
- `brcms_c_set_channel` converts a channel number to a 20 MHz chanspec,
  validates it, marks `bandinit_pending` if down and a different unlocked band
  is needed, updates default BSS, and performs a suspend/change/enable sequence
  when up.

Rate and mode configuration:

- `brcms_c_set_gmode` selects 2.4 GHz G mode, short-slot override, default
  rateset, and OFDM basic rates depending on GMODE.
- `brcms_c_set_nmode` enables 11n/HT, forces G auto, sets default BSS HT flag,
  builds MCS rates, and propagates MCS sets to each band hardware rateset.
- `brcms_c_set_rateset` validates user-provided legacy rates against current
  or other unlocked band hardware ratesets and preserves MCS sets when 11n is
  enabled.
- `brcms_c_rate_lookup_init`, `brcms_c_set_ratetable`, and
  `brcms_c_write_rate_shm` maintain basic-rate lookup and ucode SHM mappings.

Protection state is centralized in `brcms_c_protection_upd`, which writes
fields in `wlc->protection` by index. The function is used early in attach and
by mode configuration. Its lack of consistency validation is intentional but
means callers must maintain coherent combinations.

WME/EDCF:

- `brcms_c_wme_setparams` converts mac80211 queue params into ucode SHM AC
  entries, including TXOP units, AIFS, CW min/max/current, random backoff
  slots, and `WME_STATUS_NEWAC`.
- It updates beacons and probe responses after changing parameters and can
  suspend MAC around the change.
- `brcms_c_edcf_setparams` applies defaults for all ACs.
- `brcms_c_set_rate_limit` validates SRL/LRL, updates hardware retry limits,
  updates per-AC WME retry fields, and writes retry SHM when clocked.

## Shared Memory, Object Memory, Template RAM

The file provides the core memory access routines used by other modules:

- `brcms_b_read_objmem` and `brcms_b_write_objmem` select object memory via
  `objaddr` and access low/high 16-bit halves via `objdata`.
- `brcms_b_read_shm` and `brcms_b_write_shm` specialize object memory access
  to SHM.
- `brcms_b_copyto_objmem` and `brcms_b_copyfrom_objmem` copy even-sized,
  even-offset byte buffers as 16-bit little-endian values.
- `brcms_c_copyto_shm` wraps SHM writes for common state.
- `brcms_b_write_template_ram` writes template RAM as 32-bit words and handles
  D11 big-endian mode.

These helpers silently return for invalid offset/length combinations in copy
paths. Callers must ensure offsets and lengths are even, and template writes
must provide lengths rounded up by callers.

## Radio Monitor, Watchdog, And Health Checks

`brcms_b_radio_read_hwdisabled` reads the hardware radio disable signal. It may
temporarily turn xtal on and D11 core out of reset to access registers, then
restores the previous state. `brcms_c_radio_hwdisable_upd` maps the hardware
state to `wlc->pub->radio_disabled`. `brcms_c_radio_monitor_start` holds PLL
through `BRCMS_PLLREQ_RADIO_MON` and starts the radio timer while down due to
rfkill; `brcms_c_radio_monitor_stop` reverses it.

`brcms_c_watchdog` runs while public state is up. It detects device removal,
updates radio disable state, exits if radio-disabled, calls `brcms_b_watchdog`,
periodically snapshots MAC stats every `SW_TIMER_MAC_STAT_UPD`, and updates NPHY
temperature sensing every `BRCMS_TEMPSENSE_PERIOD`.

`brcms_b_watchdog` increments hardware seconds, checks FIFO error interrupt
status through `brcms_b_fifoerrors`, refills RX DMA buffers, and calls the PHY
watchdog. FIFO overflow, descriptor errors, data errors, and TX underflows can
invoke `brcms_fatal_error`.

`brcms_c_statsupd` snapshots ucode MAC stats from SHM and resets DMA counters.
Under DEBUG it reports deltas for RX FIFO overflow and TX underflow counters.

## State And Persistence Behavior

Most state is volatile driver runtime state, not persistent storage. Durable
inputs come from SPROM/board descriptors, firmware/ucode arrays loaded by
`ucode_loader`, and mac80211 configuration. Important runtime state includes:

- Public state: `wlc->pub->up`, `hw_up`, `hw_off`, `radio_disabled`,
  `associated`, `cur_etheraddr`, hardware metadata, and mac80211 handle.
- Hardware state: `wlc_hw->up`, `clk`, `sbclk`, `phyclk`, `forcefastclk`,
  `pllreq`, `maccontrol`, `wake_override`, `mute_override`, `suspended_fifos`,
  active `band`, `chanspec`, DMA handles, FIFO sizes, retry limits, and antenna
  state.
- Common state: active `band`, `bandlocked`, `bandinit_pending`,
  `macintstatus`, `macintmask`, `defmacintmask`, watchdog/radio timers, WME
  TXOP/retry arrays, protection config, default/current BSS, beacon/probe SKBs,
  channel/rate/shortslot configuration, TSF programming, and ucode revision.
- Per-band state: phy/radio identity, PHY handle, hardware/default ratesets,
  basic-rate table, 40 MHz capability, antenna gain, CW min/max.

There is no file persistence. Hardware persistence occurs through register,
SHM, SCR, object memory, and template RAM writes. Several state transitions are
cached in software first and then written only if the hardware is clocked or
up, so down/up paths must reprogram them.

## Dependencies And Integration Points

External kernel dependencies:

- `linux/pci_ids.h`, `linux/if_ether.h`, `net/cfg80211.h`,
  `net/mac80211.h`.
- mac80211 APIs for TX/RX status, queues, rates, channels, and vif behavior.
- SKB helpers and endian helpers.

Broadcom infrastructure:

- `brcm_hw_ids.h`, `aiutils.h`, `chipcommon.h`, BCMA core register access,
  SPROM, chip IDs, chipcommon GPIO/clock helpers.
- D11 register definitions, SHM offsets, MHF flags, TX/RX headers, and ucode
  constants from local headers.

Local driver modules:

- `rate.h` and rate tables/helpers.
- `scb.h` for per-station sequence and capability state.
- `phy/phy_hal.h` for PHY attach/init/calibration/radio/RSSI/power/hold state.
- `channel.h` for chanspec validation and TX power limits.
- `antsel.h`, `stf.h`, and `ampdu.h` for antenna, transmit stream, and
  aggregation behavior.
- `mac80211_if.h` for brcmsmac/mac80211 wrapper types and calls.
- `ucode_loader.h` for firmware/init tables.
- `dma.h` for DMA ring lifecycle, enqueue, reclaim, status, and RX.
- `debug.h` and `brcms_trace_events.h` for logging and tracepoints.

The file assumes these modules honor clocking and state preconditions. For
example, PHY operations are often called only after D11 clock and band state
are valid, while AMPDU TX status assumes the SKB and SCB pointers line up with
descriptor metadata.

## Risks And Failure Modes

- Hardware sequencing risk: clock, PLL, D11 reset, PHY reset, MAC suspend, and
  ucode wake sequences are order-sensitive. Register access with `clk` false or
  MAC running when suspended access is required can hang or corrupt state.
- Large monolithic TX descriptor logic: `brcms_c_d11hdrs_mac80211` combines
  rate control, protection, duration, PLCP, antenna, bandwidth, frame ID, and
  TXOP logic. Small changes can affect multiple 802.11 modes.
- Silent returns in low-level helpers: invalid MHF masks, invalid object memory
  offsets/lengths, and invalid maccontrol masks often return without explicit
  error. This prevents crashes but can hide programming bugs.
- Device removal races: many paths call `brcms_deviceremoved`, but other paths
  rely on cached state and direct register access. Hot removal or suspend/resume
  remains a sensitive area, as noted by TODO comments.
- Bounded DPC requeue: TX and RX bounded loops set interrupt status bits again.
  Missing reschedule at the caller would leave work pending.
- TX queue flow control race: the code intentionally tolerates one frame after
  queue stop via `TX_HEADROOM`; larger mac80211 queue races can trigger warnings
  or `-ENOSPC`.
- RX limitation: A-MSDU frames are dropped in this path.
- Beacon template race: if both templates are valid, the code defers and
  enables `MI_BCNTPL`; incorrect interrupt mask handling could stall beacon
  updates.
- Multi-band assumptions: `OTHERBANDUNIT` and fixed band indices assume at
  most two bands and band0 as 2.4 GHz, band1 as 5 GHz.
- Firmware table coupling: core revision and PHY type select ucode and init
  tables. Unsupported combinations only log errors in some inner paths; attach
  validation must catch them earlier.
- Endianness/template risk: `brcms_b_write_template_ram` handles big-endian
  maccontrol mode manually. Buffer length is stepped by 4 and relies on callers
  rounding lengths.

## Test Signals

Useful validation signals for this file include:

- Attach/probe tests on supported PCI and SoC device IDs, including unsupported
  IDs and unsupported core/PHY revisions to verify error paths.
- Up/down cycles with rfkill off/on, including start while hardware radio is
  disabled, radio monitor timer behavior, and return to full up after rfkill.
- Suspend/resume or hibernate resume coverage around comments warning about
  AI/BCMA window restoration and hardware power cycling.
- TX smoke tests for each AC queue, queue stop/wake under descriptor pressure,
  and TX status feedback into mac80211/Minstrel.
- AMPDU and non-AMPDU TX status tests, including intermediate status handling.
- RX tests for valid CCK/OFDM/MCS frames, bad FCS filtering with and without
  `FIF_FCSFAIL`, PLCP CRC reporting, RSSI/rate/channel metadata, and A-MSDU
  drop behavior.
- Channel switch tests across 2.4/5 GHz, 20/40 MHz bandwidth changes, and
  `bandinit_pending` while down.
- Beacon/probe response AP and adhoc tests, including dual template rollover,
  TIM/DTIM offsets, probe response enable/disable, and WME parameter changes
  that refresh management templates.
- Watchdog/fatal error injection for FIFO overflow, TX underflow, PSM watchdog,
  and dead-chip register reads.
- Static analysis around integer truncation in duration calculations, buffer
  length rounding for template RAM, sequence/frame ID construction, and invalid
  SHM/object memory offsets.

## Research Notes

The file was read in full. Function indexing was used to verify coverage of
the attach, lifecycle, interrupt, TX, RX, beacon/probe, rate, SHM, and hardware
helper regions. The key architectural observation is that this file is both
the common driver state manager and the BMAC hardware sequencer; correctness
depends less on isolated algorithms and more on preserving preconditions across
clock state, MAC suspend state, DMA ownership, and mac80211 callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/main.h

## Purpose

`main.h` is the central internal contract for the `brcmsmac` common/BMAC
implementation. It defines the primary driver state structures, hardware and
802.11 control constants, bitfield helpers, protection and transmit-stream
state, BMAC hardware state, common driver state, BSS configuration state, and
function prototypes exported by `main.c` to the rest of the driver.

The header is included by local brcmsmac components that need access to core
state or low-level helpers. It is not a public kernel UAPI. It encodes the
driver's internal understanding of D11 core limits, MAC suspend timing, wake
override bits, interrupt masks, FIFO counts, channel/band mapping, and shared
state layout.

## Important Macros And Constants

General driver limits and protocol constants:

- `INVCHANNEL` marks an invalid channel.
- `BRCMS_MAXMODULES` limits registered module callbacks to 22.
- `SEQNUM_SHIFT` and `SEQNUM_MAX` describe 802.11 sequence number layout.
- `NTXRATE` sets the TX MPDU rate-report array size.
- `BRCMS_MAX_MAC_SUSPEND` is the maximum wait for MAC suspend, based on a
  worst-case packet time.
- `BRCMS_PRB_RESP_TIMEOUT` configures probe-response timeout; the value in this
  tree disables timeout by default.
- `TXOFF` is the maximum TX headroom needed for D11 TX header plus PHY header.

Bitfield helpers:

- `BITFIELD_MASK(width)` builds masks.
- `GFIELD(val, field)` extracts named fields using `<field>_S` and
  `<field>_M`.
- `SFIELD(val, field, bits)` updates named bitfields.

Hardware and mode constants:

- `MAXCOREREV` and the `D11CONF` compile-time check prevent unsupported D11
  revisions from being enabled.
- Short slot overrides use `BRCMS_SHORTSLOT_AUTO`, `_OFF`, and `_ON`.
- Preamble flags include long, short, greenfield, and mixed-mode values.
- TX frame ID masks define queue, sequence, rate-probe, and rate-epoch fields.
- Wake override bits cover clock control, PHY register access, MAC suspend,
  TX FIFO suspend, and force-fast-clock cases.
- Interrupt masks `I_ERRORS`, `DEF_RXINTMASK`, and `DEF_MACINTMASK` define the
  default error summary and enabled MAC interrupts.
- `MAXTXPKTS`, frameburst constants, `NFIFO`, and PLL request bits describe
  queue and hardware resource limits.
- `CHANNEL_BANDUNIT` and `OTHERBANDUNIT` map channels and current band state
  to internal band units.

PHY capability helpers:

- `BRCMS_STF_SS_STBC_TX` decides if single-stream STBC TX is allowed based on
  chain count, band STBC policy, SCB capability, and selected channel
  algorithm.
- `BRCMS_STBC_CAP_PHY` and `BRCMS_SGI_CAP_PHY` encode PHY revision capability
  tests.
- `BRCMS_CHAN_PHYTYPE` and `BRCMS_CHAN_CHANNEL` extract RX channel metadata.

These macros are consumed heavily by `main.c`, `stf`, `ampdu`, and other
brcmsmac internals. Many assume specific local naming conventions for bitfield
shift/mask symbols.

## Core Types

### `struct brcms_protection`

Holds 11g/11n protection configuration and overrides:

- 11g protection: `_g`, `g_override`, `gmode_user`, `overlap`.
- 11n protection: `nmode_user`, `n_cfg`, `n_cfg_override`, `nongf`,
  `nongf_override`, `n_pam_override`, `n_obss`.

`main.c` updates this through `brcms_c_protection_upd`. The struct is runtime
configuration state rather than hardware-backed storage by itself.

### `struct brcms_stf`

Tracks space-time/stream/antenna configuration:

- Hardware and active TX/RX chain bitmaps.
- TX/RX stream counts.
- RX antenna override and user TX antenna.
- PHY TX antenna value used in D11 TX headers.
- Single-stream operating mode and algorithm selection state.
- LDPC mode, selected TX core per stream count, and spatial policy.

This state feeds TX descriptor construction, PHY chain initialization, antenna
updates, and STBC/SGI capability decisions.

### `struct brcms_core`

Represents active MAC core state:

- `coreidx` for the enumerated core.
- `txavail[NFIFO]` pointers to DMA TX availability counters.
- `macstat_snapshot` for last-read MAC counters.

The common state points at one active `brcms_core`. `main.c` allocates and
resets its MAC-stat snapshot across reset and stats-update paths.

### `struct brcms_band`

Represents common per-band PHY/radio state:

- Band identity: `bandtype`, `bandunit`.
- PHY/radio type, revision, IDs, PHY handle, and encore flag.
- 11g mode, default/hardware ratesets, basic-rate lookup table.
- STF/STBC settings, 40 MHz MIMO capability, antenna gain, CW min/max.
- Embedded `ieee80211_supported_band` for mac80211 exposure.

`main.c` initializes one or two of these, one per supported band, and switches
`wlc->band` between them for channel operations.

### `struct modulecb`

Stores registered module down callbacks:

- Fixed-size name.
- Module handle.
- `down_fn` callback returning count of timers/callbacks still pending.

The array is bounded by `BRCMS_MAXMODULES`. `main.c` registers/unregisters
entries and invokes `down_fn` during `brcms_c_down`.

### `struct brcms_hw_band`

Represents hardware-facing per-band state:

- Band identity and PHY/radio metadata.
- MHF shadow array.
- Hardware STF single-stream mode.
- CW min/max.
- Core flags used for reset.
- PHY handle and encore flag.

This is separate from `struct brcms_band` because lower-level BMAC code keeps
hardware shadows and MHF values apart from common mac80211-facing state.

### `struct brcms_hardware`

The main BMAC/hardware state object. It contains:

- Backpointer to `brcms_c_info`.
- DMA handles per FIFO and TX availability pointers.
- Device identity, board/SROM flags, MAC capabilities.
- AI/SI, BCMA D11 core, PHY shim/shared PHY, active hardware band and band
  state array.
- Hardware retry limits, chanspec shadow, FIFO sizes, PLL requests.
- MAC control shadow state: suspended FIFOs, cached maccontrol,
  suspend depth, wake/mute overrides.
- Current MAC address, reset/clock flags, ucode-loaded flag.
- STF/antenna hardware mode and antenna selection availability.

Most low-level functions in `main.c` accept this struct when they directly
touch D11, PHY, DMA, clock, SHM, or template RAM.

### `struct brcms_c_info`

The primary common driver state object. It aggregates public state, mac80211
integration, active hardware, current band/core, queues, modules, BSS config,
timers, protection, STF, rates, channel, beacon/probe, and control flags.

Important fields include:

- `pub`, `wl`, `hw`: public, wrapper-private, and hardware state.
- Interrupt fields: `macintstatus`, `macintmask`, `defmacintmask`.
- Active and per-band/core state: `band`, `core`, `bandstate`, `corestate`.
- Module handles: AMPDU, antenna selection, channel manager.
- Device IDs, ucode revision, permanent MAC address.
- Band transition and lifecycle flags: `bandlocked`, `bandinit_pending`,
  `radio_monitor`, `going_down`, `beacon_template_virgin`, `clk`.
- Timers: watchdog and radio monitor.
- mac80211 filtering flags and power-save/beacon listen intervals.
- WME TXOP and retry arrays.
- BSS config, module callbacks, default BSS, protection, STF.
- Channel and PHY config: home/active chanspec, frag/RTS/retry thresholds,
  shortslot, PLCP header override.
- TX duty cycle, wiphy, primary SCB, VIF, cached beacon/probe SKBs, beacon TIM
  metadata.

The size and breadth of this struct reflects that `main.c` is the coordination
layer for the whole driver.

### `struct antsel_info`

Internal antenna-selection module state:

- Backpointers to `brcms_c_info` and `brcms_pub`.
- Antenna selection type and board switch type.
- Availability flag.
- 11n and current antenna configuration.

### `enum brcms_bss_type` And `struct brcms_bss_cfg`

The enum distinguishes station, AP, and adhoc operating modes.
`brcms_bss_cfg` stores:

- Backpointer to `wlc`.
- Interface type.
- SSID length and bytes.
- BSSID.
- Current BSS parameters pointer.

`main.c` currently uses a primary/default BSS config rather than a large
multi-BSS abstraction in this header.

## Function Prototype Groups

The prototypes expose the `main.c` services needed by sibling files:

TX and rate/duration:

- `brcms_c_txfifo`
- `brcms_c_calc_lsig_len`
- `brcms_c_rspec_to_rts_rspec`
- `brcms_c_compute_rtscts_dur`

Configuration and mac80211-facing common state:

- `brcms_c_set_gmode`
- `brcms_c_mac_promisc`
- `brcms_c_update_probe_resp`
- `brcms_c_set_nmode`
- `brcms_c_beacon_phytxctl_txant_upd`
- `brcms_c_inval_dma_pkts`
- `brcms_c_init_scb`

BMAC/hardware operations:

- `brcms_b_xmtfifo_sz_get`
- `brcms_b_antsel_type_set`
- `brcms_b_set_chanspec`
- `brcms_b_write_shm`
- `brcms_b_read_shm`
- `brcms_b_mhf`
- `brcms_b_corereset`
- `brcms_b_mctrl`
- `brcms_b_phy_reset`
- `brcms_b_bw_set`
- `brcms_b_core_phypll_reset`
- `brcms_c_ucode_wake_override_set`
- `brcms_c_ucode_wake_override_clear`
- `brcms_b_write_template_ram`
- `brcms_b_rate_shm_offset`
- `brcms_b_copyto_objmem`
- `brcms_b_copyfrom_objmem`
- `brcms_b_switch_macfreq`
- `brcms_b_get_txant`
- `brcms_b_phyclk_fgc`
- `brcms_b_macphyclk_set`
- `brcms_b_core_phypll_ctl`
- `brcms_b_txant_set`
- `brcms_b_band_stf_ss_set`

The prototypes expose low-level routines that rely on caller-held driver
state, clock state, and MAC suspend preconditions. The header does not encode
those preconditions in types.

## Control Flow Supported By The Header

The types and prototypes support these core flows:

- Attach: allocate `brcms_c_info` and substructures, initialize hardware state,
  bands, PHY, DMA, channel manager, modules, timers, and public state.
- Up/init: power and clock hardware, reset D11, download ucode, initialize
  core and band state, program SHM/tables/templates, enable MAC and interrupts.
- TX: use `brcms_stf`, `brcms_band`, `brcms_hardware`, and rate helpers to
  construct TX headers and enqueue to DMA FIFOs.
- RX: use D11 RX channel macros and active PHY/band state to build mac80211 RX
  status.
- Channel/band changes: switch active common and hardware band pointers, update
  PHY chanspec, ratesets, antenna selection, and ucode SHM.
- Down/detach: invoke module callbacks, stop timers, reset/disable hardware,
  detach PHY/DMA/submodules, and free allocated state.

## State And Persistence Behavior

All structures in `main.h` define in-memory driver state. Persistence across
hardware resets is manual: `main.c` repopulates D11 registers, SHM, SCR,
template RAM, rates, retry limits, beacon/probe templates, and PHY state from
these C structs during init/up paths.

The most important state split is:

- `brcms_c_info`: common/mac80211-facing state and high-level policy.
- `brcms_hardware`: hardware/BMAC state and D11 access shadows.
- `brcms_band`: common per-band rates/PHY/radio state.
- `brcms_hw_band`: hardware per-band MHF/PHY/radio/reset state.

Because these are shadows, stale fields can become bugs if a hardware reset,
band switch, or rfkill transition does not reapply them. The header makes
state directly mutable by many local files, so ownership is conventional rather
than enforced.

## Dependencies And Integration Points

The header depends on:

- Linux Ethernet helpers for `ETH_ALEN`.
- `brcmu_utils.h` for Broadcom utility types/macros.
- Local `types.h`, `d11.h`, and `scb.h`.
- Mac80211 and cfg80211 types indirectly through structures and prototypes in
  included local headers and declarations in `main.c`.

The structures integrate with:

- `main.c` for lifecycle, hardware programming, and packet flow.
- `stf.c` for transmit-chain and antenna policy.
- `ampdu.c` for aggregation state and TX status.
- `antsel.c` for antenna selection state.
- `channel.c` for regulatory/channel validation and TX power.
- `dma.c` for FIFO DMA handles and descriptor availability.
- `mac80211_if.c` for public mac80211-facing wrapper state.
- PHY HAL code for PHY/radio identity, calibration, RSSI, power, and clock
  state.

## Risks And Maintenance Notes

- The header exposes large internal structs, so modules can become tightly
  coupled to layout details and mutate state without central validation.
- Several fields are duplicated across common and hardware band structures.
  Band switching and attach/init must keep them coherent.
- `BRCMS_MAXMODULES` is fixed; `brcms_c_module_register` has no duplicate
  detection and can exhaust the table.
- `OTHERBANDUNIT` assumes two band units and should not be generalized without
  changing the macro and all users.
- Bitfield helpers require the `_M`/`_S` naming convention and do not mask
  shifted input beyond the provided mask in every possible misuse scenario.
- Wake override bits and MAC suspend depth are shared coordination state. A
  missing clear can hold the device awake; an extra clear can let ucode sleep
  during required register access.
- Interrupt masks in the header define the default event surface. Adding or
  removing bits changes DPC behavior in `main.c`.
- `TXOFF`, FIFO counts, and D11 header constants must remain aligned with
  actual hardware descriptor definitions.

## Test Signals

Header-level validation is mostly compile-time and integration-driven:

- Build coverage for all brcmsmac files including this header.
- Sparse/smatch/Coccinelle checks for struct-field misuse, invalid enum/int
  conversions, and direct mutation of shadow state.
- Compile-time checks for D11 core revision configuration through the existing
  `#error`.
- Runtime attach/up/down tests that exercise each major struct field cluster:
  band state, hardware clocks, module callbacks, WME arrays, BSS config,
  beacon/probe SKBs, and DMA `txavail` pointers.
- Multi-band tests to detect divergence between `brcms_band` and
  `brcms_hw_band`.
- Interrupt and wake-override tests to catch mismatched mask/depth updates.

## Research Notes

The header was read in full. Its key role is not algorithmic; it is the
driver's internal schema for all common and BMAC runtime state. Any change here
should be reviewed against `main.c` first, then against STF, AMPDU, antenna,
channel, DMA, PHY, and mac80211 wrapper code that relies on direct field
access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/main.h -->
