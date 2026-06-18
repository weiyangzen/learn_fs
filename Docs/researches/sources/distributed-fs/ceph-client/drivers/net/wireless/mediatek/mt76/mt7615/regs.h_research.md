# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/regs.h

Purpose: Central register map and bitfield definition header for MT7615/MT7663/MT7622 variants across MMIO, USB, and SDIO transports.

Important APIs and constants: `enum mt7615_reg_base` indexes chip-specific base arrays. Macros cover hardware IDs, firmware state, MCU remap windows, HIF/PDMA registers, interrupt masks, PLE/PSE/PP/DMASHDL scheduler fields, PHY/RF controls, MAC CFG/AGG/ARB/TMAC/RMAC blocks, WTBL update/rate/key fields, LPON TSF registers, MIB counters, LED controls, efuse controls, MT7622 infracfg, UDMA, and antenna switch controls.

Control flow and integration: Executable files combine these macros with `dev->reg_map` to read/write logical device blocks. `mmio.c` maps high logical addresses via `mt7615_reg_map()`. PCI/USB/SDIO initialization, PM ownership, testmode antenna setup, DMA scheduling, MAC reset, RX filtering, WTBL rate updates, LED callbacks, efuse reads, and survey/MIB updates all use these definitions.

State and persistence: The file describes hardware state stored in registers: interrupt sources/masks, DMA enable/busy state, firmware ownership and readiness, WTBL contents, MIB counters, efuse data, LED blink state, and scheduler quotas. It does not store host state itself.

Dependencies: Linux `BIT`, `GENMASK`, and field-prep helpers through included kernel headers. Depends on callers having a `dev` variable in scope for many macros, which is a deliberate local style.

Risks: Register offsets and bit masks are hardware ABI. A wrong base index, overlapping mask, or variant mismatch can corrupt unrelated hardware blocks. Some names are duplicated, such as `MT_HIF0_MIN_QUOTA`, reflecting shared bit positions; edits need caution. Macros that use implicit `dev` are easy to misuse outside mt7615 code.

Test signals: Successful probe across chip variants, correct ASIC revision, interrupt delivery, firmware readiness polling, efuse reads, DMA scheduling, LED behavior, testmode antenna switching, and survey/MIB values.
