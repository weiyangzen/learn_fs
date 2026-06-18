# sources/distributed-fs/ceph-client/include/net/request_sock.h

Purpose: declares generic request socket infrastructure for pending connection requests, SYN-ACK/reset callbacks, accept queues, Fast Open queueing, and skb socket stealing.

Important APIs and types: `struct request_sock_ops` supplies family, size/slab metadata, ACK/reset/destructor callbacks. `struct request_sock` overlays `sock_common` fields, tracks retransmits/timeouts, syncookie status, timestamp, timer, ops, child/listener pointers, saved SYN, security IDs, and timeout. `struct fastopen_queue` tracks TFO pending/RST request lists, lock, qlen/max, and context. `struct request_sock_queue` stores accept FIFO, qlen/young counts, defer-accept flag, flood warning, and TFO queue. Helpers convert between sock/request_sock, steal sockets from skbs, refcount/free requests, remove accept entries, account qlen/young, and clamp SYNACK window.

Control flow: listening protocols allocate request sockets on SYN, retransmit SYNACK by timer, move established children to accept queue, optionally co-own TFO requests with child sockets, and free requests by refcount.

State and persistence: all state is listener/request runtime state; saved SYN is in-memory only.

Dependencies and integration points: depends on sock core, timers, slabs, refcounts, TCP states, SYN cookies, security labels, Fast Open, and reset reason enum.

Risks and test signals: risks include request refcount underflow, stealing prefetched syncookie sockets incorrectly, accept queue races, TFO listener/child lifetime, qlen/young imbalance, and window-scale hardening regressions. Test SYN/SYNACK/ACK, retransmits/timeouts, syncookies, TFO accept/remove/reset, accept queue FIFO, listener close, and skb_steal_sock BPF-prefetched cases.
