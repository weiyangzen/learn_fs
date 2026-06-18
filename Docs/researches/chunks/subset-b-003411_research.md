# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_0_sh_mask.h lines 4584-5648

## Scope

This chunk covers the second and final range of the generated AMD SMU 7.1.0 shift/mask register header. The range begins in the middle of the `GENERAL_PWRMGT` definition, after the first power-management control fields that appear in the previous chunk, and continues through the closing `#endif /* SMU_7_1_0_SH_MASK_H */`.

The covered lines define preprocessor constants only. There are no C functions, structs, variables, memory allocations, locks, callbacks, or runtime branches in this slice. Its behavior comes from how AMDGPU power-management and ASIC initialization code uses these mask and shift constants when reading or writing SMU registers.

## Purpose

`smu_7_1_0_sh_mask.h` describes the bit layout of SMU 7.1.0 hardware registers. This tail chunk supplies field masks and least-significant-bit shifts for power-management controls, DPM/current-state reporting, clock-throttling votes, deep-sleep controls, LCAC monitor programming, and ROM access registers.

The generated convention is consistent throughout the chunk:

- `<REGISTER>__<FIELD>_MASK` isolates or clears a bitfield in a 32-bit hardware register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's right-shift amount after masking, or the left-shift amount before composing a value.

Consumers combine this file with `smu_7_1_0_d.h`, which provides the `ix*` and `mm*` register addresses, and with register-access helpers such as `RREG32_SMC`, `WREG32_SMC`, `WREG32_P`, `cgs_read_ind_register`, `cgs_write_ind_register`, `PHM_WRITE_INDIRECT_FIELD`, and related field helpers. The header therefore provides the bit-level contract for SMU/DPM code; it does not itself perform access sequencing or validation.

## Important Macro Families

### General and Northbridge Power Management

The chunk starts with the latter part of `GENERAL_PWRMGT`:

- `GPU_COUNTER_ACPI`, `GPU_COUNTER_CLK`, `GPU_COUNTER_OFF`, and `GPU_COUNTER_INTF_OFF` expose GPU counter and clock/off state bits.
- `ACPI_D3_VID` records the voltage ID used for ACPI D3 handling.
- `DYN_SPREAD_SPECTRUM_EN` controls dynamic spread-spectrum support.
- Several `SPARE*` fields reserve or preserve undocumented bits.

The beginning of `GENERAL_PWRMGT`, including `GLOBAL_PWRMGT_EN`, `STATIC_PM_EN`, `THERMAL_PROTECTION_DIS`, `THERMAL_PROTECTION_TYPE`, `SW_SMIO_INDEX`, low-voltage ACPI bits, and `VOLT_PWRMGT_EN`, is in chunk `subset-b-003410`. Any final file-level analysis must stitch both chunks together to describe this register completely.

`CNB_PWRMGT_CNTL` defines northbridge-related power-management bits:

- `GNB_SLOW_MODE` and `GNB_SLOW` control or report slow-mode behavior.
- `FORCE_NB_PS1` can force a northbridge power state.
- `DPM_ENABLED` gates dynamic power-management behavior.
- `SPARE` covers the upper reserved range.

These fields are part of the low-level dynamic power management surface. Errors in masks here can disable power management, mishandle thermal protection, or program the wrong voltage/clock state during ACPI transitions.

### SCLK Power Management and Profile State

`SCLK_PWRMGT_CNTL` contains the main SCLK/GFX clock power-management control layout in this range:

- Power gating and low-power entry controls: `SCLK_PWRMGT_OFF`, `SCLK_LOW_D1`, `DYN_PWR_DOWN_EN`, `DYN_GFX_CLK_OFF_EN`, `DYN_LIGHT_SLEEP_EN`, `AUTO_SCLK_PULSE_SKIP`, `DYNAMIC_PM_EN`, `DPM_DYN_PWR_DOWN_CNTL`, and `DPM_DYN_PWR_DOWN_EN`.
- Counter and state reset controls: `RESET_BUSY_CNT` and `RESET_SCLK_CNT`.
- GFX clock force/request bits: `GFX_CLK_FORCE_ON`, `GFX_CLK_REQUEST_OFF`, `GFX_CLK_FORCE_OFF`, and ACPI D1/D2/D3 off bits.
- Light-sleep and voltage transition controls: `LIGHT_SLEEP_COUNTER`, `VOLTAGE_UPDATE_EN`, `GFX_VOLTAGE_CHANGE_EN`, and `GFX_VOLTAGE_CHANGE_MODE`.
- Forced DPM interrupt bits: `FORCE_PM0_INTERRUPT` and `FORCE_PM1_INTERRUPT`.

