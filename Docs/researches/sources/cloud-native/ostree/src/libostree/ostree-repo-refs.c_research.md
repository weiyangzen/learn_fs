# sources/cloud-native/ostree/src/libostree/ostree-repo-refs.c

## Purpose

This file implements OSTree ref resolution, ref enumeration, remote summary ref listing, collection-ref handling, and ref persistence. It is the repository layer that maps human-readable ref names, remote refspecs, and collection refs to commit checksums stored on disk or advertised by remote summaries.

## Important APIs, Types, and Functions

- `ostree_repo_resolve_rev()` and `ostree_repo_resolve_rev_ext()` resolve a checksum, abbreviated checksum, parent suffix refspec, local ref, or remote ref into a full commit checksum.
- `ostree_repo_resolve_collection_ref()` resolves `OstreeCollectionRef` keys and honors local-only flags, transaction state, mirrors, remotes, and parent repositories.
- `ostree_repo_list_refs()`, `ostree_repo_list_refs_ext()`, and `_ostree_repo_list_refs_internal()` enumerate `refs/heads` and optionally `refs/remotes`.
- `ostree_repo_remote_list_refs()` and `ostree_repo_remote_list_collection_refs()` parse a fetched remote summary and expose summary refs as checksum maps.
- `ostree_repo_list_collection_refs()` enumerates collection-aware refs from `refs/heads`, `refs/mirrors`, and configured remote collection IDs.
- `_ostree_repo_write_ref()`, `_ostree_repo_update_refs()`, and `_ostree_repo_update_collection_refs()` persist new ref values or aliases.
- Helpers such as `add_ref_to_set()`, `write_checksum_file_at()`, `find_ref_in_remotes()`, `enumerate_refs_recurse()`, and `relative_symlink_to()` hold most filesystem-specific behavior.

## Control Flow

Resolution first accepts full checksums directly, then tries a unique abbreviated commit checksum with `ostree_repo_list_commit_objects_starting_with()`. A trailing `^` resolves the parent commit by recursively resolving the base ref and loading the commit variant. Otherwise, `ostree_parse_refspec()` splits a remote/ref pair and `resolve_refspec()` checks transaction-pending refs, on-disk local refs, remote refs, fallback remote search, and finally the parent repo if configured.

Listing builds hash tables by recursively walking ref directories. Ref fragments are validated before use, so extra files from mirroring tools are ignored. Local listing reads `refs/heads`; remote listing reads `refs/remotes/<remote>` or all remote subdirectories unless excluded. Collection listing additionally maps local refs to the repository collection ID, maps mirror refs under `refs/mirrors/<collection-id>`, and maps remote refs only when the remote has a valid configured `collection-id`.

Ref writes validate remote names, collection IDs, ref names, and checksums, choose a directory based on local/remotes/mirrors semantics, then either unlink, replace a checksum file, or atomically install a symlink alias. After a successful write, repository mtime is updated and the summary may be regenerated outside transactions.

## State and Persistence Behavior

Persistent state is ordinary filesystem state under the repository directory: `refs/heads`, `refs/remotes`, and `refs/mirrors`. Ref values are checksum text files with trailing newlines. Aliases are symlinks with relative targets. In-memory transaction refs in `self->txn.refs` and `self->txn.collection_refs` shadow disk until transaction commit; access is guarded by `self->txn_lock`. Parent repositories are read-only fallback sources for resolution. Remote summaries are fetched through `ostree_repo_remote_fetch_summary()` and parsed as `OSTREE_SUMMARY_GVARIANT_FORMAT`.

The write path handles a file/directory conflict by listing refs below the candidate name, rejecting conflicting descendants, removing the directory, and retrying the file replacement. This protects against replacing a ref namespace that contains unrelated refs.

## Dependencies and Integration Points

The file depends heavily on libglnx fd-relative filesystem helpers, GLib `GVariant`, `GHashTable`, and repo-private helpers for summary regeneration, temporary symlink creation, checksum validation, and remote configuration. It integrates with commit object storage for abbreviated checksum lookup and parent resolution, with transaction machinery, and with remote summary metadata including collection maps.

## Risks and Edge Cases

Important risks are ref namespace conflicts, invalid remote collection configuration, accidental fallback to a remote when local-only semantics were intended, stale transaction state, and symlink alias handling. Partial checksum resolution returns an error when ambiguous but deliberately returns success with `NULL` when no match exists so regular ref parsing can continue. Collection-ref conflict detection is called out as incomplete for a directory/file replacement case.

## Test Signals

Useful tests include resolving full and partial checksums, ambiguous partial checksums, parent suffix resolution, local-only versus remote-fallback behavior, transaction-pending refs, parent-repo fallback, invalid ref fragment filtering during list, alias symlink listing through `OSTREE_REPO_LIST_REFS_EXT_ALIASES`, remote summary parsing, collection map parsing, and write conflict cases where a directory already exists at the desired ref path.
