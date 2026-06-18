# File Research: sources/block-storage/cryptsetup/lib/utils_keyring.c

## Purpose
Wraps Linux kernel keyring syscalls and provides parsing/lookup helpers for cryptsetup key descriptions.

## Key Responsibilities
- Maps local key types to Linux key type names.
- Wraps `request_key`, `add_key`, `keyctl describe/read/link/unlink`.
- Finds keys by type and description through `request_key()` or `/proc/keys` fallback.
- Adds keys to arbitrary or thread keyrings.
- Reads key payload size and payload into safe memory.
- Parses `%<type>:<desc>` key names and `@t`, `@p`, `@s`, etc. keyring aliases.
- Provides unsupported stubs when kernel keyring support is not compiled in.

## Important Details
- `/proc/keys` fallback validates descriptions with `KEYCTL_DESCRIBE` because key types can append suffixes after colons.
- `keyring_check()` probes logon key request behavior to detect syscall support.
- Payload reads allocate with `crypt_safe_alloc()`.
- `keyring_find_keyring_id_by_name()` only accepts keyring aliases, keyring type names, or numeric ids.

## Dependencies
Uses Linux keyctl syscalls directly, `utils_keyring.h`, safe memory helpers, and libcryptsetup constants.
