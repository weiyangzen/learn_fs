# sources/cloud-native/ostree/src/ostree/ot-builtin-diff.c

## Purpose
Implements `ostree diff`, comparing two revisions or filesystem directories and optionally reporting object reachability statistics. With one argument it compares the argument's parent revision to the argument itself.

## Important APIs, Types, And Functions
`ostree_builtin_diff()` is the entry point. `parse_file_or_commit()` maps absolute or `./` paths to `GFile`s and other inputs to commit roots via `ostree_repo_read_commit()`. `reachable_set_intersect()` and `object_set_total_size()` support `--stats`. The implementation uses `ostree_diff_dirs_with_options()`, `ostree_diff_print()`, `ostree_repo_traverse_commit()`, and `ostree_repo_query_object_storage_size()`.

## Control Flow
The command parses options and requires at least one revision/directory argument. If only one is supplied, it appends `^` to form the source. If neither `--stats` nor `--fs-diff` is set, filesystem diff is enabled by default. Filesystem diff resolves both inputs, creates modified/removed/added arrays, applies xattr and owner override options, computes the diff, and prints it. Stats mode resolves both revisions, traverses each commit's reachable objects, prints object counts, intersects the sets, computes total storage size for common objects, and prints the formatted total.

## State And Persistence
The command is read-only. It creates transient `GFile`, `GPtrArray`, and reachability hash-table data structures but does not mutate refs, objects, or repository configuration.

## Dependencies And Integration Points
This file integrates the CLI with libostree diff and traversal APIs. It also accepts local filesystem trees, making it a comparison bridge between checked-out directories and repository commits. Owner override options feed `OstreeDiffDirsOptions` to normalize local file ownership during comparison.

## Risks And Edge Cases
Path detection is simple: only absolute paths and `./` prefixes are treated as files; other relative paths are interpreted as revisions. Stats mode requires both inputs to be resolvable revisions, not arbitrary directories. Object size summation can be expensive for large histories. Ignoring xattrs can hide security-relevant differences.

## Test Signals
Signals include default parent-vs-rev diff, explicit two-revision diff, directory-vs-directory diff, `--no-xattrs`, owner UID/GID normalization, stats counts and common size, invalid revision/path failures, and mixed path/revision behavior.
