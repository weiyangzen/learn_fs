# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_6_0_sh_mask.h

## Purpose

`smu_6_0_sh_mask.h` is the SMU 6.0 field-layout companion to `smu_6_0_d.h`. It exports generated bit masks and shift values for Southern Islands SMU, clock, thermal, GPIO, power-management, LCAC/CAC, and SMC indirect/mailbox registers. It has no executable code; its role is to let consumers compose and decode register values safely by symbolic field names.

The include guard is `SMU_6_0_SH_MASK_H`. The generated naming convention is:

- `REGISTER__FIELD_MASK` is the bit mask already positioned in the 32-bit register value.
- `REGISTER__FIELD__SHIFT` is the shift amount for encoding or decoding the field.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or variables. The macro namespace is the API.

Important groups include:

- Clock-gating and timer fields: `CG_AT__CG_R/L`, `CG_BSP__BSP/BSU`, `CG_GIT__CG_GICST/CG_GIPOT`, `CG_SSP__SST/SSTU`, `CG_FFCT_0__UTC_0/DTC_0`, and `CG_CAC_CTRL__CAC_WINDOW`.
- Clock pin and display gap fields: `CG_CLKPIN_CNTL__XTALIN_DIVIDE`, `CG_CLKPIN_CNTL__BCLK_AS_XCLK`, `CG_CLKPIN_CNTL_2__FORCE_BIF_REFCLK_EN`, `CG_CLKPIN_CNTL_2__MUX_TCLK_TO_XCLK`, and `CG_DISPLAY_GAP_CNTL__*`.
- SPLL fields: `CG_SPLL_FUNC_CNTL__SPLL_RESET`, `SPLL_SLEEP`, `SPLL_BYPASS_EN`, `SPLL_REF_DIV`, `SPLL_PDIV_A`; `CG_SPLL_FUNC_CNTL_2__SCLK_MUX_SEL`, `SPLL_CTLREQ_CHG`, `SCLK_MUX_UPDATE`; `CG_SPLL_FUNC_CNTL_3__SPLL_FB_DIV`, `SPLL_DITHEN`; `CG_SPLL_STATUS__SPLL_CHG_STATUS`; and spread-spectrum fields `SSEN`, `CLK_S`, and `CLK_V`.
- Thermal/fan fields: `CG_THERMAL_CTRL__DPM_EVENT_SRC/DIG_THERM_DPM`, `CG_THERMAL_STATUS__FDO_PWM_DUTY`, `CG_THERMAL_INT__DIG_THERM_INTH/INTL` and interrupt masks, multi-thermal temperature fields, `CG_FDO_CTRL*`, and `CG_TACH_*`.
- General power and SCLK fields: `GENERAL_PWRMGT__GLOBAL_PWRMGT_EN`, static PM, thermal protection, SMIO index, voltage PM, dynamic spread spectrum, and `SCLK_PWRMGT_CNTL__*` clock-off/light-sleep controls.
- GPIO fields: whole-pad masks for `GPIOPAD_A`, `EN`, `Y`, `MASK`, pull-up/down, receiver select, interrupt enable/polarity/type/status/status-enable, software interrupt bits, pinstrap bits `0..30`, strength fields, and external trigger controls.
- LCAC fields: `LCAC_MC0_*` through `LCAC_MC5_*` enable, threshold, override-select, and override-value fields.
- SMC indirect/mailbox fields: `SMC_IND_ACCESS_CNTL__AUTO_INCREMENT_IND_0..3`, 32-bit data/index fields, `SMC_MESSAGE_*__SMC_MSG`, `SMC_RESP_*__SMC_RESP`, and `SMC_PC_C__smc_pc_c`.
- Thermal monitor indexed data fields: repeated `THM_TMON0_*` and `THM_TMON1_*` definitions for `TEMP`, `VALID`, and `Z` across `INT_DATA`, `RDIL0..15`, and `RDIR0..15`, plus debug fields.

## Control Flow And Data Flow

This header has no runtime control flow. In consumers, the data flow is:

1. Select an address from `smu_6_0_d.h`.
2. Read a register value or initialize a new value.
3. Clear fields with `~REGISTER__FIELD_MASK`.
4. Encode new values with `value << REGISTER__FIELD__SHIFT` and the corresponding mask, or decode by masking and shifting right.
5. Write the final value through the appropriate MMIO or SMC helper.

Concrete flows in this tree include:

