# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_offset.h

## Purpose

`thm_13_0_2_offset.h` is the generated register-address map for the THM 13.0.2 block. It defines `reg*` register offsets and matching base-index macros for the thermal controller aperture whose base address is documented in the file as `0x59800`. It covers current temperature, HTC, thermal trip, GPIO-style thermal pins, interrupts, TMON sensor data, die/software temperatures, fan and pump controls, local thermal-controller state, THM power management, sideband/SBRMI, SMBus, and remote TMON windows.

This file supplies addresses only. Field definitions live in the companion `thm_13_0_2_sh_mask.h`; some field names are also compatible with earlier THM mask headers where hardware layout is shared. SMU13 code uses these `reg*` names with SOC15 register accessors.

## Important APIs, Types, And Constants

There are no functions, types, or variables. The interface is a large list of register offset constants:

- Core thermal controller registers: `regTHM_TCON_CUR_TMP`, `regTHM_TCON_HTC`, `regTHM_TCON_THERM_TRIP`, `regTHM_CTF_DELAY`, and GPIO controls for PROCHOT, THERMTRIP, PWM, tach input, pump out, and pump input.
- Interrupt registers: `regTHM_THERMAL_INT_ENA`, `regTHM_THERMAL_INT_CTRL`, and `regTHM_THERMAL_INT_STATUS`.
- TMON0 and TMON1 sensor data: repeated `RDIL0` through `RDIL15`, `RDIR0` through `RDIR15`, and `INT_DATA` registers, plus `regTHM_TMON0_CTRL` and `regTHM_TMON0_CTRL2`.
- Temperature and thermal aggregation: `regTHM_DIE1_TEMP`, `regTHM_DIE2_TEMP`, `regTHM_DIE3_TEMP`, `regTHM_SW_TEMP`, `regCG_MULT_THERMAL_CTRL`, `regCG_MULT_THERMAL_STATUS`, `regCG_THERMAL_RANGE`, `regTHM_TMON_CONFIG`, `regTHM_TMON_CONFIG2`, and TMON coefficient registers.
- Fan/tach/pump controls: `regCG_FDO_CTRL0`, `regCG_FDO_CTRL1`, `regCG_FDO_CTRL2`, `regCG_TACH_CTRL`, `regCG_TACH_STATUS`, `regCG_THERMAL_STATUS`, `regCG_PUMP_CTRL0`, `regCG_PUMP_CTRL1`, `regCG_PUMP_CTRL2`, `regCG_PUMP_TACH_CTRL`, `regCG_PUMP_TACH_STATUS`, and `regCG_PUMP_STATUS`.
- Local THM state: `regTHM_TCON_LOCAL0` through `regTHM_TCON_LOCAL15`, with `LOCAL13` intentionally listed after `LOCAL14` and `LOCAL15` by its generated offset order.
- Clock/power and MACO: `regXTAL_CNTL`, `regTHM_PWRMGT`, and `regTHM_GPIO_MACO_EN_CTRL`.
- Sideband and management interfaces: `regSBTSI_REMOTE_TEMP`, `regSBRMI_CONTROL`, `regSBRMI_COMMAND`, SBRMI write/read data, core enable, APIC, and MCE status registers.
- SMBus controls: `regSMBUS_CNTL0`, `regSMBUS_CNTL1`, block read/write command controls, timing controls, trigger control, and UDID controls.
- Remote TMON windows: `regTHM_TMON0_REMOTE_START/END`, `regTHM_TMON1_REMOTE_START/END`, and `regTHM_TMON2_REMOTE_START/END`.
- Each register has a `_BASE_IDX` macro set to `0`.

## Control Flow

The header has no executable control flow. Runtime behavior is in SMU13 consumers:

1. SMU13 code includes this offset header and the matching shift/mask header.
2. It reads or writes a THM register using `RREG32_SOC15(THM, 0, reg...)` or `WREG32_SOC15(THM, 0, reg...)`.
3. It extracts or sets fields with `REG_GET_FIELD` and `REG_SET_FIELD`.

For example, `smu_v13_0_set_fan_speed_pwm()` reads `regCG_FDO_CTRL1`, scales a user PWM request by `CG_FDO_CTRL1__FMAX_DUTY100`, writes `regCG_FDO_CTRL0` with `CG_FDO_CTRL0__FDO_STATIC_DUTY`, and then switches the controller into static PWM mode. Other SMU13 thermal paths use the interrupt and temperature-related offsets in the same access pattern.

## State And Persistence Behavior

The header stores no software state and persists nothing. Its register offsets point to hardware MMIO state. Writes through these offsets can persist in THM hardware until reset, firmware action, suspend/resume transition, or another register write changes them.

Because the file represents a complete register map for an ASIC generation, address stability is critical. A single incorrect offset can redirect driver writes to a different THM register and cause persistent hardware misconfiguration for the current boot session.

## Dependencies

The header is guarded by `_thm_13_0_2_OFFSET_HEADER` and has no includes. It depends on:

- SOC15 THM instance access conventions that understand `reg*` names and `_BASE_IDX`.
- Companion field definitions, usually `thm_13_0_2_sh_mask.h`.
- Correct ASIC selection in PM/SMU code so THM 13.0.2 offsets are not used on incompatible hardware.

## Integration Points

The main visible integration point is `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c`, which includes this header and uses `regCG_FDO_CTRL*` in fan PWM control. Other SMU13 platform files can rely on the same register map for thermal interrupt handling, temperature telemetry, fan/tach/pump control, and sideband/SMBus operations.

The register groups indicate integration with:

- Thermal telemetry paths for current, die, software, local/remote TMON, max/min, and critical temperature reporting.
- Thermal safety paths for HTC, thermal trip, CTF delay, PROCHOT, THERMTRIP, and interrupt routing.
- Cooling-device paths for fan duty, static PWM mode, tachometer target/status, and pump control/status.
- Power-management paths for THM clock gating, MACO enable, XTAL control, and sideband interfaces.
- Platform-management side channels via SBRMI and SMBus command/status registers.

## Risks

- ASIC-generation mismatch is the dominant risk. THM 13.0.2 uses `reg*` offsets that do not match the smaller THM 11.0.2 `mm*` map; mixing headers can access wrong registers.
- The file contains many repeated TMON offsets. Off-by-one generation errors in repeated `RDIL`/`RDIR` blocks could skew sensor selection while still compiling cleanly.
- Fan, pump, and thermal trip registers are operationally sensitive. Wrong offsets can affect cooling, acoustic control, or thermal protection.
- Sideband and SMBus register offsets can affect platform-management communication; incorrect writes may break command transactions or expose stale status.
- `LOCAL13` appears after `LOCAL14` and `LOCAL15` in generated order. Consumers should use symbolic names, not assume monotonic source order implies semantic sequence.

## Test Signals

Good validation signals include:

- Build coverage for SMU13 code that includes `thm_13_0_2_offset.h`.
- Register-access trace comparison against THM 13.0.2 hardware specifications or a known-good AMDGPU version.
- Fan PWM validation on SMU13 hardware: manual mode should change `regCG_FDO_CTRL0` duty and reported duty/status predictably.
- Temperature telemetry tests covering current, die, TMON, and aggregated max/min readings across idle and load.
- Thermal interrupt and trip tests checking threshold writes, event clear/status behavior, and interrupt delivery.
- Suspend/resume, runtime PM, and MACO/BACO-adjacent tests to catch registers that lose or incorrectly retain THM state across power transitions.
