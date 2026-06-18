# File Research: sources/block-storage/cryptsetup/src/utils_luks.c

## Purpose
Shared LUKS helper implementation for cryptsetup actions and reencryption code. It handles type normalization, passphrase verification policy, activation flags, PBKDF setup, retry policy, adjusted key sizes, JSON token I/O, keyslot context creation, token unlock, and volume-key context setup.

## Type And Policy Helpers
- `luksType()` maps user-facing `luks`, `luks1`, and `luks2` strings to libcryptsetup type constants.
- `isLUKS1()` and `isLUKS2()` check concrete libcryptsetup type strings.
- `verify_passphrase()` disables verification in batch mode unless `--verify-passphrase` is set, and disables it on non-tty input with an error if explicitly requested.
- `set_tries_tty()` only retries interactive stdin use; keyring descriptions reduce tries to one.

## Activation And PBKDF
- `set_activation_flags()` maps CLI flags to libcryptsetup activation flags, including readonly, discards, performance flags, persistent override, unbound key testing, keyring key activation, serialized memory-hard PBKDF, no journal, and large IV sectors.
- `set_pbkdf_params()` builds a `crypt_pbkdf_type` from defaults plus CLI overrides and supports forced-iteration no-benchmark mode.
- `get_adjusted_key_size()` implements optional XTS default key-size doubling and adds integrity key size.

## JSON I/O
- `tools_read_json_file()` reads token JSON from a file or stdin up to `LUKS2_MAX_MDA_SIZE`, temporarily unblocks signals, optionally prompts on tty, NUL-terminates the buffer, and zeroes on failure.
- `tools_write_json_file()` writes token JSON to a file or stdout and handles signal interruption.

## Keyslot Contexts
- `luks_init_keyslot_context()` creates a keyslot context from keyring description, keyfile, or interactive/passphrase input.
- `luks_try_token_unlock()` initializes a token keyslot context, tries activation or resume, reports token/keyslot errors, and optionally prompts for PIN when the token requires it.
- `luks_init_keyslot_contexts_by_volume_keys()` creates one or two keyslot contexts from volume-key files or keyring descriptions, with file input taking precedence.

## Notes
This file depends on the cryptsetup CLI option globals from `cryptsetup_args.h`; it is not a generic library helper independent of CLI state.
