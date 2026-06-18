# sources/cloud-native/ostree/src/ostree/ot-builtin-log.c

## Purpose
Implements `ostree log`, printing a commit and recursively walking parent commits to show history.

## Important APIs, Types, And Functions
`ostree_builtin_log()` resolves the starting revision. `log_commit()` loads a commit variant, prints it with `ot_dump_object()`, obtains its parent with `ostree_commit_get_parent()`, and recurses. `OstreeDumpFlags` controls raw output.

## Control Flow
The command parses `--raw`, requires a revision, resolves it to a checksum, and calls `log_commit()`. Each recursive call loads the commit object. If a parent is missing during recursion, it prints a marker indicating history beyond that commit was not fetched and stops successfully. Other load failures propagate. Loaded commits are dumped, then parent recursion continues until there is no parent.

## State And Persistence
The command is read-only. It allocates variants and strings while walking history and writes formatted history to stdout.

## Dependencies And Integration Points
It depends on repository revision resolution, commit object loading, parent extraction, and the shared dump helpers in `ot-dump.c`. Its missing-parent behavior is important for shallow pulls or partial local history.

## Risks And Edge Cases
Recursion depth follows commit history and could be large. Only missing parents during recursive history are downgraded to a message; a missing starting commit is fatal. Raw mode delegates byte-swapped variant formatting to dump helpers.

## Test Signals
Tests should cover linear history output, root commits without parents, shallow history missing a parent, invalid revisions, raw output, and formatting consistency with `ostree show` for commit objects.
