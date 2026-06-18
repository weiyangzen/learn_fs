# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8195.h

## Purpose
This header defines the packed SCP/AP shared-memory configuration layout for MT8195-class MDP3 processing, also reused by MT8188 driver data.

## Important APIs, Types, and Functions
It defines `IMG_MAX_SUBFRAMES_8195`, 32-bit component frame/subframe structures, per-block data for RDMA, FG, HDR, AAL, RSZ, TDSHP, COLOR, OVL, PAD, TCC, WROT, WDMA, ISP metadata, `struct img_compparam_8195`, and `struct img_config_8195`.

## Control Flow
SCP-generated config is read by CMDQ path and component code to program every block. The extra fields support multi-RDMA, multi-postprocessor, merge, HDR/PQ, 10-bit, ESL, and advanced VPP routing features.

## State and Persistence
These packed structures are per-frame shared-memory state and are overwritten per job.

## Dependencies and Integration Points
It includes `mtk-mdp3-type.h` and is selected through `struct img_config`/`img_compparam` unions in `mtk-img-ipi.h`. Component ops in `mtk-mdp3-comp.c` read many of its nested fields.

## Risks and Edge Cases
The ABI must match the SCP prebuild MD5 noted in the file. Array bounds depend on `IMG_MAX_SUBFRAMES_8195` and `IMG_MAX_COMPONENTS`. Adding fields or changing packing breaks firmware/kernel compatibility.

## Test Signals
MT8195/MT8188 SCP config dumps, maximum subframe paths, dual postprocessor jobs, advanced block enablement, and structure-size assertions are useful validation.
