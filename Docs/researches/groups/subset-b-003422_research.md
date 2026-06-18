# subset-b-003422 research

This grouped report covers AMD SMU/SMUIO generated register definition headers used by the amdgpu kernel driver. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_8_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_8_0_sh_mask.h

## Purpose
`smu_8_0_sh_mask.h` is a generated-style hardware register bitfield contract for SMU 8.0-era AMD GPU/APU power, thermal, mailbox, timer, DRAM, interrupt, and clock-management blocks. It exports C preprocessor `*_MASK` and `*__SHIFT` constants that driver code can combine with register offsets from sibling ASIC register headers to read, extract, compose, and write 32-bit MMIO register fields without embedding literal bit positions in logic.

## Important APIs, Types, And Functions
This header defines no C functions, structs, enums, or storage. Its API is the macro namespace guarded by `SMU_8_0_SH_MASK_H`. Important groups include `THM_TCON_*`, `THM_GPIO_*`, `THM_THERMAL_INT_*`, `TMON0_*`, `TMON1_*`, and `THM_FUSE*` thermal/fuse fields; `MP0PUB_IND_*`, `MP0_IND_ACCESS_CNTL`, `MP0_MSP_MESSAGE_*`, `SMU_MP1_SRBM2P_MSG_*`, `SMU_MP1_SRBM2P_RESP_*`, and `SMU_MP1_SRBM2P_ARG_*` mailbox/indirect-access fields; `MP0_DISP_TIMER*` and `SMU_DISP*_TIMER_INT_CONTROL` display timer fields; `MP_DRAM_CNTL_*` read/write request and return fields; `MP_IOC_*` IOC transaction fields; `CURRENT_STATE_CPU*`, `CURRENT_VID_*`, `CURRENT_FREQ_STATE_NB`, `CURRENT_PSTATE_NB`, and `UNBPM_*` CPU/NB power-management status fields; per-core `POWERON_CPU_*`, `POWERREADY_CPU_*`, `RCC3*`, `SPMI_*`, and core fuse-transfer fields; and GPU-facing `GENERAL_PWRMGT`, `CNB_PWRMGT_CNTL`, `SCLK_DEEP_SLEEP_*`, `LCLK_DEEP_SLEEP_*`, `CG_FREQ_TRAN_VOTING_*`, `PCIE_PGFSM*`, `VDDGFX_IDLE_*`, `LCAC_*`, and `GC_CAC_*` fields.

## Control Flow
There is no runtime control flow in the header. Compile-time inclusion makes the constants available to call sites. Runtime control flow lives in amdgpu/SMU power-management code that typically reads a register, masks and shifts a field, or builds an updated register value before an MMIO write. Several macro families imply hardware polling flows, such as TCON CSR request completion via `THM_TCON_CSR_DATA__TCC_REQ_DONE_MASK`, IOC master busy/read-valid fields, SPMI FSM busy/trigger fields, PCIe PGFSM read-valid/busy fields, display timer start/clear/int-ack fields, and mailbox message/response/argument windows.

## State And Persistence
The file itself has no mutable state and persists nothing. The constants describe persistent hardware-visible state in registers, fuse fields, power-management handshakes, thermal thresholds, scratch registers, mailbox payloads, and counters. Writes by consumers can affect device behavior across runtime power states until overwritten or reset by firmware/hardware. Reserved field masks are also present and should be preserved by read-modify-write paths so callers do not accidentally alter undocumented bits.

