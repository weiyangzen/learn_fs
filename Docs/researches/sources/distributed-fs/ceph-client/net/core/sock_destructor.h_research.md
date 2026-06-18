# sources/distributed-fs/ceph-client/net/core/sock_destructor.h

## Purpose
This small internal header centralizes the predicate for recognizing skb destructors that account against socket write memory. It lets code distinguish skbs whose destructor releases `sk_wmem_alloc` from other skb owner/destructor styles.

## APIs, Types, and Functions
The only API is `is_skb_wmem(const struct sk_buff *skb)`. It returns true when `skb->destructor` is `sock_wfree`, `__sock_wfree`, or, with `CONFIG_INET`, `tcp_wfree`. The header includes `<net/tcp.h>` because `tcp_wfree` is part of the predicate when INET is enabled.

## Control Flow, State, and Persistence
There is no state. The inline function performs direct function-pointer comparisons and is compiled into callers.

## Dependencies and Integration
It depends on socket skb destructor functions from `sock.c` and TCP write destructor support. It is an integration point for cleanup/debug logic that needs to classify write-owned skbs without duplicating destructor knowledge.

## Risks and Test Signals
The main risk is drift: adding a new write-memory destructor without updating this predicate can make diagnostics or cleanup logic misclassify skbs. Build coverage across `CONFIG_INET=y/m/n`, TCP transmit tests, and leak/debug paths that consume `is_skb_wmem()` are the relevant signals.
