# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.h

## Purpose
Defines public constants for the Samsung MIPI-CSIS receiver driver.

## Important APIs, Types, and Functions
Constants include driver/subdev names, maximum receiver entities, lane limits for CSIS0 and CSIS1, sink/source pad indices, pad count, and default pixel dimensions.

## Control Flow
The header determines media pad layout and naming used by probe, media-device registration, and link creation. `CSIS_MAX_ENTITIES` bounds media-device arrays and DT mux-id validation.

## State and Persistence
No software state is stored here; constants constrain runtime state allocated in `mipi-csis.c` and `media-dev.h`.

## Dependencies and Integration Points
Consumed by MIPI-CSIS implementation and the top-level media device for entity array sizing and link pad indices.

## Risks and Edge Cases
Lane-limit constants are not directly enforced in `mipi-csis.c`, which relies on DT `bus-width` as `max_num_lanes`; board descriptions must match hardware limits. Increasing entity count requires matching media-device array expectations.

## Test Signals
Compile-test link creation against pad constants, validate DT mux ids remain below `CSIS_MAX_ENTITIES`, and confirm default format dimensions are visible before userspace configuration.
