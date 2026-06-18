# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.h

Purpose: Debugfs state and lightweight counter helpers for the CW1200 driver.

Important APIs and types: `struct cw1200_debug_priv` stores a debugfs root dentry and counters for TX, aggregated TX/RX, multi-TX, cache misses, alignment fixes, TTL expirations, bursts, and block-ack stats. Declares `cw1200_debug_init` and `cw1200_debug_release`. Inline helpers increment counters from hot paths.

Control flow: Other modules call inline helpers at notable events, avoiding function-call overhead and centralizing counter names.

State and persistence: Counter state is per-device, in memory, and reset on driver reinitialization. No locking is used for increments, so values are diagnostic rather than strict accounting.

Dependencies and integration: Requires `struct cw1200_common` to hold `priv->debug`. Used by TX/RX, queue GC, BH burst paths, and debugfs rendering.

Risks: Inline helpers dereference `priv->debug`; they require debug initialization before use and no use after release. Unsynchronized increments can lose counts under concurrency.

Test signals: Build users with debugfs enabled/disabled configs and compare debugfs `status` counter movement during TX, RX, bursts, and queue TTL expiration.
