# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h lines 1-3029

## Purpose

This chunk is the opening section of AMDGPU's generated DCE 11.2 register address header. It contains the MIT-style AMD license block, the `DCE_11_2_D_H` include guard, and a large set of C preprocessor constants that map symbolic display-controller register names to numeric MMIO or indexed-register addresses.

There are no functions, structs, enums, global variables, or executable statements in this range. Its purpose is to provide compile-time register addresses for the DCE 11.2 display engine used by AMD display, clock, power, and SMU code. Driver code pairs these `mm*` and `ix*` address constants with bit masks from `dce_11_2_sh_mask.h`, then performs actual hardware I/O through AMDGPU/DC register helpers.

The covered range defines the first part of the DCE 11.2 address map: display pipe power gating, backlight and ABM, six CRTC/timing-generator instances, DAC and display performance counters, DCCG clock-generation and PLL controls, DMIF/MCIF/DVMM display-memory interface registers, DCIO link/GPIO/pad controls, debug registers, and the beginning of a large eight-instance UNIPHY macro-reserved register table. The chunk ends mid-family at `mmUNIPHY_MACRO_CNTL_RESERVED156`; the next chunk continues with `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED156` and following entries.

## Important APIs, Types, And Macros

The exported interface is the macro namespace. Important groups in this line range are:

- `mmPIPE0_PG_*` through `mmPIPE5_PG_*`, `mmDCPG_INTERRUPT_*`, `mmDC_PGFSM_*`, and `mmDC_PGCNTL_STATUS_REG`: display pipe power-gating configuration, enable, status, interrupts, FSM control, and test/debug addresses.
- `mmBL1_PWM_*`, `mmBL_PWM_*`, `mmDC_ABM1_*`, and `mmABM_TEST_DEBUG_*`: backlight PWM and adaptive backlight management registers, including ambient/user/target/current ABM levels, duty-cycle bounds, ACE coefficients and thresholds, histogram/luma statistics, sample rates, and ABM debug access.
- `mmCRTC_*` plus `mmCRTC0_CRTC_*` through `mmCRTC5_CRTC_*`: generic and per-instance CRTC/timing-generator addresses. The table covers horizontal/vertical totals, blanking, syncs, variable vertical total, nominal VSYNC interrupts, triggers, counter force/reset/readback, stereo, snapshots, update locks, test patterns, GSL, CRC windows/results, external timing sync, static-screen control, and vertical interrupt positions/controls.
- `mmDAC_*`: DAC enable/source, CRC, sync tristate, autodetect, force-output, power, comparator, FIFO, and debug registers.
- `mmPERFCOUNTER_*`, `mmPERFMON_*`, and `mmDC_PERFMON0_*` through `mmDC_PERFMON13_*`: display performance monitor control, state, current/latched counter values, high/low data, interrupt misc, and test/debug addresses across multiple DC perfmon blocks.
- `mmREFCLK_*`, `mmDPREFCLK_*`, `mmDCE_VERSION`, `mmDCCG_*`, `mmDENTIST_DISPCLK_CNTL`, `mmDISPCLK_*`, `mmSYMCLK*`, `mmCRTCn_PIXEL_RATE_CNTL`, `mmDP_DTO*`, `mmPHYPLL*_PIXCLK_RESYNC_CNTL`, `mmCPLL_MACRO_CNTL_RESERVED*`, and `mmPLL_MACRO_CNTL_RESERVED*`: DCCG/display clock, DP reference clock, global timer, DTO, gate-disable, clock-gating, PLL, and reserved PLL macro-control addresses.
- `mmDMIF_*`, `mmPIPE*_ARBITRATION_CONTROL3`, `mmPIPE*_MAX_REQUESTS`, `mmPIPE*_DMIF_BUFFER_CONTROL`, `mmDVMM_*`, `mmMCIF_*`, `mmDCI_*`, `mmRBBMIF_*`, and `mmCC_DC_PIPE_DIS`: display-memory interface, display virtual memory manager, memory client interface, pipe arbitration/request throttling, memory power, interface reset/status, and timeout registers.
- `mmDC_GENERICA`, `mmDC_GENERICB`, `mmDC_PAD_EXTERN_SIG`, `mmDC_REF_CLK_CNTL`, `mmDC_GPIO_DEBUG`, `mmUNIPHY[A-G]_*`, `mmUNIPHYLPA_*`, `mmUNIPHYLPB_*`, `mmUNIPHY_IMPCAL_*`, `mmAUXP_IMPCAL`, `mmAUXN_IMPCAL`, and `mmDCIO_IMPCAL_*`: DCIO generic, pad, UNIPHY link/channel crossbar, low-power UNIPHY, and impedance-calibration registers.
- `mmLVTMA_PWRSEQ_*`, `mmDCIO_GSL_*`, `mmDC_GPU_TIMER_*`, `mmDCIO_CLOCK_CNTL`, `mmDCIO_DEBUG*`, `mmDCIO_SOFT_RESET`, `mmDCIO_DPHY_SEL`, `mmDCIO_DPCS_*`, and `mmDCIO_SEMAPHORE*`: panel sequencing, genlock/swaplock pads, GPU timer, debug, soft reset, PHY selection, DPCS interrupts, and DCIO semaphores.
- `ixDCIO_DEBUG*`, `ixDMIF_DEBUG02_CORE*`, and `ixIDDCCIF*_DBG_DCCIF_*`: indexed debug-register selectors that are used with the corresponding test/debug index/data register pairs rather than as ordinary direct MMIO offsets.
- `mmDC_GPIO_*`, `mmPHY_AUX_CNTL`, `mmDVO_*`, and `mmDC_GPIO_AUX_CTRL_*` / `mmDC_GPIO_HPD_CTRL_*`: GPIO/DDC/sync/genlock/HPD/power-sequence/I2C/I2S/SPDIF pad and AUX/HPD control addresses.
- `mmUNIPHY_MACRO_CNTL_RESERVED0` through `mmUNIPHY_MACRO_CNTL_RESERVED156`, with instance aliases `mmDCIO_UNIPHY0_*` through `mmDCIO_UNIPHY7_*` for entries through reserved 155 in this chunk: a repetitive UNIPHY macro-control address matrix. The base instance starts around `0x48c0`, instance 1 around `0x4960`, and instances 2-7 in the `0x9a00` through `0x9d..` regions.

