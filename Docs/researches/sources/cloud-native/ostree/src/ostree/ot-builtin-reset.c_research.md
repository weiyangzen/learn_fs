# sources/cloud-native/ostree/src/ostree/ot-builtin-reset.c

## Purpose
Implements `ostree reset`, moving an existing normal ref to a target commit.

## Important APIs, Types, And Functions
`ostree_builtin_reset()` is the only function. It uses `ostree_repo_list_refs()` to validate the ref exists, `ostree_repo_resolve_rev()` to resolve the target, and `ostree_repo_prepare_transaction()`, `ostree_repo_transaction_set_ref()`, and `ostree_repo_commit_transaction()` to persist the ref update.

## Control Flow
The command parses options, opens a writable repo, requires `REF COMMIT`, lists known refs, rejects unknown refs, resolves the target revision to a checksum, prepares a transaction, queues the ref update, commits the transaction, and aborts any remaining transaction state on exit.

## State And Persistence
Successful execution changes one normal ref to point at the resolved target checksum. It does not create new refs and does not support collection refs, as noted by a FIXME. Objects are not written; the target must already resolve.

## Dependencies And Integration Points
This is a simple ref mutation command integrated with repository transactions and revision resolution. It overlaps conceptually with `ostree refs --create --force` but requires the ref already exist.

## Risks And Edge Cases
Collection refs are unsupported. The error domain/code for invalid refs uses `G_IO_ERROR` for both domain and code in the source, which looks suspicious because the code should normally be a `GIOErrorEnum`. Unknown refs are rejected before target resolution, so it cannot be used to create a ref.

## Test Signals
Tests should cover moving an existing ref, rejecting missing args, rejecting unknown refs, rejecting invalid target revisions, transaction rollback after induced commit failure, and documenting collection-ref unsupported behavior.
