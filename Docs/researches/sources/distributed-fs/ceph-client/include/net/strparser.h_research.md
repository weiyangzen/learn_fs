<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/strparser.h -->
# sources/distributed-fs/ceph-client/include/net/strparser.h

Purpose: Defines the stream parser framework used by TCP upper layers such as TLS and BPF stream parsers to split a byte stream into message skbs.

Important APIs/types/functions: `struct strp_stats` and `struct strp_aggr_stats` track message, byte, memory, header, size, timeout, abort, and interrupt counters. `struct strp_callbacks` supplies parser operations: `parse_msg`, `rcv_msg`, `read_sock`, `read_sock_done`, `abort_parser`, and optional lock/unlock callbacks. `struct strp_msg` and `_strp_msg` overlay skb control buffer state with full length, offset, and accumulated length. `struct sk_skb_cb` reserves skb `cb[]` space for private parser state, TLS control, and BPF temporary register. `struct strparser` stores the attached sock, paused/stopped/aborted flags, current skb chain, needed bytes, work items, stats, and callbacks.

Control flow: `strp_init()` attaches the parser to a socket. Data-ready paths call `strp_data_ready()` or `strp_check_rcv()`, which schedule parser work and use the callback `read_sock` to pull bytes. `parse_msg` determines message length; when enough bytes are accumulated, `rcv_msg` receives the completed skb. `strp_pause()` and `strp_unpause()` throttle delivery. `strp_stop()` and `strp_done()` shut down work and timers.

State and persistence behavior: Parser state is in memory and tied to a lower socket. `paused`, `stopped`, `aborted`, and interrupt flags gate processing. Delayed work implements message timeout behavior, and statistics can be saved or aggregated when a parser is detached.

Dependencies/integration points: Depends on `skbuff.h` and `sock.h`, and is used by TCP BPF stream parser paths declared from `tcp.h` plus TLS receive processing.

Risks: skb control-buffer overlays must fit with other users. Parser callbacks are called with the attached socket lock held, so lock inversion is possible. Incorrect `full_len` or `need_bytes` handling can split messages incorrectly, leak skbs, or overrun maximum message size.

Test signals: TLS and BPF stream parser selftests, partial-header/body delivery, pause/unpause, timeout/abort paths, memory allocation failure, oversized-message rejection, and skb `cb[]` size build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/strparser.h -->
