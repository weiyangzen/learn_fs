<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context_bus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/context_bus.c

## Purpose

`context_bus.c` defines and registers the Linux bus type used for host1x memory-context child devices.

## Important APIs, Types, And Functions

- `const struct bus_type host1x_context_device_bus_type = { .name = "host1x-context" }`.
- `host1x_context_device_bus_init()` registers the bus at `postcore_initcall` time.

## Control Flow

At postcore init, the bus is registered before the host1x platform driver creates context devices. Failure is logged and returned from the initcall.

## State And Persistence Behavior

The registered bus type persists globally for the kernel lifetime. Context devices created by `context.c` attach to this bus.

## Dependencies And Integration Points

It depends on Linux device core and exports the bus symbol for the context implementation. The ordering matters because `device_add()` in `context.c` expects the bus to exist.

## Risks And Test Signals

The bus has no match/probe callbacks, so it is purely a device-model grouping mechanism. Test signals are successful early registration, context-device creation under `/sys/bus/host1x-context`, and clean behavior if bus registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context_bus.c -->
