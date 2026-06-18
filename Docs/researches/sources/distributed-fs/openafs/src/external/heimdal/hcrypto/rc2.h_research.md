# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.h

Purpose: declares RC2 constants, key structure, and encryption APIs.

Important APIs/types/functions: defines `RC2_ENCRYPT`, `RC2_DECRYPT`, `RC2_BLOCK_SIZE`, `RC2_BLOCK`, `RC2_KEY_LENGTH`, `RC2_KEY` with 64 expanded words, and prototypes for `RC2_set_key`, `RC2_encryptc`, `RC2_decryptc`, and `RC2_cbc_encrypt`.

Control flow: consumers expand a key, then call block or CBC operations with direction flag.

State and persistence: expanded key material persists in `RC2_KEY`; CBC IV state is caller-owned and mutated by implementation.

Dependencies and integration points: used by `rc2.c` and EVP RC2 providers.

Risks and test signals: declaration drift and deprecated algorithm use are the main risks. RC2 known-answer and CBC round-trip tests validate it.
