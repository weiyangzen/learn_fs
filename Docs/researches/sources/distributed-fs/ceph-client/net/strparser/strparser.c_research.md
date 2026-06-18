# sources/distributed-fs/ceph-client/net/strparser/strparser.c

Purpose: Implements the generic stream parser framework that converts a byte stream or supplied skb fragments into complete message skbs according to upper-layer callbacks.

Important APIs/types/functions: Exported APIs are `strp_init()`, `strp_process()`, `strp_data_ready()`, `strp_unpause()`, `strp_done()`, `strp_stop()`, and `strp_check_rcv()`. Core internals include `__strp_recv()`, `strp_read_sock()`, `strp_parser_err()`, `strp_abort_strp()`, `strp_msg_timeout()`, and workqueue callbacks. `strp_wq` is the single-thread workqueue used for deferred parsing.

Control flow: `strp_init()` validates callbacks and sets default socket lock/unlock and abort/read_done handlers. In socket mode, `strp_data_ready()` either parses immediately under lower socket conditions or queues work if the socket is owned by user context or memory pressure occurs. `strp_read_sock()` pulls data through either callback or socket `read_sock`, which calls `__strp_recv()`. The parser clones/appends skbs, asks `parse_msg` for full length, starts a timeout while waiting for header/body, rejects oversized or bad lengths, and calls `rcv_msg` when a complete message is assembled. General mode uses `strp_process()` directly on supplied skb ranges.

State and persistence behavior: `struct strparser` tracks stopped/paused flags, current `skb_head`, append pointer, needed bytes, timeout work, parser work, stats, callbacks, and lower socket pointer. State is in-memory and must be stopped before `strp_done()` cancels work and frees partial skb chains.

Dependencies and integration points: Depends on skb control-buffer layout from `include/net/strparser.h`, socket `peek_len`/`read_sock`, workqueues, timers, and upper-layer parse/receive callbacks. Used by stream protocols that need message framing over TCP-like transports.

Risks and test signals: Risks include skb frag-list ownership mistakes, parse callback returning inconsistent lengths, timeout races, pause/unpause memory ordering, socket lock ordering, and skb `cb[]` overlay size. Test partial header/body delivery, multiple messages in one skb, message spanning fragments, oversized/bad lengths, pause/unpause, timeout abort, no-socket general mode, memory allocation failures, and `BUILD_BUG_ON` for control-buffer size.
