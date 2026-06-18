# File Research: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.c

## Purpose
Provides a generic storage wrapper that can read/write raw data, userspace-encrypted data, or temporary dm-crypt-encrypted data through one interface.

## Key Responsibilities
- Initializes userspace crypto storage backends.
- Initializes temporary private dm-crypt mappings as fallback or requested backend.
- Opens underlying devices with direct/blockwise-aware parameters.
- Handles cipher-null as a no-op wrapper.
- Reads raw data, reads and decrypts data, decrypts an in-memory buffer, writes raw data, and encrypts then writes data.
- Destroys userspace backends or removes temporary dm devices.
- Exposes fdatasync and wrapper type.

## Important Details
- Data offsets must be sector-aligned for dm-crypt compatibility.
- Userspace backend can be rejected if it falls back to kernel crypto while `CSW_DISABLE_KCAPI` is set.
- Temporary dm names include pid and a static counter.
- For dm-crypt wrappers, I/O offsets are relative to the mapped device, not the original data offset.
- Wrapper destruction force-removes temporary dm mappings.

## Dependencies
Uses device abstraction, dm target creation/removal, volume keys, cipher parsing, storage backend APIs, and blockwise I/O helpers.
