# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvdec.h

Purpose: declares the R535 NVDEC/BSP allocation payload used by `nvdec.c`.

Important type: `NV_BSP_ALLOCATION_PARAMETERS` contains `size`, `prohibitMultipleInstances`, and `engineInstance`. The allocator sets `size` and `engineInstance`, leaving the multiple-instance prohibition defaulted.

Control flow and state: the structure is only used at RM object allocation time. The chosen `engineInstance` selects the physical decoder instance.

Dependencies and integration: included by `r535/nvdec.c` and indirectly used by the R535 API table's `.nvdec` engine allocator.

Risks and tests: incorrect structure size or instance value can break allocation. Test signals are successful object creation and decode workloads across all discovered NVDEC instances.
