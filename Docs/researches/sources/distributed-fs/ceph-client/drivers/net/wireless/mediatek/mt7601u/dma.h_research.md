# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/dma.h

## Purpose
Defines MT7601U USB DMA header layout, packet/command descriptor fields, queue selectors, RX descriptor fields, event types, and inline TX SKB wrapping helpers.

## Important APIs, Types, And Functions
Important constants are `MT_DMA_HDR_LEN`, `MT_RX_INFO_LEN`, `MT_FCE_INFO_LEN`, `MT_DMA_HDRS`, TX/RX descriptor `GENMASK` fields, packet flags such as `MT_TXD_PKT_INFO_80211` and `MT_TXD_PKT_INFO_WIV`, and RX packet/error flags. Enums define DMA ports, info types, queue selectors, and MCU event types. `mt7601u_dma_skb_wrap()` and `mt7601u_dma_skb_wrap_pkt()` prepend TXINFO and pad SKBs.

## Control Flow
Inline wrapping computes the rounded transfer length, encodes destination port and info type, pushes a little-endian TXINFO word, and pads to a 4-byte boundary plus trailing zero word.

## State And Persistence
The header modifies SKB contents in place for TX. Descriptor definitions describe hardware-visible state exchanged with the USB DMA/FCE engine.

## Dependencies And Integration Points
Used by `dma.c` for data packets and by MCU command paths for command packet framing. Depends on Linux SKB, unaligned access, and bitfield helpers.

## Risks
Incorrect padding or length fields will desynchronize the USB DMA engine. The wrapping helper mutates SKB headroom, so callers must ensure sufficient headroom before calling.

## Test Signals
TX packets accepted by firmware/hardware, command responses parsed correctly, no SKB headroom warnings, and RX descriptor type/length checks matching observed USB data.
