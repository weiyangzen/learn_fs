# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.h

## Purpose
This header exposes Poulsbo-specific clock functions to the shared GMA500 driver.

## Important APIs, Types, and Functions
It declares `extern const struct gma_clock_funcs psb_clock_funcs;`, implemented in `psb_intel_display.c`.

## Control Flow
There is no executable flow. Poulsbo chip ops reference this clock-function table so CRTC mode setting can compute PLL values.

## State and Persistence Behavior
The header has no state. The referenced object is static runtime dispatch metadata.

## Dependencies and Integration Points
It connects `psb_device.c` to `psb_intel_display.c` without pulling in broader implementation details.

## Risks
If `psb_clock_funcs` is changed or removed, Poulsbo mode setting will fail to link or lack PLL helpers.

## Test Signals
Build coverage for Poulsbo ops and successful mode setting using `psb_clock_funcs`.
