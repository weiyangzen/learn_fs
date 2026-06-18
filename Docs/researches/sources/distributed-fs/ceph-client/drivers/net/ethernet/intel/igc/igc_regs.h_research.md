# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_regs.h

## Purpose
`igc_regs.h` is the register map and low-level MMIO access header for the IGC Ethernet driver. It gives symbolic offsets for core device control, interrupts, RX/TX rings, statistics, filtering, timestamping, TSN, PCIe PTM, wake, EEE, LTR, and PHY/NVM related registers.

## Important APIs, Types, and Functions
The header defines `IGC_*` register offsets and indexed offset macros such as `IGC_RDBAL(_n)`, `IGC_TDBAL(_n)`, `IGC_EITR(_n)`, `IGC_SRRCTL(_n)`, `IGC_TXQCTL(_n)`, and `IGC_TQAVCC(_n)`. It declares `struct igc_hw` and `u32 igc_rd32(struct igc_hw *hw, u32 reg)`. Access helpers are `wr32(reg, val)`, `rd32(reg)`, `wrfl()`, `array_wr32()`, `array_rd32()`, and `IGC_REMOVED()`.

## Control Flow
There is no runtime control flow beyond the write/read helper macros. `wr32()` snapshots `hw->hw_addr` with `READ_ONCE()`, checks `IGC_REMOVED()`, and writes with `writel()`. `rd32()` delegates to `igc_rd32()`. `wrfl()` reads `IGC_STATUS` to flush posted writes.

## State and Persistence Behavior
The file does not store state itself. Its definitions describe persistent device MMIO state and are used by other driver modules to mutate runtime hardware state. The helpers avoid MMIO writes after the device memory address has been removed.

## Dependencies and Integration Points
Every IGC module that touches hardware depends on this header, including PTP (`SYSTIM`, `TSYNCTXCTL`, PTM), TSN (`TQAVCTRL`, Qbv/Qav registers), ring setup, statistics, filters, NVM, wake, EEE, and interrupt handling. It assumes bit macros such as `BIT()` and `GENMASK()` are available through included driver/kernel headers.

## Risks and Edge Cases
Incorrect offsets or indexed strides can corrupt unrelated device state. `wr32()` silently skips writes after removal, so callers must still handle device teardown races. `rd32()` behavior depends on `igc_rd32()` handling removed hardware safely. Register definitions are shared across many features, so changes have wide blast radius.

## Test Signals
Build coverage is the primary signal. Runtime smoke tests should include probe/remove, reset, interrupt setup, RX/TX ring bring-up, hwtstamp/PTP, TSN offload, ethtool stats, wake/EEE paths, and device removal under load to exercise the MMIO helper assumptions.
