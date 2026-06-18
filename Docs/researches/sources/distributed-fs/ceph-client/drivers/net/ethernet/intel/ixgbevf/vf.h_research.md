# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/vf.h

## Purpose
`vf.h` defines the shared hardware model for ixgbevf: operation tables, MAC/mailbox state, hardware identity, VF stats, board info, MMIO access helpers, and exported helper prototypes.

## Important APIs, Types, and Functions
- `struct ixgbe_mac_operations` is the main hardware abstraction table used by the driver.
- `struct ixgbe_mac_info`, `struct ixgbe_mbx_operations`, `struct ixgbe_mbx_info`, and `struct ixgbe_hw` hold hardware and mailbox runtime state.
- `struct ixgbevf_hw_stats` stores base, last, current, and saved reset counters.
- `struct ixgbevf_info` maps PCI board IDs to MAC type and ops table.
- Inline MMIO helpers write/read registers and arrays, using `ixgbevf_read_reg()` for removal-aware reads.

## Control Flow
This header is structural. The driver copies operation tables into `hw->mac.ops` and `hw->mbx.ops`, then calls through those function pointers. Inline register writes skip removed devices by checking `hw_addr`.

## State and Persistence Behavior
The structs declared here are the central in-memory state for VF hardware, mailbox, stats, and board capabilities. `hw->back` points to `ixgbevf_adapter`, bridging generic hardware ops back to the Linux netdev driver.

## Dependencies and Integration Points
It includes Linux PCI, delay, interrupt, Ethernet and netdevice headers, plus local `defines.h`, `regs.h`, and `mbx.h`. It is included by low-level hardware, mailbox, and main driver files.

## Risks and Edge Cases
- Operation pointers must be initialized before use; mailbox wrappers explicitly reject missing ops.
- Register write helper does not report failure if device is removed.
- `IXGBE_REMOVED()` only checks null MMIO pointer, while failed read detection is implemented in `ixgbevf_read_reg()`.

## Test Signals
Build and sparse checks for function pointer signatures, register array address math, stats width handling, and removal-aware read/write behavior.
