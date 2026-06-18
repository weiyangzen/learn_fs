# sources/distributed-fs/ceph-client/include/linux/host1x_context_bus.h

## Purpose
`host1x_context_bus.h` declares the optional host1x context device bus type used for Tegra host1x memory/context isolation devices.

## Important APIs, Types, And Functions
When `CONFIG_TEGRA_HOST1X_CONTEXT_BUS` is enabled, it declares `extern const struct bus_type host1x_context_device_bus_type`. There are no other functions or structures.

## Control Flow And State
There is no local control flow. Bus registration and device matching happen in the implementation guarded by the same config option. State is owned by the Linux device model and host1x context device code.

## Dependencies And Integration Points
It includes `linux/device.h` for `struct bus_type`. It integrates with `host1x_memory_context` and drivers that need a distinct context-device bus for IOMMU or stream-ID handling.

## Risks
Consumers must guard references with the same config or otherwise avoid unresolved symbols. The header intentionally exposes only the bus symbol, so behavior changes belong in the bus implementation.

## Test Signals
Build with `CONFIG_TEGRA_HOST1X_CONTEXT_BUS=y/m/n`, verify context devices bind on the bus when enabled, and confirm no symbol references remain in disabled builds.
