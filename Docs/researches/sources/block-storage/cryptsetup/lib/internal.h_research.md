# File Research: sources/block-storage/cryptsetup/lib/internal.h

Central internal header for libcryptsetup shared types, helper declarations, logging macros, device APIs, volume-key APIs, and internal utility contracts.

Key points:
- Pulls in core utility headers, crypto backend API, public libcryptsetup API, macros, and symbol versioning.
- Declares volume-key lifecycle, key descriptions, kernel keyring upload/drop, linked volume-key lists, and key state helpers.
- Declares PBKDF setup, verification, benchmarking, cipher spec retrieval, and memory adjustment helpers.
- Declares device allocation/open/check/size/topology/block-adjust/locking functions and metadata/data device accessors.
- Declares dm-device creation/reload helpers and integrity-aware creation.
- Defines logging macros around `crypt_logf()`.
- Declares random source initialization/use/cleanup.
- Declares plain-mode activation/hash helpers, LUKS2 reencryption accessors, wipe helpers, keyring helpers, and serialization locks.
- Provides `uint64_mult_overflow()` used by FileVault2 offset calculations.
- Defines key verification constants and exposes `crypt_check_cipher()`.

Storage relevance:
- This is the common dependency surface for FileVault2, integrity, keyslot context, and crypto-adjacent code.
- The file does not implement behavior, but it defines the internal coupling points for block devices, dm targets, key material, and crypto.
