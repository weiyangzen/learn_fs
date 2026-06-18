# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/ofa.h

Purpose: declares the R535 optical-flow accelerator allocation payload.

Important type: `NV_OFA_ALLOCATION_PARAMETERS` contains `size` and `prohibitMultipleInstances`. Unlike NVDEC/NVENC/NVJPG, the R535 OFA payload has no explicit `engineInstance` field, and `ofa.c` only sets the size.

Control flow and state: allocation-time only. RM selects/constructs the OFA object according to class and payload.

Dependencies and integration: included by `r535/ofa.c` and selected through the R535 RM API table.

Risks and tests: if newer GPUs expose multiple OFA instances, this R535 shape cannot select an instance; R570 adds OFA1 engine identity elsewhere. Test signals are successful OFA object allocation and workload execution where OFA is present.
