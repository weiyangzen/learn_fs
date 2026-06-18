# File Research: sources/block-storage/cryptsetup/lib/utils_keyring.h

## Purpose
Declares kernel keyring wrapper types and APIs.

## Key Responsibilities
- Defines fallback `key_serial_t`.
- Defines supported key types: logon, user, big_key, trusted, encrypted, invalid.
- Declares type/name conversion, key lookup, keyring lookup, support check, request, read, add, and unlink functions.

## Important Details
- Keeps Linux keyring integration behind a small internal API so callers need not invoke syscalls directly.
