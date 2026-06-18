# sources/distributed-fs/ceph-client/lib/crypto/tests/sha512-testvecs.h

Purpose: generated SHA-512 test vectors for the shared hash/HMAC KUnit template.

Important APIs/types/functions: data definitions `hash_testvecs[]`, `hash_testvec_consolidated`, and `hmac_testvec_consolidated` using `SHA512_DIGEST_SIZE`.

Control flow: none locally. Runtime behavior is provided by the including suite and template, which use the length/digest table to validate SHA-512 streaming and HMAC results. The vector set includes empty input, small lengths, SHA-512 block-boundary lengths around 128 bytes, and large multi-block data up to 16 KiB.

State and persistence: read-only static data; no mutable state or side effects.

Dependencies: `SHA512_DIGEST_SIZE`, `u8`, `size_t`, and the shared hash test naming convention. Generated provenance is `scripts/crypto/gen-hash-testvecs.py sha512`.

Integration points: included by `sha512_kunit.c`, which maps the table to SHA-512 and HMAC-SHA512 library calls.

Risks: manual byte corruption is difficult to spot visually. The table tests deterministic generated input rather than named external message strings, so failures must be diagnosed through the generator/template.

Test signals: good regression coverage for SHA-512 padding, 128-byte block processing, length encoding, digest output, and HMAC wrapper behavior.
