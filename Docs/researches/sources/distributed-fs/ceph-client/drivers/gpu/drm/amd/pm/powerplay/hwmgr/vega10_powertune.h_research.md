# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.h

## Purpose

This header defines the Vega10 PowerTune register-description types, PowerContainment feature masks, and public hwmgr entry points implemented by `vega10_powertune.c`.

## Important APIs, Types, and Functions

`enum vega10_pt_config_reg_type` classifies generic PowerTune register locations as MMR, SMC indirect, DIDT indirect, cache, or max. `enum vega10_didt_config_reg_type` selects the indirect register aperture used by DIDT programming: DIDT, GC CAC, or SE CAC. `struct vega10_pt_config_reg` and `struct vega10_didt_config_reg` describe offset/mask/shift/value writes; the latter is the active structure for the table-driven DiDt implementation. `struct vega10_pt_defaults` preserves legacy default knobs for SVI load line, TDC, and DTE-related behavior. The exported functions cover PowerTune defaults, BAPM/fuse/CAC declarations, power containment, power limit/overdrive control, and DiDt enable/disable.

## Control Flow, State, and Persistence

The header itself holds no state, but it defines the contracts used to mutate `hwmgr->pptable`, `hwmgr->platform_descriptor`, `hwmgr->power_limit`, and `vega10_hwmgr` SMC feature state. Its register tuple structs are consumed as static const arrays in the C file, usually ending with an `offset` sentinel of `0xFFFFFFFF`.

## Dependencies and Integration Points

It assumes `struct pp_hwmgr` and fixed-width integer types are available through earlier hwmgr includes. The prototypes are consumed by `vega10_hwmgr.c` and related Vega10 backend code. Several declared functions, such as BAPM/fuse/CAC population, are not implemented in the paired file in this source subset, so their definitions must be resolved elsewhere or may be vestigial for this tree revision.

## Risks and Test Signals

The generic `vega10_pt_config_reg_type` is broader than the implementation visible here, which can mislead maintainers about supported paths. Tests should compile all users of this header, verify declarations match definitions, and exercise any code that constructs register tables against the expected sentinel convention and enum aperture values.
