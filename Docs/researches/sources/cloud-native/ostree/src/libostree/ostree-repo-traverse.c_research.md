# sources/cloud-native/ostree/src/libostree/ostree-repo-traverse.c

## Purpose

This file implements commit and dirtree traversal for OSTree repositories. It exposes an iterator over commit tree entries and higher-level functions that collect all objects reachable from a commit, optionally across parent commits and with parent-object backreferences.

## Important APIs, Types, and Functions

- `_OstreeRepoRealCommitTraverseIter` stores iterator state, current directory variant, current entry name, result state, index, and content/meta checksums.
- `ostree_repo_commit_traverse_iter_init_commit()` initializes traversal from a commit root.
- `ostree_repo_commit_traverse_iter_init_dirtree()` initializes traversal from a dirtree variant.
- `ostree_repo_commit_traverse_iter_next()`, `ostree_repo_commit_traverse_iter_get_file()`, and `ostree_repo_commit_traverse_iter_get_dir()` implement file-first then directory iteration.
- `ostree_repo_traverse_new_reachable()` and `ostree_repo_traverse_new_parents()` allocate hash tables with the correct key semantics.
- `ostree_repo_traverse_commit_with_flags()`, `ostree_repo_traverse_commit_union_with_parents()`, `ostree_repo_traverse_commit_union()`, and `ostree_repo_traverse_commit()` collect reachable objects.
- `ostree_repo_traverse_parents_get_commits()` resolves parent-map entries back to owning commits.

## Control Flow

Iterator initialization from a commit reads child indexes 6 and 7 to obtain root dirtree and dirmeta checksums. The first call to `next()` for a commit loads the root dirtree and returns a directory result. Subsequent calls read file entries first from child 0 of the dirtree variant, then directory entries from child 1. File results expose a content checksum. Directory results expose content and metadata checksums.

Reachability traversal serializes object names as `(checksum, object type)` variants. For each file, it adds the file object and optional parent reference. For each directory, it adds the dirmeta object, then adds and recursively traverses the dirtree object if it has not already been seen. Commit traversal adds the commit object itself, optionally skips non-commit traversal under `OSTREE_REPO_COMMIT_TRAVERSE_FLAG_COMMIT_ONLY`, then follows parent commits until `maxdepth` is reached or no parent exists.

Partial commits are handled by loading commit state and allowing missing dirtree/dirmeta errors when the commit is marked partial. In that case the missing subtree is skipped rather than treated as fatal.

## State and Persistence Behavior

This file does not write repository state. It loads commit and dirtree variants and returns in-memory reachable-object and parent maps. The iterator refs the repo and variants until cleared. Parent maps store either a single parent variant or an array of parent variants to reduce memory use in the common single-parent case.

## Dependencies and Integration Points

Traversal is a shared service for static delta generation, pruning, object enumeration, and any feature that needs to know which objects belong to a commit. It depends on `ostree_repo_load_variant()`, `ostree_repo_load_variant_if_exists()`, `ostree_repo_load_commit()`, checksum variant validation, and object-name serialization helpers.

## Risks and Edge Cases

Iterator getters return borrowed pointers into iterator-owned storage and are only valid for the current result. Parent maps can contain nested parent chains, so callers need `ostree_repo_traverse_parents_get_commits()` to resolve final owning commits. Partial commit behavior intentionally suppresses missing subtree errors, which is correct for partial repositories but can hide corruption if commit state is wrong. Traversal avoids infinite recursion by checking the reachable set before descending into a dirtree.

## Test Signals

Tests should cover iterator ordering, root commit traversal, nested directory traversal, commit-only traversal, maxdepth parent traversal, duplicate shared dirtrees, parent map construction with multiple parents, missing parent commits in partial repositories, missing dirtrees in non-partial repositories, and borrowed-pointer lifetime assumptions.
