# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-psil.c

## Purpose
This file implements the generic K3 PSI-L endpoint lookup and replacement API used by TI K3 UDMA. It selects the proper SoC endpoint map at runtime and returns endpoint configuration for a PSI-L thread ID.

## Important APIs, Types, and Functions
The exported APIs are `psil_get_ep_config(u32 thread_id)` and `psil_set_new_ep_config(struct device *dev, const char *name, struct psil_endpoint_config *ep_config)`. Internal state is `soc_ep_map`, protected during first selection by `ep_map_mutex`. `k3_soc_devices[]` maps SoC family strings (`AM65X`, `J721E`, `J7200`, `AM64X`, `J721S2`, `AM62X`, `AM62AX`, `J784S4`, `AM62PX`, `J722S`) to endpoint maps.

## Control Flow
`psil_get_ep_config()` lazily matches the running SoC with `soc_device_match()`. If no match exists, it returns `ERR_PTR(-ENOTSUPP)`. For destination thread IDs with a destination map, it first scans the destination array for an exact ID. It then clears `K3_PSIL_DST_THREAD_ID_OFFSET` and scans the source array, enabling symmetric source/destination fallback. If no entry matches, it returns `ERR_PTR(-ENOENT)`. `psil_set_new_ep_config()` finds a named DMA entry in a device tree node, parses the matching `dmas` phandle, obtains the endpoint config by thread ID, and copies the supplied config into the map entry.

## State and Persistence
`soc_ep_map` is cached after first SoC match and persists for the lifetime of the module/kernel image. Endpoint configs are returned as mutable pointers into static SoC arrays. `psil_set_new_ep_config()` persistently mutates the selected static map entry, affecting all later users of that thread ID.

## Dependencies and Integration Points
The file depends on the Linux SoC device matching API, OF phandle parsing, module exports, mutexes, and the SoC maps declared in `k3-psil-priv.h`. It is selected by the TI K3 UDMA Kconfig path and consumed by UDMA/glue code that needs endpoint metadata.

## Risks
The SoC map is selected globally once; systems with unexpected family strings fail with `-ENOTSUPP`. Linear lookup is simple but table duplicates return the first match. Runtime replacement lacks copy-on-write or refcounting, so callers must coordinate if changing configs after users have cached pointers. Device-tree parsing in `psil_set_new_ep_config()` depends on matching `dma-names` and `dmas` indices.

## Test Signals
Test successful map selection for every family string, explicit destination lookup, symmetric fallback lookup, missing thread IDs, and missing SoC match. For `psil_set_new_ep_config()`, test invalid device/no OF node, missing `dma-names`, missing `dmas`, invalid thread ID, and successful mutation visible through a subsequent `psil_get_ep_config()`.
