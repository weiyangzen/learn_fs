# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.h

Purpose: Declares the optional dynamic ACK timeout data structures and entry points used by ath9k when `CONFIG_ATH9K_DYNACK` is enabled. The feature samples transmit and ACK timestamps to adapt ACK timeout values for long-distance links.

Important APIs and types: `ATH_DYN_BUF` fixes the TX and ACK timestamp ring depth at 64 entries. `struct ath_dyn_rxbuf` stores ACK receive timestamps; `struct ath_dyn_txbuf` stores TX timestamp/duration records plus destination/source address pairs; `struct ath_dynack` is the per-hardware state block containing enable state, current timeout, node list, spinlock, and both rings. Public hooks are `ath_dynack_init()`, `ath_dynack_reset()`, node init/deinit, `ath_dynack_sample_ack_ts()`, and `ath_dynack_sample_tx_ts()`. When the config option is disabled, most hooks compile to no-op inline stubs.

Control flow: TX completion and ACK receive paths call the sampling hooks, while node lifecycle calls maintain the dynamic ACK peer list. The implementation is elsewhere, but this header makes the call sites compile regardless of feature configuration.

State and persistence: State is runtime-only under `struct ath_hw`. Ring heads/tails and timestamp buffers are protected by `qlock`; peer state is tracked through a linked list of `ath_node` entries. There is no durable persistence.

Dependencies and integration points: Depends on ath9k hardware/node types, socket buffers, TX status, mac80211 station pointers, list heads, and spinlocks. It integrates with TX status handling, RX ACK observation, and hardware ACK timeout programming.

Risks: Ring depth and timestamp wrap handling are central to correctness. Compile-time stubs mean callers must not rely on side effects when dynamic ACK is disabled. Lock ordering around timestamp queues and node teardown must avoid use-after-free during station removal.

Test signals: Build with and without `CONFIG_ATH9K_DYNACK`, associate/disassociate stations while traffic is active, run long-distance traffic that triggers timeout adaptation, and verify no timestamp queue races under concurrent TX/RX.
