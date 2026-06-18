# subset-b-004786 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_n.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_n.h

## Purpose
`phy_n.h` is the N-PHY hardware contract for the B43 Broadcom wireless driver. It defines the register offsets and bit masks used by `phy_n.c` to initialize, tune, calibrate, and operate 802.11n PHY hardware, and it declares the N-PHY private state carried in `struct b43_phy_n`. It also publishes the N-PHY operation table symbol `b43_phyops_n` for the broader driver PHY dispatch layer.

## Important APIs, Types, And Definitions
- Register map: `B43_NPHY_*` constants cover baseband config, channel selection, band control, RF control sequences, RSSI/TSSI, IQ estimation, TX power control, radar detection, classifier, BPHY compatibility, GPIO, revision-3-plus, and revision-7 RF-control registers. Most constants wrap `B43_PHY_N()` or `B43_PHY_N_BMODE()` from `phy_common.h`.
- Bit fields: many registers include masks and shift constants such as `B43_NPHY_RFCTL_CMD_*`, `B43_NPHY_TXPCTL_CMD_*`, `B43_NPHY_TXPCTL_*`, `B43_NPHY_IQEST_*`, `B43_NPHY_CLASSCTL_*`, and gain/min/max masks for both cores.
- `enum b43_nphy_spur_avoid`: declares disable, automatic, and forced spur-avoidance policies.
- `struct b43_chanspec`: stores a center frequency and `enum nl80211_channel_type` width/sideband type. N-PHY caches use this to determine whether calibration data matches the current channel.
- `struct b43_phy_n_iq_comp`, `struct b43_phy_n_rssical_cache`, and `struct b43_phy_n_cal_cache`: hold cached IQ, RSSI, TX-calibration radio registers, and PHY coefficients for 2.4 GHz and 5 GHz bands.
- `struct b43_phy_n_txpwrindex`: tracks per-core TX power index state plus saved AFE, radio gain, BB multiplier, IQ, LO compensation, and internal index values.
- `struct b43_phy_n_pwr_ctl_info`: records idle TSSI per band.
- `struct b43_phy_n`: the central N-PHY state block embedded under `dev->phy.n`. It persists calibration flags and caches, TX/RX chain state, TX power state, spur workarounds, classifier/clip saved state, IQ/RSSI channel specs, cached PPR limits, and board/radio capability booleans.
- External symbol: `extern const struct b43_phy_operations b43_phyops_n;` integrates the N-PHY implementation into the generic PHY operation dispatcher.

## Control Flow And State
This header has no executable control flow, but it shapes nearly every N-PHY control path. `phy_n.c` reads and writes the register constants during PHY init, channel switching, RSSI/IQ/TX calibration, TX power recalculation, radio setup, and workaround paths. State in `struct b43_phy_n` persists across those calls while the wireless device object is alive. Examples include:
- Calibration persistence: `cal_cache`, `rssical_cache`, `iqcal_chanspec_*`, and `rssical_chanspec_*` allow calibration results to be reused per band/channel instead of recomputed blindly.
- TX power persistence: `tx_pwr_max_ppr`, `tx_pwr_last_recalc_freq`, `tx_pwr_last_recalc_limit`, `tx_pwr_idx`, `tx_power_offset`, `adj_pwr_tbl`, `txpwrindex[]`, `txcal_bbmult`, and `txiqlocal_*` track limits, offsets, coefficients, and last recalculation conditions.
- PHY/radio chain state: `phyrxchain`, `hw_phyrxchain`, `hw_phytxchain`, `txrx_chain`, saved TX/RX calibration registers, and RF-control save registers are used when entering and leaving calibration or special operating modes.
- Workaround and mode flags: `hang_avoid`, `mute`, `spur_avoid`, `aband_spurwar_en`, `gband_spurwar_en`, `ipa2g_on`, `ipa5g_on`, `crsminpwr_adjusted`, and `noisevars_adjusted` drive hardware-specific branches.

