# sources/distributed-fs/ceph-client/kernel/crash_dump_dm_crypt.c

## Purpose
`crash_dump_dm_crypt.c` preserves dm-crypt keys across a kexec crash dump by collecting configured logon keys from the current kernel keyring, adding them as a kexec buffer in crash memory, and restoring them into the kdump kernel's user keyring. It exposes a configfs interface for selecting keys, reusing already-saved keys, and restoring keys in the crash kernel.

## Important APIs, types, and functions
Key data types are `struct dm_crypt_key`, containing size, description, and up to 256 bytes of key data; `struct keys_header`, a counted flexible-array header; and `struct config_key`, a configfs item with a key description. Globals include `key_count`, `keys_header`, exported `dm_crypt_keys_addr`, `is_dm_key_reused`, `restore`, and configfs subsystem `crash_dm_crypt_keys`.

Important functions are `setup_dmcryptkeys()`, weak `dm_crypt_keys_read()`, `read_key_from_user_keyring()`, `build_keys_header()`, `crash_load_dm_crypt_keys()`, `restore_dm_crypt_keys_to_thread_keyring()`, `get_keys_from_kdump_reserved_memory()`, configfs attribute handlers for `description`, `count`, `reuse`, and `restore`, and `configfs_dmcrypt_keys_init()`.

## Control flow
The normal kernel exposes configfs items under `crash_dm_crypt_keys`. Users create per-key items and write key descriptions. During crash-image load, `crash_load_dm_crypt_keys()` returns early if no keys are configured. Otherwise it builds a fresh `keys_header` unless reuse mode is active, reads each configured logon key with `request_key(&key_type_logon, description, NULL)`, copies the payload under the key semaphore, and adds the header as a randomized `kexec_buf`. The crash image records the resulting physical address and size.

In a kdump kernel, the early `dmcryptkeys=` parameter sets `dm_crypt_keys_addr`. The configfs subsystem uses a reduced item type exposing only `restore`. Writing restore triggers `restore_dm_crypt_keys_to_thread_keyring()`, which reads the key count and header from old memory through `dm_crypt_keys_read()`, allocates a local header, and recreates user keys in `KEY_SPEC_USER_KEYRING` with `key_create_or_update()`.

Reuse mode checks that a crash image has a stored dm-crypt key address, unprotects crash reserved memory, maps the saved page, copies the header into current memory, and re-protects the crash reserved region.

## State and persistence behavior
Configured key descriptions persist only as configfs kernel objects until removed. Key material is copied into `keys_header` and then into a kexec buffer in crash reserved memory; that memory intentionally persists across kexec into the dump kernel. The kdump kernel restores keys into the current user's keyring. `key_count` is global and tracks configfs items, while `keys_header` is reused and freed with `kvfree()`/`kzalloc()` across loads. No disk files are written by this code.

## Dependencies and integration points
The file integrates with the kernel key retention service, logon key type, user keyring permissions, configfs, kexec file buffer loading, crash reserved memory protection, old-memory reads, confidential-computing memory-encryption attributes, `is_kdump_kernel()`, and kexec image fields `dm_crypt_keys_addr` and `dm_crypt_keys_sz`.

## Risks and edge cases
This code handles sensitive key material. Risks include inadequate zeroization of freed `keys_header`, global `key_count` and `keys_header` races through configfs operations, off-by-one maximum-key check because item creation rejects only `key_count > KEY_NUM_MAX`, and restoring from old memory with weak validation of `dm_crypt_keys_read()` return values. `config_key_release()` frees the `struct config_key` but not its duplicated `description`, which is a leak unless configfs releases attributes elsewhere. `restore_dm_crypt_keys_to_thread_keyring()` leaks the looked-up keyring reference on early failure after `lookup_user_key()`. A malformed old-memory header can carry invalid per-key sizes or descriptions unless all fields are checked before key creation.

## Test signals
Test signals include configfs create/remove/count behavior, description length and empty-description rejection, loading with zero keys, missing logon key, revoked key, oversized key payload, multiple keys up to the maximum, reuse from crash reserved memory, restoration in a kdump kernel with `dmcryptkeys=`, encrypted-memory oldmem reads, keyring permission failures, and repeated load/unload cycles with memory-leak and key-material lifetime checks.
