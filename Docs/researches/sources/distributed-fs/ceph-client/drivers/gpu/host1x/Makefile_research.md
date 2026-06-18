# sources/distributed-fs/ceph-client/drivers/gpu/host1x/Makefile

## Purpose

The Makefile builds the Tegra host1x core and optional context bus support.

## Important APIs, Types, And Functions

`host1x-y` includes bus, syncpoint, device, interrupt, CDMA, channel, job, debug, MIPI, fence, and per-generation hardware files from host1x01 through host1x08. `context.o` is added when `CONFIG_IOMMU_API` is enabled. `context_bus.o` is built from `CONFIG_TEGRA_HOST1X_CONTEXT_BUS`.

## Control Flow

No runtime flow. Kbuild links the objects into `host1x.o` for `CONFIG_TEGRA_HOST1X`.

## State And Persistence Behavior

No runtime state. Build composition determines which host1x subsystems are present.

## Dependencies And Integration Points

The object list reflects host1x's bus/client infrastructure, scheduler/channel/job submission, synchronization, debug, MIPI, fence, and hardware-generation abstraction layers.

## Risks And Test Signals

Risk is missing generation-specific object or context support in configurations. Test by building with and without IOMMU API and context bus.
