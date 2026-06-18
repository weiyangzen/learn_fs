# sources/distributed-fs/ceph-client/fs/fat/namei_vfat.c

## Purpose
`namei_vfat.c` implements the VFAT filesystem variant with long filename support, short alias generation, case-sensitive or case-insensitive dentry operations, and full VFS namespace operations including `RENAME_EXCHANGE`. It builds long-name slot arrays and delegates physical directory mutation to `dir.c`.

## Important APIs, Types, and Functions
- `vfat_revalidate()` and `vfat_revalidate_ci()` invalidate negative dentries when parent i_version changes or create/rename intent requires a case-accurate lookup.
- `vfat_hash()`, `vfat_hashi()`, `vfat_cmp()`, and `vfat_cmpi()` implement trailing-dot stripping and optional case folding.
- `xlate_to_uni()` converts user names to UTF-16 using UTF-8, NLS, or `:xxxx` unicode escape sequences.
- `vfat_create_shortname()` derives a unique 8.3 alias, including Win95/WinNT case rules and numeric/randomized tails.
- `vfat_build_slots()` creates VFAT long-name slots plus the final short entry.
- `vfat_lookup()`, create/unlink/mkdir/rmdir, `vfat_rename()`, and `vfat_rename_exchange()` implement VFS namespace behavior.

## Control Flow
Lookup strips trailing dots, searches both long and short names through `fat_search_long()`, builds the inode from the located short entry, and handles alias dentries when the same inode was previously reached by an 8.3 alias or long name. Negative dentries remember the parent i_version so new aliases can invalidate them.

Creation converts the user name to UTF-16, rejects bad characters and trailing spaces, builds a unique short alias, optionally emits long-name slots with checksum and order markers, writes slots, increments parent i_version, builds the inode, and instantiates the dentry. Mkdir first allocates and initializes a directory cluster, then writes the VFAT entry.

Normal rename creates or reuses the destination slot, detaches any replaced inode, moves the old inode's `i_pos`, syncs it, updates `..` when crossing directories, removes old slots, updates metadata, and rolls back on failure. `RENAME_EXCHANGE` swaps `i_pos` between two existing inodes and updates both `..` entries and link counts as needed.

## State and Persistence
VFAT persistent names are a sequence of one or more `ATTR_EXT` slots followed by an 8.3 alias entry. The alias checksum connects the long-name slots to the short entry. In-core dentry state stores parent i_version in `d_fsdata` for negative dentry validation. Rename and exchange persist by changing which on-disk slot each inode's metadata writes to, not by rewriting the whole source name in place.

## Dependencies and Integration Points
The file uses NLS tables from mount setup, common FAT directory slot functions, inode build/detach/attach/sync helpers, timestamp helpers, and VFS dentry/namei operations. It registers the `vfat` filesystem type and delegates common mount parsing/fill to `fat_parse_param()` and `fat_fill_super()`.

## Risks and Test Signals
Short alias generation is performance-sensitive and collision-prone in large directories. Unicode conversion can fail on invalid UTF-8/NLS sequences or names longer than `FAT_LFN_LEN`. Case-insensitive positive dentries cannot always support case-only renames. Tests should cover UTF-8/NLS mounts, unicode escape mode, bad-character rejection, trailing dot/space behavior, alias collisions, `nonumtail`, shortname policies, lookup by alias and long name, negative dentry invalidation, cross-directory rename, replacement, and `RENAME_EXCHANGE`.