## Dependencies And Integration Points
- Depends on `phy_common.h` for PHY register-address macros and on `ppr.h` for `struct b43_ppr`.
- Depends indirectly on mac80211 channel typing through `enum nl80211_channel_type`.
- Consumed heavily by `phy_n.c`, which uses `B43_NPHY_*` constants for register programming and embeds `struct b43_phy_n` as the N-PHY private data contract.
- Shares radio integration with `radio_2055.h`, `radio_2056.h`, and N-PHY table helpers. The channel/radio register constants in this header must line up with the radio tables and `phy_n.c` sequencing.
- `tx_pwr_max_ppr` connects this header to `ppr.c`/`ppr.h`; `phy_n.c` clears, loads, clamps, and adjusts that per-rate power table during TX power limit recalculation.

## Risks
- Register-map drift is the main risk. A wrong offset, mask, or shift can silently misprogram RF, power, radar, gain, or calibration hardware.
- Revision-specific aliases are easy to misuse. Several register addresses are reused with `REV3` and `REV7` names, so callers must gate them correctly by PHY/core revision.
- `struct b43_phy_n` is large and stateful. Missing reset, stale calibration channel specs, or incorrect save/restore of register snapshots can cause failures that only appear after band changes, suspend/resume, or calibration retries.
- Power-control fields are safety-sensitive because they feed hardware TX power decisions. Incorrect PPR, TSSI, base-index, or offset state can violate regulatory or board limits.
- This header does not enforce locking. Callers must preserve existing driver synchronization around hardware state mutation.

## Test Signals
- Build-time signals: all users should compile with no undefined register/type references after changes; `ppr.c` also has a `BUILD_BUG_ON` that protects the `struct b43_ppr` layout used here.
- Runtime signals: successful N-PHY device probe, channel changes across 2.4 GHz and 5 GHz, calibration completion, stable TX power recalculation, no PHY/RF warnings, and no regressions in mac80211 association/traffic.
- Hardware-focused tests should exercise PHY revisions that use rev3 and rev7 aliases, both chains, 20/40 MHz channel types, spur-avoidance toggles, and suspend/resume or radio reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_n.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.c

## Purpose
`pio.c` implements Programmed I/O data transfer support for the B43 driver. It is the non-DMA transmit and receive path used when PIO is forced or DMA is unavailable/fails. It allocates PIO queues, maps mac80211 traffic priorities to hardware queues, writes TX headers and frames into PIO FIFOs, receives frames from the direct FIFO RX path, handles TX status cookies, applies queue backpressure, and suspends/resumes TX queues around power-management events.

## Important APIs And Functions
- `b43_pio_init(struct b43_wldev *dev)`: disables big-endian MAC mode, clears the shared RX padding offset, allocates four QoS TX queues plus multicast and one RX queue, and enables direct FIFO RX through the DMA helper.
- `b43_pio_free(struct b43_wldev *dev)`: frees allocated PIO queues when PIO is active and drops any queued SKBs through `ieee80211_free_txskb()`.
- `b43_pio_tx(struct b43_wldev *dev, struct sk_buff *skb)`: public TX entry. Selects the target queue, validates queue capacity, applies mac80211 queue stop on overflow, generates a TX header, writes data to hardware, and handles `-ENOKEY` by dropping the frame without unencrypted transmission.
- `b43_pio_handle_txstatus(struct b43_wldev *dev, const struct b43_txstatus *status)`: maps firmware TX status cookies back to a PIO queue/packet slot, fills mac80211 status, accounts buffer usage and packet slots, returns the slot to the free list, and wakes a previously stopped queue.
- `b43_pio_rx(struct b43_pio_rxqueue *q)`: drains available RX frames until the hardware has no ready frame or a safety cap trips.
- `b43_pio_tx_suspend()` / `b43_pio_tx_resume()`: set and clear PIO TX suspend request bits on all queues, wrapped with power-saving control.
- Internal helpers: `generate_cookie()`, `parse_cookie()`, `index_to_pioqueue_base()`, setup/destroy helpers, `select_queue_by_priority()`, 2-byte and 4-byte queue writers, `pio_tx_frame()`, `pio_rx_frame()`, and per-queue suspend/resume helpers.

## Control Flow
Initialization starts in `b43_pio_init()`. It programs MAC/shared-memory PIO settings, creates TX queues for AC_BK, AC_BE, AC_VI, AC_VO, and multicast, then creates RX queue 0 and enables direct FIFO RX. Error handling unwinds already-created queues in reverse order.

