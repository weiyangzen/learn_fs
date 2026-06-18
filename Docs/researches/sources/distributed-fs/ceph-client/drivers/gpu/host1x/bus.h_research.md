<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.h

## Purpose

`bus.h` is the local declaration boundary for the Tegra host1x bus registration layer. It lets the host1x platform driver register and unregister a `struct host1x` controller and exposes the `host1x_bus_type` consumed by client-device code without pulling in implementation details.

## Important APIs, Types, And Functions

- `extern const struct bus_type host1x_bus_type`: the Linux bus type for host1x clients.
- `host1x_register(struct host1x *host1x)` and `host1x_unregister(struct host1x *host1x)`: controller lifecycle hooks called from `dev.c`.
- Forward declarations for `struct bus_type` and `struct host1x` keep this header lightweight.

## Control Flow

The header has no executable control flow. Runtime control is in the bus implementation: `host1x_probe()` calls `host1x_register()` after core resources are initialized, and remove/error paths call `host1x_unregister()`.

## State And Persistence Behavior

No state is stored here. The declared APIs mutate global Linux device-model state by registering host1x clients on `host1x_bus_type` and tracking a controller instance.

## Dependencies And Integration Points

It integrates `dev.c` with the host1x bus implementation and downstream DRM/media clients that bind to host1x children. The stable contract is the bus type plus register/unregister pair.

## Risks And Test Signals

The main risk is lifecycle ordering: bus registration must not expose clients before syncpoints, channels, interrupts, debugfs, and runtime PM are ready. Useful tests are host1x probe/remove, deferred-probe of child devices, and module unload with clients bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/bus.h -->
