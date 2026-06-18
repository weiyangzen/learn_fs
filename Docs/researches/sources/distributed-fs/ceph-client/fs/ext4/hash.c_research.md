# sources/distributed-fs/ceph-client/fs/ext4/hash.c

## Purpose
`hash.c` computes ext4 directory-entry hashes for htree indexed directories. It supports legacy signed/unsigned hashes, half-MD4, TEA, SipHash for encrypted+casefolded directories with keys, optional Unicode casefolding, and seed-based hash randomization.

## Important APIs, types, and functions
The external entry point is `ext4fs_dirhash`. Internal algorithms include `TEA_transform`, `half_md4_transform`, `dx_hack_hash_unsigned`, `dx_hack_hash_signed`, `str2hashbuf_signed`, `str2hashbuf_unsigned`, and `__ext4fs_dirhash`. Hash mode and output live in `struct dx_hash_info`, including `hash_version`, `seed`, `hash`, and `minor_hash`.

## Control flow
`ext4fs_dirhash()` optionally casefolds the input name with the superblock Unicode map when the directory is casefolded and either unencrypted or the encryption key is present. If casefolding fails, it hashes the opaque byte sequence. `__ext4fs_dirhash()` initializes the default MD4-like seed, replaces it with a nonzero caller seed when supplied, dispatches by hash version, and clears the low bit of the major hash. It avoids returning the htree EOF sentinel. SipHash requires an fscrypt key and returns `-EINVAL` with a warning when unavailable.

## State and persistence behavior
Directory hashes are not separately persisted here, but they determine htree lookup/split ordering and therefore persistent directory layout. The hash seed can come from the superblock. Unicode casefolding and encryption-key availability affect whether semantically equivalent names hash identically or as opaque bytes.

## Dependencies and integration points
This file integrates with ext4 directory indexing, fscrypt filename SipHash, Unicode normalization/casefolding, superblock encoding state, and warning paths. It is used by directory lookup/allocation code, including Orlov top-directory placement in `ialloc.c`.

## Risks and test signals
Risks include signedness compatibility regressions, Unicode fallback mismatches, SipHash use without keys, hash-version validation, sentinel handling, PATH_MAX allocation failure for casefolding, and cross-endian seed interpretation. Test signals include all hash versions with known vectors, signed versus unsigned legacy names above ASCII, encrypted casefolded directories with and without keys, invalid hash versions, zero-length support probes, htree splits, and Unicode normalization/casefold collision cases.
