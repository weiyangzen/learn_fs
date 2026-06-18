# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/regs.h

## Purpose
`regs.h` centralizes VF-visible ixgbe register offsets and RSS control bit definitions used by the VF driver.

## Important APIs, Types, and Constants
It defines offsets/macros for VF control/status/link, interrupt cause/mask/throttle/IVAR, Rx and Tx descriptor ring base/length/head/tail/control registers, DCA controls, packet-split type, hardware counters, mailbox-flush read, and RSS registers (`VFMRQC`, `VFRSSRK`, `VFRETA`) plus RSS field bits.

## Control Flow
This file has no executable flow. It enables driver code to use `IXGBE_READ_REG()`/`IXGBE_WRITE_REG()` against symbolic offsets. Array-like macros compute queue register addresses from queue index.

## State and Persistence Behavior
No software state is stored here. The constants describe MMIO-backed device state that persists in hardware until reset or explicit writes.

## Dependencies and Integration Points
Included by `vf.h` and consumed heavily by `ixgbevf_main.c`, `vf.c`, and `mbx.c`. It is the common address contract for VF hardware access.

## Risks and Edge Cases
Incorrect offsets or queue-stride math would cause silent MMIO corruption. `IXGBE_WRITE_FLUSH()` reads `VFSTATUS`, which also participates in removal detection via failed reads in `ixgbevf_main.c`.

## Test Signals
Compile coverage, hardware smoke tests for queue enable/disable, interrupt masking, RSS programming, stats reads, and register-access behavior after PCI removal.
