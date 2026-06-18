# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_9_0_sh_mask.h

## Purpose
This generated AMDGPU register header describes bit shifts and masks for the THM 9.0 thermal-management register block. It contains no executable code; it is compile-time metadata used by AMD power-management and thermal code to read, write, and preserve fields in THM, CG thermal, fan, pump, BACO, SBRMI, and SMBus registers.

## Important APIs, Types, and Functions
The exported interface is a set of preprocessor macros named `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Important families include `THM_TCON_CUR_TMP`, `THM_TCON_HTC`, `THM_TCON_THERM_TRIP`, repeated `THM_GPIO_*_CTRL` fields, `THM_THERMAL_INT_ENA`, `THM_THERMAL_INT_CTRL`, `THM_THERMAL_INT_STATUS`, many `THM_TMON*_*_DATA` fields, `THM_DIE*_TEMP`, `CG_MULT_THERMAL_*`, fan and pump families (`CG_FDO_*`, `CG_TACH_*`, `CG_PUMP_*`), `THM_TCON_LOCAL*`, `THM_BACO_*`, `XTAL_CNTL`, `SBRMI_*`, and `SMBUS_*`. There are no C types or functions; consumers use these macros through `REG_GET_FIELD`, `REG_SET_FIELD`, direct masks, and SOC15 register accessors.

## Control Flow
This header has no runtime control flow. It participates when included by PM code. Vega thermal code reads `CG_MULT_THERMAL_STATUS__CTF_TEMP`, programs `THM_THERMAL_INT_CTRL` thresholds, clears events through `THM_THERMAL_INT_ENA`, and masks or unmasks thermal interrupts. SMU v11/v13 code uses the same thermal interrupt fields for handler credits, high/low thresholds, trigger masks, and CTF shutdown paths. Older hwmgr code reads `THM_TCON_CUR_TMP` to convert sensor fields into temperatures.

## State and Persistence Behavior
The header itself stores no state. The macros describe hardware registers whose values persist in GPU register state until reset, suspend/resume reprogramming, BACO/MACO transitions, firmware intervention, or driver writes. Fields here can affect persistent hardware behavior such as thermal interrupt enablement, fan and pump PWM mode, GPIO output enable, BACO isolation timing, and SMBus readiness.

## Dependencies and Integration Points
It depends only on the C preprocessor and include guards. It is paired with `thm_9_0_offset.h` and `thm_9_0_default.h`. Integration points include `pm/powerplay/hwmgr/vega10_thermal.c`, `vega12_thermal.c`, `vega12_inc.h`, SMU thermal setup in `pm/swsmu/smu11/smu_v11_0.c`, related SMU v13 thermal code, and SOC15 THM IP base tables.

## Risks
The primary risk is hardware field drift. A wrong mask or shift can corrupt adjacent control bits, misreport temperature, suppress thermal interrupts, or program unsafe fan, pump, PROCHOT, or CTF behavior. Thermal fields are safety relevant: incorrect threshold or CTF mask handling can delay shutdown or create spurious shutdowns. Repeated GPIO and TMON macro families are easy to copy incorrectly, and callers must apply the correct temperature unit conversion.

## Test Signals
Compile-test AMDGPU configurations that include Vega, SMU11, and SMU13 thermal paths. Runtime signals include correct `hwmon` temperature readings, thermal interrupt registration, high/low threshold programming, fan and pump PWM behavior, BACO/MACO stability, and CTF handling. Register dumps should verify `THM_THERMAL_INT_CTRL`, `THM_THERMAL_INT_ENA`, `CG_MULT_THERMAL_STATUS`, and `THM_TCON_CUR_TMP` field placement.
