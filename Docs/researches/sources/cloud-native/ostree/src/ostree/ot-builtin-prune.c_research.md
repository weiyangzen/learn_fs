# sources/cloud-native/ostree/src/ostree/ot-builtin-prune.c

## Purpose
Implements `ostree prune`, deleting or reporting unreachable objects and supporting explicit commit deletion, static-delta pruning, depth-based retention, branch-specific retention, branch filtering, age-based retention, and commit-only pruning.

## Important APIs, Types, And Functions
`ostree_builtin_prune()` is the entry point. `delete_commit()` ensures an explicit commit is not referenced before deleting it as a tombstone commit. `traverse_keep_younger_than()` builds a reachable set down a parent chain until commits are older than a parsed timestamp. The command uses `ostree_repo_prune()`, `ostree_repo_prune_static_deltas()`, `ostree_repo_traverse_commit_with_flags()`, `ostree_repo_prune_from_reachable()`, and exclusive repo locking.

## Control Flow
After parsing, the command requires writability unless `--no-prune`. If `--delete-commit` is set, it rejects `--no-prune`, then either prunes static deltas for that commit or verifies the commit is not referenced and deletes it. Without `--delete-commit`, `--static-deltas-only` is rejected. It builds prune flags and either delegates to the classic prune API when no advanced retention options are present, or manually computes reachability under an exclusive lock. The advanced path parses `--keep-younger-than`, parses `--retain-branch-depth` entries, lists refs, converts `--only-branch` into retain rules for all other refs, traverses refs according to per-branch or global depth/age rules, and prunes from the reachable set. It prints total objects and deleted or would-delete counts.

## State And Persistence
Normal prune deletes unreachable objects unless `--no-prune`. Explicit commit deletion enables tombstone commits and deletes the commit object. Static-delta-only mode deletes delta artifacts. Advanced prune holds an exclusive lock to avoid racing new content against reachability computation.

## Dependencies And Integration Points
The command integrates repo traversal, pruning APIs, tombstone support, static delta metadata, ref listing, date parsing, and repo locking. Its output and behavior are important for repository maintenance, mirror management, and storage reclamation.

## Risks And Edge Cases
Advanced pruning currently lists normal refs and has a FIXME about collection refs. `--only-branch` first verifies each named branch exists. Date parsing is user-facing and errors can block cleanup. Incorrect retention rules can delete history. `--commit-only` avoids traversing content and uses both traversal and prune flags. Static-deltas-only is intentionally restricted to explicit commit deletion.

## Test Signals
Tests should cover dry-run/no-prune counts, classic depth prune, explicit commit deletion rejection while referenced, tombstone creation, static delta pruning, keep-younger-than traversal, retain-branch-depth parsing and behavior, only-branch interactions, commit-only pruning, and concurrent lock behavior.
