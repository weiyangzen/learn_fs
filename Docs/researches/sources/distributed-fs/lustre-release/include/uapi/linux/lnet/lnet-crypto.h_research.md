# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-crypto.h

Purpose: shared crypto algorithm descriptors and helpers for LNet/libcfs.

Important APIs/types: `cfs_crypto_hash_type` maps hash algorithm names to default key and digest size. `cfs_crypto_crypt_type` maps cipher names to key sizes. Hash enum includes null, adler32, crc32, crc32c, md5, sha1, sha256, sha384, sha512, max, speed-test cutoff, and unknown. Crypt enum includes null and AES-256 CTR. Static descriptor arrays define names/sizes. Inline helpers return type, name, digest/key size, and enum lookup by name. `cfs_crypto_hash_digest()` declares a one-shot digest API.

Control flow: lookup helpers validate enum bounds and descriptor names, then return metadata or fallback values such as `"unknown"` and zero sizes.

State and persistence: static descriptor arrays are compiled into each including translation unit; `cfs_crypto_hash_speeds` is extern runtime state.

Dependencies/integration: included by kernel and possibly user ABI consumers; relies on Linux types and string functions.

Risks and test signals: static non-const arrays in a UAPI header can create duplicate mutable definitions in multiple translation units. Lookup functions call `strcmp(hash_types[hash_alg].cht_name, algname)` without checking null for all enum slots, though current loop excludes `CFS_HASH_ALG_MAX`. Test signals are name/enum round trips, digest-size max, speed-tested subset, unknown values, and one-shot digest behavior for each algorithm.
