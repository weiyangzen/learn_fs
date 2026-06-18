# sources/distributed-fs/glusterfs/xlators/meta/src/subvolumes-dir.c

Purpose: implements the virtual `subvolumes` directory beneath each xlator, listing child translators as numeric symlinks.

Important APIs/types/functions: `subvolumes_dir_fill()` counts `xl->children`, allocates `struct meta_dirent` entries, names them `0`, `1`, etc., sets type `IA_IFLNK`, and uses `meta_subvolume_link_hook`. `meta_subvolumes_dir_hook()` propagates parent xlator context and attaches `subvolumes_dir_ops`.

Control flow: readdir of `subvolumes` materializes numeric dirents from the current child list. Lookup/readlink of each numeric entry resolves to the corresponding child xlator.

State and persistence behavior: generated dirents are cached per directory fd; the directory mirrors live in-memory graph topology but does not persist it.

Dependencies and integration points: depends on `xlator_t.children`, `gf_strdup`, `GF_MALLOC`, and `subvolume-link.c`.

Risks and edge cases: allocation uses `count` without an explicit null terminator because dynamic dirent count is returned separately; callers must respect the count. Child-list changes after readdir can make numeric entries stale or point to different children on later lookup.

Test signals: readdir for xlators with zero, one, and many children; readlink targets; fd release cleanup of numeric names; and graph reload/reopen behavior.
