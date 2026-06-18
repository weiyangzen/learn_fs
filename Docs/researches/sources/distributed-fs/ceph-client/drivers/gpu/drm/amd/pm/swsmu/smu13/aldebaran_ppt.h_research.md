# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.h

## Purpose
`aldebaran_ppt.h` is the public header for the Aldebaran SMU13 power-play table implementation. It defines Aldebaran-specific DPM/PCIe table shapes and exposes `aldebaran_set_ppt_funcs(struct smu_context *smu)` for PPT registration.

## Important APIs, Types, And Constants
The exported API is `aldebaran_set_ppt_funcs`. The main types are `aldebaran_dpm_level`, `aldebaran_dpm_state`, `aldebaran_single_dpm_table`, `aldebaran_pcie_table`, and `aldebaran_dpm_table`. Constants define UMD pstate levels, a maximum of 16 DPM levels, and two PCIe configurations.

## Control Flow
ASIC selection code calls the registration function, after which the implementation satisfies the generic `pptable_funcs` contract. The structs are implementation data used to cache PMFW/VBIOS-derived DPM levels and PCIe settings.

## State And Persistence
The header owns no storage. Its structures represent in-memory runtime state; persistence across suspend/resume depends on the owning Aldebaran implementation rebuilding or restoring those tables.

## Dependencies And Integration Points
It depends on the AMDGPU SMU framework and `struct smu_context`. It integrates with DPM clock reporting, UMD pstates, PCIe link reporting, and the PPT dispatch model.

## Risks
The fixed arrays are the main correctness boundary. Implementations must clamp firmware-reported counts to `MAX_DPM_NUMBER` and `ALDEBARAN_MAX_PCIE_CONF`. Struct changes must stay synchronized with the C implementation.

## Test Signals
Successful Aldebaran probe, populated DPM sysfs levels, valid PCIe level output, suspend/resume DPM restoration, and no table-count overflow warnings are the most relevant signals.
