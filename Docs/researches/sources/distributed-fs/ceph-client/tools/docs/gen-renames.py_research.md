# sources/distributed-fs/ceph-client/tools/docs/gen-renames.py

Purpose: Walks git history to generate old-to-current documentation page rename mappings for `.rst` files.

Important APIs, types, and functions: `normalize()` strips `Documentation/` prefix and `.rst` suffix. `Name` tracks the chain of names for a file. Main code runs `git log --reverse --find-renames --diff-filter=RD --name-status` from `v4.8` to `--rev`, updates rename chains, drops deleted chains, collects current `.rst` files with `git ls-tree`, and prints old/current pairs excluding recreated names.

Control flow: Rename records move a `Name` chain from old key to new key or create a new chain. Delete records remove active chains. After history traversal, current files are used to avoid redirecting names that exist again. All old names in surviving chains map to the final name.

State and persistence: Read-only git queries; writes mappings to stdout.

Dependencies and integration points: Depends on git history, tag `v4.8`, Documentation tree, and downstream `gen-redirects.py`.

Risks: Rename detection depends on git similarity heuristics. Deletes remove chain state and do not propose alternatives. Only `.rst` files are tracked. History range assumes `v4.8` exists in the repo.

Test signals: Run at HEAD, at older revisions, with synthetic rename/delete/recreate histories, and verify no mapping points from a currently existing page.
