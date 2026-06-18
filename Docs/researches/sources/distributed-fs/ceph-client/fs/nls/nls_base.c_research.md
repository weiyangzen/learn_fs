# sources/distributed-fs/ceph-client/fs/nls/nls_base.c

## Purpose
`nls_base.c` is the core Linux filesystem Native Language Support implementation. It provides UTF-8/UTF-16 conversion helpers, maintains the global list of registered `struct nls_table` instances, supports module autoloading for charset names, and supplies the built-in `"default"` one-byte table used when `CONFIG_NLS_DEFAULT` cannot be loaded.

## Important APIs, types, and functions
The UTF helpers are `utf8_to_utf32()`, `utf32_to_utf8()`, `utf8s_to_utf16s()`, and `utf16s_to_utf8s()`, all exported. `struct utf8_table` describes UTF-8 sequence masks, minimum values, and shifts. Constants define `UNICODE_MAX`, `PLANE_SIZE`, and surrogate masks. `put_utf16()` and `get_utf16()` handle native, little-endian, and big-endian UTF-16 storage.

The registry APIs are `__register_nls()`, `unregister_nls()`, `load_nls()`, `unload_nls()`, and `load_nls_default()`. `find_nls()` searches by `.charset` or `.alias` and pins the owning module with `try_module_get()`. `tables` is the global linked list head, initialized to `default_table`, and `nls_lock` protects list mutation and lookup. `load_nls()` wraps lookup in `try_then_request_module(find_nls(charset), "nls_%s", charset)` so missing tables can be autoloaded.

The default table is a generated identity-style 8-bit mapping through `0xff`, with `charset2uni`, `page00`, reverse page pointers, and byte case tables. Its `struct nls_table` is named `"default"`.

## Control flow
UTF-8 decoding in `utf8_to_utf32()` walks `utf8_table`, accumulates continuation bits, rejects overlong encodings, values above `0x10ffff`, surrogate code points, incomplete sequences, and malformed continuation bytes. UTF-8 encoding in `utf32_to_utf8()` rejects invalid Unicode/surrogates, returns zero if the output pointer is NULL, and emits the shortest fitting sequence or `-EOVERFLOW`.

`utf8s_to_utf16s()` scans a NUL-terminated bounded UTF-8 input, decodes non-ASCII through `utf8_to_utf32()`, emits surrogate pairs for non-BMP code points when space permits, and stops when input, NUL, or output capacity ends. `utf16s_to_utf8s()` reads bounded UTF-16, stops at NUL, combines valid surrogate pairs, ignores unmatched low or invalid surrogate sequences, and stops rather than overflowing when encoded bytes do not fit.

Registration flow sets the module owner, checks that the table is not already linked, inserts at the head under `nls_lock`, and returns `-EBUSY` for duplicates. Unregister searches and unlinks under the same lock. Loading first searches the existing list, then asks kmod to request `nls_<charset>` if absent. Unloading decrements the module owner reference.

## State and persistence behavior
State is in-memory only. The global table list persists while the kernel runs and changes as NLS modules load or unload. The default table is always present. UTF conversion helpers keep no state between calls. There is no on-disk persistence, but filesystem-visible behavior depends on which NLS table is loaded and referenced by a mounted filesystem.

## Dependencies and integration points
This file is the integration point for all generated charset modules in `fs/nls`. It exports symbols used by filesystems and by other NLS modules. It depends on kernel module loading, spinlocks, byte-order helpers, errno conventions, and the `struct nls_table` ABI. Filesystems such as FAT/VFAT call `load_nls()`, store table pointers in superblock state, call conversion callbacks and case helpers, then call `unload_nls()` during teardown.

## Risks and test signals
The registry must avoid duplicate insertion, stale owner references, and races between lookup and unload. UTF conversion risks include accepting overlong UTF-8, surrogate values, truncated input, or writing past output bounds. The default table's zero-entry convention means NUL is invalid for callback conversion even though other bytes map identity-style. Tests should cover concurrent module load/unload, alias lookup, autoload request names, fallback through `load_nls_default()`, invalid UTF-8 sequences, surrogate handling, non-BMP UTF-16 pairs, endian modes, output capacity boundaries, and filesystem mount/unmount paths that load and release NLS tables.
