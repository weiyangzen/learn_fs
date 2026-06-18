# sources/distributed-fs/coda/coda-src/auth2/codatoken.c

Purpose: Generates, encrypts, authenticates, and validates Coda authentication tokens.

Important APIs/functions: Public `getauth2key`, `generate_CodaToken`, and `validate_CodaToken`; internal `generate_Secret` and `validate_Secret`.

Control flow: `getauth2key` derives a 48-byte key from a token key using secure PBKDF. Token generation builds a clear token with Vice ID, start time backdated 15 minutes, end time, random handshake key, and encrypted secret token. The secret payload contains magic bytes, key length, identity length, expiry, session key, identity, padding, AES-CBC encryption, and AES-XCBC authentication truncated to 8 bytes. Validation checks token size, MAC, block alignment, decrypts, validates magic/header/padding, extracts key/identity/end time, parses Vice ID, and returns the handshake key.

State and persistence: Stateless except for secure library initialization/randomness. Token blobs are consumed by auth2 and Vice; durable storage is handled by token files or Venus.

Dependencies and integration: Depends on `rpc2/secure.h`, RPC2 token types from `auth2.h`, and server/client code in `auth2.c` and `avice.c`.

Risks and test signals: Some validation error paths return before freeing encryption/auth contexts, causing small leaks. Identity is NUL-terminated inside the decrypted token buffer, relying on unused checksum space. `assert` is used for algorithm availability and context init in generation. Expiration enforcement happens in callers such as `avice.c`, not in `validate_CodaToken`.
