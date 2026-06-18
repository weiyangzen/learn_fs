# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvjpg.h

Purpose: declares the R535 NVJPG/NVJPEG allocation payload.

Important type: `NV_NVJPG_ALLOCATION_PARAMETERS` contains `size`, `prohibitMultipleInstances`, and `engineInstance`. The R535 allocator fills the size and instance fields.

Control flow and state: used only during RM object allocation. Persistent state after success is the RM object handle, not the stack/flexible payload.

Dependencies and integration: included by `r535/nvjpg.c` and aligned with NVJPEG engine indexes in `engine.h`.

Risks and tests: multiple-instance hardware needs correct `engineInstance` selection. Test signals include allocation and JPEG engine workload success for each advertised instance.
