# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/nvrm/engine.h

Purpose: defines R535 engine identity constants used to translate RM/GSP engine descriptions into Nouveau subdevice and NV2080 engine types.

Important definitions: `MC_ENGINE_IDX_*` enumerates master-control interrupt engine indexes, including GSP, DISP, CE0-CE9, GR, NVDEC0-7, NVENC/MSENC0-2, NVJPEG0-7, and OFA0. `RM_ENGINE_TYPE` enumerates RM engine types for GR, copy, video, display-adjacent engines, NVJPEG, OFA, and support engines. `NV2080_ENGINE_TYPE_*` defines control/channel-facing engine types and helper macros for ranges and indexes.

Control flow and state: declarative only. In this work item, `r535_gsp_xlat_mc_engine_idx()` consumes `MC_ENGINE_IDX_*` to register interrupt vectors, and FIFO/channel code consumes `RM_ENGINE_TYPE`/`NV2080_ENGINE_TYPE` to translate RM engine discovery into Nouveau engine instances.

Dependencies and integration: included by `nvrm/gsp.h`, FIFO headers, and GSP code. It is a central contract between firmware tables and Nouveau engine enumeration.

Risks and tests: enum order and numeric values are ABI-sensitive. Unknown or shifted values can drop interrupts, bind channels to wrong engines, or skip discovered engines. Validation should compare RM engine info tables against Nouveau runlists and verify interrupt vectors, channel binding, and engine object allocation across all engine classes present on a GPU.
