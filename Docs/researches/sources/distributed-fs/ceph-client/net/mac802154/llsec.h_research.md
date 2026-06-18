# sources/distributed-fs/ceph-client/net/mac802154/llsec.h

Purpose: declares the private mac802154 link-layer security model used by `llsec.c` and the public entry points used by the rest of mac802154.

Important types and APIs: `struct mac802154_llsec_key` wraps the generic IEEE key with AEAD/CTR transform handles and a `kref`. `struct mac802154_llsec_device` wraps per-peer state, hash nodes, an RCU head, and a spinlock for frame-counter/key-list mutation. `struct mac802154_llsec` owns current parameters, the exported table, short/long-address hash tables, and an rwlock for parameters. The function declarations cover parameter, key, device, device-key, security-level, encrypt, and decrypt operations.

Control flow and state: the header makes ownership boundaries explicit: table lists are visible through `ieee802154_llsec_table`, while implementation-only wrappers carry locks, hashes, crypto transforms, and RCU lifetime fields. Persistent runtime state is in memory only and scoped to an `ieee802154_sub_if_data` security object.

Dependencies and integration: includes Linux hash/kref/spinlock facilities and IEEE 802.15.4 netdev types. `mib.c` and `mac_cmd.c` call these APIs; `tx.c`/`rx.c` call encrypt/decrypt.

Risks and test signals: callers need to respect the locking implied by `struct mac802154_llsec` because most table walkers are RCU-aware but not globally serialized in the header contract. Tests should verify exported APIs keep generic table pointers valid while preserving hidden wrapper lifetime.
