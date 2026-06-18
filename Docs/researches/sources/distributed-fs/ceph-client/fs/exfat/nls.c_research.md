# sources/distributed-fs/ceph-client/fs/exfat/nls.c

## Purpose
`nls.c` implements exFAT filename case folding, Unicode/NLS/UTF-8 conversion, name validation and hash calculation, and upcase table loading. exFAT stores filenames as UTF-16 and performs case-insensitive matching through an upcase table; this file owns both the default table and on-disk table verification/loading.

## Important APIs, types, and functions
The large `uni_def_upcase` table is the compressed recommended upcase table. `bad_uni_chars` lists forbidden ASCII characters. Conversion helpers include `exfat_convert_char_to_ucs2()`, `exfat_convert_ucs2_to_char()`, `exfat_utf16_to_utf8()`, `exfat_utf8_to_utf16()`, `__exfat_utf16_to_nls()`, and `exfat_nls_to_ucs2()`.

Public APIs are `exfat_toupper()`, `exfat_uniname_ncmp()`, `exfat_utf16_to_nls()`, `exfat_nls_to_utf16()`, `exfat_create_upcase_table()`, and `exfat_free_upcase_table()`. Upcase loading internals are `exfat_load_upcase_table()` and `exfat_load_default_upcase_table()`.

## Control flow
Lookup and create paths convert VFS byte names into `struct exfat_uni_name`. UTF-8 mounts use kernel UTF-8 helpers; NLS mounts convert via `nls_io`. Invalid conversion falls back to `_` and sets `NLS_NAME_LOSSY` for NLS mode; creation rejects lossy names while lookup can tolerate them for compatibility. Both conversion paths reject control characters and the forbidden ASCII punctuation set. The uppercased UTF-16 name is checksummed with `exfat_calc_chksum16()` for the stream extension name hash.

Read paths convert UTF-16 names back to either UTF-8 or the configured NLS encoding. NLS output replaces unsupported surrogate-pair code points with `_` because the kernel NLS framework cannot represent code points above U+FFFF. Case-insensitive comparisons call `exfat_toupper()` per UTF-16 unit.

At mount, `exfat_create_upcase_table()` scans root directory entries for `TYPE_UPCASE`. If found, it reads the upcase table clusters, expands compressed identity/skip markers into a 65536-entry table, computes the 32-bit checksum, and accepts it only if index coverage and checksum match. Non-I/O validation failure falls back to the built-in default table; missing table also falls back. `exfat_free_upcase_table()` releases `sbi->vol_utbl`.

## State and persistence behavior
Persistent state read here is the upcase table dentry and table file. Runtime state is `sbi->vol_utbl`, a 65536-entry array where zero means identity mapping. Filename hashes are persisted into stream dentries by callers. No on-disk state is directly modified in this file.

## Dependencies and integration points
This file depends on root-directory scanning, dentry type decoding, FAT chain traversal, checksum helpers, NLS and UTF-8 kernel APIs, and mount option `utf8`. It is used by dcache hashing/comparison, lookup, create, rename, readdir, and volume-label ioctls.

## Risks and test signals
Risks include lossy conversion policy mismatches, surrogate-pair handling differences between UTF-8 and NLS mounts, upcase-table checksum/expansion bugs, forbidden-character compatibility gaps, name-hash collisions or drift, and fallback to default table hiding a corrupt table. Tests should cover non-ASCII case-insensitive lookups, invalid byte sequences, names with forbidden characters, surrogate pairs, max-length names, UTF-8 versus iocharset mounts, corrupt upcase table checksum, missing upcase table fallback, and volume labels with lossy conversion.
