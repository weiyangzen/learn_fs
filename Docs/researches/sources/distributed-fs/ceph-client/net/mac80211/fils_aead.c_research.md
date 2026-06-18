<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.c -->
# sources/distributed-fs/ceph-client/net/mac80211/fils_aead.c

## Purpose
Implements FILS authenticated encryption for association and reassociation request/response frame bodies. It applies AES-SIV using CMAC-derived synthetic IVs and AES-CTR encryption so FILS-protected IEs after the FILS Session element can be encrypted and authenticated against station/AP addresses and nonces.

## Important APIs, Types, and Functions
The public functions are `fils_encrypt_assoc_req()` and `fils_decrypt_assoc_resp()`, declared in `fils_aead.h` and used by managed MLME association code. Internal crypto helpers are `gf_mulx()` for S2V doubling in GF(2^128), `aes_s2v()` for RFC-style AES-CMAC S2V derivation, `aes_siv_encrypt()` for IV plus ciphertext output, and `aes_siv_decrypt()` for CTR decrypt followed by S2V verification. The functions use `struct ieee80211_mgd_assoc_data` fields `fils_nonces`, `fils_kek`, and `fils_kek_len`.

## Control Flow
Encryption identifies whether the SKB is association or reassociation, locates the FILS Session extension element, and sets the encrypted region to the bytes after that element through the end of the frame. It builds five AAD vectors: STA address, AP/BSSID address, STA nonce, AP nonce, and the management frame region from capability information through the FILS Session element inclusive. It appends one AES block of space to the SKB for the SIV and encrypts in place at `encr`.

Decryption validates the response length, locates the FILS Session element, constructs the mirrored AAD order for response frames, ensures the encrypted data includes at least a synthetic IV block, decrypts the ciphertext into the same buffer, verifies the recomputed S2V against the frame IV, and subtracts the AES block from the caller's frame length. Failures are reported with `-EINVAL`, crypto-layer errors, or allocation errors, with MLME debug logs on malformed/decrypt-failed responses.

## State and Persistence
The file stores no persistent state. Per-call state includes stack arrays of AAD pointers/lengths, temporary CMAC blocks, a duplicated plaintext buffer for encrypt-side CTR overlap safety, and allocated skcipher requests. Persistent inputs live in association state: FILS nonces and KEK remain in `ieee80211_mgd_assoc_data` for the ongoing MLME exchange.

## Dependencies and Integration Points
Depends on kernel crypto APIs for AES-CMAC and `ctr(aes)`, scatterlists, `crypto_xor()`, unaligned big-endian helpers, SKB mutation, cfg80211 element parsing, and MLME debug logging. It integrates with `mlme.c` when transmitting FILS association requests and receiving FILS association responses. The exact AAD ordering follows FILS frame semantics, so callers must pass frames with intact addresses, nonces, FILS Session element, and association capability fields.

## Risks
`aes_siv_decrypt()` computes `iv_c_len - AES_BLOCK_SIZE` before its own length check; current callers check `crypt_len >= AES_BLOCK_SIZE`, so direct future callers must preserve that precondition. Encryption calls `skb_put()` before invoking crypto and does not roll back the length on later crypto failure. In-place encrypt/decrypt depends on the SIV layout and temporary plaintext copy on encryption; changes to buffer ownership could break overlap assumptions. Key length is split in half without local validation beyond crypto setkey failures. Authentication is highly sensitive to AAD ordering, FILS Session length, and nonce layout.

## Test Signals
Strong tests would use FILS association request/response vectors with known KEK/nonces, malformed or missing FILS Session elements, tampered ciphertext/IV/AAD returning `-EINVAL`, short encrypted response bodies, reassociation request offsets, allocation or crypto algorithm failure injection, and verification that successful response decrypt reduces `frame_len` by exactly `AES_BLOCK_SIZE`. Integration signals are successful FILS association in managed mode and MLME debug messages for bad AP responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/fils_aead.c -->
