# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/shared.rs

This file is the shared cryptsetup/LUKS2 support layer for the Stratis engine. It wraps `libcryptsetup-rs`, Clevis command helpers, kernel keyring helpers, and Stratis encryption metadata conventions.

Key responsibilities:
- Configures cryptsetup logging and safely acquires/loads LUKS2 `CryptDevice` handles.
- Adds and validates Stratis keyring-backed LUKS2 keyslots and tokens.
- Parses LUKS2 JSON tokens into Stratis `EncryptionInfo`, including key-description tokens and Clevis tokens.
- Interprets Clevis Tang/SSS/TPM2 metadata, including nested SSS recursion limits and Tang trust requirements.
- Activates encrypted devices by passphrase, token, or keyring-backed volume key, with V2 process-keyring volume key handling.
- Deactivates and wipes crypt devices, including fallback manual zeroing when libcryptsetup handle acquisition fails.
- Backs up/restores LUKS2 headers.
- Registers a Clevis token callback with cryptsetup and bridges callback errors through global `CLEVIS_ERROR`.
- Supports online reencryption setup and execution by duplicating keyslots/tokens onto a new volume key, then invoking the external reencryption command.

Important behavior:
- `activate()` enforces the metadata-version precondition: V1 has no pool UUID for volume-key keyring loading, V2 does.
- `get_keyslot_number()` expects each Stratis token to map to exactly one keyslot and errors on multiple keyslots.
- `encryption_info_from_metadata()` ignores unrelated token types but errors if no valid unlock mechanism remains.
- `interpret_clevis_config()` requires each Tang config to include trust material unless Stratis’ trust-url directive is set.
- `handle_setup_reencrypt()` is designed to be rollback-capable; `handle_do_reencrypt()` is explicitly not rollback-capable.

Tests:
- Unit tests cover Tang/SSS trust-information detection and recursion-related Clevis config handling.
