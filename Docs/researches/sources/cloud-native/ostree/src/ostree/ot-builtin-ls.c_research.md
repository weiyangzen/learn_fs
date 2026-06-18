# sources/cloud-native/ostree/src/ostree/ot-builtin-ls.c

## Purpose
Implements `ostree ls`, listing file metadata for paths inside a commit, with optional recursion, checksums, xattrs, and NUL-separated filename output.

## Important APIs, Types, And Functions
`ostree_builtin_ls()` reads a commit root. `print_one_argument()` resolves requested paths relative to the root. `print_directory_recurse()` enumerates directories. `print_one_file_text()` formats type, mode, owner, size, checksums, xattrs, path, and symlink target. `print_one_file_binary()` implements `--nul-filenames-only`.

## Control Flow
The command requires a commit, reads its root as an `OstreeRepoFile`, and either lists requested paths or `/`. For each path it queries fast file info without following symlinks, prints that entry, and if it is a directory, recurses indefinitely for `--recursive`, one level for default directory listing, or not at all for `--dironly`. Text output resolves repo file checksums before formatting. Binary output writes the path bytes followed by NUL.

## State And Persistence
The command is read-only. It walks virtual repository file objects and prints metadata to stdout. Xattr variants are read transiently when requested.

## Dependencies And Integration Points
It depends on `OstreeRepoFile`, GIO file enumeration/query APIs, `OSTREE_GIO_FAST_QUERYINFO`, and repo-file checksum/xattr helpers. Output is a user-facing inspection surface for commit contents created by commit, pull, or static delta application.

## Risks And Edge Cases
Recursive listing can be large. Invalid GIO file types are treated as hard errors in text mode. `--checksum` prints both directory contents checksum and object checksum for directories, which consumers must parse carefully. NUL mode prints only filenames, not metadata. Path resolution is relative to the commit root and errors are prefixed with the requested path.

## Test Signals
Tests should cover regular files, directories, symlinks, special files, default one-level directory listing, recursive and dironly modes, checksums, xattrs, NUL output, missing paths, and invalid commit resolution.
