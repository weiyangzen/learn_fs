# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpiu.c

## Purpose

`coresight-tpiu.c` implements the Arm CoreSight Trace Port Interface Unit as an output sink. It registers AMBA and platform/ACPI TPIU devices, manages optional clocks and runtime PM, and provides enable/disable sink operations.

## Important APIs, Types, and Functions

`struct tpiu_drvdata` stores MMIO base, optional ATCLK/PCLK, CoreSight device, and spinlock. `tpiu_enable_hw` currently only unlocks and locks the device around a TODO. `tpiu_disable_hw` programs formatter stop-on-flush, triggers manual flush, waits for flush completion and formatter stopped, then relocks. CoreSight sink ops are `tpiu_enable` and `tpiu_disable`. Common probe/remove logic is in `__tpiu_probe` and `__tpiu_remove`, with AMBA and platform wrappers.

## Control Flow

Probe allocates a CoreSight name, drvdata, clocks, maps registers, disables the TPIU for older devices, gets platform data, and registers a CoreSight sink of subtype `SINK_PORT`. Enable locks, calls the mostly-empty hardware enable hook, increments refcount, and returns success. Disable decrements refcount and only flushes/stops hardware on the final user; otherwise it returns `-EBUSY`.

## State and Persistence Behavior

Persistent state is drvdata plus CoreSight refcount. Runtime PM suspend disables ATCLK and PCLK, and resume re-enables PCLK then ATCLK with rollback on failure. No trace data is buffered in this driver.

## Dependencies and Integration Points

The driver depends on AMBA IDs, platform ACPI match `ARMHC979`, CoreSight core registration, clock helpers, runtime PM, and CoreSight timeout helpers. It integrates as a port sink at the end of CoreSight paths.

## Risks and Edge Cases

The enable path has no hardware programming beyond unlock/lock, so correctness depends on external/default TPIU configuration. Disable returns `-EBUSY` after decrementing when other users remain, matching sink conventions but requiring callers to tolerate that code. Timeout return values in `tpiu_disable_hw` are ignored.

## Test Signals

Probe should be tested for AMBA and platform/ACPI, clock failure rollback, initial disable programming, final-disable flush behavior, runtime PM suspend/resume, and CoreSight refcount behavior across multiple users.
