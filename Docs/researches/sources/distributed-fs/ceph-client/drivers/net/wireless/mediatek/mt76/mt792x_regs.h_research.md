# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_regs.h

## Purpose
This shared register header maps MT792x hardware blocks: MCU/WFDMA, PLE/PSE, TMAC, DMA, WTBL, AGG, ARB, RMAC, MIB/ETBF, WFDMA rings/interrupts, top/conn-on PM registers, DMASHDL, USB UDMA, and WFSYS reset fields.

## Important APIs, Types, And Functions
It defines register address constructors such as `MT_WF_TMAC()`, `MT_WF_MIB()`, `MT_WFDMA0()`, bitfields for timing/MIB/filter/aggregation/DMA/interrupt state, firmware ownership registers, USB DMA flags, and chip-specific reset/init-done addresses. There are no functions.

## Control Flow
All control flow is indirect: MAC timing/stat code writes TMAC/AGG/MIB/RMAC registers, DMA code programs WFDMA/DMASHDL and interrupt masks, USB code accesses UDMA and endpoint reset controls, and PM code polls conn-on ownership bits.

## State And Persistence
The macros name persistent hardware state. WFDMA registers control queue operation and interrupt delivery; MIB registers accumulate counters; PM ownership bits determine host/firmware control; USB UDMA bits gate TX/RX; WFSYS reset bits reset the wireless subsystem.

## Dependencies And Integration Points
It is included by `mt792x.h`, MT7925 register extensions, shared MAC/DMA/USB files, debugfs, and bus drivers. It relies on Linux bit macros and mt76 register access helpers.

## Risks
Incorrect register offsets or masks can silently corrupt hardware state, especially around WFDMA reset, firmware ownership, and MIB clear-on-read counters. The header spans multiple chip generations, so chip-specific users must select compatible fields.

## Test Signals
Working DMA, IRQ, PM ownership, USB power/reset, MAC timing, MIB stats, queue debugfs output, and reset recovery across MT7921/MT7922/MT7925 variants validate this register map.
