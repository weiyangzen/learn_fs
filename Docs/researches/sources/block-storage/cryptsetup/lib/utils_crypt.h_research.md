# File Research: sources/block-storage/cryptsetup/lib/utils_crypt.h

## Purpose
Declares cryptographic parsing and conversion helper APIs plus shared length limits.

## Key Responsibilities
- Defines cipher, keyfile, keyring, CAPI, and integrity string size limits.
- Declares cipher/mode, integrity, PBKDF, hex, logging, null-cipher, and CAPI conversion functions.

## Important Details
- The CAPI limits are sized for nested crypto API strings and bounded `sscanf` parsing.
- The header keeps helpers available to both library and CLI sources.
