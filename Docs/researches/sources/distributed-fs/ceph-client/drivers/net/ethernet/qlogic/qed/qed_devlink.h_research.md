# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.h

## Purpose
`qed_devlink.h` is the small internal declaration surface for the `qed` devlink integration. It lets the main driver register and unregister devlink state, create and destroy firmware health reporters, and report fatal hardware errors without exposing the implementation details in `qed_devlink.c`.

## Important APIs, Types, And Functions
The header declares `qed_devlink_register(struct qed_dev *cdev)`, `qed_devlink_unregister(struct devlink *devlink)`, `qed_fw_reporters_create(struct devlink *devlink)`, `qed_fw_reporters_destroy(struct devlink *devlink)`, and `qed_report_fatal_error(struct devlink *dl, enum qed_hw_err_type err_type)`. It includes `linux/qed/qed_if.h` for core qed types and `<net/devlink.h>` for the devlink object.

## Control Flow
The intended call flow is probe-side registration through `qed_devlink_register()`, optional reporter creation as part of registration, fatal-error reporting through `qed_report_fatal_error()` during error handling, and remove-side cleanup through `qed_devlink_unregister()`. The explicit reporter create/destroy declarations also allow code that already has a devlink object to manage health reporters independently, although current implementation creates them inside registration.

## State And Persistence Behavior
This header owns no state. The implementation stores state in devlink private data and in the associated `struct qed_dev`. Callers are responsible for retaining the returned `struct devlink *` and passing it back on unregister and fatal report paths.

## Dependencies And Integration Points
It is included by `qed_devlink.c` and by main/common operation wiring that exposes devlink support to the upper driver. Its dependency on netdev devlink APIs makes it kernel-version-sensitive if devlink function signatures change.

## Risks And Edge Cases
The declarations do not provide stubs for builds without devlink, implying the surrounding build always expects devlink support for this driver version. Callers must handle `ERR_PTR()` from register and `NULL` devlink in unregister. Fatal report callers should not assume the report produced a dump, because reporter creation may have failed.

## Test Signals
Compile coverage catches signature drift. Runtime signals are successful devlink registration, safe unregister on a valid pointer or `NULL`, and correct propagation of fatal report calls to the reporter when one exists.