TX flow begins at `b43_pio_tx()`. Multicast frames marked `IEEE80211_TX_CTL_SEND_AFTER_DTIM` are routed to the multicast queue and get `IEEE80211_FCTL_MOREDATA`; other frames use QoS priority mapping when QoS is enabled or AC_BE otherwise. The function checks total rounded header plus frame size against `q->buffer_size`, checks packet slots, may stop the corresponding mac80211 queue with `b43_stop_queue()`, and calls `pio_tx_frame()`. `pio_tx_frame()` chooses the first free metadata slot, generates a nonzero cookie with queue ID in the high nibble and packet index in the low 12 bits, builds the B43 TX header in `wl->pio_scratchspace`, stores multicast cookie state in shared memory when needed, writes the header and SKB payload to the PIO FIFO, removes the slot from the free list, and updates buffer accounting.

Hardware write width depends on core revision. Revisions before 8 use 16-bit PIO TXCTL/TXDATA and mask high/low byte lanes for odd tails. Revisions 8 and newer use 32-bit TXCTL/TXDATA and byte-lane masks for 1-3 byte tails. Both paths set frame-ready, stream header then payload, and finish by setting EOF.

TX completion enters through `b43_pio_handle_txstatus()`, normally dispatched from `xmit.c` when PIO is active. The cookie is parsed back to a queue and packet slot. The SKB status is filled, buffer usage and free slots are restored, `ieee80211_tx_status_skb()` returns the SKB to mac80211, and a stopped queue is woken.

RX flow is interrupt-driven through `b43_pio_rx(dev->pio.rx_queue)` in `main.c` when PIO transfers are active. `pio_rx_frame()` checks FRAMERDY, acknowledges it, waits briefly for DATARDY, reads the firmware RX header into `wl->pio_scratchspace`, validates length and FCS policy, allocates an SKB with expected two-byte alignment padding plus optional hardware padding, reads the payload with 16-bit or 32-bit block I/O and tail handling, and hands the frame to `b43_rx()`. Errors acknowledge DATARDY to discard the frame and continue draining.

## State And Persistence
- Queue objects persist in `dev->pio` and hold `mmio_base`, `buffer_size`, `buffer_used`, `free_packet_slots`, `stopped`, `queue_prio`, revision shortcut, fixed packet metadata array, and free-list head.
- Packet slots persist until TX status arrives. Each active `struct b43_pio_txpacket` owns the SKB pointer and index that the firmware cookie later resolves.
- Queue backpressure state persists through `q->stopped`; status completion wakes the last stored `queue_prio`.
- `wl->pio_scratchspace` and `wl->pio_tailspace` are shared PIO staging buffers protected by the broader `wl->mutex` contract described in `b43.h`.
- Multicast DTIM state persists via `B43_SHM_SH_MCASTCOOKIE`, allowing firmware to clear the more-data bit on the last multicast frame.
- RX does not persist SKBs internally; successful frames are immediately passed to the normal B43 RX path.

## Dependencies And Integration Points
- Uses hardware accessors from `b43.h`: MMIO reads/writes, shared memory writes, block I/O, MAC control, PIO base constants, and `b43_using_pio_transfers()`.
- Uses DMA helper `b43_dma_direct_fifo_rx()` to enable direct FIFO RX even though normal DMA structures are not used.
- Uses TX/RX framing helpers from `xmit.h` and main driver paths: `b43_txhdr_size()`, `b43_generate_txhdr()`, `b43_fill_txstatus_report()`, and `b43_rx()`.
- Integrates with mac80211 through SKBs, `IEEE80211_SKB_CB`, queue mappings, TX control flags, `ieee80211_tx_status_skb()`, and `ieee80211_free_txskb()`.
- Called from `main.c` for device init/free, RX draining, and TX path selection; `xmit.c` forwards TX status and suspend/resume events when PIO is active.

