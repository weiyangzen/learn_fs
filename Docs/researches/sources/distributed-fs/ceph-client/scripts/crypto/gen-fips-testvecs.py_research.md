# sources/distributed-fs/ceph-client/scripts/crypto/gen-fips-testvecs.py

## Purpose
`gen-fips-testvecs.py` generates a C header body for FIPS self-test vectors covering fixed test data/key material, HMAC digests, SHA3-256, and AES-CMAC.

## Important APIs, Types, and Functions
The constants are `fips_test_data` and `fips_test_key`. `print_static_u8_array_definition()` emits `static const u8 ... __initconst __maybe_unused` arrays in 8-byte rows. The script uses `hmac.new()`, `hashlib.sha3_256()`, `cryptography.hazmat.primitives.ciphers.algorithms.AES`, and `cryptography.hazmat.primitives.cmac.CMAC`.

## Control Flow and State
Execution is top-level: print SPDX and generated comments, include `<linux/fips.h>`, emit data/key arrays, compute HMAC for sha1, sha256, and sha512, compute SHA3-256, then compute AES-CMAC. Output goes to stdout; no input args or persistent state are used.

## Dependencies and Integration
It depends on Python 3 and the `cryptography` package. Generated output is intended for `lib/crypto/fips.h` or similar kernel generated headers.

## Risks and Test Signals
The AES key length is 16 bytes, so the vector is AES-128 despite the generic variable name. Reproducibility depends on Python library implementations. Test by regenerating and diffing expected header output, checking byte formatting, import failure behavior, and comparing vectors with independent crypto tools.
