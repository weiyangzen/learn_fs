# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/dma.h

This header defines the b43 DMA hardware ABI and software ring model. It contains DMA IRQ bits, 32-bit and 64-bit controller register offsets and masks, descriptor formats, ring memory sizes, RX buffer sizes/offsets for firmware formats, slot counts, pointer poisoning helpers, metadata structures, DMA operation vectors, DMA type/address enums, `struct b43_dmaring`, inline DMA register accessors, and public DMA API prototypes.

The implementation uses `struct b43_dma_ops` to abstract descriptor operations between 32-bit and 64-bit DMA. `struct b43_dmaring` owns coherent descriptor memory, optional TX header cache, DMA address, slot counters, frame offset, RX buffer size, MMIO base, controller index, type, stopped state, queue priority, debug counters, and flexible per-slot metadata.

This header integrates `dma.c` with b43 core, debugfs, interrupt/data paths, and mac80211 through `struct b43_wldev` and skbs. Risks include incorrect hardware bit definitions, mismatch between `B43_TXRING_SLOTS` and slots consumed per frame, RX buffers too small for firmware format, and confusing the poison pointer with a real skb. Test signals are DMA init, descriptor programming, TX/RX traffic, ring wraparound, debug stats, and clean DMA API teardown.
