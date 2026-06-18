# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_ccmp.c

## Purpose
Provides host-based CCMP encryption/decryption for libipw using the kernel AEAD crypto API with `ccm(aes)`. It implements the `libipw_crypto_ops` plugin named `CCMP`, including header/MIC insertion, AAD/nonce construction, replay protection, key management, and diagnostic stats.

## Important APIs, Types, and Functions
`struct libipw_ccmp_data` stores the 128-bit temporal key, key-set flag, TX/RX packet numbers, replay/decrypt error counters, key index, AEAD transform, and AAD scratch buffers. Important functions are `libipw_ccmp_init`, `libipw_ccmp_deinit`, `ccmp_init_iv_and_aad`, `libipw_ccmp_hdr`, `libipw_ccmp_encrypt`, `ccmp_replay_check`, `libipw_ccmp_decrypt`, `libipw_ccmp_set_key`, `libipw_ccmp_get_key`, `libipw_ccmp_print_stats`, `libipw_crypto_ccmp_init`, and `libipw_crypto_ccmp_exit`.

## Control Flow
Initialization allocates per-key state and a `ccm(aes)` AEAD transform. TX increments the 48-bit packet number, inserts an 8-byte CCMP header between the 802.11 header and payload, builds the CCM nonce from QoS control, transmitter address, and PN, appends an 8-byte MIC, and encrypts the payload/MIC with AAD covering masked 802.11 header fields. RX validates length, ExtIV, key index, and configured key, reconstructs PN, rejects replays, decrypts/authenticates through AEAD, updates `rx_pn`, then removes the CCMP header and MIC from the SKB.

## State and Persistence Behavior
The per-key context persists TX/RX PN across packets and reports CCMP format, replay, and decrypt error counts through `print_stats`. `set_key()` zeroes most state while preserving key index and AEAD transform, installs the key, optionally seeds RX PN from userspace sequence bytes, and configures auth size and key material in the crypto transform. `get_key()` returns the key and current TX sequence in Wireless Extensions byte order.

## Dependencies and Integration Points
Depends on `crypto_aead`, scatterlists, SKB head/tail operations, IEEE 802.11 header helpers, and libipw's crypto registry. `libipw_wx_set_encodeext()` creates this context for `IW_ENCODE_ALG_CCMP`; `libipw_tx.c` and `libipw_rx.c` invoke it via `encrypt_mpdu` and `decrypt_mpdu`.

## Risks
AAD/nonce construction is tightly coupled to 802.11 header layout, A4, and QoS rules; incorrect masking breaks interoperability. Replay checking assumes one RX PN per key context rather than per TID. Encryption mutates SKBs in place and requires exact headroom/tailroom from the TX allocator. `crypto_alloc_aead` is requested with `CRYPTO_ALG_ASYNC`, but requests are used synchronously without completion callback, so provider behavior matters. Key reset clears counters and PNs.

## Test Signals
Association with WPA2/CCMP, TX/RX encrypted unicast, QoS and non-QoS frames, A4/WDS-form headers if reachable, replay injection, wrong key index, missing ExtIV, MIC failure, seeded RX sequence, crypto provider errors, key replacement during traffic, and module unload after CCMP use are the main signals.
