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

## Important APIs And Functions

The file exposes the common driver operations used by the mac80211 interface
layer and sibling modules:

- Lifecycle: `brcms_c_attach`, `brcms_c_detach`, `brcms_c_up`,
  `brcms_c_down`, `brcms_c_init`, `brcms_c_reset`, `brcms_c_pub`.
- Interrupt and DPC: `brcms_c_isr`, `brcms_c_intrsupd`, `brcms_c_dpc`,
  `brcms_c_intrson`, `brcms_c_intrsoff`, `brcms_c_intrsrestore`.
- TX path: `brcms_c_sendpkt_mac80211`, `brcms_c_txfifo`,
  `brcms_c_tx_flush_completed`, `brcms_c_inval_dma_pkts`,
  `brcms_c_get_header_len`.
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

## Control Flow

Attach starts in `brcms_c_attach`. It allocates `brcms_c_info` and subobjects,
initializes defaults, then calls `brcms_b_attach` for hardware discovery.
`brcms_b_attach` attaches AI/SI state, validates device/core/board/PHY support,
forces clocks and resets, attaches PHY and DMA for each band, records SPROM
metadata, then leaves the hardware in the down state. `brcms_c_attach` finishes
common setup by initializing STF, ratesets, modules, timers, the channel
manager, default BSS state, MIMO bandwidth capability, SGI, and antenna state.

Bring-up is staged through `brcms_c_up`. It powers hardware if needed, applies
board-specific host flags, checks hardware radio disable, starts radio
monitoring if rfkill is active, otherwise prepares BMAC, calls the outer
`brcms_init`, handles pending channel/band changes, enables interrupts, writes
WME retry state, arms watchdog, and synchronizes antenna/LDPC settings.

Full hardware initialization occurs in `brcms_c_init` and `brcms_b_init`.
These select channel/band, reset and initialize the D11 core, download ucode,
write ucode init tables, program FIFO sizes, initialize PHY and DMA, write
shared-memory rate/probe/beacon/duty-cycle/AMPDU state, set MAC/BSSID, enable
EDCF, read ucode version, and finally enable the MAC.

Shutdown starts in `brcms_c_down`. It disables interrupts and PHY, calls module
down callbacks, stops watchdog, marks public state down, unmutes PHY, resets or
disables D11, powers down PCI/xtal when possible, and clears clock state.
Detach then tears down DMA, PHY, shared PHY, AI/SI, timers, modules, channel
manager, and memory.

Interrupt flow starts in `brcms_c_isr` or `brcms_c_intrsupd`, both built around
`wlc_intstatus`. The ISR masks, disables, and clears hardware interrupt bits
and stores them in `wlc->macintstatus`. `brcms_c_dpc` consumes those bits and
dispatches TX status, RX DMA, TBTT/ATIM, noise, PSM watchdog, timer, rfkill,
and beacon-template events. Bounded TX/RX processing requeues status bits for
later DPC scheduling.

TX flow is mac80211 SKB to D11 DMA. `brcms_c_sendpkt_mac80211` maps AC to FIFO,
`brcms_c_d11hdrs_mac80211` pushes PLCP and D11 headers and fills rate,
duration, protection, antenna, bandwidth, RTS/CTS, and TXOP metadata,
`brcms_c_tx` commits BCMC frame IDs if needed, and `brcms_c_txfifo` enqueues
through DMA and stops mac80211 queues when descriptors are low. TX completion
reads D11 status registers in `brcms_b_txstatus`, converts status in
`brcms_c_dotxstatus`, reports to AMPDU or mac80211, frees fatal packets, wakes
queues when descriptors recover, and kicks DMA.

RX flow starts in `brcms_b_recv` from the DPC DMA interrupt path. It drains DMA
frames into a temporary queue, refills RX buffers, endian-fixes each D11 RX
header, and calls `brcms_c_recv`. `brcms_c_recv` strips hardware offset and pad,
filters bad frames, drops A-MSDU, and calls `brcms_c_recvctl`, which prepares
mac80211 RX status, strips PLCP/FCS, unmutes after beacon if needed, and calls
`ieee80211_rx_irqsafe`.

## State And Persistence Behavior

