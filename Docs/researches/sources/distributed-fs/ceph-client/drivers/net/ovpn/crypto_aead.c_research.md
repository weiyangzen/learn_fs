# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.c

Purpose: implements OpenVPN AEAD encryption/decryption for data channel packets and creates/destroys AEAD-backed crypto key slots.

Important APIs/types/functions: `ovpn_aead_encrypt()` encapsulates and encrypts skb payloads. `ovpn_aead_decrypt()` authenticates and decrypts received packets. `ovpn_aead_crypto_key_slot_new()` allocates transforms and initializes nonce/packet-id state. `ovpn_aead_crypto_key_slot_destroy()` frees transforms. Helpers compute temporary buffer layout for IV, request, and scatterlist.

Control flow: encryption ensures headroom and writable skb data, allocates an atomic temporary crypto buffer, maps payload into scatterlist, reserves auth tag, obtains next packet ID, builds nonce from packet ID and transmit nonce tail, prepends wire nonce and DATA_V2 opcode, sets AAD, and submits `crypto_aead_encrypt()` with `ovpn_encrypt_post` callback. Decryption validates packet length, pulls AAD/tag, maps payload and tag, reconstructs IV from wire nonce plus receive nonce tail, sets AAD, and submits decrypt with `ovpn_decrypt_post`.

State and persistence: key slots hold encrypt/decrypt `crypto_aead` transforms, nonce tails, key id, packet ID xmit/recv replay state, refcount, and RCU head. Per-packet temporary buffers are recorded in skb control block and freed by post callbacks.

Dependencies and integration: uses Linux crypto AEAD API, skbuff scatterlist helpers, ovpn protocol constants, packet ID helpers, peer state, and async completion functions in `io.c`. Supported algorithms are AES-GCM and ChaCha20-Poly1305.

Risks: error paths after temporary allocation must be paired with post-callback cleanup; early returns from mapping or packet-id errors leave cleanup responsibility delicate. Nonce exhaustion returns `-ERANGE` and higher layers kill the key. AEAD IV size is assumed to be 12 bytes.

Test signals: encrypt/decrypt valid packets with both algorithms, reject unsupported ciphers or nonce sizes, test fragmented/nonlinear skbs, force packet ID exhaustion, authentication failure, short packets, async completion, and key-slot destroy after in-flight refs.
