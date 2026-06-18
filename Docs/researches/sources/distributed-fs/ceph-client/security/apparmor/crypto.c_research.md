# sources/distributed-fs/ceph-client/security/apparmor/crypto.c

## Purpose
`crypto.c` implements optional SHA-256 hashing for loaded AppArmor policy blobs and profiles. The hashes support userspace introspection and integrity comparison between compiled userspace policy and kernel-loaded policy.

## Important APIs and functions
- `aa_hash_size` returns `SHA256_DIGEST_SIZE`.
- `aa_calc_hash` allocates a digest buffer and hashes arbitrary data.
- `aa_calc_profile_hash` hashes the little-endian policy version followed by profile data into `profile->hash`, honoring the runtime `aa_g_hash_policy` switch.
- `init_profile_hash` logs that hashing is enabled after AppArmor initialization.

## Control flow
Policy load code calls `aa_calc_profile_hash` when hash support is compiled. If runtime hashing is disabled, the function returns success without allocating or writing a hash. Otherwise it allocates profile hash storage, initializes a SHA-256 context, includes the policy ABI version in little-endian form, hashes the raw profile byte range, and finalizes into the profile.

## State and persistence
The persistent kernel state is the allocated `profile->hash` field and optional `aa_loaddata->hash` elsewhere. Hashes are exposed through apparmorfs profile and raw_data files but are not written to disk by this code.

## Dependencies and integration
The file depends on `CONFIG_SECURITY_APPARMOR_HASH`, `CRYPTO_LIB_SHA256`, `aa_g_hash_policy`, and AppArmor profile allocation/lifetime. The header provides stubs when the feature is disabled, so callers can be compiled unconditionally.

## Risks
Hash allocation failures fail profile hash computation and can affect policy load behavior depending on caller handling. Runtime toggling of `aa_g_hash_policy` means profiles loaded under different settings may or may not expose hashes. Hashing version plus bytes requires userspace to use the same ABI framing for comparisons.

## Test signals
Build with hash enabled and disabled. With hashing enabled at runtime, load policy and verify apparmorfs `sha256` files are populated and stable for identical input. With runtime hashing disabled, verify load succeeds and hash files are absent or empty as expected.
