# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.c

Purpose: manages OpenVPN per-peer crypto key-slot state, including primary/secondary slot reset, deletion, swapping, lookup, config reporting, and RCU-safe destruction.

Important APIs/types/functions: `ovpn_crypto_state_reset()` installs a new AEAD key slot. `ovpn_crypto_key_slot_delete()`, `ovpn_crypto_kill_key()`, and `ovpn_crypto_key_slots_swap()` mutate slot state. `ovpn_crypto_config_get()` reports non-secret config. `ovpn_crypto_state_release()` drops both slots during peer release. `ovpn_crypto_key_slot_release()` defers slot destruction through RCU.

Control flow: reset validates slot selector, creates a key slot through `ovpn_aead_crypto_key_slot_new()`, replaces the selected primary or secondary RCU pointer under spinlock, then puts the old slot. Delete and kill similarly replace matching slots with NULL and put old refs. Swap flips `primary_idx` under lock rather than moving pointers. Config get maps logical primary/secondary to physical index, dereferences under RCU, and reports cipher/key id.

State and persistence: `struct ovpn_crypto_state` contains two RCU slot pointers, a primary index, and a spinlock. Key slots are kref-counted and RCU-freed. State is volatile and owned by a peer.

Dependencies and integration: relies on AEAD slot creation/destruction in `crypto_aead.c`, packet ID state in slots, UAPI key slot/cipher enums, spinlocks, krefs, and RCU.

Risks: `ovpn_crypto_kill_key()` dereferences slot pointers before checking for NULL, so callers should ensure slots exist or this path may be fragile. Slot swap does not validate that a secondary key exists. Readers must hold refs via helper functions before async crypto use.

Test signals: install primary/secondary keys, delete each slot, swap slots, kill by key id, query missing and present configs, run concurrent encrypt/decrypt lookups under RCU, and release peers with active slot references.
