# sources/cloud-native/ostree/src/libostree/ostree-repo-file.c

## Purpose
This file implements `OstreeRepoFile`, a `GObject` that implements the `GFile` interface for files and directories inside an OSTree commit. It gives generic GIO code a read-only, lazy-resolved view over OSTree dirtree/dirmeta and content objects.

## Important APIs, Types, And Functions
The instance stores a repo reference, parent `OstreeRepoFile`, child index, name, cached file checksum, directory contents checksum/variant, and directory metadata checksum/variant. Constructors include `_ostree_repo_file_new_root()` and `_ostree_repo_file_new_for_commit()`, while children are produced internally by `ostree_repo_file_new_child()`. Public helpers include `ostree_repo_file_ensure_resolved()`, `ostree_repo_file_get_xattrs()`, tree checksum/content/metadata getters, `ostree_repo_file_tree_set_metadata()`, `ostree_repo_file_get_repo()`, `ostree_repo_file_get_root()`, `ostree_repo_file_get_checksum()`, `ostree_repo_file_tree_find_child()`, and `ostree_repo_file_tree_query_child()`.

The implemented `GFileIface` methods include duplicate, hash, equality, URI/path/name methods, parent lookup, prefix and relative path handling, relative path resolution, child display lookup, child enumeration, info query, settable/writable namespace query, and read. Mutating operations are intentionally null.

## Control Flow
A root object is created from known dirtree and dirmeta checksums or by loading a commit object and extracting its root tree checksums. Resolution is lazy. Root resolution loads the root dir tree and dir meta variants. Non-root resolution first resolves the parent, searches parent dirtree file and directory arrays by name, stores the child index, and, for directories, loads child dirtree/dirmeta variants and records their checksums. File checksums are computed from parent dirtree entries and cached.

`ostree_repo_file_tree_query_child()` resolves the directory, selects either the files array or directories array by numeric index, loads file info through `ostree_repo_load_file()` for files or dirmeta for directories, and sets standard GIO name/display/hidden attributes. `query_info` returns root dirmeta-derived info or delegates to the parent child query. `read` rejects directories, loads regular file streams by checksum, and resolves symlink targets relative to the parent before reading.

## State And Persistence
`OstreeRepoFile` is read-only from the perspective of `GFile`. It caches loaded `GVariant` tree metadata/content and computed file checksums in memory. It does not write repository state except for the specialized internal `ostree_repo_file_tree_set_metadata()`, which mutates the in-memory metadata/checksum pair for an existing object. Persistent content remains in the associated `OstreeRepo` object store.

## Dependencies And Integration Points
The implementation depends on GLib/GIO, `ostree-repo-private.h`, `ostree-repo-file-enumerator.h`, checksum conversion helpers, dirtree/dirmeta variant formats, `ostree_repo_load_variant()`, `ostree_repo_load_file()`, and utility path caches. It integrates with checkout, composefs, commit tree reuse, generic GIO traversal, and callers that treat committed OSTree content as a virtual filesystem.

## Risks And Edge Cases
Resolution assumes parent dirtree arrays are sorted for `ot_variant_bsearch_str()`. Child paths are represented by object parent/name links and do not perform native filesystem access until content is loaded from the repo. `get_parent()` returns a ref of `self->parent`, so callers should avoid requesting the parent of the root. `get_basename()` can return null for root because root has no name. Symlink `read` follows the symlink target recursively through the virtual tree, so loops or missing targets can surface as GIO read errors. `ostree_repo_file_get_checksum()` asserts the child exists and should only be called after resolution paths that guarantee existence.

## Test Signals
Useful tests include root creation from commits, lazy resolution of nested files and directories, missing child errors, xattr loading for files and directories, GIO path/URI/equality/hash behavior, relative path resolution including absolute paths and root, enumeration through `OstreeRepoFileEnumerator`, query info for requested attributes, hidden-file attribute handling, regular file reads, symlink reads, and tree reuse by commit-writing code.
