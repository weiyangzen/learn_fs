<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-lock-finalization.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-lock-finalization.c

## Purpose
Implements `ostree admin lock-finalization`, toggling whether a staged deployment is automatically finalized at shutdown.

## Important APIs and Types
Exports `ot_admin_builtin_lock_finalization`. Option `--unlock` reverses the lock. It uses `ostree_sysroot_get_staged_deployment`, `ostree_deployment_is_finalization_locked`, and `ostree_sysroot_change_finalization`.

## Control Flow
After superuser sysroot parsing, it requires a staged deployment, checks current lock state, prints idempotent messages when no change is needed, otherwise toggles finalization and prints the resulting state.

## State and Persistence
Mutates staged deployment metadata/state through `ostree_sysroot_change_finalization`.

## Dependencies and Integration Points
Uses private sysroot headers and admin parser. It complements `deploy --lock-finalization` and shutdown finalization services.

## Risks
The command assumes exactly the current staged deployment is the target. Correctness depends on `change_finalization` toggling the intended persistent metadata and any legacy runstate compatibility.

## Test Signals
Tests should cover no staged deployment, lock, unlock, idempotent lock/unlock, and later finalize-staged behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-lock-finalization.c -->
