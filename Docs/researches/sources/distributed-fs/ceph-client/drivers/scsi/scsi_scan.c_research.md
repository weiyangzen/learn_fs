# sources/distributed-fs/ceph-client/drivers/scsi/scsi_scan.c

## Purpose

`scsi_scan.c` implements SCSI target and logical-unit discovery. It allocates targets and devices, probes LUNs with INQUIRY and REPORT LUNS, applies device quirk flags, configures request queues and transport state, publishes discovered devices through sysfs, supports synchronous/asynchronous scanning, manual rescans, device resume/rescan helpers, host teardown, and pseudo-device allocation for host-internal commands.

## Important APIs, types, and functions

Public or cross-file entry points include `scsi_enable_async_suspend()`, `scsi_complete_async_scans()`, `scsi_sanitize_inquiry_string()`, `__scsi_add_device()`, `scsi_add_device()`, `scsi_resume_device()`, `scsi_rescan_device()`, `scsi_scan_target()`, `scsi_scan_host_selected()`, `scsi_scan_host()`, `scsi_forget_host()`, and `scsi_get_pseudo_sdev()`. Target/device internals are centered on `scsi_alloc_target()`, `scsi_target_reap()`, `scsi_alloc_sdev()`, `scsi_probe_lun()`, `scsi_add_lun()`, `scsi_probe_and_add_lun()`, `scsi_report_lun_scan()`, and `scsi_sequential_lun_scan()`.

Important state includes module parameters `max_luns`, `scan`, and `inq_timeout`; `async_scan_lock`; `scanning_hosts`; `struct async_scan_data`; target `reap_ref`; host lists `__targets` and `__devices`; `shost->scan_mutex`; and per-device queue/budget/VPD/inquiry fields initialized during allocation and probing.

## Control flow

Host scanning begins in `scsi_scan_host()`. Unless `scan=none` or `scan=manual`, it obtains a host runtime-PM reference, prepares an asynchronous scan when allowed, and either schedules `do_scan_async()` or runs `do_scsi_scan_host()` synchronously. The default scanner calls `scsi_scan_host_selected()` with wildcards; host templates can override this with `scan_start()`/`scan_finished()` polling.

`scsi_scan_host_selected()` validates channel/id/lun bounds, serializes through `scan_mutex`, waits for earlier async scans when needed, obtains host runtime PM, and scans channels/targets. `__scsi_scan_target()` skips the host adapter id, allocates or finds a target, probes LUN 0, and then chooses REPORT LUNS or sequential scanning. REPORT LUNS uses a temporary LUN-0 device if necessary, resizes the response buffer if the target reports more LUN data than initially allocated, and probes each returned LUN. Sequential scanning walks LUNs with quirk-controlled limits until the first missing non-sparse LUN.

Each LUN probe allocates a `scsi_device` if no existing visible device matches. `scsi_probe_lun()` issues INQUIRY in up to three passes, tolerating unit attention and some timeouts, sanitizes vendor/model/rev strings, derives device flags, records SCSI level, and decides whether LUN bits belong in CDB[1]. `scsi_add_lun()` copies inquiry data, sets device type/removability/queueing/quirk fields, transitions the device to running or blocked, configures transport and queue limits, calls low-level `sdev_configure()`, attaches VPD/CDL data, and either publishes immediately through `scsi_sysfs_add_sdev()` or defers publication during async scan. Async completion waits for previous async scans in list order, then publishes all deferred devices with `scsi_sysfs_add_devices()`.

## State and persistence behavior

Discovery persists as live `scsi_target` and `scsi_device` objects on host lists, with sysfs visibility added later by `scsi_sysfs.c`. Target lifetime is controlled by both device references and `reap_ref`; targets allocated during scans are destroyed if no child device becomes visible. Per-device persistent state includes INQUIRY copies, vendor/model/rev pointers, quirk flags, queue depth, budget map, runtime PM state, VPD pages, CDL support, and transport configuration. Module parameters influence all later scans until changed. Async scan ordering persists through `scanning_hosts` completions so devices discovered by earlier scans are announced first.

## Dependencies and integration points

The file depends on block-mq queues and queue limits, SCSI command execution, device-info quirks, transport templates, device handlers, VPD/CDL helpers, PM helpers from `scsi_pm.c`, sysfs add/remove functions from `scsi_sysfs.c`, and logging macros from `scsi_logging.h`. It is called by host registration, procfs/sysfs manual scan paths, transport code such as SAS, and exported `scsi_add_device()` consumers. It calls low-level driver hooks including `target_alloc`, `target_destroy`, `sdev_init`, `sdev_configure`, `change_queue_depth`, and host-template scan callbacks.

## Risks and edge cases

Scan code is race-sensitive. It must avoid duplicate targets while allowing a dying target to finish teardown, balance target reap references, and not publish devices out of async order. INQUIRY handling deliberately works around broken devices; changes can regress legacy USB, RBC/MMC, sparse LUN, floptical, and SCSI-2 behavior. REPORT LUNS fallback decisions depend on SCSI level, host `max_lun`, and blacklist flags; incorrect fallback can miss devices or hang on broken targets. Queue budget map reallocation freezes queues when resizing and must preserve the old map on failure. Manual and automatic scans must respect `scan=none`, `scan=manual`, host state, and runtime PM.

## Test signals

High-value tests include host scans with sync and async modes, `scan=manual`/`none`, manual sysfs/proc scans, LUN 0 absent/present combinations, REPORT LUNS success/failure/fallback, sparse LUN quirks, SCSI-2 LUN-in-CDB behavior, BLIST flags such as `NOREPORTLUN`, `FORCELUN`, `MAX5LUN`, `INQUIRY_36`, and `KEY`, and removal while scanning. KUnit or fault-injection tests should cover allocation failures, queue budget map resize failures, INQUIRY retries, malformed short inquiry data, and async scan completion ordering. Runtime validation should confirm sysfs devices appear only after successful `scsi_sysfs_add_sdev()` and that teardown through `scsi_forget_host()` removes pseudo devices last.
