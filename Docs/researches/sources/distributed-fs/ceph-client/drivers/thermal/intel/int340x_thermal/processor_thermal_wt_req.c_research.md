# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_req.c

## Purpose

`processor_thermal_wt_req.c` exposes user-requested workload type selection through a `workload_request` sysfs group backed by processor thermal mailbox commands.

## Important APIs, Types, and Functions

The workload type table includes `none`, `idle`, `semi_active`, `bursty`, `sustained`, and `battery_life`. Attributes are `workload_available_types` and read/write `workload_type`. Exports are `proc_thermal_wt_req_add()` and `proc_thermal_wt_req_remove()`.

## Control Flow

Add first probes mailbox read support and returns success without sysfs if unsupported. When supported, it creates the group. Writing parses a string, maps it to an index, sets valid/AC-DC bits for nonzero types, and sends a mailbox write. Reading sends mailbox read, masks to 8 bits, validates range, and prints the workload string.

## State and Persistence Behavior

Only `workload_req_created` is stored in the driver. Requested workload state persists in firmware/mailbox-controlled hardware until changed.

## Dependencies and Integration Points

It depends on processor thermal mailbox helpers and common MMIO setup. The core MMIO add path selects this feature when `PROC_THERMAL_FEATURE_WT_REQ` is set and no hint-only path is used.

## Risks and Test Signals

Risks include returning `false` instead of a negative errno on mailbox read/write failure, static group-created state across devices, and silently treating unsupported mailbox as successful feature add. Test signals include available type formatting, all workload writes, readback validation, unsupported mailbox probe, and group removal after creation.
