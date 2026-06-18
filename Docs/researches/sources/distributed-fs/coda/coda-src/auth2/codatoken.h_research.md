# sources/distributed-fs/coda/coda-src/auth2/codatoken.h

Purpose: Public header for auth2 key derivation and Coda token generation/validation.

Important APIs/types: Defines `AUTH2KEYSIZE` as 48 and declares `getauth2key`, `generate_CodaToken`, and `validate_CodaToken`.

Control flow and state model: Callers derive an auth2 key from configured token material, generate clear/secret tokens for clients, or validate secret tokens to recover Vice ID, end time, and session key.

Persistence and integration: Integrates auth2 server token issuance with Vice server validation. Token storage itself is external.

Risks and test signals: The API assumes fixed-size `EncryptedSecretToken` and `RPC2_EncryptionKey` from `auth2.h`. Callers must check expiry after validation and protect the derived `auth2key`.