## Risks
- The rev >= 8 TX path ends `pio_tx_frame_4byte_queue()` with `b43_piotx_write32(q, B43_PIO_TXCTL, ctl)` instead of the rev8 symbolic offset `B43_PIO8_TXCTL`. Both are currently zero, but the mixed symbolic name is fragile and can mislead future edits.
- `q->buffer_size = 1920` for rev >= 8 is explicitly marked `FIXME this constant is wrong`; wrong sizing can cause false backpressure or hardware FIFO overflow.
- Cookie parsing assumes queue index plus one maps exactly to 0x1000..0x5000 and that the packet index remains below 32. Corruption or firmware bugs can drop statuses and leak queue accounting.
- TX status handling dereferences `pack->skb` without a null guard after cookie parsing. Duplicate or stale statuses would risk a null dereference or bad accounting.
- RX length validation only rejects `len > 0x700` and zero; malformed headers that pass those checks rely on downstream parsing.
- Queue stopping stores a single `queue_prio` per PIO queue. If mappings or QoS behavior change, waking the wrong mac80211 queue is possible.
- PIO uses shared scratch and tail buffers; callers must maintain serialization.

## Test Signals
- Build with PIO enabled (`B43_PIO` / `B43_BCMA_PIO`) and with DMA enabled to catch integration drift.
- Runtime smoke tests should include forced PIO via module parameter, DMA-fallback-to-PIO paths, association, ping/throughput, multicast buffered traffic after DTIM, and traffic across all QoS access categories.
- Fault-oriented signals: `PIO: TX packet longer than queue`, `PIO: TX packet overflow`, `PIO transmission failure`, `PIO RX timed out`, and `PIO RX error` logs.
- Stress tests should watch for queue stop/wake balance, no SKB leaks on init failure/free, no underflow in `buffer_used`, and no RX drain loops hitting the `count > 10000` warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.h

## Purpose
`pio.h` declares the B43 PIO register interface, queue data structures, MMIO helper accessors, and public PIO lifecycle/TX/RX entry points. It is the shared contract between `pio.c` and the broader B43 driver for programmed I/O transfers.

## Important APIs, Types, And Definitions
- Pre-revision-8 register offsets and bits: `B43_PIO_TXCTL`, `B43_PIO_TXDATA`, `B43_PIO_TXQBUFSIZE`, `B43_PIO_RXCTL`, and `B43_PIO_RXDATA`, with TX byte-lane, EOF, frame-ready, flush, suspend, queue-suspend, and command-count masks.
- Revision-8-plus register offsets and bits: `B43_PIO8_TXCTL`, `B43_PIO8_TXDATA`, `B43_PIO8_RXCTL`, and `B43_PIO8_RXDATA`, with 32-bit byte-lane masks and EOF/FREADY/SUSPREQ/QSUSP/FLUSH bits.
- `B43_PIO_MAX_NR_TXPACKETS`: fixed metadata slot count of 32 per TX queue.
- `struct b43_pio_txpacket`: per in-flight TX frame metadata: owning queue, SKB pointer, fixed index, and list node.
- `struct b43_pio_txqueue`: per hardware TX queue state: device pointer, MMIO base, hardware buffer size and used count, available packet slots, stopped flag, queue index, mac80211 priority, slot array, free list, and core revision shortcut.
- `struct b43_pio_rxqueue`: RX queue state with device pointer, MMIO base, and core revision shortcut.
- Inline accessors: `b43_piotx_read16/32()`, `b43_piotx_write16/32()`, `b43_piorx_read16/32()`, and `b43_piorx_write16/32()` add queue-local MMIO offsets to `q->mmio_base`.
- Public functions: `b43_pio_init()`, `b43_pio_free()`, `b43_pio_tx()`, `b43_pio_handle_txstatus()`, `b43_pio_rx()`, `b43_pio_tx_suspend()`, and `b43_pio_tx_resume()`.

## Control Flow And State
This header has no executable high-level control flow beyond inline MMIO wrappers. It defines the mutable state that `pio.c` uses for PIO queue lifecycles:
- TX queue metadata slots transition from the free list to active ownership when a frame is written, then return to the list on TX status.
- `buffer_used` and `free_packet_slots` provide software-side queue capacity accounting before writing to hardware.
- `stopped` and `queue_prio` persist software backpressure state between `b43_stop_queue()` and completion-time `b43_wake_queue()`.
- Revision-specific register layouts are selected by `q->rev` in implementation code, while this header exposes both layouts.

## Dependencies And Integration Points
- Includes `b43.h` for `struct b43_wldev` and MMIO accessors, plus Linux interrupt, I/O, list, and SKB types.
- `struct b43_pio` in `b43.h` stores pointers to the queue types declared here.
- Public functions are called by `main.c` and `xmit.c`; hardware access helpers are used only by the PIO implementation.
- Register base constants live in `b43.h`, while this file defines offsets relative to each queue base.

