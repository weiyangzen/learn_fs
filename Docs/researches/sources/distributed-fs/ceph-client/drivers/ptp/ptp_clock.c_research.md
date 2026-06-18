# sources/distributed-fs/ceph-client/drivers/ptp/ptp_clock.c Research

## Purpose
`ptp_clock.c` is the common PTP hardware clock framework core. It registers the `ptp` class and character-device region, creates POSIX clock devices, manages PPS sources, queues timestamp events to open file descriptors, and exposes registration helpers for hardware drivers.

## Important APIs, Types, And Functions
Public exports include `ptp_clock_register()`, `ptp_clock_unregister()`, `ptp_clock_event()`, `ptp_clock_index()`, `ptp_clock_index_by_of_node()`, `ptp_clock_index_by_dev()`, `ptp_find_pin()`, `ptp_find_pin_unlocked()`, `ptp_schedule_worker()`, and `ptp_cancel_worker_sync()`. It defines `ptp_clock_ops` for POSIX clock callbacks and uses an xarray to allocate stable clock indexes.

## Control Flow
`ptp_init()` registers the class and chrdev region at subsystem init. Hardware drivers call `ptp_clock_register()` with `ptp_clock_info`; the core validates required callbacks, allocates `struct ptp_clock`, allocates an index, creates the default event queue, initializes locks and waitqueue, fills missing cycle helpers, starts an auxiliary kthread worker if requested, handles virtual-clock metadata, populates pin sysfs groups, optionally registers a PPS source, initializes the device, and calls `posix_clock_register()`. Unregister marks the clock defunct, wakes readers, unregisters POSIX clock, disables events, stops worker, unregisters PPS, and drops the device reference. `ptp_clock_event()` fans EXTTS/EXTOFF events into subscribed queues and forwards PPS events to the PPS subsystem.

## State And Persistence
Persistent runtime state includes class devices `/dev/ptpN`, xarray index mapping, per-clock pin config, default and per-open timestamp queues, PPS source, virtual-clock bookkeeping, and dialed frequency. Event queues are bounded ring buffers that overwrite oldest events when full.

## Dependencies And Integration Points
The core depends on POSIX clocks, Linux device/class infrastructure, PPS, xarray, debugfs, sysfs helpers in other PTP files, and driver-provided `ptp_clock_info` operations. Network, PHY, FPGA, MFD, and virtual-machine drivers register through this layer.

## Risks
Registration has many unwind branches; resource ordering is important for queues, xarray entries, kworkers, PPS, and devices. `ptp_clock_adjtime()` enforces freerun checks and adjustment ranges, so bad driver `max_adj` or phase limits affect userspace. Event fanout holds `tsevqs_lock` while enqueueing into queues, requiring careful lock ordering. PPS events assume a registered PPS source when drivers emit PPS event types.

## Test Signals
Test signals include registering mock clocks with minimal callbacks, failed allocation unwind, PPS-capable registration, aux worker scheduling/cancel, clock set/get/adjtime UAPI behavior, unregister while readers block, event queue overflow, index lookup by device and OF node, and virtual-clock child unregister paths.
