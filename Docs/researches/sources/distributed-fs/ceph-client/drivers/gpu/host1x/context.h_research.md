<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.h

## Purpose

`context.h` declares the host1x memory-context list and optional IOMMU-context lifecycle APIs. It lets `dev.c` initialize/free context devices while compiling to no-ops when `CONFIG_IOMMU_API` is disabled.

## Important APIs, Types, And Functions

- `extern struct bus_type host1x_context_device_bus_type`: bus used by context child devices.
- `struct host1x_memory_context_list`: mutex, dynamic context-device array, and length.
- `host1x_memory_context_list_init()` / `host1x_memory_context_list_free()` are real APIs under `CONFIG_IOMMU_API` and inline no-ops otherwise.

## Control Flow

No direct control flow exists in the header. The conditional compilation controls whether host1x probe actually creates IOMMU context devices.

## State And Persistence Behavior

The list state persists inside `struct host1x`. With IOMMU disabled, no context state is created and callers see unsupported behavior from public APIs.

## Dependencies And Integration Points

It includes mutex/refcount primitives and is included by `dev.h`, `context.c`, and submit paths via public host1x structures.

## Risks And Test Signals

The no-op stubs must match the real API signature. Build tests with and without `CONFIG_IOMMU_API`, plus probe on DT with and without `iommu-map`, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.h -->
