<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-undeploy.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-undeploy.c

## Purpose
Implements `ostree admin undeploy`, deleting a non-booted deployment by index.

## Important APIs and Types
Exports `ot_admin_builtin_undeploy`; uses `ot_admin_get_indexed_deployment`, `ostree_sysroot_write_deployments`, and `ostree_sysroot_cleanup`.

## Control Flow
After superuser parsing, it requires an index, parses it with `g_ascii_strtoull`, resolves the target, rejects the currently booted deployment, removes it from the deployment array, writes the new array, prints the deleted checksum/serial, and performs cleanup.

## State and Persistence
Persists deployment list changes and removes eligible deployment/repo data during cleanup.

## Dependencies and Integration Points
Uses shared admin helpers and sysroot deployment APIs. It interacts with cleanup, pinning, and bootloader state.

## Risks
Index parsing checks invalid trailing characters but not `ERANGE`. Removing deployments can affect rollback/default ordering. Booted deployment protection is essential.

## Test Signals
Tests should cover missing/invalid/out-of-range index, booted rejection, deletion of pending/rollback entries, cleanup side effects, and status output after undeploy.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-undeploy.c -->
