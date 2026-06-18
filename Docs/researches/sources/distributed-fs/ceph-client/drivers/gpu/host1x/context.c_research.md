<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.c

## Purpose

`context.c` implements host1x memory-context devices used for IOMMU-backed channel isolation. It creates one child device per `iommu-map` entry, configures DMA/IOMMU state for each, and allocates contexts to callers by PID and IOMMU device.

## Important APIs, Types, And Functions

- `host1x_memory_context_list_init()`: parses `iommu-map`, creates `host1x-ctx.N` devices on `host1x-context` bus, sets a 38-bit DMA mask, configures DMA/IOMMU with `of_dma_configure_id()`, and records stream IDs.
- `host1x_memory_context_list_free()`: unregisters context devices and frees the array.
- `host1x_memory_context_alloc()`: finds an existing context owned by the same PID or an unused compatible context, sets `owner`, and initializes/refcounts it.
- `host1x_memory_context_get()` / `host1x_memory_context_put()` manage references and clear the PID owner on last put.

## Control Flow

Probe-time initialization is optional: no `iommu-map` means zero contexts and success. When entries exist, each device is initialized, added, DMA-configured with the entry index as ID, and required to have an IOMMU mapping and stream ID. Allocation is serialized by the context-list mutex and matches contexts to the requesting device's IOMMU provider.

## State And Persistence Behavior

The context-list array persists for the host lifetime. Each context stores a child `struct device`, DMA mask/parameters, stream ID, owner PID, and refcount. Ownership persists across multiple allocations by the same PID until references are dropped.

## Dependencies And Integration Points

Depends on Open Firmware `iommu-map`, DMA/IOMMU APIs, `host1x_context_device_bus_type`, PID refcounting, and public `struct host1x_memory_context` from `<linux/host1x.h>`. It integrates with DRM Tegra UAPI and submit paths, which attach a memory context to jobs so HW6+ stream-ID commands can isolate engines.

## Risks And Test Signals

Probe fails if DT advertises contexts but IOMMU is disabled or stream IDs cannot be read. Context sharing is per PID and IOMMU device, so PID lifetime and refcount handling matter. Tests should cover no-context DT, valid contexts, IOMMU-disabled failure, allocation reuse by same PID, exhaustion returning `-EBUSY`, and submit stream-ID selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/context.c -->
