# sources/distributed-fs/ceph-client/net/rds/tcp_send.c

## Purpose
Implements the TCP transport's data transmit callback, TCP ACK interpretation, socket corking around batched sends, and write-space callback that drives ACK cleanup and send retry.

## Important APIs, Types, and Functions
Exports `rds_tcp_xmit_path_prepare()`, `rds_tcp_xmit_path_complete()`, `rds_tcp_xmit()`, `rds_tcp_is_acked()`, and `rds_tcp_write_space()`. Local helper `rds_tcp_sendmsg()` sends header bytes with `kernel_sendmsg()`.

## Control Flow
Before a send batch, `rds_tcp_xmit_path_prepare()` enables TCP cork; completion disables it. `rds_tcp_xmit()` records the TCP sequence corresponding to the last byte of the RDS message when starting a header, sets `RDS_MSG_HAS_ACK_SEQ`, sends remaining header bytes, then sends each data scatterlist with `MSG_SPLICE_PAGES`, `MSG_DONTWAIT`, `MSG_NOSIGNAL`, and `MSG_MORE` where appropriate. `-EAGAIN` is treated as temporary backpressure and converted to no-progress; other errors drop the path if it is still up. `rds_tcp_write_space()` records `snd_una`, drops RDS messages whose stored TCP ack sequence is before the unacked pointer, queues send work when space is available, chains to the original callback, and restores `SOCK_NOSPACE` so future TCP ACKs continue to trigger callbacks.

## State and Persistence
Uses TCP `write_seq` and `snd_una` to populate `t_last_sent_nxt`, `t_last_expected_una`, `t_last_seen_una`, and each message's `m_ack_seq`. It mutates socket flags and message flags but has no durable persistence.

## Dependencies and Integration
Depends on kernel TCP send APIs, splice-pages send support, RDS generic send partial-offset contract, RDS ACK cleanup, TCP stats counters, and callback state saved by `tcp.c`.

## Risks and Test Signals
Risks include 32-bit TCP sequence wrap comparisons, partial header/data accounting, page-backed send failures, repeated `SOCK_NOSPACE` callback dependence, and incorrectly treating fatal TCP errors as transient. Test signals are partial sends, `-EAGAIN` retries, ACK cleanup at sequence wrap, send-space wakeups under full sndbuf, retransmitted header flag setting, and path drop on non-EAGAIN send errors.
