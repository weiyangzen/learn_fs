<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_crypto_ctx.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_crypto_ctx.h

Purpose: provides shared CryptoCell algorithm constants and enum values for block sizes, key sizes, digest sizes, engine identifiers, crypto algorithms, directions, cipher modes, and hash modes. It is the common vocabulary used by descriptor builders and request contexts.

Important APIs, types, and functions: defines DES/AES key and IV sizes, SHA/MD5 digest and block sizes, maximum hash/HMAC buffer sizes, CPP slot/algorithm constants, `enum drv_engine_type`, `enum drv_crypto_alg`, `enum drv_crypto_direction`, `enum drv_cipher_mode`, `enum drv_hash_mode`, and `enum drv_hash_hw_mode`. There are no functions.

Control flow: this header has no runtime flow, but its enum values are passed into descriptor macros such as `set_cipher_mode()`, `set_cipher_config0()`, and flow setup throughout AEAD, cipher, and hash code. It also informs request validation such as block alignment and key size checks.

State and persistence behavior: no mutable state. The constants define compile-time sizes for DMA buffers and runtime comparisons. Changing values affects hardware programming semantics across the driver.

Dependencies and integration points: includes Linux integer types. Used by `cc_driver.h`, AEAD/cipher/hash implementations, debugfs, and hardware descriptor definitions. It bridges Linux crypto API concepts to CryptoCell hardware mode encodings.

Risks: enum numeric values must match CryptoCell hardware expectations. Reordering or renumbering modes would silently program descriptors incorrectly. Maximum-size constants determine allocated DMA buffer sizes; undersizing can corrupt memory, while oversizing may mismatch hardware transfer lengths.

Test signals: broad crypto self-tests across all algorithms, descriptor dump inspection for mode values, compile coverage for new algorithms, and hardware bring-up tests on 630/710/712/713 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_crypto_ctx.h -->
