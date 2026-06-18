# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/fw.c

## Purpose
Implements falcon firmware object construction, signature patching, VMM mapping, high-secure firmware parsing, loading, booting, and cleanup.

## Important APIs, types, and functions
Key APIs include `nvkm_falcon_fw_ctor()`, `nvkm_falcon_fw_ctor_hs()`, `nvkm_falcon_fw_ctor_hs_v2()`, `nvkm_falcon_fw_oneinit()`, `nvkm_falcon_fw_boot()`, `nvkm_falcon_fw_sign()`, `nvkm_falcon_fw_patch()`, and `nvkm_falcon_fw_dtor()`.

## Control flow, state, and persistence
Constructors parse NVIDIA firmware headers, copy firmware images, capture bootloader code when separate, derive IMEM/DMEM/non-secure ranges, and store production/debug signatures. Boot acquires the falcon, patches the selected signature, resets, optionally runs setup, syncs DMA mappings, loads code/data, and waits for boot mailbox status. Oneinit maps firmware memory into a VMM when needed.

## Dependencies and integration points
Depends on `nvfw/fw.h`, `nvfw/hs.h`, firmware loader, DMA mapping, VMM, instance memory, and generation `nvkm_falcon_fw_func`. Used heavily by ACR high-secure firmware.

## Risks and test signals
Signature selection, patch offsets, and mailbox expected values are security-critical. Signals include boot mailbox logs, firmware parsing debug, patch trace, and boot failure errors.
