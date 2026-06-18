# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_devlink.c

## Purpose
`qed_devlink.c` provides the `devlink` integration for the `qed` core. It registers a devlink instance, exposes firmware and board identity through `devlink info`, provides one runtime driver parameter for iWARP CMT mode, and creates a firmware-fatal health reporter capable of collecting a binary debug dump and initiating driver recovery.

## Important APIs, Types, And Functions
`enum qed_devlink_param_id` reserves `QED_DEVLINK_PARAM_ID_IWARP_CMT` after generic devlink ids. `struct qed_fw_fatal_ctx` carries an `enum qed_hw_err_type` to reporter dump context.

`qed_report_fatal_error()` is the external reporting entrypoint. If a firmware reporter exists, it calls `devlink_health_report()` with a fatal message and error context. `qed_fw_fatal_reporter_dump()` allocates a `vzalloc()` buffer sized by `qed_dbg_all_data_size()`, optionally sets `cdev->print_dbg_data` when invoked after a fatal event, collects debug data via `qed_dbg_all_data()`, and emits it with `devlink_fmsg_binary_pair_put()`. `qed_fw_fatal_reporter_recover()` delegates recovery to `qed_recovery_process()`.

`qed_fw_reporters_create()` and `qed_fw_reporters_destroy()` manage the `fw_fatal` health reporter. `qed_dl_param_get()` and `qed_dl_param_set()` read and write `cdev->iwarp_cmt`. `qed_devlink_info_get()` publishes board serial number from `hwfns[0].hw_info.part_num`, stored management firmware version from `common_dev_info.mfw_rev`, and running app firmware version from `common_dev_info.fw_*`. `qed_devlink_register()` allocates and registers devlink state; `qed_devlink_unregister()` reverses the setup.

## Control Flow
Registration starts in `qed_devlink_register()`: allocate devlink private storage, store `cdev`, register the `iwarp_cmt` parameter, default `cdev->iwarp_cmt` to false, create firmware health reporters, then call `devlink_register()`. Unregistration calls `devlink_unregister()`, destroys the reporter, unregisters params, and frees the devlink object.

Fatal reporting is asynchronous to normal lifecycle. A hardware error path calls `qed_report_fatal_error()`, devlink invokes the reporter dump callback when requested, and the recover callback invokes the driver's recovery process. Info queries are pull-based from userspace and read already-populated device information.

## State And Persistence Behavior
The devlink private object stores only `cdev` and the reporter pointer. The `iwarp_cmt` parameter persists in memory as `cdev->iwarp_cmt` for the life of the device and is runtime-changeable. Reporter dumps are transient vmalloc buffers. `cdev->print_dbg_data` is temporarily set based on whether dump context exists, but this function does not restore it, so later debug behavior depends on wider driver expectations.

## Dependencies And Integration Points
This file depends on Linux `devlink`, `devlink_health_reporter`, vmalloc, `qed_dbg_all_data*()`, `qed_recovery_process()`, and common device information populated during hardware prepare/init. `qed_main.c` wires these functions into the public common operations table as `.devlink_register`, `.devlink_unregister`, and `.report_fatal_error`. Userspace integration is through `devlink info`, `devlink param`, and `devlink health`.

## Risks And Edge Cases
Reporter creation failure is logged and tolerated by setting `fw_reporter` to `NULL`, so fatal errors may not produce devlink reports on low-memory or API failure paths. Dump allocation size is determined by firmware debug data size and can be large; allocation or collection failure aborts the dump. `qed_report_fatal_error()` always returns 0 even when no reporter exists. Parameter setting has no validation beyond the boolean type and may interact with hardware modes that are not active until other code observes `cdev->iwarp_cmt`.

## Test Signals
Tests should verify devlink registration/unregistration without leaks, runtime get/set of `iwarp_cmt`, `devlink info` content after successful hardware discovery, reporter creation failure handling, fatal error reporting with and without a reporter, dump allocation failure, debug data collection failure, and recover callback invocation of `qed_recovery_process()`. User-visible signals are devlink health events, binary dump presence, and firmware version strings.
