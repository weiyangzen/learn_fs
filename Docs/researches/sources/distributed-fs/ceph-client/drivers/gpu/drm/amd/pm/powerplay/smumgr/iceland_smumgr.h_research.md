# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/iceland_smumgr.h

### Purpose
`iceland_smumgr.h` declares the Iceland-specific SMU manager backend and memory-controller register table types used by `iceland_smumgr.c`. It ties common SMU7 manager state to SMU71 firmware-visible DPM, ULV, PM-fuse, and MC-register structures.

### Important APIs, Types, And Functions
`struct iceland_pt_defaults` stores PowerTune defaults and BAPM thermal model constants: SVI load-line settings, TDC fields, DTE ambient base, display CAC, BAPM temperature gradient, and flattened BAPMTI R/RC arrays sized by SMU71 DTE dimensions. `struct iceland_mc_reg_entry` stores one maximum-MCLK timing entry and its MC register values. `struct iceland_mc_reg_table` stores the driver-side MC table copied and expanded from AtomBIOS: count fields, a valid-bit mask, timing entries, and S0/S1 MC register addresses. `struct iceland_smumgr` embeds common `smu7_smumgr`, SMU71 DPM/PM-fuse/ULV state, selected defaults, converted SMU71 MC registers, and the driver-format MC register table.

### Control Flow
This header has no executable control flow. `iceland_smu_init()` allocates `struct iceland_smumgr`; initialization helpers fill the DPM, PM-fuse, ULV, and MC table members; `iceland_init_smc_table()` and MC update helpers upload those cached members into SMC SRAM. The defaults pointer is assigned based on PCI device ID before BAPM and PM-fuse population.

### State, Persistence, And Dependencies
The declared structures persist as the SMU backend for the lifetime of the hardware manager. `mc_reg_table` is driver-format state retained so later MCLK DPM changes can regenerate `mc_regs` for the SMU without repeating all AtomBIOS parsing. The header depends on `smu7_smumgr.h`, `pp_endian.h`, and `smu71_discrete.h` for common state, conversion helpers, table sizes, and firmware-visible structures.

### Integration Points
`iceland_smumgr.c` includes this header and casts `hwmgr->smu_backend` to `struct iceland_smumgr` throughout. The embedded first member allows common SMU7 routines to operate on the backend as `struct smu7_smumgr`. MC register types are the handoff between AtomBIOS MC register tables and SMU71 `SMU71_Discrete_MCRegisters` upload format.

### Risks
The `validflag` field is a 16-bit mask but `SMU71_DISCRETE_MC_REGISTER_ARRAY_SIZE` can drive loops over more entries if definitions change, so size assumptions must stay aligned. The embedded-first-member pattern is important for common cleanup and address access. BAPMTI arrays must match SMU71 DTE constants exactly or defaults will be copied incorrectly into the firmware table.

### Test Signals
Build tests should catch mismatched SMU71 constants and missing type declarations. Runtime signals include successful backend allocation, correct device-default selection, MC register table bounds validation, validflag generation, SMC MC register upload sizes, and common SMU7 finalization working through the embedded `smu7_data`.