`TARGET_AND_CURRENT_PROFILE_INDEX` reports current and target indices for selected performance dimensions:

- `TARGET_STATE` and `CURRENT_STATE`.
- Current and target MCLK indices.
- Current and target SCLK indices.
- Current and target LCLK indices.

`TARGET_AND_CURRENT_PROFILE_INDEX_1` extends this status reporting to voltage and PCIe indices:

- Current and target `VDDCI`, `MVDD`, and `VDDC` indices.
- Current and target PCIe indices.

Legacy DPM and PowerPlay code uses this style of register to observe current DPM state and to validate state transitions. The fields are status/reporting data, not a persistent software data model in the header.

### Frequency-Transition Voting

`CG_FREQ_TRAN_VOTING_0` through `CG_FREQ_TRAN_VOTING_7` form eight repeated vote-enable registers. Each register has the same bit layout:

- Front-end/system clients: `BIF`, `HDP`, `ROM`, `IH_SEM`, `PDMA`, `DRM`, `IDCT`, `ACP`, `SDMA`, `UVD`, `VCE`, `DC_AZ`, `SAM`, and `AVP`.
- Graphics block manager channels: `GRBM_0` through `GRBM_15`.
- `RLC` at bit 30.

Each field name ends in `FREQ_THROTTLING_VOTE_EN`, indicating whether that block can vote in the frequency-transition or throttling decision. The repeated register numbering likely reflects several voting banks or comparable hardware domains with identical client bit positions.

Because these registers coordinate many engines, their masks are integration-sensitive. A misplaced bit can make the SMU ignore an engine's throttling/transition vote or attribute a vote to the wrong client.

### Clock Generation, ACPI, and Display Gap Controls

The chunk defines smaller clock/power controls:

- `PLL_TEST_CNTL` exposes `TEST_RESET`, `TEST_BYPASS`, `TEST_EN`, `TEST_CLK_SRC`, and `TEST_DIV_ID`, all of which are low-level PLL test or debug controls.
- `CG_STATIC_SCREEN_PARAMETER` defines a `STATIC_SCREEN_THRESHOLD` and `STATIC_SCREEN_THRESHOLD_UNIT` used for static-screen power behavior.
- `CG_DISPLAY_GAP_CNTL` provides `DISP_GAP`, `DISP_GAP_MCHG`, `VBI_TIMER_COUNT`, `VBI_TIMER_UNIT`, `DISP_GAP_PULSE`, and `DISP_GAP_MODE`.
- `CG_DISPLAY_GAP_CNTL2` defines `VBI_TIMER_COUNT_23_16`, extending the display-gap timer count.
- `CG_ACPI_CNTL` defines `SCLK_ACPI_DPM_DIS` and `MCLK_ACPI_DPM_DIS`.

These fields bridge display timing, ACPI power-state handling, and clock-generation behavior. They are typically programmed as part of DPM policy setup or low-power display-state handling rather than by ordinary rendering paths.

### SCLK and LCLK Deep Sleep

`SCLK_DEEP_SLEEP_CNTL` controls SCLK deep-sleep entry:

- `DIV_ID`, `RAMP_DIS`, and `HYSTERESIS` configure divider and transition behavior.
- Busy/allow masks gate deep-sleep entry on activity signals such as SCLK running, memory self-refresh, northbridge pstate allowance, BIF busy, UVD busy, MC SRBM busy, memory-controller allow, SMU busy, MBUS2 active, VCE busy, and audio/display (`AZ`) busy.
- `FAST_EXIT_REQ_NBPSTATE`, `DEEP_SLEEP_ENTRY_MODE`, and `ENABLE_DS` control entry/exit policy.

`SCLK_DEEP_SLEEP_CNTL2` and `SCLK_DEEP_SLEEP_CNTL3` extend the busy mask set:

- `CNTL2` covers many GPU blocks, including graphics memory clients (`GFX`, `PA`, `SC`, `SX`, `TA`, `GDS`, `SPI`, `VGT`, `CB`, `DB`, `IA`, `WD`), compute and RLC signals (`CP_CPF`, `CP_CPC`, `CP_WD`, `CP_ME`, `CP_MEC`, `RLC_SMU_GFXCLK_OFF`), media/audio/control blocks (`UVD_VCPU`, `UVD_SCPU`, `UVD_RBC`, `UVD_CSM`, `AZ_EXT_BUSY`), and GFX clock off or CGCG state.
- `CNTL3` provides `GRBM_0_SMU_BUSY_MASK` through `GRBM_15_SMU_BUSY_MASK`.

