# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.c

Implements bcachefs dirent hashing, validation, creation, lookup, rename, empty-directory checks, readdir, and fsck dirent removal.

Key entry points:
- `bch2_casefold()` casefolds names when Unicode support and filesystem casefolding are enabled.
- `bch2_dirent_validate()` validates dirent names, casefold data, target self-links, name length, slash/dot entries, and embedded NULs.
- `bch2_dirent_init_name()` initializes normal or casefolded name payloads and shrinks the key value length.
- `bch2_dirent_create_key()`, `bch2_dirent_create_snapshot()`, and `bch2_dirent_create()` allocate and insert dirent keys.
- `bch2_dirent_read_target()` resolves normal inode targets or `DT_SUBVOL` targets into `subvol_inum`.
- `bch2_dirent_rename()` performs rename, overwrite, and exchange while preserving hash-table whiteout requirements and subvolume-dirent special rules.
- `bch2_dirent_lookup_trans()` / `bch2_dirent_lookup()` perform hash lookup with optional casefolding.
- `bch2_empty_dir_snapshot()` / `bch2_empty_dir_trans()` test directory emptiness.
- `bch2_readdir()` emits visible dirents to VFS/FUSE directory context.
- `bch2_fsck_remove_dirent()` removes a dirent through the hash-delete path during fsck.

Core mechanics:
- Dirents use `bch2_dirent_hash_desc` with the dirents btree, key type `KEY_TYPE_dirent`, 64-bit string hash, linear probing, key and bkey comparison callbacks, and subvolume visibility filtering.
- Lookup names are either stored names or casefolded names depending on `d_casefold`.
- Hash values reserve offsets 0 and 1 for dot entries by clamping to at least 2.
- Rename handles collision holes, source deletion whiteouts, overwrite/exchange target creation, and the special rule that subvolume dirents are physically deleted when moving between snapshots.
- `readdir()` copies keys into a `bkey_buf` before dropping transaction locks for `dir_emit()`.

Important invariants:
- `.` and `..` are not stored as normal dirents.
- Names cannot contain `/`, be empty, or exceed `BCH_NAME_MAX` for newly committed keys.
- Casefolded dirs require the filesystem casefold feature/encoding.
- Hash-table deletion must leave whiteouts when linear probing requires them.
- `DT_SUBVOL` dirents are visible only from their recorded parent subvolume.
- `ctx->pos` is updated for FUSE compatibility as well as VFS behavior.

Filesystem relevance:
- This is the namespace directory-entry engine for bcachefs: it maps directory/name pairs to inodes or subvolumes and underpins lookup, rename, readdir, and fsck namespace repair.
