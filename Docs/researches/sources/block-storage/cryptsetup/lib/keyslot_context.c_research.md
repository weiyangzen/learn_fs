# File Research: sources/block-storage/cryptsetup/lib/keyslot_context.c

Implements keyslot context creation, dispatch, lazy secret loading, and exported ABI wrappers.

Key points:
- Context types include passphrase, keyfile, token, raw volume key, signed key, passphrase keyring, and volume-key keyring.
- Per-context function pointers dispatch to LUKS2 segment key open, LUKS1 volume key open, plain/integrity direct keys, BitLocker, FileVault2, verity signed keys, and passphrase retrieval.
- Passphrase context directly supplies passphrase bytes and can unlock LUKS1/LUKS2/BitLocker/FileVault2.
- Keyfile context lazily reads the keyfile into `i_passphrase` through `crypt_keyfile_device_read()` and then uses passphrase unlock paths.
- Token context calls LUKS2 token unlock for volume keys or passphrases, caches returned passphrase, and updates token id.
- Keyring passphrase context lazily retrieves passphrase bytes from the user keyring by description.
- Raw key context returns allocated `volume_key` objects and supports LUKS, plain, BitLocker, FileVault2, verity-without-signature, and integrity paths.
- Signed-key context returns separate volume key and signature keys for verity.
- Volume-key keyring context fetches a safe-allocated volume key by key description and can cache key size.
- `crypt_keyslot_context_init_common()` initializes version, error, and cached passphrase state.
- New exported constructors create self-contained contexts that copy secret/path/description inputs; old symbol versions preserve v1 pointer-lifetime behavior.
- `crypt_keyslot_context_set_pin()` replaces token PIN, safe-copying when context is self-contained.
- `crypt_keyslot_context_destroy_internal()` invokes type-specific cleanup and securely frees cached passphrases.
- `keyslot_context_type_string()` maps context type constants to readable names.

Storage relevance:
- This is the central unlock abstraction connecting user-provided credentials to LUKS, BitLocker, FileVault2, verity, plain, and integrity volume-key acquisition.
- Its ABI-versioned self-contained behavior matters for safe lifetime management of passphrases, PINs, and volume keys.
