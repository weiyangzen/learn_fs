# sources/distributed-fs/ceph-client/net/tipc/crypto.c

## Purpose

`crypto.c` implements TIPC packet confidentiality/integrity, key lifecycle, session-key distribution, and crypto diagnostics for `CONFIG_TIPC_CRYPTO`. It wraps TIPC v2 packets in the encrypted header defined by `crypto.h`, encrypts/decrypts them with AEAD `gcm(aes)`, manages per-net TX crypto state and per-peer RX crypto state, and coordinates cluster-key and per-node-key operation.

## Important APIs, Types, and Functions

The key internal objects are `struct tipc_key`, `struct tipc_tfm`, `struct tipc_aead`, `struct tipc_crypto_stats`, and `struct tipc_crypto`. `struct tipc_crypto` owns RCU-protected AEAD slots `aead[0..3]`, pending/active/passive key state, key generation, delayed work, per-CPU stats, per-peer TX sequence state, peer RX active-key tracking, and flags such as `working`, `key_master`, `legacy_user`, and `nokey`. Public entry points include `tipc_crypto_start()`, `tipc_crypto_stop()`, `tipc_crypto_timeout()`, `tipc_crypto_xmit()`, `tipc_crypto_rcv()`, `tipc_crypto_key_init()`, `tipc_crypto_key_flush()`, `tipc_crypto_key_distr()`, `tipc_crypto_msg_rcv()`, `tipc_crypto_rekeying_sched()`, `tipc_aead_key_validate()`, and `tipc_ehdr_validate()`.

AEAD helpers validate `gcm(aes)` keys, allocate one or more crypto transforms up to `sysctl_tipc_max_tfms`, rotate per-CPU transform selection, build IVs from salt plus sequence number, and handle synchronous or async crypto callbacks. Key helpers attach, flush, align, pick, clone, revoke, distribute, receive, and activate keys.

## Control Flow

Transmit starts in `tipc_crypto_xmit()`. If TX crypto is inactive the skb is left unchanged. Otherwise it selects a key in pending/master/active preference order, optionally clones probing or grace-period messages, builds `struct tipc_ehdr`, encrypts the original TIPC header and payload, and returns either an encrypted skb or async ownership. `tipc_aead_encrypt_done()` sends or frees the skb after async completion.

Receive starts in `tipc_crypto_rcv()`. It reads the encrypted header's TX key, finds a matching per-peer RX key, attempts RX key slot alignment when a peer rejoined with a shifted key index, or falls back to local TX cluster keys for bootstrap/decryption of unknown peers. `tipc_crypto_rcv_complete()` strips the encryption header and tag, validates the inner TIPC message, marks the skb decrypted, and calls `tipc_crypto_key_synch()` to update peer RX-active tracking and key-distribution needs.

Key distribution uses `MSG_CRYPTO/KEY_DISTR_MSG`. TX delayed work generates a fresh session key from the current template, attaches it as pending, distributes it via unicast or broadcast, and reschedules rekeying. RX delayed work sends a key to a peer that lacks one and attaches a received session key when possible.

## State and Persistence Behavior

State is in memory only: per-net TX crypto hangs off `tipc_net`, while per-peer RX crypto hangs off `tipc_node`. AEAD slots are RCU-protected and refcounted; key material is duplicated with sensitive allocation and freed with `kfree_sensitive()`. Key state persists across packets as pending/active/passive slots, generation counters, sequence counters, user counts, and timers. `tipc_crypto_timeout()` advances pending keys to active, retires passive keys, clears legacy grace state, and handles debug command dispatch through the `max_tfms` sysctl escape path.

## Dependencies and Integration Points

The file depends on Linux crypto AEAD/RNG APIs, skb scatter-gather helpers, RCU/refcounting, delayed workqueues, per-CPU stats, TIPC node/bearer/message helpers, broadcast transmit, and net namespace lifetime management. It integrates with link receive in `link.c` for `MSG_CRYPTO`, with netlink/sysctl configuration for keys and rekeying, with `tipc_node` for per-peer RX crypto, and with bearer media send callbacks for async encryption completion.

## Risks and Edge Cases

This is security-sensitive code. Risks include nonce reuse on sequence wrap, incorrect key slot activation, RCU/refcount lifetime mistakes, failure to clear sensitive key material, peer bootstrap using TX cluster-key fallback, and async completion racing bearer/net namespace teardown. The pending/active/passive state machine depends on user counts and jiffies thresholds; small ordering mistakes can keep dead keys alive or revoke live ones. `sysctl_tipc_max_tfms` has a dual role as TFM limit and debug command trigger above `TIPC_MAX_TFMS_LIM`, which is easy to misuse.

## Test Signals

Useful signals include builds with `CONFIG_TIPC_CRYPTO`, netlink key validation failures for wrong algorithm/key length, packet traces showing `MSG_CRYPTO` distribution and encrypted LINK_CONFIG/LINK_PROTOCOL traffic, per-CPU crypto stats printed by debug command `0xfff1`, rekey interval tests, peer restart tests that force key-slot alignment, and namespace teardown tests while async crypto operations are outstanding.
