# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/fiji_smumgr.h

### Purpose
`fiji_smumgr.h` declares the Fiji-specific SMU manager private data used by `fiji_smumgr.c`. It binds common SMU7 manager state to the SMU73 discrete table layouts required by Fiji firmware.

### Important APIs, Types, And Functions
`struct fiji_pt_defaults` defines default PowerTune fields used to seed the SMU PM-fuse and DPM tables: SVI load-line enable/value, TDC throttle release, TDC MAW time, TDC waterfall control, and DTE ambient temperature base. `struct fiji_smumgr` is the private backend stored in `pp_hwmgr.smu_backend`; it embeds `struct smu7_smumgr`, an `SMU73_Discrete_DpmTable`, an `SMU73_Discrete_Ulv`, an `SMU73_Discrete_PmFuses`, and a pointer to the selected defaults.

### Control Flow
The header itself has no executable control flow. At runtime `fiji_smu_init()` allocates this structure, helper functions fill its DPM/ULV/PM-fuse members, and upload paths copy those members into SMC SRAM. The defaults pointer is selected during SMC table initialization before PM-fuse and BAPM population.

### State, Persistence, And Dependencies
The declared state is in-memory driver state that persists for the lifetime of the hardware manager backend and is released by the common SMU7 finalizer. It depends on `smu73_discrete.h` for firmware-visible table types, `smu7_smumgr.h` for common SMU7 state, and `pp_endian.h` for host/SMC conversion macros used by the implementation.

### Integration Points
This header is included by `fiji_smumgr.c` and is part of the ASIC-specific PowerPlay SMU manager boundary. Generic code sees the backend through `pp_smumgr_func`; Fiji-specific code casts `hwmgr->smu_backend` back to `struct fiji_smumgr` to access cached table addresses and SMU73 table instances.

### Risks
The structure layout must remain consistent with implementation casts and common-finalizer expectations: `smu7_data` is the first member, allowing common SMU7 code to treat the backend as `struct smu7_smumgr`. The firmware-visible table members are large and layout-sensitive; changing their types or conversion assumptions would break SMC uploads.

### Test Signals
Build coverage should catch missing SMU73 type definitions and include-order regressions. Runtime signals include successful allocation, common SMU7 initialization, SMC table population without NULL defaults, and correct common cleanup through the embedded first-member `smu7_data`.
