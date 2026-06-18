# sources/distributed-fs/ceph-client/include/linux/dsa/ksz_common.h

## Purpose
This header contains common Microchip KSZ DSA tagger support for timestamp decoding, deferred transmission, hardware timestamp state callbacks, and skb control-block data.

## Important APIs, types, and functions
`KSZ_TSTAMP_SEC_MASK` and `KSZ_TSTAMP_NSEC_MASK` define the 2-bit seconds plus 30-bit nanoseconds timestamp format. `ksz_decode_tstamp()` converts that format to `ktime_t`. `struct ksz_deferred_xmit_work` stores DSA port, skb, and kthread work. `struct ksz_tagger_data` carries tagger callbacks. `struct ksz_skb_cb` stores clone, PTP type, correction-update flag, and timestamp. `KSZ_SKB_CB()` casts an skb control block, and `ksz_tagger_data()` returns `ds->tagger_data`.

## Control flow, state, and persistence
Deferred transmit state persists in `kthread_work` until executed. Per-packet timestamp state is stored in `skb->cb` and must survive through tagger transmit/completion handling. Hardware timestamp enable state is controlled through the tagger callback.

## Dependencies and integration points
It depends on DSA, skbuff, kthread work, bitfield helpers, and time conversion helpers. It integrates with KSZ switch taggers and PTP timestamping paths.

## Risks and test signals
Risks include misinterpreting the nonstandard timestamp layout, skb control-block collisions with other users, and missing deferred work cleanup on port teardown. Tests should validate timestamp conversion around second rollover, TX/RX PTP clone handling, and tagger callback presence.
