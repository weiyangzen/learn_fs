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

## Important APIs, Types, And Macros

General driver limits and protocol constants:

- `INVCHANNEL` marks an invalid channel.
- `BRCMS_MAXMODULES` limits registered module callbacks to 22.
- `SEQNUM_SHIFT` and `SEQNUM_MAX` describe 802.11 sequence number layout.
- `NTXRATE` sets the TX MPDU rate-report array size.
- `BRCMS_MAX_MAC_SUSPEND` is the maximum wait for MAC suspend.
- `BRCMS_PRB_RESP_TIMEOUT` configures probe-response timeout.
- `TXOFF` is the maximum TX headroom needed for D11 TX header plus PHY header.

Bitfield helpers:

- `BITFIELD_MASK(width)` builds masks.
- `GFIELD(val, field)` extracts named fields using `<field>_S` and
  `<field>_M`.
- `SFIELD(val, field, bits)` updates named bitfields.

Hardware and mode constants include `MAXCOREREV`, short-slot overrides,
preamble flags, TX frame ID masks, wake override bits, `I_ERRORS`,
`DEF_RXINTMASK`, `DEF_MACINTMASK`, frameburst/FIFO limits, PLL request bits,
`CHANNEL_BANDUNIT`, and `OTHERBANDUNIT`.

PHY capability helpers include `BRCMS_STF_SS_STBC_TX`, `BRCMS_STBC_CAP_PHY`,
`BRCMS_SGI_CAP_PHY`, `BRCMS_CHAN_PHYTYPE`, and `BRCMS_CHAN_CHANNEL`.

Core structs:

- `struct brcms_protection`: 11g/11n protection settings and overrides.
- `struct brcms_stf`: TX/RX chain, stream, antenna, STBC/LDPC, and spatial
  policy state.
- `struct brcms_core`: active MAC core index, DMA TX availability pointers,
  and MAC-stat snapshot.
- `struct brcms_band`: common per-band PHY/radio identity, ratesets,
  basic-rate table, STF/STBC, 40 MHz capability, antenna gain, contention
  windows, and `ieee80211_supported_band`.
- `struct modulecb`: registered module down-callback table entry.
- `struct brcms_hw_band`: hardware-facing per-band MHF, STF, CW, core flags,
  and PHY/radio state.
- `struct brcms_hardware`: BMAC hardware state including DMA engines, device
  metadata, BCMA/AI/PHY handles, active hardware band, FIFO sizing, PLL and
  clock flags, maccontrol shadow, wake/mute overrides, and antenna state.
- `struct brcms_c_info`: primary common driver state spanning public/mac80211
  state, hardware, active band/core, interrupts, modules, timers, WME, BSS,
  protection, STF, channel/rate config, TX duty cycle, wiphy/vif/SCB, and
  beacon/probe SKBs.
- `struct antsel_info`: antenna selection module state.
- `enum brcms_bss_type` and `struct brcms_bss_cfg`: station/AP/adhoc BSS
  configuration and current BSS state.

Prototype groups:

- TX and rate/duration: `brcms_c_txfifo`, `brcms_c_calc_lsig_len`,
  `brcms_c_rspec_to_rts_rspec`, `brcms_c_compute_rtscts_dur`.
- Configuration/common state: `brcms_c_set_gmode`, `brcms_c_mac_promisc`,
  `brcms_c_update_probe_resp`, `brcms_c_set_nmode`,
  `brcms_c_beacon_phytxctl_txant_upd`, `brcms_c_inval_dma_pkts`,
  `brcms_c_init_scb`.
- BMAC/hardware operations: `brcms_b_xmtfifo_sz_get`,
  `brcms_b_antsel_type_set`, `brcms_b_set_chanspec`,
  `brcms_b_write_shm`, `brcms_b_read_shm`, `brcms_b_mhf`,
  `brcms_b_corereset`, `brcms_b_mctrl`, `brcms_b_phy_reset`,
  `brcms_b_bw_set`, `brcms_b_core_phypll_reset`,
  `brcms_c_ucode_wake_override_set`,
  `brcms_c_ucode_wake_override_clear`,
  `brcms_b_write_template_ram`, `brcms_b_rate_shm_offset`,
  `brcms_b_copyto_objmem`, `brcms_b_copyfrom_objmem`,
  `brcms_b_switch_macfreq`, `brcms_b_get_txant`,
  `brcms_b_phyclk_fgc`, `brcms_b_macphyclk_set`,
  `brcms_b_core_phypll_ctl`, `brcms_b_txant_set`,
  `brcms_b_band_stf_ss_set`.

## Control Flow

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

The header depends on Linux Ethernet helpers, `brcmu_utils.h`, and local
`types.h`, `d11.h`, and `scb.h`. It integrates with `main.c`, `stf.c`,
`ampdu.c`, `antsel.c`, `channel.c`, `dma.c`, `mac80211_if.c`, PHY HAL code,
and rate code.

The structures are central to module boundaries: PHY and DMA state is stored
inside `brcms_hardware`; rate and band state is stored in `brcms_band`; module
callbacks are registered through `modulecb`; AP/STA/adhoc state is held in
`brcms_bss_cfg`; and TX stream decisions are routed through `brcms_stf`.

## Risks

- The header exposes large internal structs, so modules can mutate state
  without central validation.
- Several fields are duplicated across common and hardware band structures.
  Band switching and attach/init must keep them coherent.
- `BRCMS_MAXMODULES` is fixed; callback registration has no duplicate
  detection and can exhaust the table.
- `OTHERBANDUNIT` assumes two band units and should not be generalized without
  changing the macro and all users.
- Bitfield helpers rely on the `_M`/`_S` naming convention.
- Wake override bits and MAC suspend depth are shared coordination state; a
  missing clear can hold the device awake, while an extra clear can let ucode
  sleep during required register access.
- Interrupt masks in the header define the default DPC event surface.
- `TXOFF`, FIFO counts, and D11 header constants must remain aligned with
  actual hardware descriptor definitions.

## Test Signals

Header-level validation is mostly compile-time and integration-driven:

- Build coverage for all brcmsmac files including this header.
- Static analysis for struct-field misuse, invalid enum/int conversions, and
  direct mutation of shadow state.
- Compile-time checks for D11 core revision configuration through the existing
  `#error`.
- Runtime attach/up/down tests that exercise band state, hardware clocks,
  module callbacks, WME arrays, BSS config, beacon/probe SKBs, and DMA
  `txavail` pointers.
- Multi-band tests to detect divergence between `brcms_band` and
  `brcms_hw_band`.
- Interrupt and wake-override tests to catch mismatched mask/depth updates.

## Research Notes

The header was read in full. Its key role is not algorithmic; it is the
driver's internal schema for all common and BMAC runtime state. Any change here
should be reviewed against `main.c` first, then against STF, AMPDU, antenna,
channel, DMA, PHY, and mac80211 wrapper code that relies on direct field
access.
