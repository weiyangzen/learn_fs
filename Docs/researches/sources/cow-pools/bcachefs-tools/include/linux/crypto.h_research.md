# File Research: sources/cow-pools/bcachefs-tools/include/linux/crypto.h

This is a minimal Crypto API compatibility header. It defines `CRYPTO_MINALIGN`, `CRYPTO_MINALIGN_ATTR`, forward-declares `struct crypto_type`, and defines `struct crypto_alg` with list linkage, name/type metadata, and an `alloc_tfm` callback.

It declares `crypto_register_alg()` and defines `struct crypto_tfm` as a wrapper around `struct crypto_alg *`. It is enough for bcachefs-tools code that registers or references kernel-style crypto algorithms, but it is not a full crypto framework.
