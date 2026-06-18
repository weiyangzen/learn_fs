# sources/distributed-fs/ceph-client/net/smc/smc_cdc.h

## Purpose
`smc_cdc.h` defines CDC wire-format messages, SMC-D CDC layout, cursor conversion helpers, cursor arithmetic, close-state predicates, pending-send metadata, and CDC function prototypes. It is the shared contract between transmit, receive, close, SMC-R WR handling, and SMC-D memory notification paths.

## Important APIs, Types, And Functions
The header defines `SMC_CDC_MSG_TYPE`, `union smc_cdc_cursor`, `struct smc_cdc_msg`, `union smcd_cdc_cursor`, `struct smcd_cdc_msg`, and `struct smc_cdc_tx_pend`. Inline helpers include `smc_cdc_rxed_any_close()`, `smc_cdc_rxed_any_close_or_senddone()`, `smc_curs_add()`, `smc_curs_copy()`, `smc_curs_copy_net()`, `smcd_curs_copy()`, `smc_curs_diff()`, `smc_curs_comp()`, `smc_curs_diff_large()`, `smc_host_cursor_to_cdc()`, `smc_host_msg_to_cdc()`, `smc_cdc_cursor_to_host()`, `smcr_cdc_msg_to_host()`, `smcd_cdc_msg_to_host()`, and `smc_cdc_msg_to_host()`.

## Control Flow
Transmit code stages host-order CDC state in `conn->local_tx_ctrl`, then `smc_host_msg_to_cdc()` snapshots the producer and consumer cursors and converts fields to network order before posting an SMC-R WR. Receive code uses `smc_cdc_msg_to_host()` to choose SMC-R or SMC-D conversion, then imports cursor movement into `conn->local_rx_ctrl`. Cursor helpers calculate ring-buffer deltas for send-buffer space, peer RMB space, received data, and splice/urgent positioning. Close code uses the inline predicates to decide whether peer close, peer abort, or send-done flags have arrived.

## State And Persistence
The header itself owns no storage, but its data layouts directly persist in connection fields and on the wire. SMC-R CDC messages are network-byte-order WR payloads with token/sequence/cursors. SMC-D CDC messages are embedded in DMB memory with compact producer/consumer cursor unions carrying flags. `struct smc_cdc_tx_pend` persists per posted CDC WR until completion, carrying the connection pointer, sent cursor, producer cursor snapshot, and control sequence.

## Dependencies And Integration Points
`smc_cdc.h` includes `smc.h`, `smc_core.h`, and `smc_wr.h`, binding CDC to connection state, link groups, and work-request APIs. It is consumed by CDC implementation, TX/RX cursor accounting, close handling, and SMC-D receive initialization.

## Risks And Edge Cases
Cursor arithmetic is protocol-critical. The helpers assume the caller supplies correct buffer sizes and that deltas do not exceed ring capacity except in the explicit large-diff helper. Atomic cursor copying must remain consistent across host and network cursor unions. `smc_cdc_cursor_to_host()` intentionally ignores backwards cursor movement to prevent stale control messages from corrupting state. Any layout change must preserve wire format, alignment, and WR size constraints enforced in `smc_cdc.c`.

## Test Signals
Useful signals include unit-style cursor arithmetic tests for wrap, backwards movement, full-buffer deltas, and large wrap cases; byte-order/layout checks for SMC-R and SMC-D CDC messages; integration tests for close predicate behavior; and cross-architecture builds for endian bitfields and atomic64/no-atomic64 cursor paths.
