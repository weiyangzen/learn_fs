# sources/distributed-fs/ceph-client/include/uapi/linux/taskstats.h

## Purpose
Defines the generic netlink ABI for exporting per-task and per-thread-group accounting, delay accounting, I/O accounting, memory high-water marks, context switches, executable identity, and delay extrema/timestamps.

## Important APIs, Types, and Constants
`TASKSTATS_VERSION` is 17 and `TS_COMM_LEN` is 32. `struct taskstats` contains versioned fields that must only grow at the end: exit code, accounting flags, CPU/block/swap/freepage/thrashing/compact/write-protect/IRQ delay counts and totals, basic accounting, memory and I/O usage, context switches, scaled CPU times, 64-bit begin time, thread group fields, executable device/inode, delay min/max values, and max timestamps as `struct __kernel_timespec`. Netlink enums define commands (`TASKSTATS_CMD_GET`, `TASKSTATS_CMD_NEW`), types (`TASKSTATS_TYPE_PID`, `TASKSTATS_TYPE_TGID`, `TASKSTATS_TYPE_STATS`, aggregate forms), command attributes, family name `TASKSTATS`, and version.

## Control Flow, State, and Persistence
Userspace requests stats for PID/TGID or registers CPU masks for exit events. Kernel snapshots task accounting state into this append-only struct. Values are per-task runtime state and may wrap as documented.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and `<linux/time_types.h>`. Integrates with delay accounting, BSD process accounting concepts, generic netlink, and monitoring/accounting tools.

## Risks and Test Signals
Risks include struct version/offset drift, non-atomic delay counter reads, overflow, and differing availability when delay accounting is disabled. Test netlink request/response parsing, old-version userspace prefix compatibility, 64-bit alignment, disabled delay accounting, process exit events, and cputime/memory/I/O sanity.
