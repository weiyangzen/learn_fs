<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.h

## Purpose

`cyan_skillfish_ppt.h` is the public header for the Cyan Skillfish SMU11.8 PPT implementation. It exports only the function-table installer used by platform dispatch.

## Important APIs, Types, and Functions

The sole API is `extern void cyan_skillfish_set_ppt_funcs(struct smu_context *smu);`. There are no local types, macros, state objects, or inline helpers.

## Control Flow

No control flow exists here. Runtime dispatch calls the exported function implemented in `cyan_skillfish_ppt.c`, which installs Cyan Skillfish-specific `pptable_funcs`, maps, the APU flag, and message control.

## State and Persistence Behavior

The header stores no state. The implementation mutates the supplied `smu_context` by assigning function tables and platform metadata.

## Dependencies

It depends on a visible `struct smu_context` declaration from including code and the include guard `__CYAN_SKILLFISH_PPT_H__`.

## Integration Points

The header connects common SMU platform selection code to `cyan_skillfish_ppt.c`, which is compiled by the SMU11 makefile. It is part of AMDGPU's Cyan Skillfish APU PM dispatch path.

## Risks and Edge Cases

The interface is intentionally narrow; adding new exported helpers would couple platform-specific internals to common code. Consumers must call the installer only for Cyan Skillfish-compatible devices.

## Test Signals

Build coverage and successful Cyan Skillfish probe with `smu->ppt_funcs` installed are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.h -->
