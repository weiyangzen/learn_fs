# sources/distributed-fs/ceph-client/net/mptcp/syncookies.c

## Purpose
This file provides best-effort server-side state recovery for MP_JOIN requests when TCP syncookies are used. MP_CAPABLE cookie ACKs carry enough MPTCP material to rebuild request state, but MP_JOIN cookie ACKs do not carry the original token or server nonce, so this file stores a small hash-indexed side table for later reconstruction.

## APIs, Types, and Functions
`struct join_entry` stores token, remote nonce, local nonce, remote join ID, local ID, backup bit, and a valid flag. `COOKIE_JOIN_SLOTS` fixes the table at 1024 entries. Public functions are `subflow_init_req_cookie_join_save()`, `mptcp_token_join_cookie_init_state()`, and `mptcp_join_cookie_init()`. Helpers include `mptcp_join_entry_hash()` and `mptcp_join_store_state()`.

## Control Flow
On an MP_JOIN SYN that has passed token lookup and policy checks but is handled through syncookies, `subflow_init_req_cookie_join_save()` hashes the skb tuple, sequence, net namespace mix, and a random secret to pick a table slot, then stores the request's JOIN state under that slot lock. Later, after TCP validates the cookie ACK, `mptcp_token_join_cookie_init_state()` hashes the ACK in the same way, consumes the slot by clearing `valid`, looks up the saved token with `mptcp_token_get_sock()`, and repopulates the new request socket before later HMAC validation in `subflow.c`.

## State and Persistence
State is only the global `join_entries[]` table and one spinlock per slot. Entries have no timeout and are invalidated only when a matching cookie ACK consumes them or another SYN overwrites the slot. The socket reference returned by `mptcp_token_get_sock()` is stored into `subflow_req->msk` for the normal subflow accept path.

## Dependencies and Integration
The file depends on TCP skb sequence metadata, TCP headers, `jhash_3words()`, `net_hash_mix()`, per-net randomization, MPTCP request context definitions, and token lookup. It is called by `subflow_check_req()` while preparing syncookie MP_JOIN SYN/ACKs and by `mptcp_subflow_init_cookie_req()` while rebuilding request state from the cookie ACK.

## Risks
The table is intentionally lossy: slot collisions, cross-CPU races, ACKs arriving after overwrite, or any mismatch in SYN/ACK hash inputs cause JOIN failure. There is no expiration or namespace-specific table separation beyond the hash input. A valid slot is cleared before token lookup completes, so a racing duplicate ACK will not reuse it.

## Test Signals
Useful tests force TCP syncookie mode and attempt MP_JOIN joins, including collision-like high-rate joins, invalid token joins, backup/id propagation, and namespace isolation. Failure should appear as refused MP_JOIN rather than memory corruption or stale socket attachment.
