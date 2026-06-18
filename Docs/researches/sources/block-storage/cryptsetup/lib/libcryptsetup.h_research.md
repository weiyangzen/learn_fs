# File Research: sources/block-storage/cryptsetup/lib/libcryptsetup.h

This is the public libcryptsetup API header. It defines the opaque `struct crypt_device` handle, keyslot context handle, public constants, public parameter structs, enums, callbacks, and exported function prototypes for cryptsetup users.

Major API areas:
- Context lifecycle: `crypt_init`, `crypt_init_data_device`, `crypt_init_by_name(_and_header)`, `crypt_free`.
- Logging and confirmation callbacks: `crypt_set_log_callback`, `crypt_log`, `crypt_logf`, `crypt_set_confirm_callback`.
- Global/device settings: RNG selection, PBKDF configuration, metadata locking, LUKS2 metadata/keyslot area sizing, compatibility flags.
- Format types: `CRYPT_PLAIN`, `CRYPT_LUKS1`, `CRYPT_LUKS2`, `CRYPT_LOOPAES`, `CRYPT_VERITY`, `CRYPT_TCRYPT`, `CRYPT_INTEGRITY`, `CRYPT_BITLK`, `CRYPT_FVAULT2`.
- Format parameter structs for plain, LUKS1, LUKS2, loop-AES, dm-verity, TCRYPT, dm-integrity, OPAL hardware encryption, and reencryption.
- Device actions: format, load, repair, resize, suspend/resume, conversion, UUID/label changes, header backup/restore, wipe, OPAL wipe.
- Keyslot management: add/change/destroy keyslots via passphrase, keyfile, volume key, keyslot context, signed key, keyring, token, and volume-key keyring paths.
- Activation/deactivation: passphrase, keyfile, volume key, signed key, kernel keyring, LUKS2 tokens, and keyslot-context activation.
- Runtime status/query: active device info, integrity failure count, crypt status, hardware encryption status, cipher/mode/UUID/device offsets, verity/integrity info, keyslot status/priority/encryption/PBKDF.
- LUKS2 tokens: JSON token access, keyring-token helpers, assignment APIs, internal/external token handler ABI, token handler function pointer types, external-token path controls.
- LUKS2 reencryption: initialization by passphrase/keyring/keyslot context, run/resume/recovery semantics, reencryption status and resilience parameters.
- Safe memory helpers: `crypt_safe_alloc`, `crypt_safe_free`, `crypt_safe_realloc`, `crypt_safe_memzero`, `crypt_safe_memcpy`.
- Kernel keyring linking for volume keys, including old/new keys during reencryption.

Filesystem/block-storage relevance:
- This header is the library contract for constructing and managing dm-crypt, dm-verity, dm-integrity, loop-AES-compatible, LUKS, BitLocker, FileVault2, and OPAL-backed block mappings.
- Activation flags encode block-device behavior: read-only mappings, shared access, discard/TRIM, dm-crypt workqueue/performance options, dm-verity corruption policy, dm-integrity journal/bitmap/recalculate/inline modes, large-sector IV handling, keyring-backed keys, private udev behavior, and suspended-state reporting.
- Struct fields expose storage geometry and layout decisions: offsets, sector sizes, metadata areas, keyslot areas, hash/FEC offsets, integrity tag sizes, OPAL segments, reencryption data shifts/hot zones.

Important notes:
- This file contains declarations and API documentation only; implementation lives elsewhere.
- Several legacy compatibility APIs remain exposed, including deprecated memory locking, iteration-time PBKDF setting, old keyfile offset wrappers, and deprecated `crypt_reencrypt`.
- Many APIs return negative errno values; several token and activation APIs document precise `-ENOENT`, `-EPERM`, `-ENOANO`, `-EAGAIN`, and `-ESRCH` semantics.
