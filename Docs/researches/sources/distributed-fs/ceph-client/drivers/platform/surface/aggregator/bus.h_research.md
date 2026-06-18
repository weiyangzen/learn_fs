# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.h

## Purpose

This internal header exposes Surface Aggregator bus registration hooks to the core while compiling to no-op stubs when `CONFIG_SURFACE_AGGREGATOR_BUS` is disabled.

## Important APIs, Types, And Functions

The only APIs are `ssam_bus_register()` and `ssam_bus_unregister()`. With bus support enabled, they are implemented in `bus.c`; otherwise static inline stubs return success or do nothing.

## Control Flow

`core.c` calls these functions during module init and exit. The stubs keep the core init sequence identical regardless of bus configuration.

## State And Persistence

The header owns no state. When enabled, bus registration state belongs to the Linux driver core. When disabled, no bus object exists.

## Dependencies And Integration Points

It includes the public Surface Aggregator controller header for shared type visibility and is used by `core.c`. It is tied to `CONFIG_SURFACE_AGGREGATOR_BUS` from the aggregator Kconfig.

## Risks

The no-op stub means higher-level code must be properly gated by Kconfig; otherwise a build without bus support may appear to initialize successfully while bus clients cannot exist. Keeping the prototypes aligned with `bus.c` avoids link or type mismatches.

## Test Signals

Build both with and without `CONFIG_SURFACE_AGGREGATOR_BUS`. With bus enabled, verify bus registration and client binding. With it disabled, verify core probe still succeeds and no bus symbols are required by selected clients.
