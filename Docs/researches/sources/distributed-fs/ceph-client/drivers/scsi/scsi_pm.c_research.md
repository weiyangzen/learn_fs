# sources/distributed-fs/ceph-client/drivers/scsi/scsi_pm.c

## Purpose

`scsi_pm.c` supplies SCSI bus power-management operations. It coordinates system suspend/resume/freeze/thaw/poweroff/restore for SCSI devices, integrates runtime PM with block queue PM, and exposes helper functions for SCSI core and transports to hold and release runtime PM references on devices, targets, and hosts.

## Important APIs, types, and functions

`const struct dev_pm_ops scsi_bus_pm_ops` is the exported PM operations table consumed by `scsi_bus_type` in `scsi_sysfs.c`. System-sleep helpers include `scsi_bus_prepare()`, `scsi_bus_suspend_common()`, and `scsi_bus_resume_common()`, with small callback wrappers for driver PM hooks: `do_scsi_suspend()`, `do_scsi_freeze()`, `do_scsi_poweroff()`, `do_scsi_resume()`, `do_scsi_thaw()`, and `do_scsi_restore()`. Runtime PM helpers include `sdev_runtime_suspend()`, `sdev_runtime_resume()`, and `scsi_runtime_idle()`. Exported or internal reference helpers are `scsi_autopm_get_device()`, `scsi_autopm_put_device()`, `scsi_autopm_get_target()`, `scsi_autopm_put_target()`, `scsi_autopm_get_host()`, and `scsi_autopm_put_host()`.

## Control flow

For system sleep, the bus prepare hook waits for asynchronous scans to complete for host devices. For SCSI device objects, suspend-like paths first call `scsi_device_quiesce()`, then invoke the bound SCSI driver's PM callback if one exists. If the callback fails, the device is resumed to undo quiescing. Resume-like paths call the driver PM callback first and then always call `scsi_device_resume()`.

Runtime suspend for a SCSI device calls `blk_pre_runtime_suspend()` on the request queue, then the driver's `runtime_suspend()`, then `blk_post_runtime_suspend()` with the driver result. Runtime resume mirrors this with `blk_pre_runtime_resume()`, optional driver `runtime_resume()`, and `blk_post_runtime_resume()`. Runtime idle autosuspends SCSI devices and returns `-EBUSY` to keep the PM core from treating the device as fully idle immediately.

## State and persistence behavior

The file mutates runtime PM usage counters and request-queue PM state through the PM core and block layer. It does not own durable storage. System suspend temporarily quiesces device I/O and restores it on resume or suspend failure. `scsi_autopm_get_*()` increments runtime PM references; matching put calls are required to avoid keeping hardware permanently active.

## Dependencies and integration points

The file depends on `linux/pm_runtime.h`, `linux/blk-pm.h`, SCSI device/driver/host types, and `scsi_priv.h`. It integrates with `scsi_sysfs.c` through `scsi_bus_type.pm`, with scanning via `scsi_complete_async_scans()`, with discovery/removal via `scsi_autopm_get_host()`/`put_host()`, and with target/device registration in sysfs code through target and device autopm calls.

## Risks and edge cases

Suspend ordering is sensitive: scanning must finish before host suspend, and device queues must be quiesced before driver callbacks. Runtime PM get helpers treat `-EACCES` as a non-fatal disabled-runtime-PM case but roll back other negative errors; callers need to understand that success can mean PM was forbidden. Missing put calls leak PM references. The target get/put helpers ignore return values, unlike device and host helpers. Driver callbacks may run while transport-specific hooks are absent; the comments explicitly leave host/target/transport runtime hooks for future insertion.

## Test signals

System tests should cover suspend/resume with synchronous and asynchronous scanning, failed driver suspend callbacks, and resume after queued I/O. Runtime PM tests should verify block queue PM transitions, autosuspend scheduling, disabled-runtime-PM behavior, and balanced autopm references during scan, add, remove, and sysfs registration. Compile tests should cover `CONFIG_PM_SLEEP` off, where sleep hooks become `NULL`, and `CONFIG_PM` off, where `scsi_priv.h` supplies stubs.
