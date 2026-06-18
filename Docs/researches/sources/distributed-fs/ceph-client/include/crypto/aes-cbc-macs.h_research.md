# sources/distributed-fs/ceph-client/include/crypto/aes-cbc-macs.h

Purpose: library interface for AES-CMAC, AES-XCBC-MAC, and AES-CBC-MAC support.

Important APIs/types/functions: `struct aes_cmac_key`, `struct aes_cmac_ctx`, `aes_cmac_preparekey`, `aes_xcbcmac_preparekey`, `aes_cmac_init`, `aes_cmac_update`, `aes_cmac_final`, one-shot `aes_cmac`, `struct aes_cbcmac_ctx`, `aes_cbcmac_init`, `aes_cbcmac_update`, and `aes_cbcmac_final`.

Control flow: callers prepare a key, initialize a context that points to the prepared key, feed any number of updates, then finalize to produce a block-size MAC and zeroize the context. The one-shot helper wraps this sequence.

State and persistence: key structs retain expanded AES key and finalization subkeys; contexts retain the chaining value and partial block length until finalization.

Dependencies and integration points: depends on `<crypto/aes.h>`. AES-CBC-MAC is explicitly for AES-CCM internals and not a general variable-length MAC.

Risks: context stores a pointer to the key, so key lifetime must exceed context lifetime. CBC-MAC is insecure for arbitrary variable-length messages and should remain restricted to CCM construction.

Test signals: CMAC/XCBC known-answer tests, split-update tests, partial-block finalization tests, context zeroization checks, and CCM integration tests.
