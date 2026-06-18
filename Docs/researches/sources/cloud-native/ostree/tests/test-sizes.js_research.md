# sources/cloud-native/ostree/tests/test-sizes.js

## Purpose
This GJS test validates generation and encoding of `ostree.sizes` commit metadata when committing with `OSTree.RepoCommitModifierFlags.GENERATE_SIZES`.

## Important APIs, Types, And Functions
It uses GJS imports `GLib`, `Gio`, and `OSTree`; helper functions `readVarint`, `unpackByteArray`, and `validateSizes`; APIs `Repo.create/open`, `RepoCommitModifier.new`, `prepare_transaction`, `write_directory_to_mtree`, `write_mtree`, `write_commit`, `commit_transaction`, `load_variant`, and checksum/object formatting helpers.

## Control Flow
The script creates test files, a duplicate, a symlink, and another file, then commits them into an archive-z2 repo with size generation, canonical permissions, and skipped xattrs. `validateSizes` loads the commit variant, reads `ostree.sizes`, decodes each entry as checksum bytes, compressed varint, uncompressed varint, and object type, and compares exact expected sizes. It then deletes one file, updates expected objects and dirtree checksum, commits again, validates sizes, and repeats the same commit with cached objects to ensure metadata is still correct.

## State And Persistence
Persistent state includes the test data directory, archive-z2 object store, three commits, and `ostree.sizes` metadata in commit objects. The expected object map stores exact compressed and uncompressed sizes.

## Dependencies And Integration Points
This integrates GJS bindings, commit modifiers, varint encoding, archive-z2 compression, checksum/object naming, symlink object handling, duplicate object reuse, and commit metadata loading.

## Risks
Exact compressed sizes can change if compression, object serialization, or canonical permissions change. Metadata must be regenerated per commit rather than reused from cached objects, especially after deletion and repeated commits.

## Test Signals
Three printed TAP lines cover initial sizes, file-deleted sizes, and repeated cached-object sizes. Any mismatch throws a JS error with object and size details.
