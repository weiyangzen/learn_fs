# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.h

Purpose: declares the AEAD crypto operations used by ovpn transmit/receive and crypto state management.

Important APIs/types/functions: exports `ovpn_aead_encrypt()`, `ovpn_aead_decrypt()`, `ovpn_aead_crypto_key_slot_new()`, `ovpn_aead_crypto_key_slot_destroy()`, and `ovpn_aead_crypto_alg()`.

Control flow: this header has no runtime logic; it defines the interface between generic key-slot management in `crypto.c`, packet I/O in `io.c`, and AEAD implementation in `crypto_aead.c`.

State and persistence: no direct state; all state is passed through `struct ovpn_peer`, `struct ovpn_crypto_key_slot`, and `struct sk_buff`.

Dependencies and integration: includes `crypto.h`, kernel integer types, and skbuff declarations. It is a narrow boundary around the AEAD implementation.

Risks: prototypes expose async crypto semantics through callbacks hidden in `crypto_aead.c`; callers must set up skb control block expectations and hold peer/key references as done in `io.c`.

Test signals: compile interface users, verify encrypt/decrypt callers link, and run key-slot creation/destruction coverage for supported and unsupported algorithms.
