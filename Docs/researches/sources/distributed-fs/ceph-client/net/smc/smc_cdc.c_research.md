# sources/distributed-fs/ceph-client/net/smc/smc_cdc.c

## Purpose
`smc_cdc.c` implements Connection Data Control processing for SMC. CDC messages carry producer and consumer cursors, flow-control flags, urgent-data indications, close/abort bits, and failover validation state. The file handles CDC send completion, CDC send construction for SMC-R and SMC-D, pending WR accounting, receive-side cursor updates, wakeups, close scheduling, failover validation, SMC-D tasklet receive, and registration of the CDC work-request receive handler.

## Important APIs, Types, And Functions
Public functions include `smc_cdc_get_free_slot()`, `smc_cdc_msg_send()`, `smcr_cdc_msg_send_validation()`, `smc_cdc_get_slot_and_msg_send()`, `smc_cdc_wait_pend_tx_wr()`, `smcd_cdc_msg_send()`, `smcd_cdc_rx_init()`, and `smc_cdc_init()`. Key internal helpers are `smc_cdc_tx_handler()`, `smc_cdc_add_pending_send()`, `smcr_cdc_get_slot_and_msg_send()`, `smc_cdc_handle_urg_data_arrival()`, `smc_cdc_msg_validate()`, `smc_cdc_msg_recv_action()`, `smc_cdc_msg_recv()`, `smcd_cdc_rx_tsklet()`, and `smc_cdc_rx_handler()`.

## Control Flow
On SMC-R transmit, callers obtain a WR slot with `smc_cdc_get_free_slot()`, fill it through `smc_cdc_msg_send()`, increment `cdc_pend_tx_wr`, and post it via `smc_wr_tx_send()`. Completion enters `smc_cdc_tx_handler()`, which advances confirmed TX cursors, frees local send-buffer space, records completed CDC sequence, decrements pending WRs, wakes waiters, and triggers pending TX if the last CDC completed. SMC-D bypasses WR slots: `smcd_cdc_msg_send()` writes a CDC header into peer DMB memory and updates local confirmed receive cursor and local send-buffer space unless nocopy DMB requires waiting for peer consumption.

Receive starts from `smc_cdc_rx_handler()` for SMC-R work completions or `smcd_cdc_rx_tsklet()` for SMC-D DMB notifications. The handler validates length/type, finds the connection by alert token in the link group, drops stale sequence numbers, handles failover validation, then calls `smc_cdc_msg_recv_action()`. That action imports peer cursors, increases peer RMB space when the peer consumes data, increases local `bytes_to_rcv` when the peer produces data, handles urgent data, wakes readers/writers, schedules TX when consumer updates request more sends, marks reset on peer abort, and queues close work for close or send-done flags.

## State And Persistence
CDC state persists in `struct smc_connection`: `local_tx_ctrl`, `local_rx_ctrl`, `tx_curs_sent`, `tx_curs_fin`, `local_tx_ctrl_fin`, `rx_curs_confirmed`, `peer_rmbe_space`, `sndbuf_space`, `bytes_to_rcv`, `tx_cdc_seq`, `tx_cdc_seq_fin`, `cdc_pend_tx_wr`, `cdc_pend_tx_wq`, urgent fields, `out_of_sync`, and `tx_in_release_sock`. Pending send-private state is stored in `struct smc_cdc_tx_pend` until completion.

## Dependencies And Integration Points
The file depends on SMC WR posting and receive-handler registration, TX pending logic, RX wakeups, close workqueue handling, SMC-D ISM write and nocopy capability, link-group connection lookup, socket wait queues, and RDMA completion status. It is the flow-control bridge between `smc_tx.c`, `smc_rx.c`, `smc_close.c`, and lower SMC-R/SMC-D transports.

## Risks And Edge Cases
Pending WR counters must stay balanced on post failures, killed connections, and failover validation sends. Cursor import rejects backwards movement but must tolerate wrap semantics. SMC-D nocopy changes when send-buffer space is released, relying on peer consumer updates. `sock_owned_by_user()` paths defer TX to `release_cb()` to avoid socket-lock recursion. Out-of-sync failover validation schedules abort work and changes the connection link under `send_lock`.

## Test Signals
High-value tests include CDC sequence wrap and stale-message drops, peer consumer updates freeing send space, producer updates waking readers, `cons_curs_upd_req` causing TX, urgent-data inline and out-of-band behavior, peer done/closed/abort close scheduling, killed connection send failure, SMC-D nocopy and non-nocopy send-space release, failover validation handling, pending WR wait wakeups, and KCSAN/lockdep coverage around cursor and `send_lock` updates.
