# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_regs.h

## Purpose
`e1000_regs.h` is the central MMIO register map for the igb family. It defines offsets for control/status, NVM, PHY MDIC/I2C, flow control, interrupts, TX/RX queue registers, statistics, filtering, wakeup, virtualization, RSS, PTP time sync, DMA coalescing, EEE, thermal sensors, i210 flash/iNVM, and helper macros for safe register reads/writes.

## Important APIs, Types, and Functions
Most content is `#define` constants. Important macro families include scalar register offsets such as `E1000_CTRL`, `E1000_STATUS`, `E1000_EECD`, `E1000_MDIC`, `E1000_RCTL`, `E1000_TCTL`, `E1000_MANC`, and `E1000_SW_FW_SYNC`; indexed register macros such as `E1000_RDBAL(_n)`, `E1000_TDBAL(_n)`, `E1000_EITR(_n)`, `E1000_RETA(_i)`, and `E1000_ETQF(_n)`; and access helpers `wr32`, `rd32`, `wrfl`, `array_wr32`, and `array_rd32`. It declares `struct e1000_hw` and `u32 igb_rd32(struct e1000_hw *hw, u32 reg)`.

## Control Flow
The only executable behavior is in the access macros. `wr32` reads `hw->hw_addr` with `READ_ONCE`, checks `E1000_REMOVED`, and writes with `writel` when the BAR is still mapped. `rd32` delegates to `igb_rd32`. `wrfl` forces a posted-write flush by reading `E1000_STATUS`. Indexed queue macros compute different register strides for queue numbers below and above four, matching hardware layout differences.

## State and Persistence
This header names hardware state rather than storing driver state. Many registers are read-clear counters or interrupt causes, some are write-one-clear or write-only, and many queue/control registers persist until reset. Because the macros are used across the driver, changing a register offset affects data path setup, diagnostics, ethtool dumps, filters, PTP, and power management.

## Dependencies and Integration Points
Every file in this work item indirectly relies on this map. `e1000_nvm.c` uses `E1000_EECD`, `E1000_EERD`, `E1000_EEWR`, and RAL/RAH access. `e1000_phy.c` uses `E1000_MDIC`, `E1000_I2CCMD`, `E1000_CTRL`, and status/control registers. `igb_ethtool.c` uses a broad set for register dumps, tests, RSS, EEE, filters, and loopback. `igb_hwmon.c` relies on thermal sensor register definitions through MAC callbacks.

## Risks
The main risk is semantic, not algorithmic: wrong offsets, duplicate definitions, or using a register with read-clear side effects can break runtime behavior. The ethtool register dump deliberately reads aliases like EICS/ICS to avoid clearing causes, showing that access semantics matter. Queue index macros must stay aligned with hardware generation differences. `wr32` silently skips writes after device removal, so callers must be robust to hardware disappearing.

## Test Signals
Signals include successful driver probe and reset, correct ethtool register dumps, passing register self-tests, stable queue operation beyond four queues, working RSS/filter/PTP/EEE paths, and absence of MMIO faults during hot unplug or device removal.
