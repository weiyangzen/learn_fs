# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/hkdf.c

## Scope

HKDF-SHA512 implementation for FreeBSD ZFS encryption key derivation, using the platform HMAC helpers from `crypto_os.c`.

## Main Interfaces

- `hkdf_sha512()` performs extract then expand.
- Internal `hkdf_sha512_extract()` computes HMAC-SHA512 using `salt` as the HMAC key and `key_material` as input.
- Internal `hkdf_sha512_expand()` expands the extract key with `info` and counter blocks.

## State And Control Flow

Extract initializes a `crypto_key_t` from the salt and computes a SHA512 digest. Expand creates a `crypto_key_t` from the extract key, computes numbered HMAC blocks `T(i) = HMAC(PRK, T(i-1) || info || i)`, and copies the requested number of output bytes. It rejects expansion requiring more than 255 digest blocks.

## Dependencies

Uses `crypto_mac*()` HMAC helpers, `crypto_key_t`, SHA512 digest constants, and ZFS error macros.

## Correctness Notes

The block-count expression is intended to cap HKDF output at the RFC limit of 255 hash-length blocks. The code does not explicitly zero `extract_key` or temporary `T` before returning, so secret material lifetime depends on stack reuse and compiler behavior.
