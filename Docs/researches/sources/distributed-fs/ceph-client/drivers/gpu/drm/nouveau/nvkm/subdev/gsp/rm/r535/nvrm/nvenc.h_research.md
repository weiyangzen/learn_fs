# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/nvenc.h

Purpose: declares the R535 NVENC/MSENC allocation payload used by `nvenc.c`.

Important type: `NV_MSENC_ALLOCATION_PARAMETERS` contains `size`, `prohibitMultipleInstances`, and `engineInstance`. `engineInstance` selects NVENC0, NVENC1, or NVENC2 in the R535 ABI.

Control flow and state: no executable code. The payload is populated immediately before RM allocation and then owned by firmware as part of object construction.

Dependencies and integration: consumed by the R535 NVENC engine allocator and tied to engine translation constants from `engine.h`.

Risks and tests: the layout is small but ABI-sensitive. Tests should allocate NVENC objects and run encode submissions on GPUs with one or more encoders.
