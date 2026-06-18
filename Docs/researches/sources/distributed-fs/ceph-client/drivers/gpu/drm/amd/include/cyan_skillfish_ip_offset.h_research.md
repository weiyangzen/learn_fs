# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cyan_skillfish_ip_offset.h

## Purpose
This generated-style AMDGPU header provides Cyan Skillfish SOC15 register base offsets by hardware IP block, instance, and segment. It is a static address-map contract used by Cyan Skillfish register initialization and display code so common register-access macros can derive the correct per-IP base address.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 6 and `MAX_SEGMENT` as 5. `struct IP_BASE_INSTANCE` contains one segment array, and `struct IP_BASE` contains the per-instance table; both are marked `__maybe_unused` to tolerate include sites that only consume flattened macros.

Static `IP_BASE` tables cover `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DMU_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC0_BASE`, and `UVD0_BASE`. Most blocks only populate instance 0. `CLK_BASE` populates all six instances, and several blocks expose multiple segments, notably `DMU_BASE`, `NBIO_BASE`, `SMUIO_BASE`, `GC_BASE`, and `UVD0_BASE`. The bottom half mirrors the table values as `*_BASE__INSTn_SEGm` constants.

## Control Flow
There are no functions. `amdgpu/cyan_skillfish_reg_init.c` includes the table and copies selected `IP_BASE.instance` pointers into `adev->reg_offset` during ASIC register-base setup. Display DCN 2.01 code also includes it for Cyan Skillfish-specific display/clock-resource offsets.

## State And Persistence
All data is immutable compiled-in address metadata. Runtime persistence is indirect: initialized `adev->reg_offset[HWIP][instance][segment]` pointers remain the active address map for the device lifetime. This header performs no allocation, mutation, or persistent storage writes.

## Dependencies And Integration Points
The data shape is coupled to AMDGPU SOC15 register infrastructure, HWIP enum consumers, and generated register headers that expect base indices. It integrates with core AMDGPU initialization and display resource/IRQ/clock management for the Cyan Skillfish APU path.

## Risks
Incorrect offsets make register reads or writes hit the wrong hardware aperture, which can break display bring-up, SMU/MP access, memory hub programming, or GPU reset. `MAX_INSTANCE` and `MAX_SEGMENT` are local to this generated header; include sites must not assume another ASIC's dimensions. The generic `IP_BASE` type names are repeated by many offset headers, so include scope should stay narrow to avoid same-translation-unit redefinition.

## Test Signals
Build coverage of `cyan_skillfish_reg_init.c` and DCN 2.01 include sites catches symbol and type drift. Runtime signals include successful Cyan Skillfish probe, register-base initialization, display enable, SMU/clock access, MMHUB/GFX register reads, and absence of invalid-register or timeout errors during suspend/resume and reset.
