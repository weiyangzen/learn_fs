# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp.h

## Purpose
This header is AtomISP's userspace-facing private V4L2 ABI. It defines ISP hardware revision constants, custom pixel/media-bus formats, statistics/configuration structures, parameter pointer bundles, private ioctls, private controls, private events, and custom color effects.

## Important APIs, Types, And Data
- Hardware constants describe ISP2300/ISP2400/ISP2401 revisions, steppings, and camera binary run modes.
- Custom formats include `V4L2_PIX_FMT_CUSTOM_M10MO_RAW` and several `V4L2_MBUS_FMT_CUSTOM_*` values.
- ISP tuning structs include noise reduction, temporal noise reduction, optical black, edge enhancement, 3A config/output/statistics, DVS/DIS coefficients and statistics, white balance, color correction, de-pixel noise, chroma enhancement, defect pixel correction, metadata, digital zoom, gamma, morphing, shading, MACC, CTC, overlay, exposure, and external ISP controls.
- `struct atomisp_parameters` is the large per-frame/global parameter bundle; most fields are pointers to specific tuning tables/configs and it ends with `per_frame_setting` by ABI requirement.
- Private ioctls under `BASE_VIDIOC_PRIVATE` configure or query ISP algorithms, 3A/DVS stats, tables, exposure, DZ, parameters, formats, fake events, array resolution, depth sync compensation, and sensor edge enhancement.
- Private controls include AtomISP postprocessing toggles, run mode, VFPP, continuous capture controls, raw buffer locking, exposure-zone count, digital zoom disable, and ISP version selection.
- Private V4L2 events signal 3A stats, metadata, acceleration completion, pause buffer, and CSS reset.

## Control Flow
The header does not execute code, but it defines ioctl/control/event contracts used by the AtomISP video-node implementation and by camera HAL userspace. Userspace populates ABI structs, sometimes with embedded `__user` pointers to large arrays, then submits private ioctls. Kernel code copies the outer structures, validates sizes/ranges, copies pointed-to buffers as needed, applies settings globally or per frame, and later emits stats/events with exposure/config IDs.

## State And Persistence
No state is stored in the header. ABI state is carried across ioctl calls in userspace-visible structs, queued per-frame parameter settings, and driver-side ISP/CSS configuration. Many structs intentionally expose persistent tuning tables that remain active until replaced.

## Dependencies And Integration Points
This file depends on Linux fixed-width types and V4L2 ioctl/control/event number spaces. It integrates every AtomISP layer that needs a stable ABI: video-node ioctl handling, sensor drivers using `struct atomisp_exposure`, CSS/ISP parameter translation, camera HALs, and media-controller pipelines.

## Risks
- ABI compatibility is the main risk: field reordering, type-width changes, or changing ioctl numbers breaks userspace.
- Several structs contain raw or `__user` pointers, including nested pointer bundles; ioctl handlers must validate and copy each pointed-to buffer carefully.
- Multiple ioctls intentionally share the same private number with different directions/types, especially DVS/DIS entries at offset 6. Dispatch code must disambiguate by command value exactly.
- Some comments contain stale or misspelled wording, but the bigger concern is that they may reflect old hardware assumptions.
- `struct atomisp_parameters` has a "keep at end" ABI warning for `per_frame_setting`; extensions must preserve layout expectations.
- Private V4L2 IDs can collide with upstream or vendor extensions if not isolated.

## Test Signals
Validation should include ioctl number ABI checks, 32/64-bit compat layout tests for every pointer-bearing struct, copy_from_user/copy_to_user fault injection, bounds checks for grids/tables/histograms, event delivery tests for stats/metadata/CSS reset, per-frame parameter ID round trips, and userspace smoke tests that exercise core private controls and `ATOMISP_IOC_S_EXPOSURE`.
