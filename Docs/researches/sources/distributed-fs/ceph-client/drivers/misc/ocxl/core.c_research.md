# sources/distributed-fs/ceph-client/drivers/misc/ocxl/core.c

## Purpose
This is the OCXL core lifecycle layer. It opens PCI functions, configures links, discovers and initializes AFUs, allocates ACTAG/PASID ranges, maps MMIO windows, activates/deactivates AFUs, and exposes metadata/accessors for other OCXL subcomponents.

## Important APIs, types, and functions
Public APIs include `ocxl_function_open()`, `ocxl_function_close()`, `ocxl_function_afu_list()`, `ocxl_function_fetch_afu()`, `ocxl_function_config()`, `ocxl_afu_config()`, `ocxl_afu_get()`, `ocxl_afu_put()`, `ocxl_afu_set_private()`, and `ocxl_afu_get_private()`. Internal helpers cover function allocation/configuration, AFU allocation/configuration/removal, ACTAG/PASID assignment/reclaim, BAR reservation, MMIO mapping, and AFU activation.

## Control flow and state
Function open requires radix MMU, allocates an `ocxl_fn`, enables PCI, reads function config, creates/registers a function device, assigns function ACTAG/PASID resources, sets up the OpenCAPI link, configures TL, then scans AFU indexes up to `max_afu_index`. Each present AFU is allocated, configured from DVSEC data, assigned ACTAG/PASID ranges, maps global/per-process MMIO, is enabled in config space, and is added to the function AFU list. Function close removes each AFU, detaches contexts, disables AFUs, releases resources, tears down link/PCI, and unregisters the function device.

## State and persistence behavior
Runtime state includes function/AFU objects, krefs, device references, AFU lists, resource bitmaps/lists, ACTAG/PASID ranges, BAR usage counts, MMIO mappings, and private AFU pointers. Hardware config persists until explicit deconfigure or reset.

## Dependencies and integration points
It depends on `config.c`, OCXL link/resource helpers, PCI, device core, IDR/list infrastructure, and internal structures. `file.c`, sysfs, and PCI frontends use AFU private pointers and metadata created here.

## Risks and test signals
Risks include resource partitioning math when enabled ACTAGs are less than supported, PASID count assumptions, BAR reference counting, MMIO ioremap failures, partial AFU init continuing after errors, device-register cleanup, and context detachment during AFU removal. Test signals include radix-disabled rejection, function open/close, AFU scan with holes, multi-AFU ACTAG/PASID allocation, BAR reuse, MMIO mapping failure unwind, and hot-unbind with active contexts.
