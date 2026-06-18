# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_common.h

## Purpose
This header provides common conntrack kernel definitions: statistics, pointer tagging masks, the generic conntrack reference object, and lightweight get/put helpers.

## Important APIs, Types, and Functions
`struct ip_conntrack_stat` tracks counters for found, invalid, insert, insert failure, clash resolution, drops, early drops, errors, expectation lifecycle, search restarts, and long chains. `NFCT_INFOMASK` and `NFCT_PTRMASK` reserve low bits in conntrack skb pointers for info tags. `struct nf_conntrack` wraps `refcount_t use`. `nf_conntrack_destroy()` is declared, while `nf_conntrack_put()` and `nf_conntrack_get()` manage references.

## Control Flow
Users increment refs when attaching or sharing conntrack objects. `nf_conntrack_put()` decrements and calls `nf_conntrack_destroy()` when the refcount reaches zero. Pointer masks let skb metadata combine a pointer with small state flags.

## State and Persistence
Conntrack objects and stats are in-memory kernel state. This header does not define durable storage. Refcounts determine object lifetime.

## Dependencies and Integration Points
It depends on `refcount.h` and uapi conntrack common definitions. It integrates with skb conntrack attachment, netfilter conntrack core, and modules that want put/get without depending directly on full conntrack internals.

## Risks
Incorrect masking can corrupt tagged pointers. Refcount leaks or double puts can leak or destroy active conntrack objects. Stats updates need appropriate per-CPU or locking discipline in implementation files.

## Test Signals
Conntrack attach/detach lifetime tests, refcount saturation/debug checks, skb pointer-tag encode/decode tests, namespace teardown, and stat counter validation under connection churn.
