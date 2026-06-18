# sources/distributed-fs/ceph-client/fs/hpfs/name.c

Purpose: this file implements HPFS filename validation, case conversion, comparison, lowercasing for presentation, long-name detection, and trailing-character adjustment.

Important APIs and functions: `hpfs_chk_name()` validates and trims names. `hpfs_translate_name()` returns the original name or an allocated lowercase copy for readdir. `hpfs_compare_names()` performs case-insensitive HPFS ordering. `hpfs_is_name_long()` determines the HPFS `not_8x3` flag. `hpfs_adjust_length()` trims trailing dots and spaces to match OS/2 behavior. `hpfs_upcase()` exposes code-page-aware uppercase conversion.

Control flow: validation rejects names over 254 bytes, empty adjusted names, disallowed control/reserved characters, and `.`/`..`. Comparison uppercases each byte via the mounted code-page table and compares lexicographically, with the HPFS last sentinel sorting after all real names. Translation optionally lowercases names for display when the mount uses lowercase mode.

State and persistence: no persistent state is changed. The functions read `sb_cp_table` and may allocate temporary display-name buffers.

Dependencies and integration: dentry hashing/comparison, directory lookup, dnode insertion/search, and readdir all depend on these semantics. `hpfs_is_name_long()` feeds the `not_8x3` dirent flag written by `hpfs_add_de()`.

Risks: `hpfs_is_name_long()` appears to test `no_dos_char(name[i])` inside the extension loop instead of `name[j]`, which is a subtle risk for DOS-name classification. Lowercase translation can return the original pointer on allocation failure, so callers must free only when the pointer differs.

Test signals: validate reserved characters and trailing dots/spaces, compare case variants and non-ASCII code-page bytes, display lowercase mode, long-name flag for 8.3 and non-DOS characters, and sentinel comparisons during dnode search.