Most state is volatile runtime state, not filesystem persistence. Durable input
comes from SPROM, device IDs, firmware/ucode tables, and mac80211
configuration. Hardware persistence is through D11 registers, SHM, SCR, object
memory, template RAM, DMA rings, and PHY state. These are reprogrammed on
reset/up/init from software shadows.

Important state clusters:

- `wlc->pub`: public up/hw_up/hw_off/radio/association/device state.
- `wlc->hw`: BMAC state including DMA handles, board flags, active hardware
  band, FIFO sizes, maccontrol shadow, wake/mute overrides, clocks, PLL
  requests, and ucode-loaded flag.
- `wlc`: common state including active band/core, interrupt status/masks,
  module handles, timers, WME arrays, BSS config, protection, STF, rates,
  channel, shortslot, beacon/probe SKBs, and primary SCB.
- Per-band structures: PHY/radio identity, ratesets, basic-rate table, 40 MHz
  capability, antenna gain, CW min/max, and MHF shadows.

The file uses software shadows heavily. For example, `brcms_b_mctrl` updates a
cached `maccontrol`; wake and mute overrides are composed during writes; MHF
state is cached per band and written to SHM only when the affected band is
active and clocked. This makes down/up and band-switch reprogramming critical.

## Dependencies And Integration Points

External kernel dependencies include PCI IDs, Ethernet helpers, cfg80211,
mac80211, SKBs, endian helpers, timers, and queue/status APIs. Broadcom
dependencies include BCMA register access, AI/SI helpers, chipcommon, SPROM,
chip IDs, D11 register definitions, SHM offsets, host flags, TX/RX header
formats, and ucode constants.

Local driver integration points include `rate.h`, `scb.h`, `phy/phy_hal.h`,
`channel.h`, `antsel.h`, `stf.h`, `ampdu.h`, `mac80211_if.h`,
`ucode_loader.h`, `soc.h`, `dma.h`, `debug.h`, and trace events. The file is a
consumer and coordinator of these modules: PHY provides calibration/RSSI/power,
DMA provides rings and packet ownership, AMPDU consumes aggregation TX status,
STF/antsel provide antenna and stream policy, and channel manager validates
chanspec/TX power.

## Risks

- Clock/reset/MAC suspend sequencing is order-sensitive. Register access with
  `clk` false or while PSM is running can hang or corrupt hardware state.
- `brcms_c_d11hdrs_mac80211` is high-risk because it combines rate control,
  protection, PLCP, duration, antenna, bandwidth, frame ID, and TXOP behavior
  in one long function.
- Several helpers silently return on invalid masks, invalid object-memory
  offset/length, or invalid field values, which can hide caller bugs.
- Device removal and suspend/resume are sensitive because many paths directly
  read/write D11 registers after checking cached state.
- Bounded DPC relies on the caller rescheduling when `brcms_c_dpc` returns
  true.
- TX queue flow control assumes the AC/FIFO mapping is consistent and that
  `TX_HEADROOM` absorbs small queue-stop races.
- RX A-MSDU is unsupported and dropped in this path.
- Beacon template updates rely on dual-template validity and `MI_BCNTPL`
  interrupt mask behavior.
- Multi-band logic assumes at most two band units and band0 as 2.4 GHz.
- Firmware/init-table selection is tightly coupled to core revision and PHY
  type.
- Template RAM writes depend on caller-rounded lengths and manual endian
  handling.

## Test Signals

Useful validation signals include supported and unsupported attach probes,
up/down and rfkill cycles, suspend/resume, TX on each AC queue, queue
stop/wake, AMPDU and non-AMPDU TX status, RX metadata for CCK/OFDM/MCS frames,
bad FCS filtering, A-MSDU drop behavior, channel switching across bands and
bandwidths, beacon/probe template rollover, WME changes, watchdog/fatal error
injection, and static analysis for duration arithmetic, buffer rounding,
sequence/frame ID construction, and SHM/object memory offsets.

## Research Notes

The file was read in full. Function indexing was used to verify coverage of
the attach, lifecycle, interrupt, TX, RX, beacon/probe, rate, SHM, and hardware
helper regions. The key architectural observation is that this file is both
the common driver state manager and the BMAC hardware sequencer; correctness
depends on preserving preconditions across clock state, MAC suspend state, DMA
ownership, and mac80211 callbacks.
