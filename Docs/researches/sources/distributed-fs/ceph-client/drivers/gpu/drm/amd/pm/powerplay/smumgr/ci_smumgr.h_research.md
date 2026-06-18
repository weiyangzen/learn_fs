# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.h

## Purpose

`ci_smumgr.h` defines the private data structures used by `ci_smumgr.c`. It captures CI-specific PowerTune defaults, memory-controller register table data, and the per-device SMU manager backend stored in `hwmgr->smu_backend`.

## Important APIs, types, and constants

The `SMU__NUM_*` macros record CI-era maximum DPM state counts for SCLK, MCLK, LCLK, and PCIe. The header includes `smu7_discrete.h`, `pp_endian.h`, and `ppatomctrl.h`, tying the private structures to SMU7 firmware layouts and VBIOS table parsing.

`struct ci_pt_defaults` stores SVI load-line defaults, TDC defaults, DTE ambient temperature base, display CAC, BAPM thermal gradient, and BAPM RC arrays sized by `SMU7_DTE_ITERATIONS * SMU7_DTE_SOURCES * SMU7_DTE_SINKS`.

`struct ci_mc_reg_entry` stores one memory-clock ceiling and the corresponding memory-controller register values. `struct ci_mc_reg_table` stores the register-address list, entry count, valid-register bitmask, and all timing entries copied and normalized from VBIOS.

`struct ci_smumgr` stores firmware-discovered offsets for soft registers, DPM table, MC register table, fan table, ARB timing table, and ULV settings; cached SMU7 DPM and PM fuse tables; selected PowerTune defaults; cached converted MC registers; and the CI MC register table.

## Control flow

This header has no runtime logic. `ci_smumgr.c` allocates `struct ci_smumgr` during SMU init, fills offsets after firmware-header parsing, populates the cached tables during SMC table initialization, and frees the structure during SMU finalization.

## State and persistence behavior

`struct ci_smumgr` is the persistent per-device software cache for the CI SMU backend. It persists for the lifetime of the hardware manager and mirrors or stages state that is also uploaded into SMC SRAM. Firmware offsets remain valid only for the loaded firmware image; cached DPM/MC/PM-fuse tables must be rebuilt or reuploaded when policy inputs change.

## Dependencies and integration points

The structures are tightly coupled to `SMU7_Discrete_DpmTable`, `SMU7_Discrete_PmFuses`, `SMU7_Discrete_MCRegisters`, ATOM MC register tables, and endian conversion helpers. They are private to the CI SMU manager but indirectly support generic `smumgr` operations through `ci_smu_funcs`.

## Risks

The `validflag` field is `uint16_t`, while `SMU7_DISCRETE_MC_REGISTER_ARRAY_SIZE` may require careful bounds discipline. If more than 16 MC registers vary, high bits cannot be represented here unless the firmware layout also limits the valid set. Firmware offsets are raw `uint32_t` values with no type distinction, so accidental use of the wrong offset field can write valid-looking data to the wrong SMC SRAM region.

Because cached tables mirror packed firmware structures, any upstream SMU7 layout change requires corresponding review of this private state.

## Test signals

Useful validation includes successful allocation/free of `smu_backend`, firmware-header offset discovery, MC table initialization from VBIOS, DPM table upload from cached `smc_state_table`, PM fuse upload from `power_tune_table`, and memory timing updates after MCLK overdrive changes.
