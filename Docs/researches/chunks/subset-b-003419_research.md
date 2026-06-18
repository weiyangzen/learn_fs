# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_sh_mask.h lines 1-4612

## Scope

This chunk covers the opening 4,612 lines of the generated AMD SMU 7.1.3 register shift/mask header. It starts with the license and `SMU_7_1_3_SH_MASK_H` include guard, then defines 4,587 preprocessor entries: the guard symbol plus 2,293 `__SHIFT` constants and 2,293 `_MASK` constants. The covered range ends at the first `GENERAL_PWRMGT__GLOBAL_PWRMGT_EN` field pair; the rest of the header is outside this chunk and must be reconciled by later chunk reports.

The file chunk contains no C functions, structs, enums, variables, allocations, loops, or branches. Its API-like surface is the generated macro namespace used by legacy AMDGPU PowerPlay SMU7 code to address and manipulate SMU/SMC indirect registers.

## Purpose

This header provides the bit positions and masks for SMU 7.1.3 hardware registers. Each field is represented by a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit for the field.
- `<REGISTER>__<FIELD>_MASK`, the raw mask used to isolate or compose the field value.

Consumers pair this header with `smu/smu_7_1_3_d.h`, which supplies register addresses such as `ixSMU_STATUS` and `mmSMC_MESSAGE_0`. PowerPlay helper macros such as `PHM_READ_INDIRECT_FIELD`, `PHM_WRITE_INDIRECT_FIELD`, `PHM_READ_VFPF_INDIRECT_FIELD`, and `PHM_WAIT_VFPF_INDIRECT_FIELD_UNEQUAL` use the shift/mask constants to read, write, poll, and update individual fields without hard-coded bit positions.

## Important Macro Families

### Clock, PLL, and DFS Controls

The opening block defines GCK and clock-generator controls for core clocks and PLL programming:

- `GCK_MCLK_FUSES` exposes startup memory-clock divisor and memory-clock ADC/DDC/DiDt fuse fields.
- `CG_DCLK_CNTL`, `CG_VCLK_CNTL`, `CG_ECLK_CNTL`, `CG_ACLK_CNTL`, and `CG_MCLK_CNTL` define divider, direct-control enable, toggle, and direct-control divider fields for display/video/engine/audio/memory clocks.
- `CG_*_STATUS` fields expose status and direct-control done toggles for DCLK, VCLK, ECLK, and MCLK.
- `GCK_DFS_BYPASS_CNTL` and `GCK_ADFS_CLK_BYPASS_CNTL1` describe per-clock bypass controls for ECLK, LCLK, EVCLK, DCLK, VCLK, DISPCLK, DPREFCLK, ACLK, ADIVCLK, PSPCLK, SAMCLK, SCLK, SPLL bypass, and MCLK.
- `CG_SPLL_FUNC_CNTL` through `CG_SPLL_FUNC_CNTL_7`, `SPLL_CNTL_MODE`, `CG_SPLL_STATUS`, and `CG_SPLL_SPREAD_SPECTRUM*` define system PLL reset, power, bypass, dividers, feedback dividers, mux update, lock/unlock, spread-spectrum, fast-lock, test, and bandwidth controls.
- `MPLL_BYPASSCLK_SEL`, `CG_CLKPIN_CNTL`, `CG_CLKPIN_CNTL_2`, `CG_CLKPIN_CNTL_DC`, `THM_CLK_CNTL`, `MISC_CLK_CTRL`, and `GCK_PLL_TEST_CNTL*` cover clock input selection, crystal/CML controls, thermal monitor clock selection, deep-sleep/ZCLK/test clocks, and PLL test counters.

These fields are used during SMU boot, clock bring-up, power-state transitions, and diagnostics. Incorrect masks can corrupt PLL setup, clock bypass routing, or DPM level programming.

### SMC/SMU Indirect Access, Mailboxes, and System Control

The chunk maps multiple indirect register windows:

