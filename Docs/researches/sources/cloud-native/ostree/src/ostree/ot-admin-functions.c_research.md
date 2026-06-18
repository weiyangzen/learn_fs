<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-functions.c

## Purpose
Provides shared helper functions for admin commands: booted deployment checks, commit version extraction, deployment lookup by index, sysroot lock waiting, and guarded reboot exec.

## Important APIs and Types
Exports `ot_admin_require_booted_deployment_or_osname`, `ot_admin_checksum_version`, `ot_admin_get_indexed_deployment`, `ot_admin_sysroot_lock`, and `ot_admin_execve_reboot`. Internal `ContextState` supports async lock waiting.

## Control Flow
The booted check returns an error only when neither a booted deployment nor explicit OS name exists. Version extraction reads commit metadata child 0. Indexed lookup validates bounds against current deployment array. Sysroot lock first tries nonblocking lock, then if needed attaches a 3-second repeating timeout that prints waiting messages, starts async lock acquisition, and iterates a private main context until acquired. Reboot only execs systemctl when the sysroot is actually booted.

## State and Persistence
No persistent state is directly changed except that lock acquisition changes sysroot lock ownership and reboot exec changes process state. The helper reads deployment arrays and commit metadata.

## Dependencies and Integration Points
Uses libglnx errors, GLib main contexts/sources, `OstreeSysroot` locking APIs, and systemctl exec. Many admin builtins depend on these helpers.

## Risks
The async lock callback does not inspect the async result in this file, relying on the lock API's behavior to wake after acquisition. `ot_admin_execve_reboot` intentionally no-ops on non-booted sysroots to avoid accidental build-host reboot. Index lookup operates on current order.

## Test Signals
Tests should cover no booted/no os error, indexed lookup bounds, version metadata presence/absence, lock wait messaging/acquisition, and reboot helper no-op vs exec failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.c -->