- `si_smc.c` uses `SMC_IND_ACCESS_CNTL__AUTO_INCREMENT_IND_0_MASK` to enable auto-increment while streaming SMC firmware words through `mmSMC_IND_DATA_0`, then clears it after the upload. The same field is disabled for single-address SRAM reads/writes.
- `si_dpm.c` decodes `CG_SPLL_FUNC_CNTL__SPLL_PDIV_A`, `CG_SPLL_FUNC_CNTL_3__SPLL_FB_DIV`, and spread-spectrum fields to build an SMC SPLL divider table, then constructs new SPLL register values with the same masks and shifts when calculating SCLK parameters.
- `amdgpu/si.c` uses SPLL bypass/reset/sleep/status and `SPLL_CNTL_MODE__SPLL_SW_DIR_CONTROL` fields in reset recovery and clock bypass logic.
- `amdgpu/cik.c` and related generation-specific code share similarly named field semantics for clock-pin division on later paths, which makes version matching important.

## State And Persistence Behavior

The header itself has no memory or persistent state. It describes fields in persistent hardware registers. State represented by the fields includes:

- Clock and PLL state: reset, sleep, bypass, reference divider, post divider, feedback divider, mux selection/update, change-status, and spread-spectrum controls.
- Power-management state: global/static PM enable, thermal protection mode/masks, voltage PM, SCLK clock-off requests, dynamic light sleep, and ULV/display-gap controls.
- Thermal/fan state: digital thermal thresholds, sensor selections, max/CTF temperature status, fan duty/PWM mode, tach response, tach target period, and tach measured period.
- GPIO state: pad value/output enable/mask, pull states, receiver select, pinstrap readback, interrupt configuration/status/acknowledge, and software-generated interrupt status.
- SMC indirect access state: selected SMC address, auto-increment flags, message registers, response registers, and SMC program-counter capture.
- Thermal monitor sample state: repeated sensor `TEMP`, `VALID`, and raw `Z` values for two monitor blocks.

These fields are part of the driver-to-ASIC ABI. Incorrect masks can preserve, clear, or set the wrong bits and leave the device in a bad state until reset or reprogramming.

## Dependencies And Integration Points

This header depends only on the C preprocessor and is normally included with `smu_6_0_d.h`.

Primary integration points are:

- Southern Islands SMC firmware copy, mailbox, and SRAM helper code in `pm/legacy-dpm/si_smc.c`.
- Southern Islands DPM/SPLL setup in `pm/legacy-dpm/si_dpm.c`.
- SI reset and clock bypass code in `amdgpu/si.c`.
- DCE6 GPIO translation and any GPIO/thermal/fan code that needs SMU 6.0 field layout.
- Common AMDGPU register helpers and generated field-helper idioms.

## Risks And Edge Cases

- Version coupling is critical. The field names mirror SMU 6.0 register layouts and should not be used with SMU 7.x or later address headers unless the consumer has explicitly verified compatibility.
- Generated masks include a few unusual literal forms, for example `CG_SPLL_FUNC_CNTL__SPLL_PDIV_A_MASK 0x007F00000` and `CG_SPLL_SPREAD_SPECTRUM_2__CLK_V_MASK 0x00000200L` with shift `0`. Consumers must trust the generated layout rather than infer width from naming.
- `SMC_IND_ACCESS_CNTL__AUTO_INCREMENT_IND_*` controls affect stateful SMC indirect accesses. Leaving auto-increment enabled after a streaming write can cause later single-register accesses to hit unexpected addresses.
- SPLL fields are used during reset and DPM transitions. Wrong masks or shifts can hang clocks, fail clock-change handshakes, or generate invalid divider tables.
- Thermal and fan fields can affect protection behavior; incorrect writes can mask thermal interrupts or set unsafe fan/PWM behavior.
- Large repeated GPIO and thermal monitor bit definitions invite copy/paste or generation drift. A single off-by-one shift in pinstrap, interrupt ack, or thermal valid/temp fields can make diagnostics misleading.
- Many full-width fields such as SMC data/index/message/response use `0xffffffffL`; consumers need external validation for value range, alignment, and semantics.

## Test Signals

Useful validation signals are:

- Build coverage for SI legacy DPM, SI SMC, SI reset, and DCE6 GPIO paths.
- SMC firmware upload tests that verify auto-increment writes, endian conversion, and subsequent single dword reads/writes.
- SMC mailbox tests that send commands, observe `mmSMC_RESP_0`, and detect timeout regressions.
- SCLK/DPM tests that cover SPLL divider table generation, SCLK switching, spread-spectrum programming, ULV/CAC controls, and suspend/resume.
- GPU reset tests that exercise SPLL bypass, reset, sleep, and change-status polling.
- Thermal/fan telemetry tests for threshold decode, sensor valid bits, PWM duty, tachometer periods, and thermal interrupts.
- GPIO tests for pinstrap readback, interrupt ack/status, pull-up/down, and receiver/strength configuration where hardware exposes those paths.
- Register-generation comparison against AMD's SMU 6.0 database to validate masks and shifts mechanically.