- `GCK_SMC_IND_INDEX/DATA`, `SMC_IND_INDEX/DATA`, `SMC_IND_INDEX_0` through `_7`, `SMC_IND_DATA_0` through `_7`, `SMU_IND_INDEX_0` through `_7`, `SMU_IND_DATA_0` through `_7`, and `SMU_SMC_IND_INDEX/DATA` expose 32-bit indirect address and data fields.
- `SMC_IND_ACCESS_CNTL` controls auto-increment for indirect windows.
- `SMC_MESSAGE_0` through `SMC_MESSAGE_11`, `SMC_RESP_0` through `SMC_RESP_11`, and `SMC_MSG_ARG_0` through `SMC_MSG_ARG_11` define mailbox message, response, and argument registers.
- `SMC_SYSCON_RESET_CNTL`, `SMC_SYSCON_CLOCK_CNTL_0`, `SMC_SYSCON_CLOCK_CNTL_1`, `SMC_SYSCON_CLOCK_CNTL_2`, `SMC_SYSCON_MISC_CNTL`, and `SMC_SYSCON_MSG_ARG_0` describe SMC reset, clock, miscellaneous, and system-controller argument fields.
- `SMU_STATUS`, `SMU_FIRMWARE`, `SMU_INPUT_DATA`, `SMU_EFUSE_0`, and `FIRMWARE_FLAGS` expose firmware boot/pass status, firmware read/write block controls, auto-start address, eFuse data, interrupt-enable status, and test counters.

Legacy SMU7 code writes SMC messages through `mmSMC_MESSAGE_0`, passes parameters through `mmSMC_MSG_ARG_0`, clears and polls `ixSMU_STATUS`, and waits for `SMU_DONE`/`SMU_PASS` after firmware upload. This header supplies the field layout for those interactions.

### GPIO, Reset Controller, Fuses, and Strap Data

This range includes GPIO pad control and platform identity/fuse data:

- `GPIOPAD_SW_INT_STAT`, `GPIOPAD_STRENGTH`, `GPIOPAD_MASK`, `GPIOPAD_A`, `GPIOPAD_EN`, `GPIOPAD_Y`, and `GPIOPAD_PINSTRAPS` define GPIO state, masks, enables, outputs, and 31 pin-strap bits.
- `GPIOPAD_INT_STAT_EN`, `GPIOPAD_INT_STAT`, `GPIOPAD_INT_STAT_AK`, `GPIOPAD_INT_EN`, `GPIOPAD_INT_TYPE`, `GPIOPAD_INT_POLARITY`, `GPIOPAD_EXTERN_TRIG_CNTL`, `GPIOPAD_RCVR_SEL`, `GPIOPAD_PU_EN`, and `GPIOPAD_PD_EN` define interrupt status/acknowledge/configuration, external trigger control, receiver selection, and pull-up/pull-down enables.
- `RCU_UC_EVENTS`, `RCU_MISC_CTRL`, and `RCU_VIRT_RESET_REQ` expose SMU boot sequence events, breakpoints, reset mode, SAMU start, FCH lock-down, interrupt state, and PF/VF virtual reset request fields.
- `CC_RCU_FUSES`, `CC_SMU_MISC_FUSES`, `CC_SCLK_VID_FUSES`, `CC_GIO_IOCCFG_FUSES`, `CC_GIO_IOC_FUSES`, `CC_SMU_TST_EFUSE1_MISC`, `CC_TST_ID_STRAPS`, `CC_FCTRL_FUSES`, and `CC_HARVEST_FUSES` define capability, disable, revision, repair, VID, harvest, and test/eFuse fields.

These definitions influence ASIC capability discovery, feature disablement, firmware boot decisions, reset behavior, and board/platform interpretation. Several fields are security- or isolation-relevant, such as debug disable, eFuse read disable, IOMMU disable, PF/VF reset request, FCH lockout, and harvested IP disable bits.

### Power, Current, Feature, Memory Timing, and Firmware Tables

The middle of the chunk moves from live status registers into firmware-visible tables:

- `TDC_STATUS`, `TDC_MV_AVERAGE`, and `TDC_VRM_LIMIT` define current/boost/throttle fields for VDD/VDDC power limiting.
- `FEATURE_STATUS` exposes firmware feature state for SCLK/MCLK/LCLK/UVD/VCE/SAMU/ACP/PCIe DPM, BAPM, LPMX, NBDPM, LHTC, VPC, voltage controller, TDC limit, GPU CAC, AVS, SPMI, and forced DPM modes.
- `ENTITY_TEMPERATURES_1` provides a full-width GPU temperature entry.
- `MCARB_DRAM_TIMING_TABLE_1` through `_96` map repeated memory-arbiter DRAM timing entries. Each set carries `McArbDramTiming`, `McArbDramTiming2`, padding bytes, and `McArbBurstTime` across a generated table layout.
- `DPM_TABLE_1` through `DPM_TABLE_440` map the SMU dynamic power-management table layout. The table includes system flags, thermal/voltage/power intervals, boot voltages and boot levels, SMIO masks and patterns, voltage tables, BAPM leakage and temperature data, graphics DPM levels, memory DPM levels, PCIe link levels, ACPI level data, UVD/VCE/ACP/SAMU levels, PID controllers, ULV settings, PPM data, and clock-stretcher data.
- `SOFT_REGISTERS_TABLE_1` through `_30` define firmware soft registers such as reference-clock frequency, PM timer period, feature enables, VBlank/train delays, voltage-change timeout, handshake disables, display PHY configs, average activities, enabled DPM levels, DRAM log addresses/buffer size, ULV counters, and ucode load status.
- `PM_FUSES_1` through `_15` define power-management fuse data for SVI load-line settings, TDC limits, LPML temperature scaling, fan deltas, GNB LPML VID limits, and base leakage.

