# sources/distributed-fs/ceph-client/include/crypto/ctr.h

Purpose: constants for CTR mode and RFC3686 nonce/IV/block sizing.

Important APIs/types/functions: `CTR_RFC3686_NONCE_SIZE`, `CTR_RFC3686_IV_SIZE`, and `CTR_RFC3686_BLOCK_SIZE`.

Control flow: none; consumers use constants to parse keys/IVs and construct counter blocks.

State and persistence: none.

Dependencies and integration points: used by CTR skcipher implementations and IPsec RFC3686 wrappers.

Risks: nonce/IV/counter layout mistakes cause keystream reuse or interoperability failures.

Test signals: CTR/RFC3686 known-answer tests and IV construction tests.
