# File Research: sources/cow-pools/openzfs/module/zfs/sha2_zfs.c

## Summary
Provides ABD-backed SHA-2 checksum implementations for ZFS checksums.

## Main Responsibilities
- Computes SHA-256 checksums over ABD buffers.
- Computes SHA-512/256 checksums in native and byteswapped forms.
- Uses QAT acceleration for SHA-256 when available and falls back to software.

## Key APIs
- `abd_checksum_sha256()`.
- `abd_checksum_sha512_native()`.
- `abd_checksum_sha512_byteswap()`.

## Important Behavior
`abd_iterate_func()` feeds ABD chunks into `SHA2Update()`. SHA-256 output is forced to big-endian word order to preserve compatibility with an older private implementation. SHA-512/256 native output is byteswapped word-by-word for the byteswap variant.

## Risks
The SHA-256 endian conversion is on-disk compatibility behavior and must not be “simplified.” QAT fallback must preserve identical digest output when hardware acceleration fails.