## Risks
- The data structures assume single-owner serialized access. Parallel TX/RX/status changes without the driver mutex or proper interrupt serialization would corrupt lists and counters.
- `buffer_size` and `buffer_used` are `u16`; any future hardware with larger PIO FIFOs would require widening or careful bounds checks.
- The fixed 32-slot queue contract is encoded into cookies in `pio.c`; increasing `B43_PIO_MAX_NR_TXPACKETS` beyond the low 12-bit cookie space would require cookie changes.
- Revision-specific offsets are easy to mix because both rev7 and rev8 TXCTL/RXCTL offsets are zero but data offsets differ.

## Test Signals
- Compile coverage should include PIO-capable configurations and catch mismatched prototypes or missing struct members.
- Runtime signals come from the `pio.c` paths: successful forced-PIO init/free, TX status completion returning slots to the list, RX frame delivery, and suspend/resume queue control.
- Static review after changes should check that every new register bit is used under the correct hardware revision gate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/pio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.c

## Purpose
`ppr.c` implements Power Per Rate helper operations for the B43 driver. It manages `struct b43_ppr`, a compact table of qdbm power limits for CCK, OFDM, and 802.11n MCS rate groups, and populates those limits from SPROM board data. N-PHY TX power code uses this table to enforce per-rate maximums and adjust them for hardware gain.

## Important APIs And Functions
- `b43_ppr_clear(struct b43_wldev *dev, struct b43_ppr *ppr)`: zeroes the full table and asserts at build time that the union has no padding beyond the rate bytes.
- `b43_ppr_add(struct b43_wldev *dev, struct b43_ppr *ppr, int diff)`: adds a signed delta to every rate and clamps each result to `[0, 127]`.
- `b43_ppr_apply_max(struct b43_wldev *dev, struct b43_ppr *ppr, u8 max)`: caps all rate powers at a maximum.
- `b43_ppr_apply_min(struct b43_wldev *dev, struct b43_ppr *ppr, u8 min)`: raises all rate powers below a minimum.
- `b43_ppr_get_max(struct b43_wldev *dev, struct b43_ppr *ppr)`: returns the maximum power value among all stored rates.
- `b43_ppr_load_max_from_sprom(struct b43_wldev *dev, struct b43_ppr *ppr, enum b43_band band)`: selects band-specific SPROM maximum power and offsets, fills CCK/OFDM/MCS entries, and applies extra CDD/STBC offsets for N-PHY rev >= 3.

## Control Flow
Most helper operations iterate over every byte in `ppr->__all_rates` using the local `ppr_for_each_entry()` macro. That intentionally treats the structured view and flat view as the same storage.

`b43_ppr_load_max_from_sprom()` first selects source data by `enum b43_band`. For 2.4 GHz it uses the minimum of the two cores' `maxpwr_2g`, `ofdm2gpo`, `mcs2gpo`, and the low nibbles of `cddpo`/`stbcpo`; for low, middle, and high 5 GHz it selects the matching max power and OFDM/MCS offset arrays and corresponding extra-offset nibbles. Invalid bands warn once and return false.

After band selection, CCK entries are filled only for 2.4 GHz from `cck2gpo`. OFDM entries are filled from the selected 32-bit OFDM power-offset word. MCS 20 SISO entries are derived from OFDM entries. MCS 20 CDD and STBC entries are filled from the first two MCS offset words and optionally reduced by extra CDD/STBC offsets for N-PHY rev >= 3. OFDM 20 CDD entries mirror selected MCS CDD entries. MCS 20 SDM entries come from the third and fourth MCS offset words.

## State And Persistence
`ppr.c` mutates only caller-owned `struct b43_ppr` memory. It has no static mutable state. In this subset the main persistent owner is `struct b43_phy_n::tx_pwr_max_ppr`; `phy_n.c` clears it, loads SPROM limits, clamps it to regulatory/current limits, subtracts hardware gain, applies a floor, and reads the maximum for hardware programming and debug output.

All stored values are `u8` qdbm values. Offsets from SPROM are 4-bit nibbles multiplied by two, then subtracted from the selected maximum power. Helper add/clamp routines keep values in the range accepted by the table representation.

