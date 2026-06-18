<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/engine.h

## Purpose
Defines the R570 RM engine namespace: MC interrupt/source engine indices, RM_ENGINE_TYPE values, and NV2080_ENGINE_TYPE values. It is the reference used when translating firmware/RM engine identifiers into Nouveau engine instances.

## Important APIs, Types, And Functions
Important definitions include MC_ENGINE_IDX_* ranges for GSP, DISP, CE0-CE19, NVENC, NVJPEG, NVDEC, OFA, GR, GSPLITE, DPAUX, etc.; RM_ENGINE_TYPE_* enum values; and NV2080_ENGINE_TYPE_* constants for graphics, copy, video decode/encode, NVJPG, OFA, and compressed/decompressed copy engines.

## Control Flow
There is no runtime control flow. Consumers such as r570_gsp_xlat_mc_engine_idx and FIFO channel allocation code compare integer engine IDs against these constants and derive nvkm_subdev_type plus instance or NV2080 engine type.

## State, Persistence, Dependencies, And Integration
State is purely symbolic compile-time ABI. Dependencies are nvrm/nvtypes.h. Integration points are GSP notification/fault decoding, FIFO runlist/channel setup, engine object allocation, and RM control payloads that name engines.

## Risks And Test Signals
Risks: numeric drift between this header and the firmware version would misattribute faults, allocate channels on wrong engines, or ignore newer engine IDs. Test signals include correct CE/NVDEC/NVENC/NVJPG/OFA instance discovery and fault recovery messages mapping to expected Nouveau engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/engine.h -->
