# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/trx.c

## Purpose
Implements RTL8192DE PCIe TX descriptor construction, command/beacon descriptor construction, TX descriptor ownership checks, and TX polling doorbells. It translates mac80211 skb/tx-info state and rtlwifi rate-control metadata into the 8192DE hardware descriptor format.

## Important APIs, Types, And Functions
`rtl92de_tx_fill_desc()` is the main data-frame descriptor builder. `_rtl92de_map_hwqueue_to_fwqueue()` maps beacons, management frames, and data priorities to firmware queue selectors. `_rtl92de_insert_emcontent()` fills the 8-byte early-mode aggregation header. `rtl92de_tx_fill_cmddesc()` builds command/beacon descriptors. `rtl92de_is_tx_desc_closed()` checks the hardware OWN bit for the current ring descriptor. `rtl92de_tx_polling()` writes `REG_PCIE_CTRL_REG` to notify hardware of queued TX work.

## Control Flow
Data TX starts by deriving frame type, sequence number, bandwidth, TCB descriptor fields, and optional early-mode skb headroom. The function DMA maps the skb, clears descriptor content, sets first-segment fields when appropriate, clamps CCK rates on 5G, enables short GI/preamble, AMPDU aggregation, RTS/CTS flags, BW/subcarrier selection, packet size, AMPDU density, encryption type, queue selector, fallback limits, rate-control policy, RDG, buffer size/address, rate ID/MAC ID, QoS, firmware-LPS hardware sequence fields, and fragmentation markers.

Command/beacon TX maps the skb, clears a descriptor, chooses 6M on 5G or 1M otherwise, uses the beacon queue selector, sets buffer address/size, enables driver rate, applies firmware-LPS sequence handling for non-QoS frames, writes a memory barrier, and sets OWN. Polling uses a special beacon bit for `BEACON_QUEUE`, otherwise shifts bit 0 by hardware queue.

## State And Persistence
The file mutates descriptors and DMA mappings owned by the PCI TX rings. It reads `rtlhal->earlymode_enable`, `rtlhal->current_bandtype`, `rtlpriv->dm.useramask`, `rtl_ps_ctl->fwctrl_lps`, `mac->bw_40`, `mac->cur_40_prime_sc`, `mac->rdg_en`, station HT bandwidth/density, and `rtl_tcb_desc` rate-control metadata. Persistent hardware-visible state is the filled descriptor plus DMA address.

## Dependencies And Integration Points
Depends on rtlwifi PCI ring structures, common TX descriptor bitfield macros from `trx_common.h`, mac80211 skb/tx-info/station structures, DMA mapping APIs, PHY band state, LED header inclusion, and rtlwifi rate-control helpers. The operation is installed as `.fill_tx_desc`, `.fill_tx_cmddesc`, `.is_tx_desc_closed`, and `.tx_polling` in `sw.c`.

## Risks
DMA mapping failure returns without filling a usable descriptor, so callers must tolerate dropped TX. The function pushes early-mode bytes into the skb and sets descriptor packet offset; incorrect headroom assumptions or packet-size accounting can corrupt TX. Descriptor bitfields are hardware-specific, and 5G CCK clamping, AMPDU limits, encryption mapping, and useramask MACID/rate-id selection must match firmware expectations. `rtl92de_is_tx_desc_closed()` ignores its `index` argument and uses `ring->idx`, which is intentional only if callers query the current descriptor.

## Test Signals
Exercise data, management, beacon, QoS, nullfunc/control, encrypted WEP/TKIP/CCMP, AMPDU, early-mode, 20/40 MHz, 2.4G/5G, and firmware-LPS TX paths. Signals include clean DMA mapping, correct descriptor OWN transitions, no TX hangs, valid rate/MACID selection, successful beacon transmission, and no hardware queue stalls.
