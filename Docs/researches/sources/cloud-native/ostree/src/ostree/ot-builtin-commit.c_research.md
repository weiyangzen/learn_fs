# sources/cloud-native/ostree/src/ostree/ot-builtin-commit.c

## Purpose
Implements `ostree commit`, the CLI path for importing one or more filesystem trees into an OSTree repository, producing a commit object, optionally attaching metadata and signatures, and optionally updating a branch ref. It is the main user-facing bridge from directories, tar archives, or existing refs into the repository object store.

## Important APIs, Types, And Functions
The entry point is `ostree_builtin_commit()`. Option state covers commit message fields, parent/ref selection, tree sources, stat/skip filters, SELinux policy, fsync, timestamp, signing, generated sizes, and composefs metadata. `CommitFilterData`, `handle_statoverride_line()`, `handle_skiplist_line()`, and `commit_filter()` implement per-path metadata rewriting and skipping. `commit_editor()` integrates `ot_editor_prompt()` to derive subject/body text. `parse_keyvalue_strings()`, `add_collection_binding()`, `add_ref_binding()`, and `fill_bindings()` build commit metadata. The implementation uses `OstreeMutableTree`, `OstreeRepoCommitModifier`, `OstreeSePolicy`, `OstreeSign`, libarchive import helpers, and repository transaction APIs.

## Control Flow
The command parses options and opens a writable repo, loads optional statoverride and skip-list files, validates that either `--branch` or `--orphan` was supplied, and resolves the parent from `--parent` or the target branch. It builds metadata and detached metadata from command-line `KEY=VALUE` inputs and optional parent metadata preservation, rejects conflicting owner/canonical/SELinux options, then creates a commit modifier if filtering, labeling, ownership, xattr, or permission behavior is needed. It prepares a transaction, optionally scans hardlinks, creates or seeds an mtree from `--base`, normalizes implicit path input to `--tree=dir=...`, and overlays each `dir=`, `tar=`, or `ref=` source into the mtree. After unmatched statoverride or skip-list checks, it writes the mtree, optionally skips the commit if unchanged from the parent, fills bindings/bootable/composefs metadata, writes the commit with normal or overridden timestamp, writes detached metadata, signs with signapi or GPG keys, updates the branch ref, commits the transaction, and prints either the checksum or table statistics.

## State And Persistence
Persistent effects include new content, directory metadata, directory tree, commit, detached metadata, signatures, and ref updates in the repo. `--consume` can delete imported local content. `--disable-fsync` changes repository durability behavior for the run. `--skip-if-unchanged` avoids writing a new commit and reuses the parent checksum. The function aborts any repository transaction on exit, including after successful commit where abort is harmless because no transaction remains active.

## Dependencies And Integration Points
This file integrates `ostree-repo-private.h`, libarchive import code, `ostree-sign`, `ot-editor`, `parse-datetime`, SELinux policy loading, and the public `OstreeRepo` commit APIs. It coordinates with ref binding verification used by fsck/pull, composefs metadata consumers, bootable commit metadata, static signature verification, and shell completion/man pages noted in comments.

## Risks And Edge Cases
The path has many option interactions: invalid parent handling, branch directory conflicts, unsigned orphan commits, tar filters requiring libarchive, SELinux-from-base being invalid with tar, and canonical permissions conflicting with nonzero owner overrides. `commit_filter()` removes matched statoverride/skip entries; unmatched entries become hard errors, which is useful but can surprise users after most import work has run. Inline private keys are supported but discouraged. Timestamp parsing truncates to seconds. Because transaction abort is unconditional, future changes must preserve commit/abort semantics carefully.

## Test Signals
Useful signals include committing `dir=`, `tar=`, and `ref=` sources; statoverride and skip-list success and unmatched failures; branch parent resolution; `--skip-if-unchanged`; generated table stats; metadata, detached metadata, bindings, and bootable metadata inspection via `ostree show`; signing and verification; SELinux policy labeling; and transaction cleanup after induced import failures.
