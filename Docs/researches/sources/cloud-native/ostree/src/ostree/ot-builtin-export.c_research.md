# sources/cloud-native/ostree/src/ostree/ot-builtin-export.c

## Purpose
Implements `ostree export`, which streams a commit or subdirectory of a commit as an uncompressed GNU tar archive to stdout or a specified output path.

## Important APIs, Types, And Functions
`ostree_builtin_export()` is the entry point. It uses libarchive write APIs, `ostree_repo_read_commit()`, `ostree_repo_load_variant()`, `ostree_commit_get_timestamp()`, and `ostree_repo_export_tree_to_archive()`. `OstreeRepoExportArchiveOptions` carries xattr, timestamp, and path-prefix settings.

## Control Flow
After parsing options and requiring a commit argument, the libarchive-enabled path creates an archive writer, hardcodes GNU tar format and no filter, opens either `--output` or stdout, reads the target commit root and commit object, copies the commit timestamp into export options, resolves `--subpath` if provided, attaches `--prefix`, and exports the tree into the archive. It closes the archive and propagates libarchive errors. Without libarchive support it returns a not-supported error.

## State And Persistence
The repository is read-only. Persistent output is the optional archive file; otherwise bytes are written to stdout. Archive entry timestamps are derived from commit metadata rather than current time.

## Dependencies And Integration Points
This command depends on `HAVE_LIBARCHIVE`, `ostree-libarchive-private.h`, `OstreeRepoFile`, and repo export helpers. It is the inverse of commit tar import paths and provides interoperability with tar-based tooling.

## Risks And Edge Cases
The format and filter are intentionally fixed, so compression and alternate archive formats are not exposed here. `--no-xattrs` can drop metadata. `--subpath` relies on resolving within the commit root; invalid paths fail during export. Builds without libarchive compile the command but always fail at runtime with a clear unsupported error.

## Test Signals
Tests should validate archive creation to stdout and file, exported GNU tar readability, commit timestamp propagation, subpath exports, prefix rewriting, xattr inclusion/exclusion, missing commit argument, invalid subpath, and behavior in builds without libarchive.