## Dependencies And Integration Points
The header depends only on the C preprocessor and fixed integer literals. It is integrated by amdgpu SMU 8.0 support and any shared helpers that use ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg`. It is meant to be paired with offset headers that define `mm...` register addresses and with helper macros/functions such as AMDGPU register read/write wrappers and field helpers. It also interacts conceptually with firmware-facing SMU/MP0/MP1 mailbox protocols, thermal management code, display timer interrupt handling, clock/deep-sleep gating code, PCIe power-gating logic, and CAC/leakage accounting.

## Risks
The highest risk is silent hardware misprogramming if a mask, shift, register generation, or ASIC-version match is wrong. Many names expose safety-critical or stability-sensitive controls: thermal trip/prochot, voltage status/control, deep-sleep enable and busy masks, power-gating state machines, PCIe PGFSM controls, mailbox arguments, and interrupt acknowledges. Because this is macro-only, type safety is absent; callers can combine a field with the wrong register or use an unshifted value incorrectly. Masks with `_MASK_MASK` naming, reserved bits, and wide repeated families such as `CG_FREQ_TRAN_VOTING_0` through `_7` are easy to misuse during manual edits. The file should be treated as generated hardware data, not hand-refactored application logic.

## Test Signals
There are no direct unit tests for the header. Useful signals are successful kernel build coverage for ASICs that include SMU 8.0 headers, absence of preprocessor redefinition errors, and runtime GPU validation: SMU firmware boot, thermal readings and interrupts, power-profile transitions, SCLK/LCLK deep sleep entry/exit, display timer interrupts, PCIe power-gating, and suspend/resume. Regressions are likely to surface as GPU initialization failures, broken power management, thermal/prochot faults, stuck mailbox transactions, interrupt storms or missing interrupts, display timing issues, or hangs under DPM/deep-sleep transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_8_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_offset.h

## Purpose
`smuio_10_0_2_offset.h` defines SMUIO 10.0.2 register offsets and base-index selectors for the AMDGPU driver. It maps symbolic `mm...` register names to numeric offsets within SMUIO address blocks so code can access scratch, pinstrap, reset, timer, TSC, and SVI telemetry registers through the normal AMD register access layer.

## Important APIs, Types, And Functions
This header exports only preprocessor constants. The public surface consists of each `mmREGISTER` offset plus a matching `mmREGISTER_BASE_IDX`. Covered blocks are `smuio_smuio_misc_SmuSmuioDec` at base address `0x5a000`, including `mmSMUIO_MCM_CONFIG`, `mmIP_DISCOVERY_VERSION`, `mmIO_SMUIO_PINSTRAP`, and `mmSCRATCH_REGISTER0` through `mmSCRATCH_REGISTER7`; `smuio_smuio_reset_SmuSmuioDec` at `0x5a300`, including `mmSMUIO_MP_RESET_INTR`, `mmSMUIO_SOC_HALT`, and `mmSMUIO_GFX_MISC_CNTL`; `smuio_smuio_ccxctrl_SmuSmuioDec`, including power-ok gap cycles and golden TSC count/increment/shadow registers; `smuio_smuio_swtimer_SmuSmuioDec`, including virtual reset request, display timers, global timer control, and power interrupt-handler control; and `smuio_smuio_svi0_SmuSmuioDec`, including plane-0 telemetry and current VID registers.

## Control Flow
There is no runtime control flow. Driver code includes the header and uses offsets with register access helpers. The expected runtime pattern is to select the correct SMUIO instance/base index, read or write the `mm...` address, and pair the raw register value with bit definitions from `smuio_10_0_2_sh_mask.h`.

## State And Persistence
The file itself stores no runtime state. It names hardware state that can be persistent for the lifetime of a boot or power-management episode: scratch registers, pinstraps, MCM/package identity, reset/SoC halt controls, golden TSC counters and shadows, virtual FLR reset requests, display timer settings, interrupt-handler credit/mask controls, and SVI telemetry/current VID. Whether a particular write persists across GPU reset, suspend, or firmware reinitialization is determined by the hardware block, not this header.

## Dependencies And Integration Points
The header depends only on inclusion by C sources and matching SMUIO 10.0.2 ASIC support. It integrates with the companion shift/mask header, AMDGPU register read/write macros, SMU reset and power-management code, display timer/interrupt code, virtualization FLR handling, IP discovery/version checks, and telemetry readers. The `BASE_IDX` values are part of the AMD register access convention and are important when a register file is split across multiple aperture/base tables.

## Risks
Incorrect offsets or base indices route reads and writes to the wrong hardware register, which can break reset, timer interrupts, firmware coordination, telemetry, or package detection. This file lacks a closing `#define` for `_smuio_10_0_2_OFFSET_HEADER`; it still uses `#ifndef`/`#endif`, but without defining the guard symbol repeated inclusion is not suppressed. That is usually harmless for identical macros if values match, but it weakens the normal include-guard contract and can produce warnings or redefinition conflicts if another include path changes a definition. Consumers must also avoid mixing these 10.0.2 offsets with masks from a different SMUIO revision.

## Test Signals
There are no direct tests. Build coverage should catch syntax and duplicate-macro problems. Runtime signals include correct IP discovery version reads, scratch register behavior, package/MCM identification, successful reset/FLR flows, display timer interrupt delivery and acknowledgement, valid golden TSC values, and reasonable SVI telemetry/VID reads on hardware that uses SMUIO 10.0.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_sh_mask.h

