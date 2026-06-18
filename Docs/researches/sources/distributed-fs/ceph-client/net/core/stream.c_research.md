# sources/distributed-fs/ceph-client/net/core/stream.c

## Purpose
This file provides generic stream-socket wait, wakeup, error, and queue cleanup helpers shared by stream protocols. It factors behavior common to TCP-like sendmsg/recvmsg implementations.

## APIs, Types, and Functions
Exported functions are `sk_stream_write_space()`, `sk_stream_wait_connect()`, `sk_stream_wait_close()`, `sk_stream_wait_memory()`, `sk_stream_error()`, and `sk_stream_kill_queues()`. The internal helper `sk_stream_closing()` checks FIN/closing states.

## Control Flow, State, and Persistence
`sk_stream_write_space()` wakes poll and async waiters when send memory becomes writable and the socket is not shut down. `sk_stream_wait_connect()` loops while the socket is in SYN states, checking errors, timeout, and signals, and increments `sk_write_pending` while sleeping. `sk_stream_wait_memory()` waits for send memory with `SOCKWQ_ASYNC_NOSPACE` and `SOCK_NOSPACE` set so later ACK-driven space changes generate wakeups; it also uses a randomized VM wait interval when memory is technically free to moderate pressure. `sk_stream_wait_close()` waits for closing states to drain. `sk_stream_kill_queues()` purges receive and error queues, asserts write queue/backlog invariants, and performs final memory reclaim.

## Dependencies and Integration
Depends on socket wait queues, TCP state bits, signal handling, poll flags, random numbers, skb queue helpers, and memory reclaim helpers from `sock.c`. Protocols call these helpers while holding the socket lock where documented.

## Risks and Test Signals
Risks are lost wakeups, incorrect timeout accounting, wrong signal-to-errno conversion, sleeping after `SOCK_DEAD`, and queue cleanup while packets can still arrive. Test signals include nonblocking connect/write tests, signal interruption tests, poll/epoll wakeup behavior, TCP close linger/drain tests, and lockdep around wait paths.