## Dependencies And Integration Points
- Includes `ppr.h` for structure layout and exported prototypes and `b43.h` for `struct b43_wldev`, `struct b43_phy`, band constants, warning macros, and SPROM access.
- Reads `dev->dev->bus_sprom`, especially `core_pwr_info[]`, CCK/OFDM/MCS power-offset fields, and CDD/STBC offsets.
- Reads `dev->phy.type` and `dev->phy.rev` to apply N-PHY-revision-specific CDD/STBC reductions.
- Used by `phy_n.c` during TX power limit recalculation through `b43_ppr_clear()`, `b43_ppr_load_max_from_sprom()`, `b43_ppr_apply_max()`, `b43_ppr_get_max()`, `b43_ppr_add()`, and `b43_ppr_apply_min()`.

## Risks
- Subtracting offsets from `u8 maxpwr` can underflow before assignment if SPROM data is malformed or max power is smaller than offset. The current code relies on sane SPROM data and later clamping helpers, but load itself does not clamp.
- The function assumes both `core_pwr_info[0]` and `[1]` are valid and uses the lower max power. Single-chain or incomplete SPROM cases need upstream guarantees.
- Extra CDD/STBC offsets are subtracted after max-minus-offset and are not clamped in the load function.
- Only 20 MHz MCS groups represented in `struct b43_ppr` are filled here. If future code expects 40 MHz or newer rate groups, the layout and loader need extension.
- The `dev` argument is unused by simple helpers except for type consistency. That is harmless but can hide future assumptions if helper behavior becomes device-specific.

## Test Signals
- Build-time `BUILD_BUG_ON(sizeof(struct b43_ppr) != B43_PPR_RATES_NUM * sizeof(u8))` catches padding/layout regressions.
- Unit-style tests can validate clear/add/min/max/get-max on synthetic tables, including negative deltas and clamp boundaries 0 and 127.
- SPROM fixture tests should cover 2.4 GHz, all three 5 GHz bands, N-PHY rev < 3 and >= 3, and invalid band handling.
- Runtime signals are correct N-PHY TX power debug output, sane per-rate limits after channel changes, and absence of regulatory/power anomalies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.h

## Purpose
`ppr.h` defines the B43 Power Per Rate data layout and helper API. It gives PHY code a compact, byte-addressable qdbm table for per-rate power limits and a structured view grouped by CCK, OFDM, and N-PHY MCS rate families.

## Important APIs, Types, And Definitions
- Rate counts: `B43_PPR_CCK_RATES_NUM` is 4, `B43_PPR_OFDM_RATES_NUM` is 8, `B43_PPR_MCS_RATES_NUM` is 8, and `B43_PPR_RATES_NUM` totals CCK plus two OFDM groups plus four MCS groups.
- `struct b43_ppr_rates`: named arrays for `cck`, `ofdm`, `ofdm_20_cdd`, `mcs_20` (SISO), `mcs_20_cdd`, `mcs_20_stbc`, and `mcs_20_sdm`.
- `struct b43_ppr`: a union exposing the same bytes as `__all_rates[]` for generic iteration and `rates` for semantic access. Values are qdbm Q5.2.
- Forward declarations: `struct b43_wldev` and `enum b43_band` avoid pulling in the full driver header.
- Public helpers: clear, add signed delta, apply max cap, apply min floor, get maximum, and load maximums from SPROM for a selected band.

## Control Flow And State
This header defines storage only. State is caller-owned and normally embedded in PHY state, especially `struct b43_phy_n::tx_pwr_max_ppr`. The union makes it possible for implementation code to iterate over all rate bytes while callers can address specific rate groups by name. There is no allocation or persistence policy in the header itself.

## Dependencies And Integration Points
- Includes only `<linux/types.h>`, keeping it lightweight for inclusion by `phy_n.h` and `ppr.c`.
- `ppr.c` implements the declared helpers and depends on the exact no-padding layout.
- N-PHY code consumes `struct b43_ppr` to carry SPROM-derived and regulatory-clamped TX power limits.
- SPROM band loading uses `enum b43_band`, so any band enum changes in `b43.h` must remain compatible with the loader.

