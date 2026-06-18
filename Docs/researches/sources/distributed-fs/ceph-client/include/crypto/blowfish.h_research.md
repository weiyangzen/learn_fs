# sources/distributed-fs/ceph-client/include/crypto/blowfish.h

Purpose: Blowfish cipher constants, context, and key setup declaration.

Important APIs/types/functions: `BF_BLOCK_SIZE`, min/max key sizes, `struct bf_ctx`, and `blowfish_setkey`.

Control flow: crypto API setkey fills P-array and S-box state in `bf_ctx`; mode implementations use that context for block operations elsewhere.

State and persistence: `bf_ctx` stores expanded key material in P and S arrays.

Dependencies and integration points: integrates with Linux crypto block cipher providers and modes.

Risks: Blowfish has a 64-bit block size and is not suitable for high-volume modern encryption modes. Expanded state is large and sensitive.

Test signals: Blowfish KATs, key length rejection tests, and mode-level crypto tests.
