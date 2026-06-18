# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.h

## Purpose
Defines shared data structures, constants, state bits, queue helpers, and variant data for the FIMC-LITE driver.

## Important APIs, Types, and Functions
Key types are `struct flite_drvdata`, `struct flite_frame`, `struct flite_buffer`, `struct fimc_lite_events`, and `struct fimc_lite`. Inline helpers check activity and push/pop active or pending buffer queues.

## Control Flow
The header establishes a two-queue model: buffers move from pending to active when programmed into DMA registers, then active to vb2 completion on frame-end IRQ. State bits distinguish low power, pending, run, stream, suspended, off, in-use, config-update, and sensor-stream conditions.

## State and Persistence
`struct fimc_lite` owns all runtime state for a device instance, including media/video entities, sensor pointer, clocks/registers, frame formats, output path, vb2 queue, buffer lists, event counters, and locks. No fields are intended for persistence beyond the driver instance.

## Dependencies and Integration Points
Includes kernel platform/IRQ/clock primitives, V4L2 subdev/control/vb2 headers, media entities, and Exynos FIMC format definitions. It is shared by the main FIMC-LITE driver and register helper layer.

## Risks and Edge Cases
The enum defines `ST_FLITE_LPM`, while `fimc-lite.c` uses `ST_LPM` from `fimc-core.h`, making state-bit ownership easy to confuse. Queue pop helpers assume the list is non-empty; all callers must check before popping.

## Test Signals
Run lockdep around queue operations, compile with state-bit warnings enabled, exercise suspend/resume bit transitions, and verify queue helpers are never invoked on empty lists.
