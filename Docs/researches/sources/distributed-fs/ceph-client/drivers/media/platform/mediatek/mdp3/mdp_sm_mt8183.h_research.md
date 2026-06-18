# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8183.h

## Purpose
This header defines the packed SCP/AP shared-memory configuration layout for MT8183 MDP3 processing.

## Important APIs, Types, and Functions
It defines `IMG_MAX_SUBFRAMES_8183`, common component frame/subframe structs, per-block data for RDMA, RSZ, WROT, WDMA, ISP metadata, `struct img_compparam_8183`, and `struct img_config_8183`.

## Control Flow
SCP firmware fills this layout in shared memory. Kernel CMDQ code reads it through `CFG_GET`, `CFG_COMP`, and `CFG_ADDR` macros to configure component contexts, frame registers, subframe registers, MMSYS controls, and mutex routing.

## State and Persistence
The packed structures are per-frame/job shared state. They persist only until overwritten by the next SCP frame configuration.

## Dependencies and Integration Points
It includes `mtk-mdp3-type.h` for shared primitive geometry and enum limits and is unioned into `struct img_config`/`img_compparam` in `mtk-img-ipi.h`.

## Risks and Edge Cases
This is firmware ABI. Packing, field width, array size, and MD5-tagged SCP prebuild compatibility must remain exact. MT8183 supports fewer subframes and component data types than MT8195.

## Test Signals
Structure size/layout checks against SCP firmware, MT8183 frame processing, maximum subframe count, and CMDQ field extraction traces validate it.