## Purpose
`smuio_10_0_2_sh_mask.h` defines bit masks and shift counts for the SMUIO 10.0.2 registers listed in the companion offset header. It lets driver code decode identity, pinstrap, scratch, reset, GFX power, TSC, virtual reset, display timer, interrupt, and SVI telemetry fields without hard-coded bit arithmetic.

## Important APIs, Types, And Functions
The API is a macro namespace guarded by `_smuio_10_0_2_SH_MASK_HEADER` via `#ifndef`. It defines `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pairs. Important groups are `SMUIO_MCM_CONFIG` fields for die/package/socket/console IDs; `IP_DISCOVERY_VERSION`; `IO_SMUIO_PINSTRAP` audio strap fields; `SCRATCH_REGISTER0` through `SCRATCH_REGISTER7` full-width scratch pads; `SMUIO_MP_RESET_INTR`; `SMUIO_SOC_HALT` watchdog force controls; `SMUIO_GFX_MISC_CNTL` GFX cold/GFXOFF/RLC clock-gating controls and status; `PWROK_REFCLK_GAP_CYCLES` and `GOLDEN_TSC_*`/shadow fields; `SOC_GAP_PWROK`; `PWR_VIRT_RESET_REQ` VF/PF FLR request bits; `PWR_DISP_TIMER_CONTROL`, `PWR_DISP_TIMER2_CONTROL`, and `PWR_DISP_TIMER_GLOBAL_CONTROL`; `PWR_IH_CONTROL`; and `SMUSVI0_TEL_PLANE0`/`SMUSVI0_PLANE0_CURRENTVID` telemetry fields.

## Control Flow
There is no runtime branch or call flow in the header. At runtime, callers read a register at an offset from `smuio_10_0_2_offset.h`, apply the relevant mask, shift down to extract a logical field, or shift/mask an input value before writing. Control-like hardware workflows represented here include FLR request signaling through `PWR_VIRT_RESET_REQ`, display timer interrupt enable/disable/mask/status-ack programming, power interrupt-handler credit and trigger masking, watchdog halt forcing, and GFXOFF/RLC clock-gating control.

## State And Persistence
The header has no storage. It describes hardware fields whose values may represent strap state, scratch state, reset requests, watchdog force bits, timer configuration, interrupt status/acknowledge state, TSC counters, GFX power state, and SVI voltage/current telemetry. Scratch registers and programmed timer/control fields are stateful hardware registers; status and telemetry fields are read-only or hardware-updated depending on the block.

## Dependencies And Integration Points
This file is designed to be used with `smuio_10_0_2_offset.h` and AMDGPU field helpers/register accessors. It integrates with SMUIO identity discovery, reset/FLR code, GFXOFF/power-management paths, display timer interrupt handling, interrupt-handler throttling/credit code, TSC synchronization, and voltage telemetry consumers. The field names mirror generated hardware documentation, so consistency with firmware and register database generation is the main dependency.

## Risks
Mask/shift errors can corrupt unrelated bits or decode telemetry and status incorrectly. Whole-register scratch and discovery masks are straightforward, but control fields that acknowledge interrupts or request FLR/reset must be used carefully because write-one-to-ack or write-trigger semantics may apply in hardware even though the header does not encode access type. The `_MASK_MASK` names such as `PWR_DISP_TIMER_CONTROL__DISP_TIMER_INT_MASK_MASK` and `PWR_IH_CONTROL__DISP_TIMER_TRIGGER_MASK_MASK` are easy to misread. Like the offset header, this file has an `#ifndef` guard but does not define the guard symbol, so repeated inclusion is not actually suppressed.

## Test Signals
Build coverage catches syntax and duplicate-definition issues. Runtime signals include correct MCM/package decode, audio pinstrap interpretation, reliable scratch register round trips if used by diagnostics, clean VF/PF FLR request behavior, GFXOFF status transitions, display timer interrupts with proper ack/mask behavior, stable golden TSC readings, and plausible SVI0 current/VID telemetry. Hardware register tracing or debugfs reads around the corresponding amdgpu paths are useful validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_10_0_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_0_offset.h

## Purpose
`smuio_11_0_0_offset.h` defines SMUIO 11.0.0 register offsets and base-index selectors for AMDGPU. Compared with the smaller 10.0.2 table, it covers a broader SMUIO register map that includes SMU SVI telemetry, MCM config, two CKSVII2C controller instances, reset/power-management registers, ROM access/status windows, GPIO/pad/pinstrap controls, SMIO controls, and a separate power block containing IP discovery, TSC, FLR, scratch, display timer, and interrupt-handler registers.

