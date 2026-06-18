# sources/distributed-fs/ceph-client/drivers/scsi/scsi.c

## Purpose
`scsi.c` is a core SCSI mid-layer implementation file. It provides logging hooks, command completion handoff, queue-depth management, VPD discovery/cache helpers, command-duration-limit detection/enabling, device reference and lookup helpers, and module initialization/teardown for the SCSI subsystem.

## Important APIs, Types, And Functions
Exported helpers include `scsi_finish_command()`, `scsi_change_queue_depth()`, `scsi_track_queue_full()`, `scsi_get_vpd_page()`, `scsi_report_opcode()`, `scsi_device_get()`, `scsi_device_put()`, `__scsi_iterate_devices()`, `starget_for_each_device()`, `__starget_for_each_device()`, `__scsi_device_lookup_by_target()`, `scsi_device_lookup_by_target()`, `__scsi_device_lookup()`, and `scsi_device_lookup()`. Internal VPD helpers include `scsi_vpd_inquiry()`, `scsi_get_vpd_size()`, `scsi_get_vpd_buf()`, and `scsi_update_vpd_page()`. CDL helpers include `scsi_cdl_check_cmd()`, `scsi_cdl_check()`, and `scsi_cdl_enable()`. When logging is enabled, `scsi_log_send()` and `scsi_log_completion()` print command and completion details.

## Control Flow
Completion flow enters `scsi_finish_command()`, marks the device unbusy, clears host/target/device blocked counters, optionally lets the upper SCSI driver adjust good-byte count through `drv->done()`, subtracts residuals when appropriate, and calls `scsi_io_completion()`. Queue-full flow coalesces events by jiffies bucket, tracks repeated depth values, and after enough repeated events calls `scsi_change_queue_depth()`.

VPD flow issues INQUIRY EVPD commands, validates supported page lists and lengths, allocates/caches selected VPD pages under `inquiry_mutex` using RCU replacement, and frees old pages with `kfree_rcu()`. RSOC/CDL flow uses MAINTENANCE IN to check opcode support and command duration limit bits, then may force READ/WRITE(16) usage and enable ATA CDL through mode sense/select. Device lookup flows take `host_lock`, skip deleted devices, and return either borrowed or refcounted SCSI devices.

Subsystem init registers procfs, devinfo, hosts, sysctl, sysfs, and netlink in order; failure unwinds previously initialized layers. Exit reverses those registrations.

## State And Persistence
Global state includes `scsi_logging_level` and subsystem registrations. Per-device state updated here includes queue depth, budget maps, queue-full counters, VPD RCU pointers, CDL support/enable flags, command-size behavior flags, and device references. No persistent disk state is written, but SCSI MODE SELECT may change volatile or device-defined CDL feature state for ATA-backed devices.

## Dependencies And Integration Points
This file depends on block queues, SCSI command execution, SCSI device/target/host structures, RCU, mutexes, spinlocks, sysfs/proc/sysctl/netlink initialization, tracepoints, and optional logging support. It is a central integration point for lower-level drivers, upper SCSI device drivers, user-visible SCSI subsystem initialization, and standards-driven VPD/RSOC/CDL device capabilities.

## Risks And Edge Cases
VPD probing must handle devices that lie about page support or length; the code uses conservative header probes, warnings, and retries. `scsi_change_queue_depth()` returns `-EINVAL` without a budget map, so low-level callers must handle unsupported depth changes. CDL enabling for ATA devices rewrites mode data and can reset device CDL statistics. Lookup helpers have strict locking/reference semantics; misuse can lead to use-after-free or module unload races. Initialization failure paths must stay paired with subsystem registration order.

## Test Signals
Signals include SCSI subsystem init and failure unwinds, logging-level output, normal command completion with driver `done()` and residual adjustment, queue-full depth reduction after repeated events, VPD page 0/0x80/0x83/0x89/0xb0/0xb1/0xb2/0xb7 attachment, long/short/missing VPD handling, RSOC support and illegal-request handling, CDL enable/disable for ATA and non-ATA devices, device get/put during deletion or module unload, locked and refcounted device lookup helpers, and clean subsystem exit.
