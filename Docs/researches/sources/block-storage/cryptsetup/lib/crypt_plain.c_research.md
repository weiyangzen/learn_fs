# File Research: sources/block-storage/cryptsetup/lib/crypt_plain.c

## Purpose
Implements key derivation for plain dm-crypt mode.

## Key Content
`crypt_plain_hash()` accepts `hash` or `hash:hash_length` syntax, derives only the requested prefix length, zero-pads the remaining key if a shorter hash length is requested, and supports `"plain"` by directly copying passphrase bytes into the key. Other hash names use the local `hash()` helper, which repeatedly hashes optional leading `"A"` bytes plus the passphrase to fill arbitrarily sized keys, following the historical hashalot-compatible scheme.

## Dependencies and Coupling
Uses libcryptsetup logging, crypto backend hash APIs, and safe memory copy helpers. This is consumed by plain-mode setup paths rather than LUKS metadata paths.

## Invariants and Risks
Plain mode has no salt or metadata authentication. `"plain"` requires passphrase length at least as large as the requested key prefix. Hash name parsing caps names at 255 bytes.
