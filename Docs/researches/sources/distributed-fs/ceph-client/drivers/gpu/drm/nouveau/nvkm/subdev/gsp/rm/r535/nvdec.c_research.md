# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvdec.c

Purpose: provides the R535 RM engine allocator for NVDEC/BSP video decode engine objects. It adapts Nouveau's generic `nvkm_rm_api_engine.alloc` signature to the R535 `NV_BSP_ALLOCATION_PARAMETERS` ABI.

Important API: `r535_nvdec_alloc()` calls `nvkm_gsp_rm_alloc_get()` against the parent channel object, using the requested RM handle and class. It fills `args->size` with `sizeof(*args)` and `args->engineInstance` with Nouveau's selected instance, then commits with `nvkm_gsp_rm_alloc_wr()`. The exported `r535_nvdec` table contains this function as `.alloc`.

Control flow and state: the function is stateless beyond initializing the RM allocation payload and the output `nvkm_gsp_object`. The object lifetime is then owned by the generic RM allocation/free path. Errors are returned directly from allocation preparation or writeback; `WARN_ON(IS_ERR(args))` highlights unexpected RM allocation setup failures.

Dependencies and integration: depends on `rm/engine.h` for the API contract and `nvrm/nvdec.h` for the R535 payload layout. It is selected from `r535_api` in `rm.c` and used by FIFO/channel object creation paths when binding decode engines.

Risks and tests: the only ABI-sensitive fields are `size` and `engineInstance`; wrong instance numbering would bind the wrong physical decoder or fail allocation. Test signals are successful creation/destruction of NVDEC objects for each discovered instance, decode workload submission, and absence of RM allocation errors for multi-NVDEC GPUs.