The `mm` prefix marks direct MMIO register offsets. The `ix` prefix marks indirect/indexed debug selectors. Many macros are intentionally paired: a generic register name such as `mmCRTC_CONTROL` or `mmUNIPHY_MACRO_CNTL_RESERVED0` names the base instance, while `mmCRTC0_CRTC_CONTROL` through `mmCRTC5_CRTC_CONTROL` or `mmDCIO_UNIPHY0_*` through `mmDCIO_UNIPHY7_*` name explicit hardware instances.

## Control Flow

This header has no runtime control flow. It influences runtime behavior by supplying exact addresses to consumers that sequence display-engine hardware.

A typical DCE 11.2 caller flow is:

1. Include `dce/dce_11_2_d.h` and `dce/dce_11_2_sh_mask.h`.
2. Select an address macro, often through a local register-list macro such as `SR(reg_name)` or `SRI(reg_name, block, id)`.
3. Read or write the register with DC helpers such as `dm_read_reg()` and `dm_write_reg()`, or with AMDGPU/PowerPlay register-access helpers.
4. Use masks/shifts from `dce_11_2_sh_mask.h` to extract or update fields.
5. Poll status, program clocks, enable/disable pipes, update timing-generator state, program GPIO/DDC/HPD paths, or configure memory-interface behavior according to display sequencing rules.

Direct examples in this tree include `dce112_hwseq.c`, which computes CRTC instance offsets from `mmCRTC0_CRTC_GSL_CONTROL - mmCRTC_GSL_CONTROL`, writes `mmCRTC_MASTER_UPDATE_MODE` after BIOS pipe-gating calls, and programs `mmDVMM_PTE_REQ` during display power-gating initialization. `dce112_resource.c` builds DCE 11.2 resource tables from `mmCRTC*`, DCP, ABM, AUX, I2C, clock, link-encoder, and related register macros. `dce112_clk_mgr.c` builds display-clock register tables and then calls BIOS clock services. `vegam_smumgr.c` includes the DCE 11.2 headers alongside SMU, GMC, OSS, GFX, and BIF register headers for Vega M power-management integration.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It names hardware registers whose values live in DCE/DCIO/DCCG/DMIF/MCIF/DVMM/UNIPHY blocks.

The hardware state represented by this chunk includes pipe power-gating state, ABM/backlight duty and luma histogram state, CRTC timing and interrupt state, CRTC update-lock and snapshot state, CRC/readback state, DAC/autodetect/power state, perfmon counters, display and reference clock controls, PLL/resync controls, display-memory arbitration and virtual-memory request behavior, memory-interface power/reset/status, DCIO link routing and pad calibration, GPIO/DDC/HPD direction/value/enable state, panel power sequencing, and UNIPHY macro-control state.

Persistence depends on the register and platform sequence. Some values are read-only status snapshots, some are counters or sticky interrupt/status bits, some are double-buffered or latch at vertical update, and some remain programmed until firmware, BIOS tables, DC code, SMU/powerplay code, suspend/resume, display power gating, soft reset, hotplug handling, or full GPU reset changes them. The address header does not encode read-only, write-one-to-clear, self-clearing, lock, double-buffer, or timing restrictions.

## Dependencies And Integration Points

The direct dependency is only the C preprocessor and the `DCE_11_2_D_H` include guard. In practice this file is one part of a generated AMD ASIC register-header set:

