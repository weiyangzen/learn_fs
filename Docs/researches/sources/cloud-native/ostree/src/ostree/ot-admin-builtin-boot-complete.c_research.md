<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-boot-complete.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-boot-complete.c

## Purpose
Implements the hidden `ostree admin boot-complete` command run by systemd after booting an OSTree deployment.

## Important APIs and Types
Exports `ot_admin_builtin_boot_complete`. It uses `OSTREE_PATH_BOOTED` as a sanity check and calls `ostree_cmd__private__()->ostree_boot_complete`.

## Control Flow
If the system is not booted into OSTree, it exits successfully. Otherwise it asserts systemd provided `INVOCATION_ID`, parses admin options requiring superuser sysroot access, and invokes the private library boot-complete operation.

## State and Persistence
The command delegates persistent boot-completion state changes to the private OSTree library operation, likely marking deployments as successfully booted and clearing pending state.

## Dependencies and Integration Points
Uses `ostree-cmd-private.h`, admin option parsing, sysroot loading, and systemd service invocation context.

## Risks
The `INVOCATION_ID` assertion can abort if manually invoked inside an OSTree boot. Correct behavior depends on private API semantics and systemd mount namespace setup.

## Test Signals
Service-level tests for boot-complete on booted and non-booted systems, plus private API tests for deployment state updates, are key.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-boot-complete.c -->
