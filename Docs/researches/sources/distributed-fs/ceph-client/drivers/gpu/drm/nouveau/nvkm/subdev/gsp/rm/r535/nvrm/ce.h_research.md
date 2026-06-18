# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ce.h

Purpose: declares the R535 copy-engine allocation payload.

Important type: `NVC0B5_ALLOCATION_PARAMETERS` contains a structure version and `engineType`. Nouveau CE allocation code uses this ABI to select the RM/NV2080 engine type for a copy engine object.

Control flow and state: the header is declarative only. The payload captures allocation-time engine selection; persistent state lives in the allocated RM object.

Dependencies and integration: included by R535 CE allocation code, selected via `r535_api.ce`, and linked to FIFO engine discovery/translation. It depends on fixed RM scalar types from `nvrm/nvtypes.h`.

Risks and tests: wrong engine type assignment can allocate an object on the wrong CE or fail channel binding. Tests should cover CE object allocation, memory copy submissions, and GPUs with multiple CEs.
