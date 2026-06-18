# File Research: sources/cow-pools/bcachefs-tools/fs/fs/dirent.c

## Purpose

Implements bcachefs directory entry hashing, validation, formatting, creation, lookup, rename, readdir, casefold support, and fsck dirent removal.

## Main Interfaces

- Hash descriptor `bch2_dirent_hash_desc`.
- Casefold/name helpers: `bch2_casefold()`, `bch2_dirent_get_name()`, `bch2_dirent_init_name()`.
- Validation/printing: `bch2_dirent_validate()`, `bch2_dirent_to_text()`.
- Creation: `bch2_dirent_create_key()`, `bch2_dirent_create_snapshot()`, `bch2_dirent_create()`.
- Target/rename/lookup: `bch2_dirent_read_target()`, `bch2_dirent_rename()`, `bch2_dirent_lookup_snapshot()`, `bch2_dirent_lookup_trans()`, `bch2_dirent_lookup()`.
- Directory operations: `bch2_empty_dir_snapshot()`, `bch2_empty_dir_trans()`, `bch2_readdir()`.
- Initialization/debug: `bch2_dirent_init()`, `bch2_filldir64_specialization_to_text()`.
- Fsck helper: `bch2_fsck_remove_dirent()`.

## Behavior

Dirents are indexed by a 64-bit string hash stored in key offset, with linear probing and whiteouts for collision deletion. The hash descriptor supplies key/bkey hash, comparisons, and a subvolume-aware visibility filter.

Validation rejects empty names, oversized names, embedded NULs, dot/dotdot, slash, self-pointing non-subvolume dirents, and invalid casefold blocks. Name initialization stores either a plain name or a packed original + casefolded name block.

Creation builds a max-sized dirent key, fills target fields for regular targets or `DT_SUBVOL`, initializes names, then inserts through the string-hash layer. Rename handles normal, overwrite, and exchange modes; it preserves hash-table correctness around collisions, emits whiteouts when needed, and specially deletes subvolume dirents across snapshots because subvolume dirents are not versioned like ordinary dirents.

Lookup optionally casefolds the input name, performs hash lookup in current or specified snapshot, and resolves `DT_SUBVOL` targets through the subvolume table. Readdir walks visible dirents in a subvolume, validates/repairs hash placement, resolves targets, and emits entries.

## Kernel Fast Path

In kernel builds, the file optionally specializes getdents64 emission. It mirrors the private `getdents_callback64` layout when build-time verification succeeded, resolves the static kernel `filldir64` symbol with a kprobe, handles x86 IBT address adjustment, faults in the user buffer, and emits dirents under btree locks using `pagefault_disable()` and unsafe user copies. If unavailable or faulting/buffer-full, it falls back to `bch2_dir_emit_slow()`, which drops transaction locks before `dir_emit()`.

Userspace/non-kernel builds always use the slow path and report the fast path unavailable.

## State And Side Effects

Mutates dirent btrees, may insert hash whiteouts, may delete subvolume dirents from old snapshots, and may repair bad hash entries during readdir through `bch2_str_hash_check_key()`. Kernel initialization sets the global `filldir64_sym`.

## Dependencies

Uses btree key buffers/methods/update, extents, string hash, subvolume lookup, Unicode casefolding when enabled, Linux dcache/readdir/uaccess/kprobes in kernel builds, and generated getdents layout data.

## Risks And Notes

Hash collision handling is subtle. Rename must preserve probe chains even while moving/deleting keys. The getdents fast path intentionally depends on verified private kernel layout; if verification or symbol lookup fails, it silently degrades to the safe slow path.