`SCLK_DEEP_SLEEP_MISC_CNTL` configures DPM and OCP divider IDs for deep sleep and shallow sleep via `DPM_DS_DIV_ID`, `DPM_SS_DIV_ID`, `OCP_ENABLE`, `OCP_DS_DIV_ID`, and `OCP_SS_DIV_ID`.

The LCLK side is represented by:

- `LCLK_DEEP_SLEEP_CNTL`, with `DIV_ID`, `RAMP_DIS`, `HYSTERESIS`, reserved bits, and `ENABLE_DS`.
- `LCLK_DEEP_SLEEP_CNTL2`, with busy/idle/wake masks such as `RFE_BUSY_MASK`, `BIF_CG_LCLK_BUSY_MASK`, `L1IMU_SMU_IDLE_MASK`, `SCLK_RUNNING_MASK`, `SMU_BUSY_MASK`, `PCIE_LCLK_IDLE1` through `PCIE_LCLK_IDLE4`, several L1/L2 IMU idle bits, inbound/outbound wake and wake-ack masks, `DMAACTIVE_MASK`, and `RLC_SMU_GFXCLK_OFF_MASK`.

These deep-sleep registers represent hardware-controlled clock state. The header does not record whether a bit is read-only, sticky, or write-one-to-clear; consumers must follow hardware sequencing and preserve reserved bits.

### ULV, SCLK Minimum Divider, and LCAC Monitor Controls

`CG_ULV_PARAMETER` defines an ultra-low-voltage threshold and threshold unit. `SCLK_MIN_DIV` exposes fractional and integer divider fields through `FRACV` and `INTV`.

The LCAC families provide local current/activity counter or monitor controls:

- `LCAC_SX0_CNTL`, `LCAC_MC0_CNTL`, `LCAC_MC1_CNTL`, `LCAC_MC2_CNTL`, `LCAC_MC3_CNTL`, and `LCAC_CPL_CNTL` all use the same shape: enable bit, threshold, block ID, and signal ID.
- Each monitor has an override-select register and an override-value register: `*_OVR_SEL` and `*_OVR_VAL`, both full-width 32-bit fields.

The repeated LCAC layout is used by DPM/PowerPlay code to configure activity/power-monitoring signals and to clear or apply overrides. In this tree, for example, legacy `kv_dpm.c` clears several LCAC override registers, and `smu7_hwmgr.c` writes LCAC control values for SMU7-era power management.

### ROM, Page Mirror, and Software ROM Access

The ROM-related macros in the final part of the file define both indirect access and software command interfaces:

