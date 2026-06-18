# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/base.c

## Purpose
Implements the common ACR subdevice. ACR prepares protected WPR firmware images, boots high-secure firmware, tracks low-secure falcons, and brokers falcon bootstrapping.

## Important APIs, types, and functions
Exports `nvkm_acr_bootstrap_falcons()`, `nvkm_acr_managed_falcon()`, `nvkm_acr_hsfw_boot()`, and `nvkm_acr_new_()`. Core callbacks include oneinit/load/fini/dtor paths, WPR firmware parsing via `nvkm_acr_ctor_wpr()`, and cleanup helpers.

## Control flow, state, and persistence
Oneinit loads/filters low-secure firmware records, orders the RTOS falcon first, culls unbootstrappable falcons, computes or imports WPR layout, allocates WPR memory, builds/patches the WPR image, creates ACR instance/VMM state, maps HS firmware, and discards temporary blobs. Init boots ACR if an RTOS LSF exists. Fini unloads via HS firmware and drops RTOS references.

## Dependencies and integration points
Depends on firmware loader, options `NvAcrWpr*`, memory/VMM, SEC2/PMU/GSP falcons, ACR generation function tables, and falcon firmware boot.

## Risks and test signals
WPR range mismatch, unsupported bootstrap masks, or bad patch adjustment can leave secure engines unusable. Signals include WPR debug ranges, comparison warnings, ACR boot errors, and successful bootstrap requests.
