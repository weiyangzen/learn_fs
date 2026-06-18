# sources/cloud-native/ostree/src/ostree/ot-builtin-rev-parse.c

## Purpose
Implements `ostree rev-parse`, resolving revision names to commit checksums, plus a `--single` mode for repositories expected to contain exactly one commit object.

## Important APIs, Types, And Functions
`ostree_builtin_rev_parse()` is the entry point. It uses `ostree_repo_resolve_rev()` for normal arguments and `ostree_repo_list_commit_objects_starting_with()` plus `ostree_object_name_deserialize()` for `--single`.

## Control Flow
After parsing, `--single` rejects additional arguments, lists all commit objects, fails if none or more than one are found, deserializes the sole object name, asserts it is a commit, prints the checksum, and returns. Normal mode requires at least one revision argument, resolves each to a checksum, and prints one checksum per line.

## State And Persistence
The command is read-only. It prints resolved checksums and allocates transient object-list data.

## Dependencies And Integration Points
It is a CLI wrapper around libostree revision resolution and object enumeration. Scripts can use it before reset, diff, static delta generation, or other commands requiring stable checksums.

## Risks And Edge Cases
`--single` counts all commit objects, not refs, so repositories with unreferenced commits fail as multiple. Normal mode stops at the first resolution error. The command does not expose collection-ref-specific resolution options.

## Test Signals
Tests should cover resolving branches, checksums, parent syntax, multiple arguments, missing argument errors, `--single` success with one commit object, and `--single` failures for zero or multiple commit objects.
