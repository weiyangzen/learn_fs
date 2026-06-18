# sources/distributed-fs/ceph/src/mds/MDSCacheObject.h

## Purpose

`MDSCacheObject.h` declares the common base class for metadata objects held in the MDS cache. It provides shared state bits, reference pins, auth-pin interfaces, replica tracking, waiter tracking, formatter dumping, and abstract hooks for subclass-specific authority, locking, freezing, and ordering.

## Important APIs And Types

Shared pin constants include `PIN_REPLICATED`, `PIN_DIRTY`, `PIN_LOCK`, `PIN_REQUEST`, `PIN_WAITER`, `PIN_DIRTYSCATTERED`, `PIN_AUTHPIN`, `PIN_PTRWAITER`, `PIN_TEMPEXPORTING`, `PIN_CLIENTLEASE`, `PIN_DISCOVERBASE`, and `PIN_SCRUBQUEUE`. State bits include `STATE_AUTH`, `STATE_DIRTY`, `STATE_NOTIFYREF`, `STATE_REJOINING`, and `STATE_REJOINUNDEF`. Wait bits include `WAIT_ORDERED`, `WAIT_SINGLEAUTH`, and `WAIT_UNFREEZE`; `waitmask_t` is 128 bits to combine object and lock wait masks.

Core ref methods are `get`, `put`, `get_num_ref`, `first_get`, `last_put`, `bad_get`, `bad_put`, `_put`, and `print_pin_set`. Authority and auth-pin behavior is abstract through `authority`, `can_auth_pin`, `auth_pin`, `auth_unpin`, `is_frozen`, and `is_freezing`. Replica APIs include `add_replica`, `remove_replica`, `clear_replica_map`, `get_replicas`, `list_replicas`, `get_replica_nonce`, and `set_replica_nonce`.

Waiter APIs are `add_waiter`, `take_waiting`, `finish_waiting`, `is_waiter_for`, and `count_waiters`. Lock-related methods default to abort and must be implemented by subclasses that expose `SimpleLock` state.

## State And Persistence Behavior

This class is in-memory lifecycle infrastructure. Ref counts and pins gate cache trimming and deletion; replica maps describe which peers have copies; waiters hold contexts until object state changes. The class itself does not encode persistent metadata, but its state determines when persistent metadata can safely be mutated, journaled, expired, or dropped.

## Dependencies And Integration Points

The header depends on Ceph mempool containers, `mdstypes`, `elist`, `MDSContext`, rank types, and `Formatter`. It is inherited by object types that `MDCache` stores in `inode_map`, dirfrag structures, dentry structures, lock code, scrub queues, export/import code, and rejoin handling.

## Risks And Test Signals

This is a high-blast-radius base class. Incorrect pin accounting can create leaks or premature frees; invalid replica map transitions can break cache coherence; waiter masks must remain compatible with lock waiters above 64 bits. Tests should exercise ref debug maps, `STATE_NOTIFYREF` callbacks, replica first/last pin behavior, auth-pin refusal reasons, waiter ordering, and subclass lock-waiter integration.
