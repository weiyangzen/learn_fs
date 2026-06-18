# sources/cloud-native/ostree/src/ostree/ot-builtin-fsck.c

## Purpose
Implements `ostree fsck`, validating repository refs, collection refs, commit bindings, optional back references, and reachable object integrity. It can report all corruption, delete corrupted objects, mark partial commits, and add tombstones for commits whose parents are missing.

## Important APIs, Types, And Functions
`ostree_builtin_fsck()` orchestrates the command. `fsck_one_object()` verifies a single object, reports missing/corrupt parents, optionally deletes corrupt objects, and marks parent commits partial. `fsck_reachable_objects_from_commits()` traverses non-partial commits and validates reachable objects with progress. `fsck_commit_for_ref()` validates ref targets and optional bindings. `fsck_one_commit()` validates back references and gathers tombstone candidates. Private binding verification is reached through `ostree_cmd__private__()->ostree_repo_verify_bindings()`.

## Control Flow
The command parses options, lists normal refs, checks each ref's commit and optional binding metadata, lists local collection refs and checks them similarly, then enumerates all commit objects. It loads every commit, validates optional back references, records partial and fsck-partial counts, optionally collects tombstones, and adds only non-partial commits to the set for full object traversal. It traverses reachable objects from those commits, fscks each object, and updates progress. If tombstone mode is enabled, it enables tombstone commits and deletes selected commit objects. Finally it reports partial commits, fails on found corruption or fsck-partial commits, and prints success otherwise.

## State And Persistence
Normal validation is read-only. `--delete` removes corrupted objects and marks commits partial with `OSTREE_REPO_COMMIT_STATE_FSCK_PARTIAL`. `--add-tombstones` enables tombstone support and deletes missing-parent commits to create tombstones. Partial state persists in commit state metadata.

## Dependencies And Integration Points
This file depends on repository traversal, object fsck, commit state, collection refs, binding metadata, tombstone support, and console progress. It enforces invariants relied on by pull, commit binding verification, prune, and repository serving.

## Risks And Edge Cases
`--all` continues after corrupt non-missing objects but still fails at the end. Missing objects with parent information trigger partial marking for parent commits except when the missing object is itself a commit. `--verify-back-refs` implies binding verification. Collection refs are checked excluding remotes, while prune has a FIXME about collection refs in one branch. `n_fsck_partial` failure text uses `n_partial`, which may overstate the fsck-partial count.

## Test Signals
Tests should inject missing content, corrupt objects, missing commits, invalid ref bindings, invalid back references, partial commits, tombstone creation, delete behavior, quiet output, all-errors behavior, and collection-ref validation.