The DPM table is the densest portion of this chunk. It encodes structured firmware data as numbered 32-bit table words rather than C structs in this header; separate SMU firmware headers and PowerPlay code define the typed C structures and copy those data blobs to or from SMC memory.

### PM Status, Thermal, Fan, Tachometer, and TMON Data

The tail of the requested range covers runtime telemetry and thermal/fan controls:

- `SMU_PM_STATUS_0` through `SMU_PM_STATUS_127` are 128 full-width status words used as firmware-visible diagnostic/status registers.
- `CG_THERMAL_INT_ENA`, `CG_THERMAL_INT_CTRL`, `CG_THERMAL_INT_STATUS`, `CG_THERMAL_CTRL`, `CG_THERMAL_STATUS`, and `CG_THERMAL_INT` define thermal interrupt threshold, mask, detect, DPM event, CTF pad, current PWM duty, alert, and status fields.
- `CG_MULT_THERMAL_CTRL` and `CG_MULT_THERMAL_STATUS` expose multi-sensor filtering, selected sensor, ready clear, ASIC max temperature, and CTF temperature fields.
- `THM_TMON2_CTRL`, `THM_TMON2_CTRL2`, `THM_TMON2_CSR_WR`, and `THM_TMON2_CSR_RD` define TMON2 power/configuration, RDIL/RDIR presence, CSR address/data, and CSR read/write command fields.
- `CG_FDO_CTRL0`, `CG_FDO_CTRL1`, `CG_FDO_CTRL2`, `CG_TACH_CTRL`, and `CG_TACH_STATUS` define fan duty, manual mode, ramp/hysteresis, min/max duty, PWM mode, temperature thresholds, tach response rate, edge count, target period, and measured tach period.
- `CC_THM_STRAPS0` defines thermal monitor strap fields for BG adjustment, acquisition count, clock selection, configuration source, and TMON disablement.
- Repeated `THM_TMON{0,1,2}_RDIL*_DATA` and `THM_TMON{0,1,2}_RDIR*_DATA` definitions expose per-sensor `Z`, `VALID`, and `TEMP` fields for RDIL/RDIR sensors 0-15. `THM_TMON*_INT_DATA`, `THM_TMON*_DEBUG`, and `THM_TMON*_STATUS` define interrupt temperature data, debug RDI/Z selection, current RDI, and measurement-done bits.
- The range ends after `GENERAL_PWRMGT__GLOBAL_PWRMGT_EN`, the first field of the general power-management register.

Thermal and fan fields are consumed by SMU7 thermal code to read PWM duty, compute fan percentages, set static or RPM modes, configure thermal thresholds, and mask/unmask thermal interrupts.

## Control Flow and State Behavior

This header has no executable control flow. Including it only makes constants available to C code.

Runtime behavior is created by downstream code that uses these constants with indirect register helpers. Typical sequences are:

1. Select an SMU/SMC register through the SMC indirect register address path or use an MMIO address from `smu_7_1_3_d.h`.
2. Read a 32-bit register value.
3. Use the generated mask and shift to extract or replace one field.
4. Write the composed value back, or poll until a field reaches the expected state.