- `dce_11_2_d.h` supplies register addresses.
- `dce_11_2_sh_mask.h` supplies masks and shifts for fields inside those registers.
- `dce_11_2_enum.h` supplies generated enum values used by DCE 11.2 field programming.
- DC and AMDGPU helpers perform the actual register I/O and enforce the display sequencing around these constants.

Direct include points found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`

The main integration points are display resource construction, timing-generator instance-offset calculation, display power-gating, DVMM PTE/request programming, display clock and DP reference clock programming, framebuffer-compression support, GPIO/DDC/HPD/link-encoder setup, and SMU/power-management coordination. Although the source path is under a local `ceph-client` mirror, this chunk is AMDGPU Linux kernel display-driver metadata and has no Ceph filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. A wrong numeric constant or a wrong generic-to-instance alias will still compile but can redirect reads or writes to the wrong display block.

The CRTC table is especially sensitive because consumers compute per-pipe offsets by subtracting a generic base register from an instance register. If one `mmCRTCn_CRTC_*` address has the wrong base, all derived register accesses for that timing generator can land on another pipe or on an unrelated register. Symptoms would include broken modesets, missed vblank/vupdate interrupts, incorrect CRC/readback, update-lock hangs, or only some display pipes failing.

Power-gating and memory-interface registers are high impact. Incorrect `PIPE*_PG_*`, `DCPG_*`, `DC_PGFSM_*`, `DVMM_*`, `DMIF_*`, `MCIF_*`, `DCI_*`, or `RBBMIF_*` addresses can cause power transitions to time out, leave display memory requests misconfigured, corrupt display fetch behavior, or create resume and hotplug failures.

Clock and link-control addresses are also sensitive. Misaddressing DCCG, DTO, PLL, pixel-rate, SYMCLK, DPREFCLK, UNIPHY, DCIO soft-reset, or GPIO/HPD/DDC registers can lead to bad pixel clocks, unstable DisplayPort links, failed AUX/DDC communication, incorrect HPD detection, panel power sequencing problems, or link-encoder routing errors.

The UNIPHY macro-reserved section is highly repetitive and crosses the chunk boundary. Entry `mmUNIPHY_MACRO_CNTL_RESERVED156` appears at the end of this chunk, but its instance-specific `mmDCIO_UNIPHY0_*` through `mmDCIO_UNIPHY7_*` aliases are in the next chunk. The final per-file reconciliation should treat this as one continuous generated table, not as an incomplete register family.

Several macros name debug or reserved registers. They may be required by firmware/debug tooling or generated register lists even if normal modeset code does not touch them. Removing or renaming them can break builds or diagnostics even when there is no obvious runtime path in display code.

## Test Signals

Useful validation signals are mostly build-time and hardware-observable:

- Kernel build coverage for DCE 11.2 display and Vega M PowerPlay paths catches missing or renamed macros in `dce112_resource.c`, `dce112_clk_mgr.c`, `dce112_hwseq.c`, `dce112_compressor.c`, and `vegam_smumgr.c`.
- Static register-map validation can compare every `mm*` and `ix*` value against AMD's generated register database and against the paired `dce_11_2_sh_mask.h` field definitions.
- Modeset tests across all six CRTCs should verify correct timing, vblank/vupdate interrupts, update-lock behavior, stereo/snapshot paths, CRC/readback, and test-pattern output.
- Suspend/resume, runtime display power gating, and DC power-state transitions should not leave pipes disabled, DVMM PTE settings stale, or display memory requests hung.
- Backlight and ABM tests should show expected PWM duty cycle, ambient/user/target/current ABM behavior, histogram/luma statistics, and panel lock behavior.
- Clock tests should confirm display clock, DP reference clock, DTO, pixel-rate, PLL/resync, and SYMCLK programming remain stable across modesets and link retraining.
- Hotplug, AUX/DDC, GPIO, HPD, panel power-sequence, and link-encoder tests should verify the DCIO/UNIPHY/GPIO address map reaches the intended physical connector path.
- Perfmon/debug smoke tests should show counters and indexed debug reads changing in expected blocks rather than another instance.

Regression symptoms from bad constants include build failures from missing macros, a single CRTC or connector failing, blank displays after modeset, incorrect vblank timing, broken backlight control, HPD/DDC/AUX failures, DP link-training failures, display clock misprogramming, resume hangs, display power-gating timeouts, or diagnostics reporting activity on the wrong pipe or UNIPHY instance.

## Cross-Chunk Notes

This is the first chunk of `dce_11_2_d.h`. Later chunks continue the UNIPHY reserved table, DCRX PHY and DP PHY/Dig front-end register groups, DCP/GRPH/viewport and other display-pipe blocks, compressor and audio/display output blocks, and eventually close the include guard. The merge/reconciliation lane should treat all chunks as one generated DCE 11.2 hardware address map paired with `dce_11_2_sh_mask.h`, not as independent executable modules.
