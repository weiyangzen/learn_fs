# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_mbx.c

## Purpose
`fm10k_mbx.c` implements the FM10K mailbox transport used for PF/VF and PF/switch-manager communication. It provides circular FIFO management, mailbox-memory copy helpers, CRC verification, PF/VF connection state handling, switch-manager version negotiation, TLV handler registration, and the exported initialization routines that populate `struct fm10k_mbx_info` operations.

## Important APIs, types, and functions
FIFO primitives include `fm10k_fifo_init()`, `fm10k_fifo_used()`, `fm10k_fifo_unused()`, `fm10k_fifo_head_len()`, `fm10k_fifo_enqueue()`, `fm10k_fifo_head_drop()`, and `fm10k_fifo_drop_all()`. These operate on `struct fm10k_mbx_fifo` and assume power-of-two buffer sizes for mask-based wraparound.

PF/VF mailbox helpers include index arithmetic (`fm10k_mbx_index_len()`, `fm10k_mbx_tail_add/sub()`, `fm10k_mbx_head_add/sub()`), mailbox-memory transfer (`fm10k_mbx_write_copy()`, `fm10k_mbx_read_copy()`, `fm10k_mbx_pull_head()`, `fm10k_mbx_push_tail()`), CRC helpers (`fm10k_crc_16b()`, `fm10k_fifo_crc()`, `fm10k_mbx_update_local_crc()`, `fm10k_mbx_verify_remote_crc()`), and state handlers (`fm10k_mbx_process_connect()`, `fm10k_mbx_process_data()`, `fm10k_mbx_process_disconnect()`, `fm10k_mbx_process_error()`, `fm10k_mbx_process()`).

Switch-manager mailbox support is implemented by `fm10k_sm_mbx_connect()`, `fm10k_sm_mbx_disconnect()`, `fm10k_sm_mbx_validate_fifo_hdr()`, `fm10k_sm_mbx_receive()`, `fm10k_sm_mbx_transmit()`, `fm10k_sm_mbx_process_reset()`, `fm10k_sm_mbx_process_version_1()`, and `fm10k_sm_mbx_process()`. Public initialization is through `fm10k_pfvf_mbx_init()` and `fm10k_sm_mbx_init()`.

## Control flow
Both mailbox variants expose operations through `mbx->ops`. Callers initialize the mailbox, register TLV handlers, connect it, enqueue Tx messages, and periodically process interrupts or polling events.

For PF/VF mailboxes, `connect()` transitions from CLOSED to CONNECT, seeds timeout and CRC state, writes a fake remote disconnect header, enables mailbox interrupts, and publishes a CONNECT header. `process()` reads the remote header, validates type/head/tail/reserved/size fields, dispatches to the type-specific handler, optionally builds an ERROR header, then writes the local header and interrupt bits. DATA processing copies newly advertised remote DWORDs into the Rx FIFO, checks message sizes, verifies CRC over data and header, parses complete TLV messages with `fm10k_tlv_msg_parse()`, advances acknowledgements, pulls Tx FIFO data into mailbox memory, and emits a DATA reply. DISCONNECT and ERROR paths reset work, drain or drop pending FIFO contents, and move toward CONNECT or CLOSED depending on state.

For PF/switch-manager mailboxes, the header layout carries local tail, version, remote head, and error fields rather than PF/VF message type/CRC fields. `connect()` starts version negotiation; version 0 is reset, version 1 is active. `process()` validates FIFO offsets and version, handles remote error flags, processes reset or version-1 data, aligns receive head to message boundaries, transmits only whole TLV messages, and sends connect/data headers reflecting local state.

## State and persistence behavior
All mailbox state is in `struct fm10k_mbx_info`: operation table, handler table, Tx/Rx FIFOs, timeout/delay, MMIO register offsets, current header/lock bits, max message size, mailbox memory length, local tail and remote head indexes, in-flight lengths (`tail_len`, `head_len`), pushed/pulled partial-message counts, local/remote CRC or SM version values, current state, last test result, and detailed counters. It is runtime state only and is reinitialized on reset or reconnect.

The Tx FIFO persists queued TLV messages until acknowledged by the remote head; completed messages are dropped from the FIFO and counted. Oversized messages can be dropped when the remote announces a smaller maximum size. The Rx FIFO keeps pushed partial data until a complete TLV message is available, then parsing drops it. Error/reset paths deliberately discard in-progress work to resynchronize both endpoints.

## Dependencies and integration points
The implementation depends on register accessors `fm10k_read_reg()`/`fm10k_write_reg()`, TLV parsing and handler metadata from `fm10k_tlv.h`, hardware type information from `fm10k_type.h`, mailbox register definitions from `fm10k_mbx.h`, and microsecond delays for bounded drain/connect loops. It is used by PCI interrupt handling, MAC/VLAN request submission, VF management, and host-state monitoring code.

`fm10k_pfvf_mbx_init()` selects VF or PF mailbox registers based on `hw->mac.type` and VF id, while `fm10k_sm_mbx_init()` binds to the PF global switch-manager mailbox. Handler registration validates ascending message IDs, ascending attribute IDs, non-null callbacks, result-array bounds, and terminators before assigning `mbx->msg_data`.

## Risks and edge cases
Mailbox correctness depends on strict head/tail arithmetic, avoidance of reserved index values, and alignment to complete TLV message boundaries. A bad remote header can otherwise make the local side read stale mailbox memory or overrun FIFO capacity. CRC handling in the PF/VF path is a major corruption guard; mismatches force error response and reconnect. The switch-manager path lacks the same CRC field and relies on header validation and version/error negotiation.

Timeout behavior is intentionally conservative but can silently drop queued Tx data when reconnecting or shrinking `max_size`. `fm10k_mbx_enqueue_tx()` returns `0` even after FIFO enqueue failure after recording `tx_busy` and clearing timeout, so callers must rely on mailbox state/counters rather than the return value alone for every delivery failure. Handler-table validation is important because the TLV parser assumes sorted metadata and bounded result indexes.

## Test signals
Test signals include successful PF/VF mailbox connect/open/disconnect cycles, SM version-1 negotiation, TLV test-message handling, expected reset on malformed head/tail/reserved/size/CRC cases, no FIFO overflow when the remote stops acknowledging, and recovery after remote ERROR or RESET headers. Counters such as `tx_busy`, `tx_dropped`, `tx_messages`, `rx_messages`, `rx_parse_err`, `tx_mbmem_pulled`, and `rx_mbmem_pushed` should move predictably during stress tests. Fault injection should verify that oversized messages, bad handler tables, and full FIFOs do not corrupt mailbox state.
