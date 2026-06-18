# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-img-ipi.h

## Purpose
This header defines the generic image IPI/frame parameter ABI used by MDP3 between the AP kernel driver and SCP firmware, plus platform-dispatch macros for MT8183 and MT8195 shared config layouts.

## Important APIs, Types, and Functions
It defines IPI message IDs, packed address/time/pixel-format/image-buffer/input/output/frameparam structures, `img_ipi_param`, `img_frameparam`, platform IDs, `CFG_CHECK`, `CFG_OFST`, `CFG_ADDR`, `CFG_GET`, `CFG_COMP`, and union wrappers `struct img_config` and `struct img_compparam`.

## Control Flow
The MDP3 VPU/SCP path exchanges `img_ipi_frameparam` and config buffers. CMDQ code uses the CFG macros to select the right packed layout based on `mdp_plat_id` and to index per-postprocessor config blocks.

## State and Persistence
Frame parameters, config/self/tuning buffer addresses, and image buffers are per-job shared state. They are not persistent beyond processing and buffer lifetime.

## Dependencies and Integration Points
It includes MT8183/MT8195 shared-memory headers and `mtk-mdp3-type.h`. It is included by CMDQ, config, and VPU/core paths.

## Risks and Edge Cases
Packed ABI structs carry kernel virtual, CM4 physical, and IOMMU addresses in adjacent fields; using the wrong address domain can break firmware or hardware. CFG pointer arithmetic must stay within `mdp->vpu.config_size`, as guarded in CMDQ code. MT8188 is represented with platform value 8195 for config layout purposes.

## Test Signals
IPI frame submission, config-buffer bounds checks, address-domain validation, dual-output frames, and platform macro dispatch tests.
