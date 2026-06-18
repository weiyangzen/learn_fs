# sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.h

Purpose: Declares WireGuard public-key and index lookup table structures and operations.

Important APIs and types: `struct pubkey_hashtable` contains an 11-bit hlist hash table, siphash key, and mutex. `struct index_hashtable` contains a 13-bit hlist hash table and spinlock. `enum index_hashtable_type` distinguishes handshake and keypair entries. `struct index_hashtable_entry` stores peer pointer, hlist node, type mask, and index. Declares alloc/add/remove/lookup/insert/replace functions.

Control flow: Header has no executable flow but defines the lookup entry embedded in Noise handshakes and keypairs.

State and persistence: Declares runtime lookup state only. Hash table size and entry type masks are protocol performance/lifetime parameters.

Dependencies and integration points: Includes message key sizes, kernel hashtable, mutex, and siphash headers. Used by device allocation, peer creation/removal, Noise, and receive.

Risks: Type masks must match lookup callers; table sizes and random indexes affect collision behavior; embedded entries require careful lifetime management.

Test signals: Compile coverage, public key lookup, index insert/replace/remove, and RCU lifetime tests under data/handshake traffic.
