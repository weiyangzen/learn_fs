# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/regs.h

Purpose: MT7603 register map and bitfield catalog. It assigns offsets and masks for top-level revision/chip ID, MCU remap, HIF/WPDMA rings, PSE flow control, PHY/AGC/RXTD, aggregation, DMA filters, WMM arbitration, TMAC/RMAC, security, WTBL, LPON timers, hardware interrupts, MIB counters, LED registers, client/PSE physical windows, and efuse access.

Important APIs/macros: defines register base helpers such as `MT_MCU()`, `MT_HIF()`, `MT_PSE()`, `MT_WF_PHY()`, `MT_WF_AGG()`, `MT_WF_DMA()`, `MT_WF_ARB()`, `MT_WF_TMAC()`, `MT_WF_RMAC()`, `MT_WF_SEC()`, `MT_WTBL_OFF()`, `MT_LPON()`, and bitfields consumed through `FIELD_PREP`, `FIELD_GET`, `mt76_rr`, `mt76_wr`, and `mt76_rmw`. WTBL layout macros describe multiple WTBL banks and per-word fields for address, key, QoS, HT/VHT, BA, rate, sequence, and counters.

Control flow: no executable flow, but the map drives all register programming in the MT7603 driver. Implementations use it for interrupt masking, DMA start/reset, scheduler and queue programming, filter programming, beacon timers, WTBL updates, EEPROM/efuse reads, LED control, CCA/MIB reads, and reset/watchdog diagnostics.

State and persistence: represents volatile hardware state. Persistent information enters through efuse/EEPROM registers; runtime state lives in hardware tables, DMA ring registers, MIB counters, and WTBL entries. Several counters are read-clear or require explicit clear bits, so call ordering matters.

Dependencies and integration: included by `mt7603.h` and all mt7603 implementation files. It relies on Linux bit macros (`BIT`, `GENMASK`) and mt76 MMIO helpers. Physical remap constants connect high physical blocks such as LED/client/PSE/efuse into PCIe remap windows.

Risks: a typo in a bit mask or offset can silently corrupt unrelated hardware state; two entries use `GENAMSK` spelling (`MT_WTBL2_W5_FAIL_COUNT_RATE1`, `MT_WTBL2_W13_AVG_RCPI2`) and will fail if referenced. Remap base/offset masks must match silicon windows. WTBL bank sizing depends on `MT7603_WTBL_SIZE`, so changing table size without recalculating offsets is unsafe.

Test signals: compile-time reference coverage catches macro spelling only when used. Runtime validation comes from working interrupt delivery, DMA rings, beacon timing, association/security setup, LED control, efuse reads, and sane MIB/WTBL debug values under traffic.
