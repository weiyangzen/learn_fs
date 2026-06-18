# sources/distributed-fs/ceph-client/drivers/net/wireguard/peerlookup.c

Purpose: Implements WireGuard peer lookup tables: public-key-to-peer for configuration/handshake identity and random-index-to-handshake/keypair for incoming response/data packet dispatch.

Important APIs and functions: `wg_pubkey_hashtable_alloc()`, `wg_pubkey_hashtable_add()`, `wg_pubkey_hashtable_remove()`, and `wg_pubkey_hashtable_lookup()` manage siphash-keyed public key buckets. `wg_index_hashtable_alloc()`, `wg_index_hashtable_insert()`, `wg_index_hashtable_replace()`, `wg_index_hashtable_remove()`, and `wg_index_hashtable_lookup()` manage random 32-bit index entries for handshakes and keypairs.

Control flow: Public-key lookup hashes remote static keys under RCU and returns a strong peer reference. Index insertion removes any old entry, picks a random unused 32-bit index with unlocked search and locked double-check, then inserts under RCU. Session establishment replaces a handshake index with a keypair index. Lookup filters by type mask and returns the indexed entry plus a strong peer reference.

State and persistence: Maintains per-device hash arrays, random siphash keys, mutex/spinlock protection, RCU hlist nodes, and index values. State is runtime-only and rebuilt on device/peer creation.

Dependencies and integration points: Used by netlink peer lookup, Noise handshake consume/session begin, receive data packet dispatch, cookie consume paths, and peer teardown. Depends on siphash, hashtable macros, RCU BH read sections, and peer krefs.

Risks: Index uniqueness search is intentionally not constant time and relies on low occupancy. Replacement initializes the old hlist node, with comments acknowledging benign RCU lookup races that drop packets. Lookups must not return peers whose kref reached zero. Public-key hash access must stay synchronized with peer removal and static key updates.

Test signals: Many peer insertion/removal cycles, index collision stress, response/data lookup by index, stale index after peer removal, RCU/kref race tests, and public-key lookup after peer replacement.