- `ROM_SMC_IND_INDEX` and `ROM_SMC_IND_DATA` provide full-width SMC indirect address/data fields.
- `ROM_CNTL` includes `SCK_OVERWRITE`, `CLOCK_GATING_EN`, SCK setup/hold timing, and prescale values for refclk and crystal clock.
- `PAGE_MIRROR_CNTL` defines page mirror base address, invalidate, enable, and usage fields.
- `ROM_STATUS` exposes `ROM_BUSY`.
- `CGTT_ROM_CLK_CTRL0` defines clock gating on-delay, off-hysteresis, and software override bits.
- `ROM_INDEX`, `ROM_DATA`, and `ROM_START` provide direct ROM indexing/data/start-address fields.
- `ROM_SW_CNTL` exposes `DATA_SIZE`, `COMMAND_SIZE`, and `ROM_SW_RETURN_DATA_ENABLE`.
- `ROM_SW_STATUS` exposes `ROM_SW_DONE`.
- `ROM_SW_COMMAND` packs an 8-bit instruction with a 24-bit address.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64` are full-width data payload words.

This register set is used for firmware/VBIOS/ROM-related access paths and for clock-gating control around ROM operations. The 64 payload registers make the chunk's tail repetitive but important for bounds and data-size correctness.

## Control Flow and State Behavior

This header has no executable control flow. It affects compiled code by replacing symbolic field names with constants during preprocessing. Runtime control flow lives in the driver code that performs read/modify/write sequences, polls status bits, or programs DPM tables.

The state represented by the macros is hardware state:

- Persistent configuration state includes global/static power management enables, DPM enable bits, SCLK/LCLK deep-sleep enables, display gap timers, ACPI DPM disable bits, LCAC thresholds and overrides, ROM clock-gating controls, and page-mirror settings.
- Dynamic status state includes current/target DPM profile indices, voltage and PCIe indices, GPU counter/off bits, ROM busy/done state, and deep-sleep busy/idle/wake conditions.
- Command-like state includes forced DPM interrupt bits, reset-counter bits, ROM software commands, ROM data payload registers, and page-mirror invalidation.

Correct behavior depends on preserving reserved fields, using the matching address header, and obeying the hardware's sequencing rules. The macros do not distinguish read-only fields from writable controls, sticky status from transient status, or ordinary writes from command-triggering writes.

## Dependencies and Integration Points

Direct dependencies for this chunk are generated AMD register headers and AMDGPU register helpers:

- `smu_7_1_0_d.h` supplies addresses such as `ixGENERAL_PWRMGT`, `ixLCAC_*`, and `ixROM_SW_*`.
- This file supplies the bit masks and shifts for those addresses.
- `smu_7_1_0_enum.h`, when used by the same consumer, supplies related enumerated values.
- Register helpers in the AMDGPU and PowerPlay stack use these constants to construct read/modify/write operations and field extraction.

Observed or likely source-tree integration points include:

- Legacy DPM code such as `si_dpm.c` and `kv_dpm.c`, which manipulates `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, DPM status registers, and LCAC overrides.
- ASIC initialization and low-level GPU code such as `cik.c`, which checks SMU power/counter state through `GENERAL_PWRMGT` fields.
- PowerPlay SMU7 management code such as `smu7_hwmgr.c`, which writes `GENERAL_PWRMGT` fields and LCAC control registers through indirect SMU register helpers.
- BIOS/ROM, firmware, or diagnostic paths that use ROM index/data/software command registers and status bits.
- Suspend/resume, ACPI, display-idle, clock-gating, dynamic power management, and thermal protection flows that must program these fields in hardware-specific order.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can enable the wrong power state, disable protection, corrupt voltage/clock state reporting, or misprogram sleep entry conditions.
- This chunk starts mid-register. File-level documentation or generation checks must combine it with chunk `subset-b-003410` or `GENERAL_PWRMGT` will appear incomplete.
- Reserved and spare fields are present in several registers. Consumers must preserve them during read/modify/write sequences unless hardware documentation says otherwise.
- Deep-sleep mask fields gate entry based on many busy/idle signals. Mislabeling or shifting one mask can allow sleep while a block is active, or prevent sleep and cause power regressions.
- Frequency-transition voting registers are repetitive across eight banks. Generation errors can be hard to spot because most fields look identical and only the register suffix changes.
- LCAC monitor programming uses compact block and signal IDs. Bad masks can point monitors at the wrong source or make override values affect unintended signals.
- ROM software-command fields combine command, address, data size, and up to 64 data registers. Incorrect data-size or address masks can truncate ROM accesses, poll the wrong done bit, or read/write stale payload words.
- Some fields are status or command-triggering rather than normal storage. Treating `ROM_BUSY`, `ROM_SW_DONE`, reset bits, interrupt force bits, or invalidation bits as simple persistent state can lose events or trigger unintended operations.

## Test and Validation Signals

Useful validation for this chunk is mostly compile-time coverage plus hardware smoke and power-management testing:

- Build AMDGPU configurations that include SMU 7.1.0/SMU7 register headers; this catches missing macros, syntax errors, and mismatched generated names.
- Exercise DPM enable/disable and confirm `GENERAL_PWRMGT`, `CNB_PWRMGT_CNTL`, and `SCLK_PWRMGT_CNTL` readbacks match expected policy.
- Verify SCLK/MCLK/LCLK/current-voltage/PCIe DPM reporting by reading `TARGET_AND_CURRENT_PROFILE_INDEX` and `TARGET_AND_CURRENT_PROFILE_INDEX_1` during forced profile changes.
- Run suspend/resume and ACPI D1/D2/D3 paths, checking low-power state entry, clock-off bits, and voltage transition behavior.
- Validate display-idle/static-screen scenarios that depend on `CG_STATIC_SCREEN_PARAMETER` and `CG_DISPLAY_GAP_CNTL*`.
- Stress workloads that keep BIF, SDMA, UVD/VCE, RLC, GRBM, memory-controller, or PCIe paths busy while observing SCLK/LCLK deep-sleep entry and exit.
- Check power/thermal regressions with frequency-transition voting enabled, especially when media, display, SDMA, and graphics clients are active.
- Exercise LCAC setup and override clearing/programming on supported hardware and compare SMU telemetry or register dumps against known-good traces.
- Validate ROM access paths by reading VBIOS/ROM data through the indirect/software interface, polling `ROM_BUSY` or `ROM_SW_DONE`, and checking command size/data size handling.
- Compare generated masks against vendor register documentation or a known-good generated header for SMU 7.1.0, with special attention to repeated `CG_FREQ_TRAN_VOTING_*`, `LCAC_*`, and `ROM_SW_DATA_*` families.
