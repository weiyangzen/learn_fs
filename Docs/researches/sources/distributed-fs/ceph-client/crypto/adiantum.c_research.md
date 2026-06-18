# sources/distributed-fs/ceph-client/crypto/adiantum.c

Purpose: implements the `adiantum(streamcipher,blockcipher)` length-preserving skcipher template, designed for storage encryption on CPUs without fast AES. It combines XChaCha12/20, NHPoly1305 hashing, and one 128-bit block-cipher invocation.

Important APIs, types, and functions: major structures are `adiantum_instance_ctx`, `adiantum_tfm_ctx`, `nhpoly1305_ctx`, and `adiantum_request_ctx`. Key functions include `adiantum_setkey()`, `adiantum_hash_header()`, `nhpoly1305_update()`, `nhpoly1305_final()`, `adiantum_hash_message()`, `adiantum_crypt()`, `adiantum_encrypt()`, `adiantum_decrypt()`, `adiantum_init_tfm()`, `adiantum_free_instance()`, `adiantum_supported_algorithms()`, and template `adiantum_create()`.

Control flow and behavior: `adiantum_create()` parses template attributes, grabs a stream cipher and block cipher, validates supported combinations, derives names/priorities, and registers a skcipher instance. `adiantum_setkey()` sets the stream key, derives block/hash subkeys by encrypting zero bytes with XChaCha nonce `1||0`, then initializes AES/block-cipher and Poly1305/NH keys. `adiantum_crypt()` hashes the tweak and left-hand message, transforms the right-hand 16-byte block, runs XChaCha over the bulk, then hashes the output bulk and writes the final right-hand block.

State and persistence: instance state stores crypto spawns; transform state stores child tfms and derived keys. Request state overlays NHPoly1305 state and a child skcipher request to save memory. No disk persistence exists, but the mode is intended for persistent encrypted storage sectors, so deterministic tweak/key handling is critical.

Dependencies and integration points: integrates with the skcipher template API, child skcipher/cipher spawns, `crypto/nh.h`, Poly1305 core, ChaCha/XChaCha constants, scatterwalk helpers, and fscrypt/dm-crypt style callers that need 32-byte tweaks. It imports `CRYPTO_INTERNAL`.

Risks and correctness concerns: the mode requires at least one 16-byte block; scatterlist fast paths must not read beyond mapped pages. NHPoly1305 buffering must produce the same hash independent of SG chunking. Subkey derivation must wipe temporary key material. Template validation must reject unsupported stream ciphers, block sizes, key sizes, and obsolete third hashing parameter.

Test signals: use known-answer tests for `adiantum(xchacha12,aes)` and `adiantum(xchacha20,aes)`, in-place and out-of-place SG layouts, single-page and multi-page paths, minimum length rejection, 32-byte tweak handling, async child cipher errors, and fscrypt/dm-crypt sector-size workloads.
