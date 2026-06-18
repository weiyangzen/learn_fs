# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.h

Purpose: declares ovpn crypto configuration and runtime key-slot structures plus inline helpers for RCU/kref-safe slot lookup.

Important APIs/types/functions: `struct ovpn_key_direction`, `ovpn_key_config`, and `ovpn_peer_key_reset` carry netlink-provided key settings. `struct ovpn_crypto_key_slot` stores AEAD transforms, nonce tails, packet ID send/receive state, refcount, and RCU head. `struct ovpn_crypto_state` stores two slots and primary index. Inline helpers initialize state, hold/put slots, find by key id, and get the primary slot.

Control flow: `ovpn_crypto_key_id_to_slot()` reads primary then secondary under RCU, validates key id, and kref-holds the slot unless its refcount is already zero. `ovpn_crypto_key_slot_primary()` fetches the current primary similarly. Mutation APIs are declared for `crypto.c`.

State and persistence: all state is per peer and volatile. Packet ID state is cacheline-aligned to reduce contention between transmit and receive.

Dependencies and integration: includes packet ID and protocol definitions, kernel kref/RCU patterns, crypto AEAD handles, and UAPI ovpn enums.

Risks: callers must put held slots. The primary index and slot pointers are read locklessly under RCU; writers must use the spinlock and RCU replacement helpers. Key material pointers in config are input views, not owned by this header.

Test signals: build with lockdep/RCU diagnostics, exercise slot lookup under concurrent reset/delete/swap, ensure missing key ids return NULL, and check reference balancing through async crypto completions.
