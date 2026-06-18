<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-prepare-soft-reboot.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-prepare-soft-reboot.c

## Purpose
Implements `ostree admin prepare-soft-reboot`, selecting a non-booted deployment as the soft-reboot target or clearing queued soft-reboot state.

## Important APIs and Types
Exports `ot_admin_builtin_prepare_soft_reboot`. Options are `--reboot` to execute `systemctl soft-reboot` after success and `--reset` to clear state.

## Control Flow
After superuser parsing, `--reset` immediately calls `ostree_sysroot_clear_soft_reboot`. Otherwise the command requires an index, parses it, resolves the deployment, rejects the currently booted deployment, marks the target with `ostree_sysroot_deployment_set_soft_reboot`, and optionally `execlp`s `systemctl soft-reboot`.

## State and Persistence
Mutates soft-reboot target state in deployment/sysroot metadata. With `--reboot`, the process image is replaced by systemctl.

## Dependencies and Integration Points
Uses shared indexed deployment helper, sysroot soft-reboot APIs, and systemd soft-reboot support.

## Risks
Index parsing does not check `ERANGE` explicitly. Preparing the booted deployment is rejected. The final `execlp` has no return on success, so callers must account for process replacement.

## Test Signals
Tests should cover reset, missing index, invalid index, booted deployment rejection, target marking, and systemctl exec failure paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-prepare-soft-reboot.c -->
