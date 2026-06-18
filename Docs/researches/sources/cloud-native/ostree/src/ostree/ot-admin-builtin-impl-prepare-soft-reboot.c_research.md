<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-impl-prepare-soft-reboot.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-impl-prepare-soft-reboot.c

## Purpose
Implements a hidden internal command that delegates soft-reboot preparation to the private OSTree command API.

## Important APIs and Types
Exports `ot_admin_builtin_impl_prepare_soft_reboot` and calls `ostree_cmd__private__()->ostree_prepare_soft_reboot`.

## Control Flow
There is no option parsing in this wrapper. It invokes the private preparation function and returns its boolean result.

## State and Persistence
Any state changes, such as preparing runtime files for a soft reboot, are performed by the private library function.

## Dependencies and Integration Points
Depends on `ostree-cmd-private.h` and is registered conditionally by the admin command table when soft reboot support is enabled.

## Risks
The wrapper has minimal validation and relies entirely on private API preconditions and service-level invocation.

## Test Signals
Private soft-reboot preparation tests and hidden command invocation smoke tests cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-impl-prepare-soft-reboot.c -->
