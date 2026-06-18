<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.c

## Purpose
Controls the Mali450 Dynamic Load Balancing Unit used to distribute PP tile-list work across pixel processors.

## Important APIs, types, and functions
Exports `lima_dlbu_enable()`, `lima_dlbu_disable()`, `lima_dlbu_set_reg()`, `lima_dlbu_init()`, `lima_dlbu_fini()`, `lima_dlbu_resume()`, and `lima_dlbu_suspend()`. `lima_dlbu_hw_init()` programs the master tile-list physical and virtual base addresses.

## Control flow
Init/resume writes the write-combined DLBU page DMA address and reserved GPU VA. PP task execution enables a PP mask for the selected processors, optionally writes task-provided DLBU registers, and uses the reserved DLBU VA as the PP frame base. Non-DLBU paths disable the PP enable mask.

## State and persistence
DLBU shared page state lives in `lima_device` as CPU and DMA addresses. Hardware registers persist the PP mask, tile-list base addresses, frame dimensions, config, and start tile position.

## Dependencies and integration points
Depends on Lima device, VM reserved VA constants, and register definitions. Integrated by Mali450 PP task dispatch in `lima_pp.c`.

## Risks
The reserved VA and DMA page must remain valid for the device lifetime. Bad PP masks or task-supplied DLBU registers can distribute work incorrectly and hang rendering.

## Test signals
Mali450 PP submissions with `use_dlbu`, multi-PP workloads, DLBU disable fallback, resume reprogramming, and register dumps of PP enable masks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_dlbu.c -->
