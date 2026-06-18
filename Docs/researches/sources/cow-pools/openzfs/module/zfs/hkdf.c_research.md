# File Research: sources/cow-pools/openzfs/module/zfs/hkdf.c

## Role

Implements HKDF-SHA512 for ZFS encryption key derivation using the kernel crypto API’s SHA-512 HMAC mechanism.

## Key Functions

- `hkdf_sha512_extract()` performs HKDF extract:
  - Configures `SUN_CKM_SHA512_HMAC`.
  - Uses the salt as the HMAC key.
  - MACs the input key material.
  - Writes a `SHA512_DIGEST_LENGTH` pseudorandom key to the output buffer.
- `hkdf_sha512_expand()` performs HKDF expand:
  - Uses the extract key as the HMAC key.
  - Iteratively computes `T(i) = HMAC(PRK, T(i-1) || info || i)`.
  - Copies full digest blocks and a final partial block into the caller output.
  - Rejects expansion requiring more than 255 digest blocks.
- `hkdf_sha512()` is the exported composition helper that extracts into a stack buffer and then expands into the requested output key.

## Error Handling

Crypto API failures are mapped to `EIO`. Overlong HKDF expansion is rejected with `EINVAL`.

## Research Notes

The code follows the standard HKDF extract/expand split. The comment notes that ZFS encryption uses this to derive new encryption keys and that the `info` parameter is referred to as salt elsewhere in the surrounding code.
