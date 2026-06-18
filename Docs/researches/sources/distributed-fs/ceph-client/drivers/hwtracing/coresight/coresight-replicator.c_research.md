# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-replicator.c

## Purpose
This file implements the CoreSight replicator link driver. A replicator splits one incoming trace stream to one or two outgoing trace paths. The driver supports static replicators and programmable dynamic replicators.

## Important APIs, Types, And Functions
`struct replicator_drvdata` stores MMIO base, clocks, the CoreSight device, a raw spinlock, and `check_idfilter_val` for hardware that loses filter context when clocks are removed. `dynamic_replicator_enable()` clears `REPLICATOR_IDFILTER0` or `REPLICATOR_IDFILTER1` to enable an output port, claiming the device when both filters were disabled. `dynamic_replicator_disable()` writes `0xff` to the selected filter and disclaims when both outputs are disabled. `replicator_enable()` and `replicator_disable()` wrap those operations in CoreSight link refcounting using `out->src_refcnt`. Sysfs management attributes expose `idfilter0` and `idfilter1`.

## Control Flow And State
Probe enters through platform or AMBA paths and shares `replicator_probe()`. It allocates a unique name, enables clocks, maps MMIO if present, reads firmware topology, initializes the spinlock, registers a `CORESIGHT_DEV_TYPE_LINK` with split subtype, and resets programmable hardware to both outputs disabled. The Qualcomm context-loss property makes enable treat both zero filters as equivalent to reset-disabled `0xff`.

## Dependencies And Integration Points
The driver uses CoreSight claim helpers, runtime PM clocks, AMBA IDs, OF/ACPI matches, `coresight_get_platform_data()`, and `coresight_init_driver()`. It is a path-builder link device, so its correctness depends on `struct coresight_connection` source-port refcounts.

## Risks And Test Signals
Only output ports 0 and 1 are supported; invalid ports trigger `WARN_ON()` and `-EINVAL` or return. Context-loss recovery is hardware-specific and depends on firmware declaring `qcom,replicator-loses-context`. Refcount imbalance can leave a filter open or prematurely disclaim the component. Test signals include dynamic and static probe, sysfs reads of ID filters, dual-output tracing, repeated enable/disable on the same outport, context-loss after runtime suspend, and claim failure propagation.
