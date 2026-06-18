# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvjpg.c

Purpose: implements the R535 RM allocation adapter for NVJPG/NVJPEG engines.

Important API: `r535_nvjpg_alloc()` allocates a `NV_NVJPG_ALLOCATION_PARAMETERS` payload under a channel object, sets `size` and `engineInstance`, and writes the allocation. The `r535_nvjpg` `nvkm_rm_api_engine` table exposes it to the rest of RM integration.

Control flow and state: no persistent local state is kept. The output object is populated by `nvkm_gsp_rm_alloc_get()` and finalized by `nvkm_gsp_rm_alloc_wr()`. Error propagation is direct, with a warning for allocation-buffer setup failure.

Dependencies and integration: depends on `rm/engine.h` and `nvrm/nvjpg.h`, and is referenced by the R535 API table. Its instance value must align with RM engine discovery and FIFO engine translation.

Risks and tests: the principal risks are stale ABI layout or wrong instance numbering, especially on GPUs with multiple NVJPEG engines. Test signals include successful NVJPG object allocation for every discovered instance and exercising JPEG decode paths without RM RC-triggered failures.
