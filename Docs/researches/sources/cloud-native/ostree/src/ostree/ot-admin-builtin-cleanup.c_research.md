<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-cleanup.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-cleanup.c

## Purpose
Implements `ostree admin cleanup`, which prunes untagged deployments and repository objects through the sysroot cleanup API.

## Important APIs and Types
Exports `ot_admin_builtin_cleanup`; its only option table is empty.

## Control Flow
The command parses admin context with superuser requirements, obtains an `OstreeSysroot`, then calls `ostree_sysroot_cleanup`.

## State and Persistence
Persistent mutations are delegated to sysroot cleanup: deployment directories, bootloader state, and repo object garbage collection may be affected.

## Dependencies and Integration Points
Depends on admin option parsing and `OstreeSysroot`. It is registered under `ostree admin cleanup`.

## Risks
Cleanup is destructive by design. Safety depends on sysroot APIs preserving booted, default, rollback, pending, staged, and pinned deployments correctly.

## Test Signals
Integration tests should verify cleanup retains required deployments and removes only eligible leftovers after deploy/undeploy/failure scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-cleanup.c -->
