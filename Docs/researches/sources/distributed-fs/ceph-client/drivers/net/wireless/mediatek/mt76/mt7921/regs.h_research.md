# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/regs.h

## Purpose
This header defines the compact MT7921-specific register map used by common and PCI/SDIO/USB code. It extends shared `mt792x_regs.h` with MDP, WFDMA interrupt, HIF L1 remap, WTBL update, and WFSYS reset registers.

## Important APIs, Types, And Functions
There are no functions or types. Important macros include `MT_MDP_DCR0/DCR1` and fields for D-AMSDU and RX header translation, per-band RX filter routing registers `MT_MDP_BNRCFR0/1`, host interrupt enable `MT_WFDMA0_HOST_INT_ENA`, TX/RX interrupt masks (`MT_INT_RX_DONE_*`, `MT_INT_TX_DONE_*`), `MT_RX_DATA_RING_BASE`, L1 remap fields (`MT_HIF_REMAP_L1*`), `MT_WFSYS_SW_RST_B`, `MT_WTBL_UPDATE`, and `MT_WTBL_UPDATE_ADM_COUNT_CLEAR`.

## Control Flow
The macros are consumed by MAC init, RX filter setup, DMA/interrupt setup, PCI remap helpers, WTBL counter clearing, and reset code. `mt7921_reg_map_l1()` in `mt7921.h` uses the L1 remap definitions to access high physical addresses.

## State And Persistence
The header names hardware state rather than storing state. The related hardware state includes MDP RX behavior, host interrupt enables, DMA ring bases, remap window selection, WFSYS reset latch, WTBL admin counters, and WTBL update busy state.

## Dependencies And Integration Points
It includes the shared mt792x register header and is included by `mt7921.h`. It integrates with `init.c`, `main.c`, `mac.c`, `mcu.c`, `pci.c`, and bus-specific reset code.

## Risks
Interrupt-mask or ring-base mistakes break RX/TX completions. L1 remap definitions are shared mutable register state and require serialized access. The file is much smaller than `mt7915/regs.h`, so unsupported blocks must come from shared `mt792x_regs.h`; adding direct MT7921 register users should avoid duplicating shared definitions.

## Test Signals
MAC init should set MDP fields correctly, interrupts should fire for data/MCU/FWDL queues, WTBL counter clearing should complete, L1 remap register reads should return chip ids/revisions, and reset code should manipulate WFSYS registers without unsupported address errors.
