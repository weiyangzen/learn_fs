<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-default.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-default.c

## Purpose
Implements `ostree admin set-default`, reordering deployments so a selected deployment becomes default.

## Important APIs and Types
Exports `ot_admin_builtin_set_default`; uses `ot_admin_get_indexed_deployment`, `ostree_sysroot_write_deployments`, and `ostree_sysroot_cleanup`.

## Control Flow
The command parses superuser context, requires an index, fetches current deployments, resolves the target deployment, removes it from its current position, inserts it at index 0, writes deployments, and runs cleanup.

## State and Persistence
Persists deployment order and bootloader state through sysroot write and cleanup operations.

## Dependencies and Integration Points
Uses shared admin helper and sysroot deployment APIs. Deployment order affects boot default and status output.

## Risks
The index is parsed with `atoi`, so invalid strings become 0 rather than explicit errors. Removing/inserting assumes the deployment list has not changed after resolving the target.

## Test Signals
Tests should cover valid reordering, invalid and out-of-range input, preserving booted/rollback entries, and cleanup side effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-default.c -->