## Important APIs, Types, And Functions
The header exports preprocessor constants under `_smuio_11_0_0_OFFSET_HEADER`. For the `smuio_smuio_SmuSmuioDec` block at base `0x5a000`, important macros include `mmSMUSVI0_TEL_PLANE0`, `mmSMUIO_MCM_CONFIG`, `mmCKSVII2C_*` and `mmCKSVII2C1_*` controller registers from `IC_CON` through component ID/version/type, `mmSMUIO_MP_RESET_INTR`, `mmSMUIO_SOC_HALT`, `mmSMUIO_PWRMGT`, the `mmROM_*` index/data/start/software command/status/data window, GPIO pad registers `mmSMU_GPIOPAD_*`, strap/select/interrupt registers such as `mmROM_CC_BIF_PINSTRAP`, `mmIO_SMUIO_PINSTRAP`, `mmSMUIO_PCC_*`, `mmSMUIO_GPIO_INT*_SELECT`, `mmSMU_GPIOPAD_MP_INT*_STAT`, and SMIO/SVI pad controls `mmSMIO_INDEX`, `mmS0_VID_SMIO_CNTL`, `mmS1_VID_SMIO_CNTL`, `mmOPEN_DRAIN_SELECT`, `mmSMIO_ENABLE`, and SCL/SDA enable registers. For `smuio_smuio_pwr_SmuSmuioDec` at base `0x5a800`, it defines `mmIP_DISCOVERY_VERSION`, `mmSOC_GAP_PWROK`, `mmGFX_GAP_PWROK`, `mmPWROK_REFCLK_GAP_CYCLES`, golden TSC registers, `mmPWR_VIRT_RESET_REQ`, scratch registers, display timer controls, and `mmPWR_IH_CONTROL`.

## Control Flow
The header has no executable flow. Runtime code uses the symbolic offsets with AMDGPU register access helpers and, where needed, a matching SMUIO 11.0.0 shift/mask header. Common access flows implied by the map include configuring CKSVII2C controllers, polling I2C status/interrupt/clear registers, indexing ROM data windows, managing GPIO pad direction/pull/interrupt controls, selecting SMIO signals, requesting virtual reset/FLR, programming display timers, and reading golden TSC or IP discovery values from the power block.

## State And Persistence
The file itself is stateless. It names stateful hardware registers: I2C controller configuration and FIFOs/status, reset and power-management controls, ROM command/data windows, GPIO pad configuration and interrupt state, pinstrap latches, SMIO open-drain/enable/SCL/SDA controls, TSC counters, scratch registers, FLR request registers, and display timer configuration. The hardware/firmware decides which fields are read-only, sticky, volatile, or reset by power transitions.

## Dependencies And Integration Points
This table integrates with SMUIO 11.0.0 ASIC support in amdgpu, register access macros that understand `BASE_IDX`, and companion mask headers. It is relevant to SMU/SMUIO initialization, IP discovery, ROM access, GPIO and pinstrap handling, SVI/SMIO voltage signaling, CKSVII2C operations, reset/FLR flows, display timer interrupts, and power-management synchronization through TSC/gap registers. It also depends on the generated register database staying consistent with silicon documentation for the 11.0.0 block.

## Risks
The principal risk is writing or reading the wrong hardware address due to an incorrect offset, stale generated table, or mixing SMUIO 11.0.0 offsets with another revision's masks. The CKSVII2C and ROM windows contain many sequential registers where off-by-one mistakes can be hard to diagnose. GPIO/pinstrap and SMIO controls can affect board-level behavior, voltage signaling, or interrupt routing. Reset and power registers can hang or destabilize the GPU if targeted incorrectly. Unlike the 10.0.2 headers in this subset, this file correctly defines its include guard symbol, so repeated inclusion is suppressed.

## Test Signals
Build coverage validates the macro table syntactically. Runtime signals include successful SMUIO 11.0.0 GPU initialization, correct IP discovery reads, usable ROM index/data access, expected GPIO/pinstrap values, working CKSVII2C transactions if exercised on the platform, valid SVI/SMIO behavior, clean MP reset/SoC halt handling, correct FLR request behavior, stable golden TSC reads, scratch register behavior, and display timer interrupt operation. Suspend/resume and GPU reset tests are especially useful because they exercise many of these stateful registers together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_0_offset.h -->
