# sources/distributed-fs/ceph-client/include/crypto/internal/cipher.h

Purpose: declares the internal single-block cipher API for `CRYPTO_ALG_TYPE_CIPHER` algorithms, primarily used by templates and modes that invoke primitive block encryption/decryption one block at a time.

Important APIs, types, and flow: `struct crypto_cipher` wraps `struct crypto_tfm`. Allocation and lookup helpers force the algorithm type/mask to single-block cipher. The API exposes block size, align mask, flags, key setup, one-block encrypt/decrypt, transform cloning, spawn grab/drop/instantiate, and access to the underlying `cipher_alg`. Templates call `crypto_grab_cipher()` during instance creation and `crypto_spawn_cipher()` when constructing per-transform children.

State and persistence: transform key schedule and implementation state live inside the allocated crypto transform. No persistent state exists.

Dependencies and integration: relies on `crypto/algapi.h`, the generic crypto transform allocator, and `cipher_alg` implementations. It is integrated by block modes, skcipher templates, and low-level cipher drivers.

Risks and test signals: callers must enforce block-size buffers and correct key lengths; using this API for stream/chained modes would omit IV/state handling. Signals include primitive cipher self-tests, template self-tests using cloned or spawned ciphers, weak-key propagation, and alignment-sensitive architecture implementations.