The hardware state represented by this chunk persists in registers, firmware SRAM tables, fuse/strap latches, counters, and telemetry/status words. Some fields are configuration state, such as PLL dividers, DPM table levels, thermal thresholds, fan modes, GPIO settings, and power-management enables. Other fields are status or command-like state, such as SMC mailbox messages/responses, firmware pass/done bits, thermal interrupt status, TMON valid bits, PM status words, and eFuse/fuse values. Access semantics such as read-only, write-one-to-clear, sticky status, or reset-only are not encoded in the macro names; callers must follow the hardware and SMU firmware protocols.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is only useful with the matching SMU 7.1.3 register address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_3_d.h` supplies register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h` includes both the address and shift/mask headers for legacy SMU7 PowerPlay code.
- `fiji_smumgr.c`, `vegam_smumgr.c`, `polaris10_smumgr.c`, `fiji_baco.c`, and `polaris_baco.c` include this header directly for SMU7-family firmware bring-up, BACO, and power-management paths.
- `smu7_smumgr.c` uses the SMC mailbox registers, while SMU7-family smumgr files poll `SMU_STATUS` and inspect `FEATURE_STATUS`.
- `smu7_hwmgr.c` writes fields such as `GENERAL_PWRMGT__GLOBAL_PWRMGT_EN` and thermal DPM controls through `PHM_WRITE_INDIRECT_FIELD`.
- `smu7_thermal.c` uses `CG_FDO_CTRL*`, `CG_THERMAL_STATUS`, `CG_THERMAL_INT`, and `CG_THERMAL_CTRL` fields for fan control and thermal threshold programming.
- Firmware table structures in SMU7-generation headers such as `smu73_discrete.h`, `smu74_discrete.h`, and related `*_ppsmc.h` headers are the typed counterparts to the numbered `DPM_TABLE_*`, `SOFT_REGISTERS_TABLE_*`, and `PM_FUSES_*` words defined here.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can silently corrupt PLL programming, firmware mailbox operation, DPM table packing, fan control, thermal interrupts, or power-management enablement.
- The DPM table section is large and generated as numbered words. Off-by-one generation errors can mispack all following firmware table fields even when individual masks look reasonable.
- Status and control fields share similar names. Treating status bits such as `SMU_DONE`, `SMU_PASS`, thermal detect bits, TMON valid bits, or PM status data as ordinary writable configuration can break polling or erase diagnostic evidence.
- Fuse and strap fields affect capability discovery and policy. Incorrect masks can mis-detect disabled IP blocks, revision IDs, debug/eFuse restrictions, IOMMU state, or harvested units.
- Clock and PLL fields require ASIC-specific sequencing. Incorrect direct-control toggles, bypass controls, or SPLL fields can cause hangs, display/video clock failures, or unstable DPM transitions.
- Thermal and fan masks are safety-sensitive. Bad threshold, PWM, tachometer, or interrupt masks can cause incorrect fan duty reporting, bad fan commands, missed thermal alerts, or unnecessary throttling.
- The chunk ends in the middle of the full header. The final per-file report must reconcile this document with the following lines, including the rest of `GENERAL_PWRMGT` and the closing include guard.

## Test and Validation Signals

Useful validation is mostly build-time and hardware/firmware integration coverage:

- Build AMDGPU with legacy PowerPlay SMU7 targets enabled so missing or renamed generated macros fail in `smu7_common.h`, `fiji_smumgr.c`, `vegam_smumgr.c`, `polaris10_smumgr.c`, `smu7_hwmgr.c`, and `smu7_thermal.c`.
- Boot representative SMU7-family ASICs and verify firmware upload sequences: clear `SMU_STATUS`, wait for `SMU_DONE`, check `SMU_PASS`, and send SMC mailbox messages with arguments and responses.
- Exercise DPM enable/disable and power-state changes for SCLK, MCLK, LCLK, PCIe, UVD, VCE, ACP, and SAMU while checking `FEATURE_STATUS`, relevant DPM table contents, and PM status words.
- Validate fan and thermal paths by reading `CG_FDO_CTRL1.FMAX_DUTY100`, `CG_THERMAL_STATUS.FDO_PWM_DUTY`, setting `CG_FDO_CTRL0/2` fields, configuring `CG_THERMAL_INT`, and observing thermal interrupt behavior.
- Compare generated `DPM_TABLE_*`, `SOFT_REGISTERS_TABLE_*`, `PM_FUSES_*`, and `MCARB_DRAM_TIMING_TABLE_*` layouts against the matching SMU firmware C structures and known-good firmware table dumps.
- Check GPIO, fuse, strap, and harvest decoding on boards with known configurations.
- Run suspend/resume, BACO, reset, and overdrive/powerplay tests because those paths reprogram clocks, DPM tables, firmware state, fan control, and general power-management fields.
