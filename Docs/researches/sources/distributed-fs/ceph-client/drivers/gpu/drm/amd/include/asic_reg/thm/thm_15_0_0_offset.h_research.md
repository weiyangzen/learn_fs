# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_15_0_0_offset.h

## Purpose
`thm_15_0_0_offset.h` is a generated AMDGPU thermal-management register offset header for the THM block named `thm_thm_SmuThmDec`, whose documented base address is `0x59800`. It defines symbolic register offsets and base-index constants for THM 15.0.0 hardware so driver code can address temperature, hot-throttle, thermal-trip, SMU SBI, SBRMI, and SMBus registers through SOC15 register access helpers.

## Important APIs, Types, And Functions
This file exports only preprocessor constants. The main API surface is the `reg...` namespace, for example `regTHM_TCON_CUR_TMP`, `regTHM_TCON_HTC`, `regTHM_TCON_THERM_TRIP`, `regCG_MULT_THERMAL_STATUS`, `regTHM_DIE1_TEMP`, `regSMUSBI_SBIREGADDR`, `regSBRMI_COMMAND`, and `regSMBUS_CNTL0`. Every offset has a companion `..._BASE_IDX` macro, all set to `0`, for use by AMDGPU's indexed SOC register macros.

## Control Flow
There is no runtime control flow. At compile time, including code expands these macros into numeric offsets. At runtime, call sites pass the symbols to helpers such as `RREG32_SOC15()` and `WREG32_SOC15()`; those helpers combine the THM block instance, base index, and offset to perform MMIO reads and writes.

## State, Persistence, And Dependencies
The header stores no software state and performs no persistence. The persistent state is the hardware register file addressed by these constants. It depends on matching AMD ASIC register-generation data and on consumers including the corresponding shift/mask header, especially `thm_15_0_0_sh_mask.h`, to decode or modify fields after reading a register.

## Integration Points
The direct in-tree include is `pm/swsmu/smu15/smu_v15_0.c`, where this header is paired with `thm_15_0_0_sh_mask.h` and MP 15 register headers. The THM register names integrate with the AMDGPU power-management stack, SMU firmware interface code, interrupt/thermal handling, and platform-management paths that need thermal status or sideband control.

## Risks
Because this file maps symbolic names to hardware addresses, an incorrect offset can make the driver read or write the wrong THM register. The THM 15.0.0 map is not a strict superset of THM 9.0: newer `reg` names omit many fan, pump, BACO, and thermal-interrupt offsets present in the older `mm` map while adding a compact local-temperature and SMU-sideband set. Mixing this header with a mismatched sh/mask header or older `mm...` call sites would silently corrupt field interpretation.

## Test Signals
Useful signals are successful AMDGPU builds for SMU 15 targets, boot logs without THM register access faults, correct temperature readings through hwmon/SMU paths, no unexpected PROCHOT/thermal-trip events, and register readback checks on THM 15.0.0 hardware that confirm offsets such as `regCG_MULT_THERMAL_STATUS` and `regSMBUS_CNTL0` land on documented registers.
