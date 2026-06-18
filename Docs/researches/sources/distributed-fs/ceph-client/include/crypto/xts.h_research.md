# sources/distributed-fs/ceph-client/include/crypto/xts.h

Purpose: defines the XTS block size and a shared key-verification helper.

Important APIs, types, and flow: `XTS_BLOCK_SIZE` is 16 bytes. `xts_verify_key()` rejects keys when the caller-provided key length is not exactly twice the underlying cipher key size or when the two halves are identical, enforcing the XTS requirement for independent data and tweak keys.

State and persistence: stateless; reads caller key bytes and transform metadata only.

Dependencies and integration: depends on skcipher transform helpers and is used by XTS mode setkey implementations.

Risks and test signals: accepting equal key halves weakens XTS, and wrong split-size logic breaks AES-XTS and other XTS ciphers. Signals include XTS setkey tests for equal halves, odd/short/long key lengths, AES-XTS vectors, and fs/dm encryption setkey coverage.