## Risks
- The union layout depends on `struct b43_ppr_rates` being exactly the same size as `__all_rates[]`. `ppr.c` has a build assertion, but any new fields require updating `B43_PPR_RATES_NUM`.
- The layout represents only the current groups. Adding 40 MHz, VHT, or other rate families requires a deliberate ABI/layout update across all iterators.
- All values are `u8` qdbm; callers must handle signed arithmetic and underflow/overflow through the helper functions or explicit clamps.

## Test Signals
- Compile with `ppr.c` to preserve the size assertion.
- Exercise helper functions through N-PHY TX power recalculation and confirm named groups match flat iteration order.
- Static review should verify any new rate group is added to both the structured layout and `B43_PPR_RATES_NUM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.c

## Purpose
`radio_2055.c` provides BCM2055 radio data tables and two helper functions for N-PHY hardware. It contains a band-dependent default radio initialization table and a channel switch table for N-PHY revision-2 style channel programming. The executable logic uploads selected radio defaults and performs channel-to-table-entry lookup; the rest of the file is static hardware calibration/programming data.

## Important APIs, Types, And Data
- `struct b2055_inittab_entry`: internal table row with 5 GHz value, 2.4 GHz value, and flags. Flags are `B2055_INITTAB_ENTRY_OK` and `B2055_INITTAB_UPLOAD`.
- `b2055_inittab[]`: indexed by BCM2055 radio register number. Rows define default per-register values for 5 GHz and 2.4 GHz. Some rows are marked uploadable by default; others are valid but normally skipped unless forced.
- `RADIOREGS(...)` and `PHYREGS(...)`: initializer macros that map compact table values into `struct b43_nphy_channeltab_entry_rev2` fields.
- `b43_nphy_channeltab_rev2[]`: static channel table covering many 5 GHz channel numbers/frequencies plus 2.4 GHz channels 1-14. Each row stores channel number, frequency, an unknown field, radio PLL/VCO/LGEN/core tuning values, and six PHY bandwidth/SFO registers.
- `b2055_upload_inittab(struct b43_wldev *dev, bool ghz5, bool ignore_uploadflag)`: writes selected init-table rows to BCM2055 radio registers using `b43_radio_write16()`.
- `b43_nphy_get_chantabent_rev2(struct b43_wldev *dev, u8 channel)`: linear-searches `b43_nphy_channeltab_rev2[]` and returns a const row pointer or `NULL`.

## Control Flow
`b2055_upload_inittab()` iterates over every index in `b2055_inittab[]`. It skips entries without `B2055_INITTAB_ENTRY_OK`. It writes a row if the row has `B2055_INITTAB_UPLOAD` or the caller passes `ignore_uploadflag`. The chosen value comes from `ghz5` or `ghz2`. Every fourth write it reads `B43_MMIO_MACCTL` to flush posted writes.

`b43_nphy_get_chantabent_rev2()` scans the static channel table in order and compares `e->channel` to the requested `u8 channel`. The returned pointer is used by N-PHY channel-switch code to program radio and PHY registers. Failure returns `NULL`; callers must handle unsupported channels.

## State And Persistence
This file has no mutable software state. Its static const tables persist for the module lifetime. Runtime state changes occur only through hardware writes in `b2055_upload_inittab()` and through callers that apply channel-table entries to radio/PHY registers. The returned channel-table pointers are immutable and should not be stored beyond normal table lifetime assumptions, although static storage makes them stable while the module is loaded.

## Dependencies And Integration Points
- Includes `b43.h` for `struct b43_wldev`, MMIO/radio write helpers, and `B43_MMIO_MACCTL`; `radio_2055.h` for register names and channel-entry type; and `phy_common.h`.
- `phy_n.c` calls `b2055_upload_inittab()` during BCM2055/N-PHY initialization and uses many `B2055_*` register names directly for calibration and channel setup.
- `phy_n.c` calls `b43_nphy_get_chantabent_rev2()` during channel switching for radio revision paths that use BCM2055 rev2 tables, then writes the returned radio fields to `B2055_PLL_REF`, `B2055_RF_PLLMOD*`, `B2055_VCO_*`, `B2055_LGEN_*`, and per-core registers; PHY fields are written through N-PHY table/register helpers.
- `radio_2055.h` declares this file's two exported helpers and defines the register constants that make the table indices meaningful.

## Risks
- Hardware table correctness is critical. A wrong byte in the init table or channel table can break only specific bands/channels, making regressions hard to spot without broad hardware coverage.
- `b2055_upload_inittab()` trusts table indices as radio register addresses. Sparse unnamed entries such as `[0xC7]` are intentional but easy to damage during refactors.
- The `ignore_uploadflag` argument can force writes to rows normally marked `NOUPLOAD`; callers must use it only when full table programming is safe.
- Channel lookup is linear but the table is small enough for driver use. The bigger risk is missing or duplicate channel rows; lookup returns the first match.
- The `unk2` field has no documented semantics in this file, so updates require care and preferably comparison against vendor tables or known-good hardware traces.

## Test Signals
- Build-time coverage must include N-PHY and BCM2055 radio support so table initializers match the struct declaration.
- Runtime tests should include initialization on 2.4 GHz and 5 GHz, channel changes across low/mid/high 5 GHz and channels 1-14, and verification that unsupported channels fail gracefully.
- Hardware logs and register traces should show expected `b43_radio_write16()` sequences and no channel-switch failures in `phy_n.c`.
- Regression tests should specifically cover rows at boundaries: first/last table entries, 2.4 GHz channel 14, and 5 GHz channels with half-step odd channel numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.h

## Purpose
`radio_2055.h` defines the BCM2055 radio register map, the N-PHY revision-2 channel-table row layout, and the public helper prototypes implemented by `radio_2055.c`. It is the shared hardware contract for BCM2055 radio initialization, calibration, and channel switching in the B43 N-PHY path.

## Important APIs, Types, And Definitions
- Register constants: `B2055_*` names map radio register addresses from `0x00` through `0xE2`, covering spare/power-down controls, RSSI, RX/TX gain controls, PLL/VCO, local generator, per-core RX/TX baseband and RF blocks, calibration, power detector, GPIO-like/spare areas, and programmed gain-control entries.
- `struct b43_nphy_channeltab_entry_rev2`: channel switch row with channel number, frequency, an unknown field, 22 radio-register values, and `struct b43_phy_n_sfo_cfg phy_regs`.
- `b2055_upload_inittab(struct b43_wldev *dev, bool ghz5, bool ignore_uploadflag)`: uploads default BCM2055 register values for the selected band, optionally ignoring the upload flags.
- `b43_nphy_get_chantabent_rev2(struct b43_wldev *dev, u8 channel)`: returns an immutable channel-table entry for an N-PHY channel or `NULL`.

## Control Flow And State
The header has no executable control flow. It shapes the runtime behavior in `radio_2055.c` and `phy_n.c`: channel switching obtains a `struct b43_nphy_channeltab_entry_rev2`, then writes the radio fields to the register constants declared here and uses `phy_regs` for N-PHY bandwidth/SFO programming. Initialization calls the upload helper to program band-specific defaults. There is no software persistence in the header itself.

## Dependencies And Integration Points
- Includes `<linux/types.h>` and `tables_nphy.h` for `struct b43_phy_n_sfo_cfg`.
- `radio_2055.c` uses these constants as table indices and write targets.
- `phy_n.c` uses many `B2055_*` names directly for channel setup, radio calibration, RSSI calibration, TX/RX IQ calibration, power-detector configuration, and workaround logic.
- The register constants must remain consistent with any vendor radio documentation or reverse-engineered tables used by the driver.

## Risks
- Register address mistakes are high-impact and can cause band-specific radio failure, calibration failure, or out-of-spec transmission.
- The channel-entry struct layout must stay aligned with `RADIOREGS()` and `PHYREGS()` initializers in `radio_2055.c`. Reordering fields without updating initializers would silently program wrong registers.
- The `unk2` field is undocumented; its consumers and meaning should be verified before changing it.
- This header is specific to BCM2055. Mixing constants with BCM2056 or later radio code would misprogram hardware.

## Test Signals
- Compile N-PHY/BCM2055 paths after any struct or macro change to catch initializer mismatches.
- Runtime tests should cover radio init, channel switching, calibration, and traffic on hardware known to use BCM2055.
- Register trace comparisons against known-good channel-switch sequences are the strongest signal for table or register-map changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.h -->
