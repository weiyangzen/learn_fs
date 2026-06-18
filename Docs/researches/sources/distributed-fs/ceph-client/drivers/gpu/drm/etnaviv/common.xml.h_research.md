# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/common.xml.h

## Purpose
Generated common Vivante GPU constants for pipes, sync recipients, endian modes, chip model IDs, feature bits, and minor feature flags.

## Important APIs, Types, and Functions
Defines `PIPE_ID_PIPE_3D/2D`, `SYNC_RECIPIENT_*`, `ENDIAN_MODE_*`, many `chipModel_*` IDs, `chipFeatures_*`, and `chipMinorFeatures0..12_*` feature bits. These flags drive capability checks throughout etnaviv.

## Control Flow
No executable flow. Runtime code reads `struct etnaviv_chip_identity` feature fields and tests these macros to choose command sequences, cache flush behavior, MMU setup, and workarounds.

## State and Persistence
No mutable state. Like the command stream header, it is generated from XML and should be regenerated rather than manually changed.

## Dependencies and Integration Points
Used by `etnaviv_buffer.c`, `etnaviv_flop_reset.c`, GPU feature probing, perfmon, MMU and scheduler paths. It provides stable names for hardware capability checks.

## Risks
Feature bit mismatches can enable unsupported paths or skip required workarounds. Because many flags are hardware-errata oriented, subtle mistakes may only appear on specific SoC revisions.

## Test Signals
Hardware probing logs, feature-specific GPU tests, build coverage across etnaviv files, and regression testing on multiple Vivante chip models are key signals.
