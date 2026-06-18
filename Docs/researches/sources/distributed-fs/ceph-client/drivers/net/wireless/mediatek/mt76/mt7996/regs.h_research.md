# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/regs.h

## Purpose
Defines the MT7996/MT7992/MT7990 register-address vocabulary used by the mt7996 driver. It is a pure hardware contract header: no executable control flow, but a large set of macros that translate driver concepts such as per-band MAC blocks, WFDMA rings, RRO queues, MIB counters, interrupt masks, remap windows, LED controls, firmware state, PCIe MAC, and PHY/RF diagnostic blocks into MMIO addresses and bitfields.

## Important APIs, Types, And Functions
The important types are `struct __map`, `struct __base`, and `struct mt7996_reg_desc`, which let runtime chip-specific tables describe base addresses, remap windows, and offset revisions. `enum base_rev` names per-band base blocks such as AGG, ARB, TMAC, RMAC, DMA, WTBLOFF, ETBF, LPON, MIB, and RATE. `enum offs_rev` names revision-dependent offsets for MIB counters, HIF remap registers, WTBL control registers, and chip-specific address ends. Macros such as `MT_WF_TMAC()`, `MT_WF_MIB()`, `MT_RXQ_RING_BASE()`, and `MT_INT_RX_DONE_ALL` are integration points for reset, DMA, interrupt, statistics, debug, and RRO code.

## Control Flow
There is no runtime control flow. Consumers populate `dev->reg` from a chip descriptor, then these macros fold band id, queue id, offset-revision id, and WFDMA mask state into concrete addresses. DMA setup reads queue ids through `MT_Q_ID()` and chooses WFDMA0/WFDMA1 through `MT_Q_BASE()`. Interrupt handlers combine queue-specific masks through `MT_INT_RX()` and `MT_INT_TX_MCU()`. Statistics paths use the MIB macros, with comments marking counters that should not be read directly because firmware may own their clear-on-read semantics.

## State And Persistence
The header describes persistent hardware state rather than owning memory itself. State lives in chip registers: RRO address tables and ACK windows, PLE page counts, MDP header translation, TMAC timing, WTBL updates, RMAC filters, WFDMA global configuration, interrupt source/mask CSRs, MCU command/status bits, firmware assertion state, LED blink controls, low-power ownership, ADIE identity, and PHYRX diagnostic counters. Revision indirection is persistent per device through `dev->reg.base` and `dev->reg.offs_rev`.

## Dependencies And Integration Points
Depends on mt76/mt7996 device structures exposing `dev->reg`, queue id arrays, queue interrupt masks, WFDMA masks, and band count definitions. It integrates with the mt7996 DMA, MMIO, MCU recovery, SER, debugfs, statistics, LED, PCIe, WED/RRO, and PHY code. The macros rely heavily on Linux `BIT`, `GENMASK`, and `FIELD_PREP/FIELD_GET` conventions.

## Risks
The main risk is silent address drift across chip revisions. A wrong base, remap offset, queue id, or interrupt mask can corrupt unrelated registers, lose interrupts, or break recovery. MIB clear-on-read comments matter: reading firmware-owned counters can destroy statistics. RRO and WFDMA macros are tightly coupled to queue enumeration; changing queue ordering without updating this header can route DMA to the wrong ring.

## Test Signals
Useful signals are successful probe on all supported mt7996-family chips, WFDMA ring setup, interrupt delivery per RX/TX/MCU queue, firmware recovery state transitions, RRO queue operation, accurate MIB accumulation, LED control, low-power ownership changes, PCIe1 dual-HIF operation, and debug register reads that match expected hardware documentation.
