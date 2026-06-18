# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_13_0_2_sh_mask.h

## Purpose

`thm_13_0_2_sh_mask.h` is a generated AMDGPU ASIC register bitfield header for the THM block on SMU/PM firmware generation 13.0.2 hardware. It does not define executable code; it defines C preprocessor constants that describe bit shifts and bit masks for fields inside THM, thermal monitor, fan, pump, clock/power, SBRMI, SBTSI, and SMBus registers. The companion offset header supplies register addresses; this file supplies the layout of each 32-bit register value once a caller has read or is preparing to write the register.

The header is consumed by the AMDGPU power-management stack through `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c`, which includes both `thm_13_0_2_offset.h` and this mask file. The most visible uses are thermal interrupt programming and fan/tachometer programming, where the driver combines `RREG32_SOC15`/`WREG32_SOC15` register IO with `REG_GET_FIELD` and `REG_SET_FIELD` bitfield helpers.

## Important APIs, types, and constants

The exported interface is entirely macro based:

- `REGISTER__FIELD__SHIFT` constants define the low bit position of a field.
- `REGISTER__FIELD_MASK` constants define the full field mask in the 32-bit register word.
- Register comments such as `//THM_TCON_CUR_TMP` and `//CG_FDO_CTRL0` segment the generated field table by hardware register.
- The include guard is `_thm_13_0_2_SH_MASK_HEADER`.

Important register families covered by this header include:

- `THM_TCON_CUR_TMP`: current temperature register fields such as `CUR_TEMP`, `CUR_TEMP_RANGE_SEL`, `CUR_TEMP_TJ_SEL`, `CUR_TEMP_TJ_SLEW_SEL`, and `MCM_EN`. `CUR_TEMP` occupies bits 31:21 via `0xFFE00000`, which is the field used by temperature-reading paths on related SMU generations.
- `THM_TCON_HTC` and `THM_TCON_THERM_TRIP`: hardware thermal control, PROCHOT, hysteresis, thermal trip enable/status, and software thermal trip fields.
- `THM_GPIO_*_CTRL`: common GPIO pad control layouts for PROCHOT, thermtrip, PWM, tach input, pump out, and pump in pins. These define pull-up/down, Schmitt enable, output enable override, pin data, and readback bits.
- `THM_THERMAL_INT_ENA`, `THM_THERMAL_INT_CTRL`, and `THM_THERMAL_INT_STATUS`: thermal interrupt set/clear, high/low threshold, trigger mask, PROCHOT mask, IH hardware enable, and interrupt credit fields.
- `THM_TMON0_*`, `THM_TMON1_*`, `THM_DIE*_TEMP`, `THM_TMON_CONFIG*`, and `THM_TMON*_COEFF`: a dense thermal monitor sensor map. The RDIL/RDIR arrays expose repeated `Z`, `VALID`, and `TEMP` fields for many sensor lanes; control/configuration fields define power-down, acquisition, calibration, coefficient, and present-bit behavior.
- `CG_MULT_THERMAL_*` and `CG_THERMAL_RANGE`: filtered/multiple thermal status and ASIC min/max thermal range fields.
- `CG_FDO_*`, `CG_TACH_*`, and `CG_THERMAL_STATUS`: fan duty, fan spin-up, manual PWM mode, hysteresis, ramp, tach target, tach status, and PWM duty readback fields.
- `CG_PUMP_*`: pump duty, pump spin-up, manual PWM mode, tach, and status fields paralleling the fan control group.
- `THM_TCON_LOCAL*`: local temperature-controller state such as global TMAX/TMIN values, sensor IDs, Tj max fields, TMON power-down controls, and boot completion.
- `XTAL_CNTL` and `THM_PWRMGT`: THM reference-clock, clock gate, fan/pump gate, and prototype TSEN clock toggle controls.
- `SBTSI_REMOTE_TEMP`, `SBRMI_*`, `SMBUS_*`, and remote TMON start/end fields: sideband temperature and management bus command/data/timing/UDID register layouts.

The file contains 1,111 `#define` lines and 1297 total lines. It is significantly broader than the v14 mask file in this work item because it includes the TMON0/TMON1 sensor arrays and remote TMON start/end definitions.

## Control flow

There is no runtime control flow inside the header. It affects control flow indirectly by making call sites select, set, clear, or decode specific hardware bits. In `smu_v13_0.c`, the constants participate in these flows:

