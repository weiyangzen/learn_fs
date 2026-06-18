<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mutable-tree.c -->
# sources/cloud-native/ostree/tests/test-mutable-tree.c

## Purpose
`test-mutable-tree.c` unit-tests `OstreeMutableTree`, the in-memory tree builder used when composing commits.

## Important APIs, Types, And Functions
Tests cover `ostree_mutable_tree_new`, metadata and contents checksum setters/getters, `ostree_mutable_tree_walk`, `ostree_mutable_tree_ensure_parent_dirs`, `ostree_mutable_tree_ensure_dir`, `ostree_mutable_tree_replace_file`, and `ostree_mutable_tree_lookup`.

## Control Flow
Individual tests create mutable trees, set checksums, create or walk nested directories, validate error cases for non-directory path components, replace file entries, and verify lookups return expected child trees or file checksums.

## State And Persistence
All state is in-memory tree nodes and checksum strings. No repository is opened and no files are written.

## Dependencies And Integration Points
This tests the mutable tree abstraction used by commit, import, and archive code before final writes to an OSTree repository.

## Risks And Test Signals
Tree mutation bugs can misclassify files/directories or corrupt commit contents. Passing signals include correct parent directory creation, replacement behavior, checksum storage, and error reporting for invalid tree walks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mutable-tree.c -->
