<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/rm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/rm.c

## Purpose
Defines R570 WPR heap layout profiles and the central R570 RM API table that combines R570-specific GSP/client/display/fifo/GR/FBSR/OFA hooks with reused R535 allocation/control/device/video-engine helpers.

## Important APIs, Types, And Functions
Important objects are r570_wpr_libos2, r570_wpr_libos3, r570_wpr_libos3_gh100, r570_wpr_libos3_gb10x, r570_wpr_libos3_gb20x, r570_api, and exported nvkm_rm_impl instances r570_rm_tu102, r570_rm_ga102, r570_rm_gh100, r570_rm_gb10x, and r570_rm_gb20x.

## Control Flow
There is no branching control flow beyond static initializer selection. Chip-specific GSP firmware interface tables select one of these nvkm_rm_impl profiles; boot/layout code then reads rm->wpr for heap/carveout/reserved sizes and rm->api for operations.

## State, Persistence, Dependencies, And Integration
State is immutable function-pointer and WPR configuration data. Dependencies are rm.h and R570/R535 helper exports. Integration points are tu102/tu116 GSP fwif entries, GH100/GB10x/GB20x GSP implementations, WPR metadata construction, and all RM object/control APIs.

## Risks And Test Signals
Risks: mixing R535 and R570 hooks assumes ABI compatibility where reused; WPR heap sizes and offset_set_by_acr change secure-boot memory layout; wrong profile for a chip can break boot or suspend. Test signals include firmware load on each listed family, correct heap sizing, object allocation across display/FIFO/GR/video engines, and suspend/resume on ACR-offset platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/rm.c -->
