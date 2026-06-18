# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_digest_pbkdf2.c

Implements the PBKDF2 digest handler used by LUKS2 and compatible with LUKS1-style master-key digest concepts.

Stored JSON fields:
- `"type": "pbkdf2"`
- `"keyslots"` and `"segments"` arrays
- `"hash"`
- `"iterations"`
- Base64 `"salt"`
- Base64 `"digest"`

Verification:
- Reads hash, iterations, salt, and digest from digest JSON.
- Base64-decodes salt and digest.
- Validates salt length is 32 bytes.
- Accepts digest length of legacy 20 bytes or the hash output size, bounded by a local 64-byte check buffer.
- Runs PBKDF2 over the supplied volume key and compares with constant-time backend comparison.
- Returns `0` for match, `-EPERM` for mismatch, and `-EINVAL` for malformed metadata or PBKDF failure.

Storage:
- Inherits PBKDF hash from the crypt device PBKDF settings, defaulting to `DEFAULT_LUKS1_HASH`.
- Uses 125 ms target PBKDF2 benchmark unless benchmarking is disabled, in which case it uses the backend minimum iteration count.
- Generates random digest salt, computes PBKDF2 digest using the HMAC size for the selected hash, base64-encodes salt/digest, and inserts or updates the digest JSON object.

Dump:
- Prints hash, iterations, salt, and digest in decoded hex form through `hexprint_base64()`.

Role:
- Supplies the concrete digest algorithm implementation consumed by `luks2_digest.c`.
