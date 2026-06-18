<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-pin.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-pin.c

## Purpose
Implements `ostree admin pin`, setting or clearing the pinned state of deployments so cleanup does or does not prune them.

## Important APIs and Types
Exports `ot_admin_builtin_pin`. Option `--unpin` clears pins. Helpers `get_deployment_index_for_type` and `do_pinning` resolve symbolic indices and apply `ostree_sysroot_deployment_set_pinned`.

## Control Flow
After parsing superuser context, each argument is parsed as `booted`, `pending`, `rollback`, or a numeric deployment index. The command resolves the deployment, compares current and desired pin state, prints idempotent status or applies the change.

## State and Persistence
Mutates deployment pin metadata in the sysroot.

## Dependencies and Integration Points
Uses deployment list queries, booted/pending/rollback identification, `ot_admin_get_indexed_deployment`, and sysroot pin APIs. Cleanup behavior consumes the pin state.

## Risks
Symbolic resolution depends on a booted deployment to identify pending/rollback. Numeric parsing checks invalid characters and range errors, but selected deployments can change if deployment order changes between commands.

## Test Signals
Tests should cover numeric and symbolic indices, missing type, invalid index, already pinned/unpinned idempotence, multiple indices, and cleanup retaining pinned deployments.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-pin.c -->
