<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.c

## Purpose
This file implements on-chip NV17/NV4x TV output encoders, including load detection, TV mode enumeration/validation, DPMS, modeset preparation, low-definition TV programming, component/HD CTV programming, property handling, and encoder creation.

## Important APIs, Types, and Functions
The public constructor is `nv17_tv_create`. Important helpers include `nv42_tv_sample_load`, `nv17_tv_detect`, low/HD mode list functions, `nv17_tv_mode_valid`, `nv17_tv_mode_fixup`, `nv17_tv_dpms`, `nv17_tv_prepare`, `nv17_tv_mode_set`, `nv17_tv_commit`, `nv17_tv_save`, `nv17_tv_restore`, `nv17_tv_create_resources`, and `nv17_tv_set_property`.

## Control Flow
Detection first rejects use when the DAC is busy, applies board quirk pin masks where present, samples load through NV42-specific or DAC sampling logic, maps pin masks to composite, S-video, component, or SCART subconnectors, and updates DRM properties. Mode enumeration chooses low-definition TV modes or CTV-derived HD modes based on the selected norm. Mode validation enforces clock, geometry, interlace, and doublescan constraints. Prepare powers off, disables FP, moves unused FP encoders away if CTV needs FP resources, updates LCD routing, and programs DACCLK routing. Mode set fills either PTV/TV encoder state for low-definition output or CTV/FP timing state for component modes. Commit updates rescaler/properties, loads TV state, sets test-control values, and powers on.

## State and Persistence Behavior
`struct nv17_tv_encoder` stores TV state snapshots, overscan, flicker, saturation, hue, selected norm/subconnector, and pin mask. The encoder also persists saved DACCLK and PTV/TV registers. Modesets update `nv04_display.mode_reg` PRAMDAC/FP/CTV fields and live hardware registers.

## Dependencies and Integration Points
The file integrates with DRM TV properties, DCB TV configuration, board quirks, GPIO TVDAC controls, DAC load detection helpers, DFP routing helpers, `tvmodesnv17.c` tables/calculations, NV04 RAMDAC/VGA helpers, and Nouveau connector/encoder state.

## Risks
Load detection relies on analog electrical sampling and board quirks; false results affect connector status and subconnector choice. CTV mode setup steals FP resources and can disturb inactive DFP encoders. Property updates for low-definition-only controls are rejected for CTV modes, but callers must handle failures. Several register values are empirical and chipset-specific. Mode changes for norm updates require connector DPMS off.

## Test Signals
Signals include load detection on composite/S-video/component/SCART, quirked pin masks, PAL/NTSC/HD norm switching, low-definition and CTV mode enumeration, DPMS GPIO and DACCLK behavior, FP coexistence on dual-head boards, overscan/flicker/saturation/hue updates, save/restore across suspend, and reject paths for invalid modes/properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.c -->
