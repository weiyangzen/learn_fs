# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.c

## Purpose
`ixgbe_mbx.c` implements the physical-function side of the ixgbe PF/VF mailbox transport. It provides generic wrapper entry points through `hw->mbx.ops`, PF mailbox register operations, posted read/write helpers with polling, mailbox event checks, statistics updates, and PF mailbox initialization for SR-IOV capable MACs.

## Important APIs and functions
The public wrapper APIs are `ixgbe_read_mbx`, `ixgbe_write_mbx`, `ixgbe_check_for_msg`, `ixgbe_check_for_ack`, and `ixgbe_check_for_rst`. They validate `hw->mbx.ops`, enforce mailbox size rules, and delegate to the operation table. `ixgbe_read_mbx` clamps reads to `mbx->size`, while `ixgbe_write_mbx` rejects oversized writes with `-EINVAL`.

The posted helpers `ixgbe_read_posted_mbx` and `ixgbe_write_posted_mbx` add polling around the raw operations. `ixgbe_poll_for_msg` and `ixgbe_poll_for_ack` loop until the operation-specific check returns success or `mbx->timeout` expires, sleeping `mbx->usec_delay` between attempts.

The PF implementation is in `ixgbe_check_for_msg_pf`, `ixgbe_check_for_ack_pf`, `ixgbe_check_for_rst_pf`, `ixgbe_obtain_mbx_lock_pf`, `ixgbe_write_mbx_pf`, and `ixgbe_read_mbx_pf`. The exported operation table `mbx_ops_generic` binds these methods. `ixgbe_init_mbx_params_pf`, under `CONFIG_PCI_IOV`, initializes size, timeout/delay, and stats for supported PF MAC generations.

## Control flow
Caller code in SR-IOV paths uses the wrapper APIs. The wrapper locates `struct ixgbe_mbx_info` in `hw->mbx`, validates operation availability, then dispatches to PF-specific handlers. PF message and ACK detection reads `IXGBE_MBVFICR(index)`, tests the VF bit, writes the bit back to clear it, and increments request or ACK counters. Reset detection reads `IXGBE_VFLRE` on 82599 or `IXGBE_VFLREC` on newer MACs, clears reset-complete bits, and increments reset counters.

For PF writes, `ixgbe_write_mbx_pf` first claims ownership with `IXGBE_PFMAILBOX_PFU`, flushes stale message and ACK state, writes each u32 to `IXGBE_PFMBMEM(vf_number)`, then writes `IXGBE_PFMAILBOX_STS` to interrupt the VF and release the buffer. PF reads mirror that flow: claim lock, copy words from `IXGBE_PFMBMEM`, then acknowledge and release with `IXGBE_PFMAILBOX_ACK`.

## State and persistence
Runtime state lives in `hw->mbx`: configured size, timeout/delay, operation table, and counters for transmitted messages, received messages, requests, ACKs, and resets. Mailbox payload and ownership are held in device registers, not persistent storage. Register writes both signal events and clear event bits, so read/check operations have side effects.

## Dependencies and integration points
The file depends on `ixgbe.h`, `ixgbe_mbx.h`, PCI/SR-IOV build support, MMIO helpers such as `IXGBE_READ_REG`, `IXGBE_WRITE_REG`, and `IXGBE_WRITE_REG_ARRAY`, and MAC type values from the ixgbe type system. It is consumed mainly by `ixgbe_sriov.c`, which dispatches VF mailbox requests and sends PF replies.

## Risks and edge cases
Mailbox operations are register side-effect heavy. A missed clear, failed PF ownership claim, or wrong VF index can lose a message or wedge VF/PF negotiation. Posted mailbox helpers return `-EIO` when no timeout is configured, so PF-side users must not assume posted operation support unless timeout/delay are initialized. Reset handling writes `IXGBE_VFLREC` even after reading `IXGBE_VFLRE` for 82599, which is intentional register behavior but should be regression-tested on older hardware.

## Test signals
Useful signals include SR-IOV VF reset and mailbox negotiation success, incrementing mailbox stats under VF traffic, successful ACK/NACK delivery for each mailbox command, and absence of mailbox timeouts during VF driver load/unload. Fault tests should cover oversized writes, unavailable `mbx->ops`, VFs that never ACK, VF reset events, and multiple VFs mapped across both `MBVFICR` index groups.
