# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/sislands_smc.h

## Purpose
`sislands_smc.h` defines the packed host/firmware ABI for Southern Islands SMC power management. It describes SMC performance levels, software states, voltage masks, fan control tables, CAC/powertune configuration, memory-controller register tables, SPLL divider tables, DTE thermal-estimation configuration, firmware-header offsets, and the SI SMC helper function prototypes implemented in `si_smc.c`.

## Important APIs, Types, And State
The `#pragma pack(push, 1)` block is essential: structures such as `SISLANDS_SMC_HW_PERFORMANCE_LEVEL`, `SISLANDS_SMC_STATETABLE`, `PP_SIslands_CacConfig`, `SMC_SIslands_MCRegisters`, `SMC_SISLANDS_SPLL_DIV_TABLE`, and `Smc_SIslands_DTE_Configuration` must be byte-exact for firmware SRAM consumption. Constants such as `SI_SMC_SOFT_REGISTER_*` and `SISLANDS_SMC_FIRMWARE_HEADER_*` are offsets into SMC soft-register and firmware metadata areas. The function declarations expose byte copy, SRAM dword access, firmware loading, SMC start/reset/clock, and SMC message operations.

## Control Flow And Integration
This header is consumed by SI DPM state construction and SMC upload code. Host code fills the packed tables, converts values as needed for the SMC address space, discovers firmware table addresses through the firmware-header offsets, and writes data through `amdgpu_si_copy_bytes_to_smc()` or dword helpers. It depends on `ppsmc.h` for message and result enums.

## Risks And Test Signals
ABI mismatch is the dominant risk: packing, array dimensions, field order, and offset constants are firmware contracts. Flexible-array state definitions require allocation discipline. Test signals include correct SMC firmware boot, valid fan and CAC behavior, successful DPM level transitions, no SRAM-bound errors from SI SMC helpers, and no thermal or memory-clock instability.
