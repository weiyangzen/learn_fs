# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.c

## Purpose
`mbx.c` implements the VF side of the ixgbe PF/VF mailbox transport. It provides polling, status-bit handling, mailbox lock ownership, message read/write, legacy and newer mailbox semantics, stats accounting, and public wrappers used by VF hardware operations.

## Important APIs, Types, and Functions
- Public wrappers: `ixgbevf_poll_mbx()` waits for a PF message then reads it; `ixgbevf_write_mbx()` writes a VF message and waits for PF ACK.
- Operation tables: `ixgbevf_mbx_ops` and `ixgbevf_mbx_ops_legacy` fill `struct ixgbe_mbx_operations`.
- Internal helpers: `ixgbevf_poll_for_msg()`, `ixgbevf_poll_for_ack()`, `ixgbevf_read_mailbox_vf()`, clear/check helpers, `ixgbevf_obtain_mbx_lock_vf()`, release helpers, and legacy/current read/write implementations.

## Control Flow
Current write obtains VF ownership (`VFU`), clears stale PF status/ACK bits, writes up to 16 dwords to `VFMBMEM`, increments Tx stats, sets `REQ`, and polls for ACK before releasing ownership. Current read checks PF status, clears it, copies dwords from `VFMBMEM`, writes `ACK`, and increments Rx stats. Legacy write/read use older ownership and ACK behavior, including no-op release for legacy.

## State and Persistence Behavior
State is stored in `hw->mbx`: timeout, delay, mailbox size, cached `vf_mailbox` read-to-clear bits, operation table, and stats (`msgs_tx`, `msgs_rx`, `reqs`, `acks`, `rsts`). The cached mailbox preserves read-to-clear status bits so separate check/clear operations do not lose PF notifications.

## Dependencies and Integration Points
The code depends on mailbox register definitions from `mbx.h`, MMIO helpers from `vf.h`/`ixgbevf_main.c`, and delay functions. `vf.c` uses these wrappers for API negotiation, reset, link state, queue discovery, VLAN, MAC, multicast, and feature requests. `ixgbevf_main.c` serializes most calls with `adapter->mbx_lock`.

## Risks and Edge Cases
- Calls fail with `IXGBE_ERR_CONFIG` when timeout or required ops are unset.
- Message sizes larger than mailbox size are rejected by `ixgbevf_write_mbx()` and clipped by `ixgbevf_poll_mbx()`.
- Lock acquisition can time out if PF/VF ownership bits do not settle.
- Stats can double count some read-to-clear flows if check and clear are both used in close succession.
- Correct operation depends on matching PF firmware/driver expectations for legacy versus ESX/new mailbox ops.

## Test Signals
Exercise successful write/ACK/read, timeout without PF response, stale ACK/status clearing, reset indication handling, lock contention, oversized message rejection, legacy mailbox path, and transition from legacy to current ops after feature negotiation.
