# File Research: sources/block-storage/cryptsetup/lib/keyslot_context.h

Declares the internal keyslot context dispatch structure and initializer functions.

Key points:
- Defines function-pointer types for LUKS2 key retrieval, LUKS1/LUKS2 volume-key retrieval, generic volume keys, BitLocker, FileVault2, signed verity keys, passphrase retrieval, context cleanup, and key-size queries.
- Defines context version constants: basic pointer-lifetime v1 and self-contained v2.
- `struct crypt_keyslot_context` stores type, version, per-type union payload, last error, cached passphrase, and dispatch function table.
- Union payloads cover passphrase, keyfile, token, raw volume key, signed key, passphrase keyring, and volume-key keyring state.
- Declares internal initializers for key, signed key, passphrase, keyfile, token, and keyring contexts plus destroy and type-string helpers.

Storage relevance:
- Header-level contract for the credential abstraction used by setup, activation, and format-specific unlock paths.
