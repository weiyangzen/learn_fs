# File Research: sources/block-storage/cryptsetup/lib/utils.c

## Purpose
General cryptsetup utility implementation for system sizing, process priority, keyfile reading, kernel version parsing, cipher usability checks, and Linux crypto API cipher-name conversion.

## Key Responsibilities
- Reports page size, online CPU count, total/free physical memory, and swap availability.
- Temporarily raises/restores process priority for expensive cryptographic operations.
- Reads passphrases/keyfiles from files or stdin with offset support, terminal rejection, newline stopping, safe allocation, and bounded default reads.
- Parses kernel version from `uname`.
- Tests cipher usability first through the storage backend and, for privileged callers, through temporary dm-crypt access.
- Converts `capi:` kernel crypto API cipher strings into cryptsetup cipher/integrity strings, including AEAD/authenc forms.

## Important Details
- Key material is allocated with `crypt_safe_alloc()` and wiped on failure.
- `keyfile_seek()` falls back to read-and-discard for non-seekable inputs such as pipes.
- Unlimited keyfile reads are still capped by `DEFAULT_KEYFILE_SIZE_MAXKB`.
- Cipher checks deliberately use random non-weak placeholder keys, not all-zero keys.
- `crypt_capi_to_cipher()` has careful bounded `sscanf`/`snprintf` handling for long crypto API strings.

## Dependencies
Uses `internal.h`, safe memory helpers, random generation, storage wrappers, dm/device metadata helpers, and low-level block I/O helpers.
