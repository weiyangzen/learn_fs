# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl_ptp.c

## Purpose
Implements PTP-specific virtchnl2 mailbox operations for IDPF. It negotiates PTP capabilities, fetches direct register offsets when direct access is supported, provides mailbox fallbacks for reading/setting/adjusting device clock time, obtains per-vport Tx timestamp latch capabilities, and asynchronously retrieves Tx timestamp latch values.

## Important APIs, Types, And Functions
`idpf_ptp_get_caps()` sends `VIRTCHNL2_OP_PTP_GET_CAPS`, records capability bits, base increment value, max adjustment, secondary mailbox peer information, and maps direct-access register offsets through `idpf_get_reg_addr()`. `idpf_ptp_get_dev_clk_time()`, `idpf_ptp_get_cross_time()`, `idpf_ptp_set_dev_clk_time()`, `idpf_ptp_adj_dev_clk_time()`, and `idpf_ptp_adj_dev_clk_fine()` are fixed-size mailbox wrappers around PTP clock operations.

`idpf_ptp_get_vport_tstamps_caps()` sends `VIRTCHNL2_OP_PTP_GET_VPORT_TX_TSTAMP_CAPS`, validates the flexible latch reply size, allocates `struct idpf_ptp_vport_tx_tstamp_caps`, creates free/in-use latch tracking lists, initializes locks and status entries, and stores direct latch offsets when applicable. `idpf_ptp_get_tx_tstamp()` builds an async request for in-use latch indexes. `idpf_ptp_get_tx_tstamp_async_handler()` matches returned latch indexes to tracked SKBs and calls `idpf_ptp_get_tstamp_value()` to extend timestamps and complete `skb_tstamp_tx()`.

## Control Flow
PTP capability negotiation happens after the main virtchnl core is initialized. The driver first asks for caps and decides direct versus mailbox access by calling `idpf_ptp_get_features_access()`. If direct access is enabled for a feature, the returned offsets are converted to MMIO addresses and stored; otherwise later clock operations use mailbox wrappers.

Per-vport timestamp setup is conditional on vport flags and PTP access modes. The latch caps request returns a variable number of latch entries. Each latch is represented by an allocated tracker object on a free list. During Tx timestamp collection, `idpf_ptp_get_tx_tstamp()` scans the in-use list, moves status entries from request to read-value state, sends latch indexes asynchronously, and the async handler later removes matching latches, timestamps and consumes SKBs, returns latch objects to the free list, and updates stats.

## State And Persistence
Adapter PTP state stores capability bits, increment and adjustment limits, secondary mailbox validity/peer IDs, and direct register addresses. Vport PTP state stores timestamp latch capabilities, free and in-use latch lists, latch status array, low-bit timestamp shift, SKB pointers, and timestamp counters. Locks include latch list spinlock and status spinlock. All state is in memory and must be released by the PTP teardown path outside this file.

## Dependencies And Integration Points
The file depends on `idpf_ptp.h`, `idpf_virtchnl.h`, the virtchnl2 PTP structs and opcodes, SKB timestamp APIs, list management, spinlocks, and the generic transaction API. It integrates with `idpf_virtchnl.c` through `idpf_vc_xn_exec()` and PTP mailbox routing, with netdev hardware timestamp reporting through `skb_tstamp_tx()`, and with direct MMIO clock access paths through populated register pointers.

## Risks
Reply size validation is strict for fixed messages and flexible latch arrays; mistakes can lead to invalid latch traversal. Latch state transitions must stay synchronized with list operations and SKB ownership, especially when async replies arrive late or not at all. `idpf_ptp_get_tx_tstamp()` can send an async message with zero latch entries if all status transitions fail; callers should tolerate a no-op reply. Secondary mailbox validity depends on the `0xffff` peer queue sentinel and must match the send path in `idpf_virtchnl.c`. Timestamp extension depends on cached PHC time elsewhere in the driver.

## Test Signals
Signals include PTP capability negotiation with direct-only, mailbox-only, mixed, and unsupported devices; correct register address setup; clock get/set/adjust returning exact message sizes; per-vport latch setup and teardown; Tx timestamp SKBs being completed once and consumed; stats increments; async error handling for invalid vport IDs, invalid latch indexes, short replies, and no available in-use latch; and behavior when secondary mailbox is unavailable.
