# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/dma.h

## Purpose
Declares the b43legacy DMA backend register definitions, descriptor layout, ring constants, metadata structures, inline MMIO accessors, public DMA APIs, and stubs for non-DMA builds.

## Important APIs, Types, and Functions
Defines DMA IRQ masks, 32-bit DMA controller register offsets and bitfields, `struct b43legacy_dmadesc32`, descriptor control flags, ring sizes, RX buffer sizes, `struct b43legacy_dmadesc_meta`, `enum b43legacy_dmatype`, and `struct b43legacy_dmaring`. Inline helpers `b43legacy_dma_read` and `b43legacy_dma_write` access controller registers. Public prototypes mirror `dma.c`.

## Control Flow
Enabled builds provide real DMA functions. Disabled builds return success/no-op for init/free/status/rx/suspend/resume and a benign zero from `b43legacy_dma_tx`, allowing the rest of the driver to compile when only PIO is selected. Runtime code uses `b43legacy_using_pio` to avoid real DMA calls when PIO is active.

## State and Persistence
The ring structure describes persistent runtime DMA state: descriptor memory, metadata, cached TX headers, DMA addresses, slot counters, frame offsets, controller index, backend type, stopped state, queue priority, and debug counters. Hardware-visible descriptors are packed ABI data shared with the DMA engine.

## Dependencies and Integration Points
Depends on `b43legacy.h`, kernel list/spinlock/workqueue/atomic headers, DMA address types, and mac80211/skb forward declarations. It is consumed by `main.c`, `dma.c`, debugfs, and transfer-mode selection code.

## Risks
Incorrect bit masks or descriptor packing can corrupt DMA. Ring constants must match controller expectations and RX frame sizes. Stub behavior in non-DMA builds means callers must not rely on DMA side effects unless DMA is compiled and selected. `queue_prio` must be initialized consistently with mac80211 queue mapping.

## Test Signals
Compile DMA-enabled and PIO-only configs, verify descriptor size and packed layout, run DMA API debug, and test TX/RX on hardware requiring 30-bit and 32-bit DMA masks. Queue stop/wake and unload-after-traffic are core validation points.
