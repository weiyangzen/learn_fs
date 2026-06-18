<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-finalize-staged.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-finalize-staged.c

## Purpose
Implements the hidden `ostree admin finalize-staged` command used by `ostree-finalize-staged.service` to finish staged deployments at shutdown.

## Important APIs and Types
Exports `ot_admin_builtin_finalize_staged`. Option `--hold` keeps `/boot` open until SIGTERM. It delegates finalization to `ostree_cmd__private__()->ostree_finalize_staged`.

## Control Flow
If not booted into OSTree, it exits successfully. It first parses without loading the sysroot. With `--hold`, it loads the sysroot unlocked, relies on the sysroot keeping `/boot` open, and blocks in `pause()`. Without `--hold`, it loads normally with superuser access and invokes private staged-finalization.

## State and Persistence
Finalization mutates staged deployment and bootloader state through the private API. Hold mode keeps file descriptors and process state alive but does not itself write deployment data.

## Dependencies and Integration Points
Integrates with systemd shutdown units, sysroot loading flags, private command APIs, signal behavior, and mount namespace expectations.

## Risks
Hold mode intentionally blocks until a signal. Loading flags are subtle: unlocked loading avoids a separate namespace so `/boot` remains held correctly. Manual invocation outside the service path can be surprising.

## Test Signals
Systemd integration tests for staged deployment finalization, lock/hold behavior, non-booted no-op behavior, and bootloader updates are needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-finalize-staged.c -->