- Fan control writes `regCG_FDO_CTRL2` and `regCG_FDO_CTRL0` with `REG_SET_FIELD(..., CG_FDO_CTRL2, TMIN, ...)`, `FDO_PWM_MODE`, and `FDO_STATIC_DUTY`.
- Fan speed conversion reads `regCG_FDO_CTRL1` and extracts `CG_FDO_CTRL1.FMAX_DUTY100`.
- Tachometer target programming writes `regCG_TACH_CTRL.TARGET_PERIOD`.
- Thermal interrupt disable masks `THERM_INTH_MASK` and `THERM_INTL_MASK`, then writes `regTHM_THERMAL_INT_ENA` to clear/disable interrupt delivery.
- Thermal interrupt enable/configuration sets `MAX_IH_CREDIT`, `THERM_IH_HW_ENA`, `DIG_THERM_INTH`, and `DIG_THERM_INTL`, then clears pending high/low/trigger bits using the `THM_THERMAL_INT_ENA__*_CLR__SHIFT` constants.
- Thermal interrupt handling adjusts high/low threshold fields in response to IH events and clears the trigger mask using `THM_THERMAL_INT_CTRL__THERM_TRIGGER_MASK_MASK`.

Because the macro names encode the register and field names, the Linux register helper macros can token-paste the selected register and field into the correct mask/shift constant. Any rename or field-layout change in this file can therefore alter compile-time expansion for driver code without changing the C call sites.

## State and persistence behavior

The file stores no software state and allocates no memory. The state it describes lives in hardware registers in the THM, fan, pump, sensor, and sideband-management blocks. Persistence is therefore governed by ASIC reset, power-management transitions, firmware initialization, BACO/low-power sequences, and suspend/resume behavior, not by this header.

Some described fields are explicitly stateful hardware latches or controls:

- Thermal interrupt status/detect bits record threshold crossings until cleared.
- `THM_TCON_HTC__HTC_ACTIVE_LOG_MASK` records HTC activity.
- `THM_TCON_THERM_TRIP__SW_THERM_TP_MASK` can assert a software thermal trip.
- TMON `VALID` fields qualify sensor data before consumers should trust `TEMP`.
- Fan and pump manual/static duty fields persist as programmed register values until another driver/firmware path changes them.
- SMBus/SBRMI command status bits describe command completion, unsupported command, abort, and status nibbles.

Driver code must treat these values as live hardware state, often shared with SMU firmware, not as ordinary software configuration.

## Dependencies and integration points

Primary dependencies are the AMDGPU register access stack and companion generated register headers:

- `thm_13_0_2_offset.h` supplies `reg...` addresses for the same THM register names.
- `smu_v13_0.c` includes this file and uses the fields through `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, and `REG_SET_FIELD`.
- `soc15_common.h` and AMDGPU SMU support code provide the register access and field helper semantics.
- THM interrupt programming integrates with the AMDGPU interrupt handler path through thermal source IDs and `SMU_THERMAL_MINIMUM_ALERT_TEMP`/alert-range logic.
- BACO paths in `smu_v13_0.c` integrate with THM-related low-power behavior, although the visible v13 BACO control flow mostly uses SMU messages rather than directly writing the `THM_BACO_*` fields from this header.

The generated names intentionally match hardware register specifications. The value of the file is not local abstraction; it is exact ABI compatibility with silicon.

## Risks

The main risk is silent hardware misprogramming if masks or shifts do not match the target ASIC. A wrong thermal threshold mask can suppress interrupts, fire interrupts at the wrong temperature, or leave trigger bits uncleared. A wrong fan or pump duty field can produce incorrect cooling behavior. A wrong GPIO bit can invert or disable PROCHOT/THERMTRIP signaling. A wrong SMBus/SBRMI field can corrupt sideband commands.

There is also a cross-generation compatibility risk. Many names match older and newer THM headers, but field presence and reserved ranges differ. For example, this v13 file lacks `THM_TCON_CUR_TMP__REMOTE_TJ_SEL`, which appears in the v14 mask file. Consumers must include the header matching the IP version selected by the SMU code and must not assume all generations expose identical fields.

Because these are preprocessor constants, type checking is minimal. If a register address from one generation is paired with masks from another generation, the code can compile while programming the wrong bits.

## Test signals

Useful validation signals include:

- Build coverage of `smu_v13_0.c` with this header included, proving all token-pasted fields resolve.
- Register read/write traces showing expected values in `regTHM_THERMAL_INT_CTRL`, `regTHM_THERMAL_INT_ENA`, `regCG_FDO_CTRL*`, and `regCG_TACH_CTRL`.
- Thermal interrupt tests that cross high/low thresholds and confirm IH delivery, threshold reprogramming, and clear-bit behavior.
- Fan control tests that set PWM modes and duty cycles and verify tachometer feedback.
- Hardware-monitor readings that compare decoded `CUR_TEMP`, ASIC max temperature, and TMON/DIE valid/temp fields against SMU telemetry.
- Suspend/resume and BACO tests that confirm THM state is reinitialized or preserved according to firmware expectations.
