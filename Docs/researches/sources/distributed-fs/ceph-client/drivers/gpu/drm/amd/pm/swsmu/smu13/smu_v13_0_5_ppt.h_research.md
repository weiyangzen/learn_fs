# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.h

## Purpose
`smu_v13_0_5_ppt.h` is the public header for the SMU13.0.5 PPT backend. It exposes the backend registration entry point and defines the SMU13.0.5 UMD pstate GFX clock value used by the implementation's clock-level and profile logic.

## Important APIs, Types, And Data
- `void smu_v13_0_5_set_ppt_funcs(struct smu_context *smu)` is the single externally visible function. ASIC selection code calls it to bind SMU13.0.5-specific `pptable_funcs`, feature maps, table maps, driver interface version, APU flag, and message-control registers into the `smu_context`.
- `SMU_13_0_5_UMD_PSTATE_GFXCLK` is defined as `700` MHz. The `.c` backend uses it as the synthetic standard/middle GFX clock displayed when the current GFX clock is neither the configured min nor max and as the default standard profile clock.
- The include guard is `__SMU_V13_0_5_PPT_H__`.

## Control Flow And Behavior
- This header has no control flow of its own. Its declaration is the linkage contract between ASIC dispatch/probe code and `smu_v13_0_5_ppt.c`.
- The macro constant influences `smu_v13_0_5_emit_clk_levels()` and `smu_v13_0_5_get_dpm_profile_freq()` by providing a fixed UMD pstate clock when firmware DPM tables do not provide a separate standard GFX point.

## State And Persistence
- The header stores no state. Persistent state is established by the implementation after `smu_v13_0_5_set_ppt_funcs()` is called.
- The macro is compile-time configuration; changing it changes user-visible clock-level output and standard profile behavior.

## Dependencies And Integration Points
- The declaration depends on `struct smu_context` being visible to users of the header, normally through existing AMDGPU SMU include ordering.
- It integrates with SMU ASIC selection code and with the SMU13.0.5 implementation file.

## Risks And Edge Cases
- Because `SMU_13_0_5_UMD_PSTATE_GFXCLK` is hard-coded, it can diverge from firmware or silicon-specific standard clocks. That affects sysfs presentation and profile-standard behavior.
- The header intentionally does not include a forward declaration for `struct smu_context`; include-order changes could expose that implicit dependency.

## Test Signals
- Build coverage should confirm consumers include this header in an order where `struct smu_context` is known.
- ASIC probe tests should verify that calling `smu_v13_0_5_set_ppt_funcs()` succeeds and the installed callbacks behave as expected.
- Clock-level/profile tests should verify the `700` MHz pstate appears only in the intended GFX standard/middle cases.
