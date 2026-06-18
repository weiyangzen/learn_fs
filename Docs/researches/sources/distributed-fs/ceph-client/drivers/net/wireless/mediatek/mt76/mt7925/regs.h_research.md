# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/regs.h

## Purpose
This header defines MT7925-specific register addresses and bitfields that extend the shared MT792x register map. It covers MDP filtering, WFDMA interrupt/ring layout, HIF remap registers, WFSYS reset, and WTBL update fields.

## Important APIs, Types, And Functions
Important macros include `MT_MDP_*` receive filter/forwarding fields, `MT_WFDMA0_HOST_INT_ENA`, MT7925 RX/TX interrupt masks, data/event ring bases, `MT_HIF_REMAP_L1/L2` fields, `MT_WFSYS_SW_RST_B`, and WTBL update helpers. There are no functions.

## Control Flow
The macros are consumed by PCI register remap and DMA setup, shared MT792x DMA/interrupt code, MAC RX filter setup, and WTBL update routines. They determine which hardware rings drive NAPI and which interrupt bits are enabled.

## State And Persistence
Register writes through these definitions persist in hardware until reset or reconfiguration. HIF remap state is backed up/restored in the PCI file, while WFDMA interrupt and ring state is managed during DMA init/reset/suspend.

## Dependencies And Integration Points
It includes `../mt792x_regs.h` and is included by `mt7925.h`. It integrates with mt76 MMIO helpers, PCI bus ops, DMA queue allocation, interrupt masking, MAC initialization, and WTBL management.

## Risks
Wrong bit definitions can misroute interrupts, break register reads through remap windows, corrupt WTBL updates, or direct RX management/control frames to the wrong destination. Conditional `MT_HIF_REMAP_BASE_L2` differs under `CONFIG_MT76_DEV`, which must match build/runtime access expectations.

## Test Signals
Interrupt delivery on all enabled rings, successful register reads above direct MMIO range, WFDMA reset/init, RX filter behavior, and WTBL update correctness validate this map.
