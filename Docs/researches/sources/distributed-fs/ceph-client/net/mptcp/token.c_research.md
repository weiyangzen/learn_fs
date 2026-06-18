# sources/distributed-fs/ceph-client/net/mptcp/token.c

## Purpose
This file owns the global MPTCP token registry. It maps 32-bit tokens to either pending passive MP_CAPABLE requests or established `struct mptcp_sock` objects so MP_JOIN SYNs and diagnostic iteration can locate the correct MPTCP connection.

## APIs, Types, and Functions
The central type is `struct token_bucket`, containing a spinlock, bounded chain length, a request chain, and a socket chain. Public APIs are `mptcp_token_new_request()`, `mptcp_token_new_connect()`, `mptcp_token_accept()`, `mptcp_token_exists()`, `mptcp_token_get_sock()`, `mptcp_token_iter_next()`, `mptcp_token_destroy_request()`, `mptcp_token_destroy()`, and `mptcp_token_init()`. Helpers `__token_lookup_req()`, `__token_lookup_msk()`, `__token_bucket_busy()`, and `mptcp_crypto_key_gen_sha()` implement hashing and collision checks.

## Control Flow
Passive MP_CAPABLE handling calculates token and IDSN from a previously generated local key and inserts the request into the bucket's request hlist if the token is nonzero, unique, and the bucket chain has fewer than `TOKEN_MAX_CHAIN_LEN` entries. Active MP_CAPABLE handling generates random keys until a usable token is found, stores the token into the parent MPTCP socket, links the socket in the msk chain, and increments protocol in-use accounting. On accept, `mptcp_token_accept()` removes the request node and inserts the fully cloned MPTCP socket under the same token.

Lookup uses RCU and nulls hlist traversal. `mptcp_token_get_sock()` restricts matches to the caller's network namespace and takes a reference only if `sk_refcnt` is nonzero, then revalidates token and namespace after acquiring the ref. Iteration walks buckets and per-bucket positions for proc/diagnostic style consumers. Destroy paths remove either request nodes or socket nodes under bucket lock and maintain chain length and protocol accounting.

## State and Persistence
The registry is a boot-time `alloc_large_system_hash()` allocation sized roughly by memory and capped at 64K buckets. Each bucket stores pending requests and established MPTCP sockets until request destruction, accept transition, or MPTCP socket teardown. Per-socket token fields are cleared on destroy.

## Dependencies and Integration
Dependencies include MPTCP crypto key hashing, request and socket context accessors from `protocol.h`, RCU nulls lists, spinlocks, network namespace checks, random bytes, and socket protocol accounting. `subflow.c` uses this file for MP_CAPABLE token creation, MP_JOIN token lookup, syncookie uniqueness checks, and request cleanup.

## Risks
Token collisions intentionally fail after bounded retries or trigger TCP fallback on passive open. Chain length limiting can reject connections under adversarial token distribution. Lookup correctness depends on RCU/nulls retry semantics and reference revalidation. Destroy paths warn if registry state does not match expected ownership, which would imply a token lifecycle bug.

## Test Signals
`token_test.c` covers request insertion, active connect insertion, accept transition, destroy no-op behavior after accept, and zero-ref lookup races. Broader signals include MP_JOIN success under concurrent connects, namespace isolation, collision retry behavior, and absence of leaked protocol in-use counts.
