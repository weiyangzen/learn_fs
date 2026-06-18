# sources/cloud-native/ostree/man/ostree-prune.xml

Purpose: documents `ostree prune`, which finds and optionally deletes unreachable repository objects.

Important APIs/types: options `--no-prune`, `--refs-only`, `--delete-commit=COMMIT`, `--keep-younger-than=DATE`, `--depth=DEPTH`, `--static-deltas-only=DEPTH`, and `--commit-only`.

Control flow: traverses refs and commit history to determine reachability, optionally limits traversal by age/depth, supports targeted commit deletion, can report only, and can restrict deletion to commits or static deltas in supported combinations.

State and persistence: deletes repository objects/static deltas unless `--no-prune` is used.

Dependencies and integration: repository garbage collection, ref deletion, admin cleanup, static delta storage, and GNU date parsing for age cutoffs.

Risks and test signals: destructive; docs note `--static-deltas-only` currently requires `--delete-commit`. Signals are reachability tests, dry-run output, delete-commit/static-delta tests, and repository fsck after prune.
