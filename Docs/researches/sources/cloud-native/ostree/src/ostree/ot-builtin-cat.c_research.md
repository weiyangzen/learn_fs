<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-cat.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-cat.c

## Purpose
Implements `ostree cat`, concatenating file contents from a commit to stdout.

## Important APIs and Types
Exports `ostree_builtin_cat`; helper `cat_one_file` reads a `GFile` and splices it to a Unix stdout output stream.

## Control Flow
The command parses repository context, requires a commit and at least one path, reads the commit root as `GFile`, creates a stdout stream, resolves each requested path relative to the commit root, and splices each file sequentially.

## State and Persistence
No persistent state is changed. It reads repository commit contents and writes bytes to stdout.

## Dependencies and Integration Points
Uses `ostree_repo_read_commit`, GIO file/input/output streams, and Unix output stream integration. It is a simple content inspection command.

## Risks
Errors on any file stop the whole command after any previous files may already have been written. It does not insert separators between multiple files, matching `cat` behavior.

## Test Signals
Tests should cover one and multiple files, missing path, directory path errors, binary content, and commit resolution failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-cat.c -->
