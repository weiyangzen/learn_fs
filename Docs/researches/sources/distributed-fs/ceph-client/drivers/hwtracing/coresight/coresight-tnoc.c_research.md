# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tnoc.c

## Purpose

`coresight-tnoc.c` implements a Trace NoC CoreSight link/merger. It programs a trace network-on-chip block to emit ATB traffic, optionally allocates a system trace ID for AMBA-discovered instances, and supports both AMBA and platform/DT instantiation.

## Important APIs, Types, and Functions

`struct trace_noc_drvdata` stores MMIO base, device, CoreSight device, optional APB clock, spinlock, and ATID. `trace_noc_enable_hw` writes ATID, sync interval, packet type bits, and port enable. `trace_noc_enable`, `trace_noc_disable`, and `trace_noc_id` implement CoreSight link ops and trace-id reporting. `_tnoc_probe` is the common probe path; `trace_noc_probe/remove` cover AMBA, while `itnoc_probe/remove` cover platform devices. `traceid` sysfs is hidden when no ATID is available.

## Control Flow

Probe allocates a device name, gets platform data, enables clocks, maps registers, initializes the lock, chooses default ATID behavior, and registers a CoreSight link of subtype `LINK_MERG`. AMBA devices allocate a system trace ID through `coresight_trace_id_get_system_id`; platform ITNoC devices set `atid` to `-EOPNOTSUPP` and simply enable the block without programming ATID. Enable is refcounted under the spinlock and only touches hardware on the first user. Disable decrements the CoreSight refcount and clears `TRACE_NOC_CTRL` on final user.

## State and Persistence Behavior

The allocated ATID persists until AMBA remove, where it is released. Runtime state is limited to `csdev->refcnt`, the spinlock-protected enable state, and runtime PM clock state for platform devices. The hardware control register is not shadowed beyond drvdata fields.

## Dependencies and Integration Points

The driver depends on AMBA, platform devices, OF matching (`qcom,coresight-itnoc`), runtime PM, CoreSight platform data, CoreSight driver init helpers, clock helpers, and the shared trace ID allocator. It integrates as an intermediate link in CoreSight paths.

## Risks and Edge Cases

Platform remove unregisters CoreSight but does not release an ATID, which is correct only because platform probe never allocates one. AMBA remove unconditionally calls `coresight_trace_id_put_system_id(drvdata->atid)`; this path expects positive ATIDs. Refcount underflow would disable the block incorrectly if CoreSight core calls are unbalanced.

## Test Signals

Test AMBA and platform probe/remove, traceid visibility for AMBA versus platform, runtime PM clock suspend/resume, first-enable and final-disable register writes, and trace ID release on AMBA unregister.
