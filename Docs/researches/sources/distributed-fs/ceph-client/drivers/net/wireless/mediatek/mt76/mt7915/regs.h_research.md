# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/regs.h

## Purpose
This header is the MT7915/MT7916/MT798x register map for the mt76 `mt7915` family. It defines generation-dependent register descriptor tables, symbolic register offsets, bit fields, queue interrupt masks, WFDMA ring address helpers, MAC/PHY/MIB register blocks, and SoC-only conninfra/ADIE/control registers used by PCI and embedded WMAC variants.

## Important APIs, Types, And Functions
The only C type is `struct mt7915_reg_desc`, which carries `reg_rev`, `offs_rev`, a bus remap table, and map size so runtime code can pick chip-specific addresses. `enum reg_rev` names absolute or base registers that differ by generation, while `enum offs_rev` names per-block offsets for TMAC, MDP, AGG, LPON, MIB, WTBL, PLE, and ETBF. `__REG()` and `__OFFS()` are the core access macros; most later register macros compose through them.

Important register families include `MT_WFDMA0/1`, `MT_MCUQ_RING_BASE`, `MT_TXQ_RING_BASE`, `MT_RXQ_RING_BASE`, interrupt masks such as `MT_INT_RX_DONE_ALL` and `MT_INT_TX_DONE_MCU`, WTBL helpers such as `MT_WTBL_UPDATE` and `MT_WTBL_LMAC_OFFS`, per-band MAC blocks (`MT_WF_TMAC`, `MT_WF_AGG`, `MT_WF_RMAC`, `MT_WF_MIB`, `MT_WF_LPON`), RX filter bits, MIB counters, LED registers, firmware exception registers, and MT798x conninfra/ADIE/AFE/SPI/reset definitions.

## Control Flow
There is no executable control flow, but the header drives control flow elsewhere. Probe code installs the correct `mt7915_reg_desc`; MMIO helpers translate logical names through `__REG` and `__OFFS`; DMA setup uses queue base and interrupt macros; MAC/statistics paths read MIB and WTBL fields; testmode and debug paths manipulate AGG/TMAC/RMAC registers; SoC bring-up uses conninfra, ADIE, SPI, AFE, sleep-protect, and power reset definitions.

## State And Persistence
The file defines persistent hardware state surfaces rather than storing state itself. Most registers describe live device state: DMA enable/reset bits, ring pointers, MCU interrupt status, firmware assert metadata, queue occupancy, WTBL airtime/accounting, MIB counters, RF filters, power ownership, LED state, ADIE calibration fields, and SoC reset/power status. Some counters are clear-on-read and the comments mark DNR counters that firmware should own.

## Dependencies And Integration Points
It depends on kernel bit helpers (`BIT`, `GENMASK`, `FIELD_PREP`) and mt76 queue enums/macros supplied by surrounding headers. It is consumed by mt7915 PCI/MMIO/SoC init, DMA, interrupt, MAC, MCU, debugfs, coredump, LED, and testmode code. The SoC-only definitions are directly coupled to `soc.c` and the MT7981/MT7986 device tree resource model.

## Risks
Address table mistakes are high impact because the same logical macro can resolve differently per generation. Clear-on-read MIB counters can corrupt firmware accounting if polled from the wrong path. Queue index helpers depend on `dev->q_id`, `dev->wfdma_mask`, and interrupt mask arrays being initialized consistently. The register map contains chip-family-specific variants, including MT7916 masks and MT798x ADIE controls, so adding hardware revisions requires careful updates to both enums and backing tables.

## Test Signals
Useful signals include successful DMA ring initialization, interrupts arriving on the expected masks, readable WTBL/MIB counters, correct debugfs/testmode register behavior on both bands, firmware assert dumps using the expected addresses, LED control on supported boards, and MT7981/MT7986 platform boot without SPI, reset, or conninfra timeout errors. Register smoke tests should include both MT7915 and MT7916-style offsets where available.
