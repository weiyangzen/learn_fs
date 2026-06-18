<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-os-init.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-os-init.c

## Purpose
Implements `ostree admin os-init` and the `stateroot-init` alias, initializing an empty deployment stateroot.

## Important APIs and Types
Exports `ot_admin_builtin_os_init`; uses `ostree_sysroot_ensure_initialized` and `ostree_sysroot_init_osname`.

## Control Flow
The command parses superuser admin context, ensures the sysroot exists, requires a `STATEROOT` argument, initializes that OS/stateroot name, and prints confirmation.

## State and Persistence
Creates or updates `ostree/deploy/<osname>` stateroot metadata on disk.

## Dependencies and Integration Points
Depends on admin option parsing and sysroot initialization. It is part of provisioning workflows before deployments are added.

## Risks
Input validation of stateroot names is delegated to sysroot APIs. Re-running against existing state must be handled idempotently by the library.

## Test Signals
Provisioning tests for new stateroot creation, missing argument, invalid names, and repeated initialization are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-os-init.c -->
