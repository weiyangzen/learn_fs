# File Research: sources/block-storage/cryptsetup/src/utils_luks.h

## Purpose
Header declaring LUKS helper functions shared across cryptsetup source files.

## Declared Areas
- Type helpers: `luksType`, `isLUKS1`, `isLUKS2`.
- CLI policy: `verify_passphrase`, `set_activation_flags`, `set_pbkdf_params`, `set_tries_tty`, `get_adjusted_key_size`.
- Formatting and reencryption entry points: `luksFormat`, `reencrypt`, `reencrypt_luks1`, `reencrypt_luks1_in_progress`.
- Keyslot context helpers: passphrase/keyfile/keyring context initialization, token unlock, two-volume-key context initialization.
- Diagnostics: `luks_check_keyslots`.

## Dependencies
Forward-declares `struct crypt_device` and includes basic integer/bool headers.

## Notes
This header bridges `cryptsetup.c`, `utils_luks.c`, `utils_reencrypt*.c`, and keyslot check code.
