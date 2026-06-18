# sources/distributed-fs/ceph-client/net/rds/bind.c

## Purpose
`bind.c` implements RDS local address binding and bound-socket lookup. It validates IPv4/IPv6 addresses, selects or verifies a transport, allocates ports, and maintains a hash table keyed by local address, port, and IPv6 scope id.

## Important APIs, Types, And Functions
Primary APIs are `rds_find_bound()`, `rds_remove_bound()`, `rds_bind()`, `rds_bind_lock_init()`, and `rds_bind_lock_destroy()`. Helpers include `__rds_create_bind_key()` and `rds_add_bound()`. The central data structure is `bind_hash_table`, an `rhashtable` keyed by `rs_bound_key`.

## Control Flow
`rds_bind()` validates the sockaddr family and rejects wildcard, broadcast, and multicast addresses. IPv4 addresses are stored as IPv4-mapped IPv6 addresses. IPv6 addresses must be unicast or valid mapped IPv4; link-local addresses require a nonzero scope id. Under the socket lock it rejects rebinding, checks scope consistency with any connected peer, then either validates a preselected transport via `laddr_check()` or asks for a preferred transport. It sets `SOCK_RCU_FREE` and calls `rds_add_bound()`.

`rds_add_bound()` either uses a requested nonzero port or randomly starts an ephemeral scan, skipping port 0 and `RDS_FLAG_PROBE_PORT`. It checks for existing keys, copies address/key state into the socket, takes a socket ref, inserts into the rhashtable, and records scope id. Lookup uses RCU and increments the socket ref only if the socket is not dead and refcount is nonzero. Removal erases the hash entry, drops the bind ref, and resets the bound address to any.

## State And Persistence
State is the global rhashtable and per-socket bound key/address/port/scope/hash seed. Bind entries hold a socket reference until removal. No disk persistence exists.

## Dependencies And Integration Points
The file integrates with transport selection (`rds_trans_get_preferred`, `laddr_check`), socket lifetime, receive-path lookup, IPv6 address classification, and RCU/rhashtable synchronization.

## Risks
Port allocation can loop over a large range under contention. Insert failure after socket state mutation must reset address and ref. Lookup races with release are handled with `SOCK_DEAD` and refcount increment; changes there could reintroduce UAF risk. Scope-id handling is essential for IPv6 link-local correctness.

## Test Signals
Tests should cover invalid address forms, link-local scope requirements, rebinding rejection, requested-port collisions, ephemeral allocation, probe-port rejection, transport unavailable errors, preselected transport `laddr_check` failure, lookup during release, and removal idempotence for unbound sockets.
