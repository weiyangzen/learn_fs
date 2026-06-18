# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001518`: lines 1-3029, `Docs/researches/chunks/subset-b-001518_research.md`
- `subset-b-001519`: lines 3030-6042, `Docs/researches/chunks/subset-b-001519_research.md`
- `subset-b-001520`: lines 6043-9068, `Docs/researches/chunks/subset-b-001520_research.md`
- `subset-b-001521`: lines 9069-10084, `Docs/researches/chunks/subset-b-001521_research.md`

## Chunk Research

### subset-b-001518: lines 1-3029

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

### subset-b-001519: lines 3030-6042

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h lines 3030-6042

## Purpose

This chunk is a generated AMD DCE 11.2 register-address map. It contains 3,013 preprocessor `#define` constants that name MMIO register offsets for several display-engine blocks: the tail of UNIPHY reserved macro-control space, DCRX and DPHY macro reserved ranges, six DCP display-pipe register instances, nine DIG/HDMI/AFMT/TMDS encoder instances, DMCU microcontroller registers, and the start of nine DisplayPort link/stream register instances.

The chunk does not implement behavior directly. Its purpose is to give DCE 11.2-specific symbolic names to hardware addresses so AMDGPU, power-management, and display code can issue register reads and writes without hard-coding numeric offsets. The file-level naming pattern is important: unqualified aliases such as `mmGRPH_ENABLE`, `mmDIG_CONTROL`, and `mmDP_LINK_CNTL` point at the first instance, while qualified names such as `mmDCP5_GRPH_ENABLE`, `mmDIG8_DIG_CONTROL`, and `mmDP8_DP_LINK_CNTL` point at explicit hardware instances.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this range. The exported interface is a set of macros consumed by register-access helpers such as `RREG32()` and `WREG32()` in other AMDGPU code.

Major macro groups in this chunk are:

- `mmUNIPHY_MACRO_CNTL_RESERVED157` through `mmUNIPHY_MACRO_CNTL_RESERVED159`, plus `mmDCIO_UNIPHY0_...` through `mmDCIO_UNIPHY7_...` aliases, finishing the UNIPHY reserved macro-control space started before this chunk.
- `mmDCRX_PHY_MACRO_CNTL_RESERVED0` through `mmDCRX_PHY_MACRO_CNTL_RESERVED379`, a contiguous reserved receiver PHY macro range from `0x5a84` through `0x5bff`.
- `mmDPHY_MACRO_CNTL_RESERVED0` through `mmDPHY_MACRO_CNTL_RESERVED63`, a contiguous transmitter/display PHY macro range from `0x5d98` through `0x5dd7`.
- DCP pipe registers for instances 0-5, with default aliases at the DCP0 offsets. These cover graphics enable/control, primary and secondary surface addresses, pitch, surface offsets, flip/update control, DFQ status, interrupts, compression surface metadata, prescale values, input/output CSC matrices, color transform matrices, denorm/round/clamp controls, keyer registers, degamma and gamut-remap registers, DCP debug registers, hardware rotation, XDMA underflow detection, regamma LUT programming, alpha control, and related per-pipe state.
- DIG encoder registers for instances 0-8, including `DIG_*`, `HDMI_*`, `AFMT_*`, and `TMDS_*` register families. These names cover encoder control, HDMI audio/video packet controls, AFMT audio packet/status/generic packet registers, infoframe/checksum registers, TMDS control, and DIG debug access.
- DMCU registers from `mmDMCU_CTRL` through DMCU interrupt/performance/DPRX interrupt controls, plus master/slave communication mailbox registers.
- DP link and secondary-stream registers for instances 0-8, beginning at `mmDP_LINK_CNTL` and continuing through `mmDP3_DP_MSE_SAT0` at the chunk boundary. This includes link control, pixel format, MSA colorimetry/misc/timing overrides, video timing and M/N values, link framing, HBR2 and DPHY training/test/CRC controls, secondary-data packet controls, audio M/N readback, timestamps, and MSE rate-control registers.

The companion `dce_11_2_sh_mask.h` header supplies field masks and shifts for many of these registers. This `_d.h` header supplies only addresses.

## Control Flow

This chunk has no runtime control flow. Its operational flow is compile-time macro expansion:

1. A DCE 11.2 consumer includes `dce/dce_11_2_d.h`, often with `dce/dce_11_2_sh_mask.h`.
2. The consumer selects either a concrete instance macro, such as `mmDP4_DP_SEC_CNTL`, or a base alias plus a runtime offset, such as `mmGRPH_ENABLE + amdgpu_crtc->crtc_offset`.
3. The resulting integer offset is passed to AMDGPU register helpers for MMIO access.
4. Hardware state changes only in the external code that reads or writes the selected register.

The repeated instance layout is the key control convention. DCP instances use offsets `0x1a00`, `0x1c00`, `0x1e00`, `0x4000`, `0x4200`, and `0x4400` for corresponding pipe registers. DIG/DP instances use mostly regular per-link blocks at `0x4a00`, `0x4b00`, `0x4c00`, `0x4d00`, `0x4e00`, `0x4f00`, `0x5400`, `0x5600`, and `0x5700` regions. Code that relies on adding per-instance offsets depends on those generated constants staying aligned with the hardware register map.

## State And Persistence Behavior

The header stores no software state and has no persistence by itself. It is a declarative map from names to numeric hardware offsets.

When external code writes these registers, the affected state lives in the display hardware. Examples include scanout surface address state in DCP registers, color conversion and gamma LUT state in DCP color registers, HDMI/AFMT packet state in DIG registers, DMCU firmware/control/mailbox state, and DisplayPort link-training, stream, audio, CRC, and MST/MSE state in DP registers. That hardware state persists until reprogrammed, reset by the relevant display block, or cleared by GPU reset/suspend/resume paths.

The reserved PHY macro ranges are also stateful if touched by diagnostics or bring-up code, but their semantics are intentionally not represented in this header. They should be treated as ASIC-register database entries rather than self-documenting software contracts.

## Dependencies

This chunk depends on the surrounding generated DCE 11.2 register-header ecosystem:

- The include guard and license/header context from the top of `dce_11_2_d.h`.
- Matching field definitions in `dce_11_2_sh_mask.h`.
- AMDGPU register access helpers and display/power-management code that consume `mm*` offsets.
- ASIC-specific display hardware for DCE 11.2, including DCP, DIG, DMCU, DCIO/UNIPHY, DCRX/DPHY, and DP blocks.

One direct in-tree inclusion is `drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`, which includes both `dce_11_2_d.h` and `dce_11_2_sh_mask.h`. Similar DCE generation patterns are used by display paths such as older `dce_v*_0.c` files, where calls like `WREG32(mmGRPH_ENABLE + amdgpu_crtc->crtc_offset, ...)` and `RREG32(mmDP_SEC_CNTL + dig->afmt->offset)` show the intended base-plus-instance-offset style.

## Integration Points

The DCP section integrates with scanout plane programming, page flips, cursor/display pipe state, color management, and per-pipe debug/status paths. Register families such as `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_UPDATE`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `REGAMMA_*`, and `ALPHA_CONTROL` are the low-level address layer beneath DRM/KMS plane and color-management logic.

The DIG/HDMI/AFMT/TMDS section integrates with digital encoder setup, HDMI packet generation, audio infoframes, generic infoframe packet transmission, and debug access for encoder front ends. Each register has a default alias plus `DIG0` through `DIG8` instance forms, allowing either table-driven instance selection or explicit register use.

The DMCU section integrates with display microcontroller firmware loading/control, DMCU interrupt routing, scratch registers, and host-to-microcontroller mailboxes (`MASTER_COMM_*` and `SLAVE_COMM_*`). Power-management code including the VegaM SMU manager includes this DCE 11.2 map, so address drift can affect display-related power and firmware coordination.

The DP section integrates with DisplayPort link bring-up, main-stream attribute programming, video timing, DPHY training/test controls, CRC diagnostics, secondary-data packet and audio clock programming, and MST/MSE bandwidth allocation. The chunk ends in the middle of the MSE saturation register family at `mmDP3_DP_MSE_SAT0`; the later chunk must be reconciled for the complete per-file DP/MSE view.

## Risks And Edge Cases

- These constants are raw hardware offsets. A wrong address compiles cleanly but can read or write the wrong display register, causing blank displays, bad color, failed link training, audio packet loss, or difficult suspend/resume failures.
- The chunk starts in the middle of the UNIPHY reserved sequence and ends in the middle of the DP MSE saturation sequence. A final per-file report must merge adjacent chunks before drawing conclusions about those register families.
- Default aliases such as `mmGRPH_ENABLE`, `mmDIG_CONTROL`, and `mmDP_SEC_CNTL` map to instance 0. Code using a default alias must add the correct runtime instance offset when targeting other pipes or links.
- The generated instance layout is not perfectly inferred from simple arithmetic. For example, the visible `DP_DPHY_SCRAM_CNTL` instance list has `mmDP8_DP_DPHY_SCRAM_CNTL` at `0x56b6` and no `mmDP7_DP_DPHY_SCRAM_CNTL` line in this chunk, while nearby DP DPHY registers define both DP7 at `0x56xx` and DP8 at `0x57xx`. Consumers should trust the generated header for this ASIC but static validation should flag such irregularities for review against the source register database.
- Reserved DCRX/DPHY/UNIPHY macro-control names provide no bit-level semantics. Hand-written code should avoid programming them unless backed by ASIC documentation or known firmware/display bring-up requirements.
- DCP surface-address and compression-address registers encode memory addresses; programming the wrong pipe or stale address can point scanout at invalid or unintended framebuffer memory.
- DMCU mailbox and firmware-control registers are coordination points between host driver and display microcontroller. Incorrect ordering or offsets in consumer code can deadlock firmware handshakes or misroute interrupts even though this header itself has no ordering rules.
- DP secondary-data and audio M/N registers are timing-sensitive. Using the wrong per-link offset can produce valid MMIO transactions that affect a different active connector.

## Test Signals

Useful validation for this chunk is mostly build-time, static, and hardware-integration oriented:

- Kernel/driver builds that include `dce_11_2_d.h` and `dce_11_2_sh_mask.h` should compile without missing macro or duplicate-definition diagnostics.
- Static checks should compare repeated DCP0-5, DIG0-8, and DP0-8 groups for expected address progression and known exceptions.
- Register-table generation tests should confirm that default aliases map to the intended first instance and that explicit instance macros match the ASIC register database.
- Display smoke tests should exercise plane enable/disable, flips, color-management updates, hardware cursor/alpha paths, and compressed-surface scanout on DCE 11.2 hardware.
- HDMI/DP hotplug and modeset tests should verify encoder setup, infoframe/audio packet programming, DP link training, CRC diagnostic paths, and MST/MSE bandwidth allocation.
- Suspend/resume and GPU reset tests should verify that DCP, DIG, DMCU, and DP state programmed via these offsets is restored to working hardware state.
- Low-level debug reads of representative registers, such as `mmDCP0_GRPH_ENABLE`, `mmDIG0_DIG_CONTROL`, `mmDMCU_STATUS`, and `mmDP0_DP_LINK_CNTL`, should return plausible values on matching DCE 11.2 hardware and should not access unrelated blocks.

### subset-b-001520: lines 6043-9068

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h lines 6043-9068

## Scope And Purpose

This chunk is part of AMDGPU's generated DCE 11.2 register address header. It contains no executable logic; it is a compile-time map from symbolic register names to numeric MMIO or indexed-register addresses for the display engine on DCE 11.2 ASICs. The paired `dce_11_2_sh_mask.h` file supplies bit masks and shifts, while this `*_d.h` file supplies the register addresses used by `dm_read_reg()`, `dm_write_reg()`, `RREG32()`, `WREG32()`, and generated register-table macros.

The line range covers a broad display pipeline slice:

- DisplayPort MST stream allocation and AUX-channel registers.
- DVO, framebuffer compression, formatter, line buffer, scaler, color-management, unpacker, and memory-input related display pipe registers.
- Legacy VGA indexed and direct registers.
- DMIF/display pipe arbitration, watermark, urgency, stutter, and debug registers.
- HDMI/DisplayPort audio through Azalia/HDA controller, stream, converter, pin, endpoint, and input endpoint registers.
- Blender, writeback/conversion, DC front-end, hotplug detect, I2C, virtual plane/CRTC, XDMA, and display PHY command-bus lane registers.

Most families appear both as a generic base macro and as per-instance aliases. For example `mmSCL_MODE` aliases pipe 0 at `0x1b42`, while `mmSCL0_SCL_MODE` through `mmSCL5_SCL_MODE` name the six pipe instances at the pipe-specific offsets. Virtual-pipe families use `V`, `V0`, and `V1` naming and map to two virtual instances, typically around `0x46xx/0x47xx` and `0x98xx/0x99xx`. The source path sits under a Ceph source mirror, but this chunk is AMDGPU kernel display-register metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or variables in this range. The API surface is the macro namespace itself:

- `mm...` macros name MMIO register addresses.
- `ix...` macros name indexed register offsets selected through an index/data register pair.
- Unqualified block macros such as `mmLB_DATA_FORMAT`, `mmSCL_MODE`, and `mmBLND_CONTROL` generally name instance 0.
- Qualified aliases such as `mmLB3_LB_DATA_FORMAT`, `mmSCL5_SCL_MODE`, `mmHPD4_DC_HPD_CONTROL`, and `mmXDMA_MSTR_PIPE2_XDMA_MSTR_HEIGHT` name a concrete hardware instance.
- The same numeric address can intentionally appear under multiple names to support both generic offset arithmetic and explicit instance-address tables.

Major macro families in this chunk:

- `mmDP*_DP_MSE_*` and `mmDP_MSE_*` define DisplayPort Multi-Stream Transport stream allocation table, update, link-timing, status, and debug addresses for DP instances 0-8. The range begins in the middle of the `SAT0` family, so the first included line is `mmDP4_DP_MSE_SAT0`.
- `mmAUX_*`, `mmDP_AUX0_*` through `mmDP_AUX5_*`, and `ixDP_AUX_DEBUG_A` through `ixDP_AUX_DEBUG_Q` define six DP AUX engines plus indexed debug selectors. These cover software AUX control/status/data, link-service data, DPHY TX/RX controls and status, GTC sync error/status registers, and test debug access.
- `mmDVO_*` defines DVO enable/source/output/control, CRC, FIFO error, and test-debug registers.
- `mmFBC_*` defines framebuffer compression control, start/stop delay, compression mode, debug, indirect LUT entries, CSM region offsets, client-region masks, status, alpha controls, and test-debug registers.
- `mmFMT*` defines six formatter instances. Registers cover clamp components, dynamic expansion, bit depth, dithering seeds and programmable temporal dither matrices, clamp control, CRC masks/results, side-by-side stereo, 4:2:0 hblank timing, memory control, and formatter debug.
- `mmLB*` and `mmLBV*` define line-buffer and virtual line-buffer registers. They include data format, memory control and size status, desktop height, vline/vblank counters and statuses, sync reset selection, black/keyer colors, buffer level/urgency/status, outstanding-request status, and debug.
- `mmMVP_*` and `ixMVP_*` define multi-view/multi-plane support registers for AFR flip, DC MVP line-buffer control, master controls, FIFO/slave status, in-band capability, black keying, CRC, receive counters, and debug.
- `mmSCL*` and `mmSCLV*` define pipe and virtual scalers. Registers include coefficient RAM select/tap data, mode, tap/control/bypass settings, manual replication, automatic mode, horizontal/vertical filter control, scale ratios, filter init and bottom init, round offsets, update, sharpness/ALU controls, coefficient-RAM conflict status, viewport start/size, extended overscan, mode-change detect/mask, and debug.
- `mmCOL_*`, `mmINPUT_*`, `mmOUTPUT_*`, `mmPRESCALE_*`, `mmDENORM_*`, `mmGAMMA_*`, and `mmPACK_FIFO_ERROR` define color-management and stream-formatting registers. They cover manual color update, prescale, input/output CSC matrices and clamp/rounding, denormalization clamp, gamma correction regions, stream format descriptors and payload capability, and FIFO error reporting.
- `mmUNP*` defines unpacker/memory input for virtual/underlay style graphics. It covers graph enable/control, expansion, mode, primary/secondary L/C surface addresses and high bits, pitch, tiling, stereo, viewport/source offsets, luma/chroma start/end coordinates, update, outstanding request limit, in-use addresses, DVMM PTE/debug, interrupts, flip control, CRC, rotation, and debug.
- Legacy VGA families include `mmGENMO_*`, `mmGENFC_*`, `mmGENS*`, `mmDAC_*`, `mmSEQ8_*`, `ixSEQ*`, `mmCRTC8_*`, `ixCRT*`, `mmGRPH8_*`, `ixGRA*`, `mmATTR*`, `ixATTR*`, `mmVGA_*`, and per-display `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`.
- `mmDPG_*`, `mmDMIF_PG*_*`, `mmDPGV*_*`, and `mmDMIFV_PG*_*` define display pipe memory-interface arbitration, watermark, urgency, DPM, stutter, NB P-state, repeater, hardware debug, preprocessing, DVMM status, and test-debug registers for six physical pipes and two virtual pipes.
- `mmAZROOT_*`, `mmAZALIA_*`, `ixAZALIA_*`, `mmAZF0STREAM*_*`, `mmAZF0ENDPOINT*_*`, `mmAZF0INPUTENDPOINT*_*`, `ixAUDIO_DESCRIPTOR*`, and `ixSINK_DESCRIPTION*` define display audio/HDA controller and codec endpoint registers. This includes HDA global control/status, CORB/RIRB DMA rings, immediate command interfaces, stream descriptors, wall clocks, wake/status/interrupts, codec root/function parameters, converter and pin controls, audio descriptors, sink descriptions, channel status, CRC/debug, output endpoints, and input endpoints.
- `mmBLND*` and `mmBLNDV*` define physical and virtual blender control/update/underflow/status/debug registers.
- `mmWB_*` and `mmCNV_*` define writeback and color-conversion registers, including enable, error-correction config, CSC matrix, clamp/round offsets, test CRC, debug, soft reset, and warm-up mode controls.
- `mmDCFE*` and `mmDCFEV*` define display front-end clock, reset, debug, memory power, flush, DMIFV power, and misc registers.
- `mmDC_HPD_*` and `mmHPD0_*` through `mmHPD5_*` define six hotplug-detect interrupt/status/control, fast training, and toggle-filter registers.
- `mmDCO_*`, `mmDISP_INTERRUPT_STATUS*`, `mmDPDBG_*`, `mmDIG_SOFT_RESET*`, `mmDC_I2C_*`, and `mmGENERIC_I2C_*` define global display controller scratch, memory power, clock/power, interrupt fanout, DP debug, DIG reset, and I2C control/status/debug registers.
- `mmCRTCV*` defines virtual CRTC timing, control, overscan/black color, CRC windows/results, and test-debug registers.
- `mmXDMA_*` defines display XDMA master/slave registers for cross-device or remote-surface movement, including PCIE/client config, local/remote surface base/high, pitch, urgent controls, NACK/status, pipe command/dim/height/cache/channel start/perf, slave latency, flip-pending, and per-channel remote GPU address registers.
- `mmCMD_BUS_TX_CONTROL_LANE0/1/2` and `mmDC_COMBOPHYTXREGS*_CMD_BUS_TX_CONTROL_LANE*` begin the COMBOPHY TX command-bus lane-control address family; this chunk ends at `mmCMD_BUS_TX_CONTROL_LANE2`, so later lines complete lane 2 and following PHY registers.

## Control Flow

This chunk has no local control flow. Its runtime effect is indirect: DCE 11.2 display code uses these symbolic addresses to read, write, poll, snapshot, or acknowledge hardware state. The common patterns are:

1. A block-specific object or register table selects a base macro or per-instance macro.
2. Driver code reads with `dm_read_reg()` or `RREG32()`, often using an instance offset or generated register list.
3. It updates fields using masks from `dce_11_2_sh_mask.h`, or writes a full programming value.
4. It writes through `dm_write_reg()` or `WREG32()`.
5. For update-locked blocks, code writes an update register, waits for a status bit, or synchronizes with vblank/vupdate to avoid visible tearing.

Concrete integration patterns visible in this source tree include:

- DCE 11.2 display components include this header directly: `dce112_compressor.c`, `dce112_hwseq.c`, `dce112_clk_mgr.c`, and `dce112_resource.c` include both `dce_11_2_d.h` and `dce_11_2_sh_mask.h`.
- `dce112_compressor.c` uses `mmDPG_PIPE_STUTTER_CONTROL_NONLPTCH` through DCE/DMIF register macros to program framebuffer-compression and stutter behavior.
- Generic DCE paths show how HPD and DMIF registers are consumed. `dce_v10_0.c` reads and writes `mmDC_HPD_INT_STATUS`, `mmDC_HPD_INT_CONTROL`, `mmDC_HPD_CONTROL`, and `mmDC_HPD_TOGGLE_FILT_CNTL` using HPD offsets; it also writes `mmDPG_PIPE_URGENCY_CONTROL` and `mmLB_DATA_FORMAT` with CRTC offsets. Those are the same style of base-address-plus-instance programming represented by this DCE 11.2 header.
- `dce110_mem_input_v.c` uses virtual unpacker registers such as `mmUNP_GRPH_PRIMARY_SURFACE_ADDRESS_HIGH_C`, `mmUNP_GRPH_PRIMARY_SURFACE_ADDRESS_C`, `mmUNP_GRPH_ENABLE`, `mmUNP_GRPH_CONTROL`, luma/chroma pitch/start/end registers, and `mmUNP_GRPH_UPDATE` for virtual memory-input programming.
- `dce110_timing_generator_v.c` uses virtual CRTC addresses such as `mmCRTCV_H_TOTAL`, matching the `CRTCV` family in this chunk.
- The generated `mmAZALIA_*` and `ixAZALIA_*` addresses are integration points for display audio routing, stream setup, converter/pin control, ELD/sink information, and HDA interrupt/status handling.

Because these are address macros, an error does not produce a local compiler-visible algorithmic bug. It makes distant control flow operate on the wrong hardware register: an HPD interrupt may not acknowledge, a scaler update may hit the wrong pipe, an AUX transaction may time out, audio streams may map to the wrong endpoint, or a memory-input surface update may latch incomplete state.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It describes state held in DCE 11.2 hardware registers. Persistence depends on register semantics, not encoded here:

- Many display pipe programming registers persist until overwritten, a modeset reprograms the pipe, a block reset fires, or suspend/resume reinitializes display state.
- Status and interrupt registers, such as HPD status, DISP interrupt status, FIFO/underflow status, vline/vblank status, and audio status, may be sticky, level-driven, write-one-to-clear, or self-clearing depending on the companion mask documentation and hardware behavior.
- Update registers such as `mmSCL_UPDATE`, `mmUNP_GRPH_UPDATE`, `mmBLND_UPDATE`, and `mmCNV_UPDATE` are synchronization controls rather than ordinary persistent configuration. They typically coordinate double-buffered state latching at frame or vertical-update boundaries.
- Surface address, pitch, tiling, viewport, line-buffer, scaler, color, and formatter registers describe the active display scanout path. Bad or partially updated values can create visible corruption, underruns, or page-flip failures.
- FBC, DMIF, DPG, DCFE, and DCFEV registers influence power, stutter, memory arbitration, flush, and latency behavior. Their values can interact with dynamic power management and memory P-state transitions.
- Azalia/HDA registers model controller state, ring buffers, command/response interfaces, streams, endpoints, pin controls, sink descriptors, and audio-enabled/format-changed interrupt state. Some values are software-owned, while codec response/status values are hardware-owned.
- Legacy VGA indexed state persists in the VGA compatibility register file and can affect boot consoles, VGA arbitration, or fallback display paths if programmed incorrectly.
- XDMA master/slave registers describe remote/local transfer channels and related performance/status state. They are operational state for XDMA display movement, not general-purpose memory.

The macros do not mark registers as read-only, write-only, write-one-to-clear, indexed, latch-on-update, clock-gated, or safe only under blanking. Callers must use the block-specific sequencing and masks supplied elsewhere.

## Dependencies And Integration Points

This file depends on the generated DCE register-header ecosystem:

- `dce_11_2_sh_mask.h` supplies field masks and shifts for the addresses defined here.
- `dce_11_2_enum.h` supplies generated enum values used by some fields.
- DCE 11.2 display code includes this address header in compressor, hardware sequencing, clock manager, and resource-construction code.
- DCE register-access helpers (`dm_read_reg()`, `dm_write_reg()`, `RREG32()`, `WREG32()`, register-table macros, and offset macros) turn these numeric addresses into MMIO operations.

Important subsystem integration points:

- Display connector management uses the HPD families for plug/unplug, IRQ enable/ack, debounce/toggle filtering, and DP fast training.
- DP link and MST support uses DP MSE allocation/status and AUX-channel control/data/status/debug registers.
- Modeset and plane programming uses LB, SCL, COL, UNP, FMT, BLND, DCFE, and CRTC/CRTCV families to program surface format, scaling, viewport, color conversion, timing, blending, and update synchronization.
- Display memory and power management use DPG/DMIF, DCFE, FBC, and DCO register families for watermarks, urgency, stutter, memory power, compression, and flush paths.
- Display audio uses Azalia/HDA global, stream, endpoint, converter, pin, descriptor, sink, CORB/RIRB, and interrupt/status registers.
- Virtual display/underlay paths use `LBV`, `SCLV`, `UNP`, `DPGV`, `DMIFV`, `BLNDV`, `DCFEV`, and `CRTCV` aliases.
- Legacy VGA support uses VGA direct/indexed register addresses and per-display VGA control gates.
- XDMA and COMBOPHY families integrate with cross-device display transfers and PHY lane programming, respectively.

## Risks And Maintenance Notes

- Address aliasing is intentional but fragile. Generic macros usually point at instance 0, while explicit per-instance aliases use larger offsets. Replacing explicit aliases with generic names can accidentally force all programming to pipe 0.
- Several families are incomplete at the chunk boundaries. The range starts after earlier `DP_MSE_SAT0` aliases and ends inside COMBOPHY lane-control definitions. A final per-file report must reconcile adjacent chunks before drawing whole-file conclusions.
- The `mm`/`ix` distinction matters. `ixAZALIA_*`, `ixDP_AUX_DEBUG_*`, `ixFMT_*`, legacy `ixCRT*`, `ixGRA*`, `ixATTR*`, and similar indexed constants are not standalone MMIO addresses; they are indices selected through an index/data register interface.
- Many registers need sequencing with clocks, power gates, blanking, vupdate, or register locks. Address macros alone do not encode these constraints.
- Interrupt/status naming is not enough to infer clear semantics. HPD, DISP, underflow, vline/vblank, audio, and XDMA status registers may require write-one-to-clear or paired control/status operations.
- Display audio endpoint and converter indices are dense and easy to confuse. Wrong `AZF0STREAM`, `AZF0ENDPOINT`, or `AZF0INPUTENDPOINT` addressing can break only specific audio stream or input endpoint combinations.
- Surface-address families split luma/chroma and low/high address components. Partial updates or mixed instance aliases can cause incorrect scanout, memory faults, or corruption.
- Power and latency families (`FBC`, `DPG`, `DMIF`, `DCFE`, `DCFEV`, `DCO`, `XDMA`) are high-risk because values interact with runtime power management, memory P-state transitions, clock gating, and underrun behavior.
- XDMA addresses overlap with OSS-style register namespaces in other headers. Consumers must include the correct ASIC-generation header and avoid mixing DCE 11.2 addresses with unrelated OSS/DCE versions.

## Test Signals

This macro-only header is best validated by compile-time inclusion plus runtime display behavior on DCE 11.2 hardware. Useful signals include:

- A kernel build that includes DCE 11.2 display code without duplicate, missing, or mismatched register macro errors.
- Modeset smoke tests across all physical pipes using different pixel formats, scaling ratios, color-management settings, and rotation/underlay paths.
- DP and MST testing that exercises AUX transactions, MST payload allocation/status, HPD IRQ handling, unplug/replug, and link retraining.
- HDMI/DP audio tests covering stream enable/disable, format changes, sink ELD/descriptor reads, hotplug audio enable/disable interrupts, and multi-stream endpoint routing.
- FBC and stutter validation under idle, video playback, page flip, and memory-clock transition workloads, watching for underflow and visual corruption.
- Virtual/underlay plane tests that exercise `UNP`, `LBV`, `SCLV`, `BLNDV`, `DPGV`, `DMIFV`, `DCFEV`, and `CRTCV` register paths.
- Legacy VGA fallback and handoff tests for boot console, VGA disable/enable, and multi-display VGA source selection.
- Writeback/conversion tests validating `WB`/`CNV` CSC, clamp, CRC, soft reset, and warm-up programming.
- Interrupt tracing for HPD, DISP status fanout, vline/vblank, underflow, audio, and XDMA-related events to detect missed acknowledges or wrong instance offsets.
- Register-dump comparisons against known-good DCE 11.2 hardware after modeset, suspend/resume, hotplug, and power-gating transitions.

### subset-b-001521: lines 9069-10084

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h lines 9069-10084

## Scope And Purpose

This chunk is the closing section of AMDGPU's generated DCE 11.2 register address header. It contains no executable C logic; it publishes compile-time MMIO register address constants for display PHY, PLL, display PLL, and DisplayPort/clock-source transmitter blocks on ASICs using the DCE 11.2 register map.

The range starts in the middle of the COMBOPHY TX-lane table, beginning with `CMD_BUS_TX_CONTROL_LANE2` instance aliases, then covers:

- Per-lane COMBOPHY transmitter controls for lanes 0-3 across COMBOPHY TX register instances 0-7.
- Repeated `TX_DISP_RFU*` transmitter reserved/display-specific registers for RFU slots 0-12 across lanes 0-3 and instances 0-7.
- COMBOPHY common-register addresses for margin/de-emphasis nominal settings, lane power management, transmitter control, TMDS/DisplayPort support, lane resets, impedance/calibration code control, and common display RFU registers.
- COMBOPHY PLL register addresses for frequency, bandwidth, calibration, loop, debug, regulator, observe, DFT, and PLL wrapper control registers across PLL instances 0-7.
- Display PPLL register addresses for three display PLL instances.
- DPCSTX transmitter register addresses for eight DisplayPort clock-source transmitter instances.

The file path lives under a local `ceph-client` source mirror, but this chunk is AMDGPU Linux kernel display-driver hardware metadata. It does not describe Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or preprocessor conditionals in this chunk except the closing include guard. The macro namespace is the API:

- `mm<REGISTER>` names the base address for the first/default instance of a register family.
- `mmDC_COMBOPHYTXREGS<n>_<REGISTER>` names the same TX-lane register for COMBOPHY TX instance `n`, where `n` runs from 0 to 7 in this chunk.
- `mmDC_COMBOPHYCMREGS<n>_<REGISTER>` names the common COMBOPHY register for common instance `n`.
- `mmDC_COMBOPHYPLLREGS<n>_<REGISTER>` names the COMBOPHY PLL register for PLL instance `n`.
- `mmDC_DISPLAYPLLREGS<n>_<REGISTER>` names the display PLL register for display PLL instance `n`, where this table covers instances 0-2.
- `mmDPCSTX<n>_<REGISTER>` names the DPCSTX transmitter register for transmitter instance `n`, where `n` runs from 0 to 7.

The per-lane COMBOPHY TX address families include `CMD_BUS_TX_CONTROL_LANE2`, `CMD_BUS_TX_CONTROL_LANE3`, `MARGIN_DEEMPH_LANE0` through `MARGIN_DEEMPH_LANE3`, `CMD_BUS_GLOBAL_FOR_TX_LANE0` through `CMD_BUS_GLOBAL_FOR_TX_LANE3`, and `TX_DISP_RFU0_LANE0` through `TX_DISP_RFU12_LANE3`. These addresses are arranged in a regular pattern: lanes are offset by 0x10, RFU/common register slots advance by 1, and COMBOPHY instances occupy repeated address windows such as `0x48xx`, `0x49xx`, and `0x9axx` through `0x9dxx`.

The common COMBOPHY families include `COMMON_MAR_DEEMPH_NOM`, `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, `COMMON_ZCALCODE_CTRL`, and `COMMON_DISP_RFU1` through `COMMON_DISP_RFU7`. These are per-PHY common controls rather than per-lane registers.

The COMBOPHY PLL families include `FREQ_CTRL0` through `FREQ_CTRL3`, `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, `DEBUG0`, `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, `DFT_OUT`, `PLL_WRAP_CNTRL1`, and `PLL_WRAP_CNTRL`. The display PPLL families include `PPLL_VREG_CFG`, `PPLL_MODE_CNTL`, `PPLL_FREQ_CTRL0` through `PPLL_FREQ_CTRL3`, `PPLL_BW_CTRL_COARSE`, `PPLL_BW_CTRL_FINE`, `PPLL_CAL_CTRL`, `PPLL_LOOP_CTRL`, `PPLL_REFCLK_CNTL`, `PPLL_CLKOUT_CNTL`, `PPLL_DFT_CNTL`, `PPLL_ANALOG_CNTL`, `PPLL_POSTDIV`, `PPLL_DEBUG0`, `PPLL_OBSERVE0`, `PPLL_OBSERVE1`, `PPLL_UPDATE_CNTL`, `PPLL_OBSERVE0_OUT`, `PPLL_STATUS_DEBUG1`, `PPLL_DEBUG_MUX_CNTL`, `PPLL_DIV_UPDATE_DEBUG`, and `PPLL_STATUS_DEBUG0`.

The DPCSTX families include `DPCSTX_PHY_CNTL`, `DPCSTX_TX_CLOCK_CNTL`, `DPCSTX_TX_CNTL`, `DPCSTX_CBUS_CNTL`, `DPCSTX_REG_ERROR_STATUS`, `DPCSTX_TX_ERROR_STATUS`, `DPCSTX_PLL_UPDATE_ADDR`, `DPCSTX_PLL_UPDATE_DATA`, `DPCSTX_INDEX_MODE_ADDR`, `DPCSTX_INDEX_MODE_DATA`, `DPCSTX_DEBUG_CONFIG`, and `DPCSTX_TEST_DEBUG_DATA`.

## Control Flow

This chunk has no runtime control flow. Every line is a preprocessor `#define` that maps a symbolic register name to a numeric MMIO address.

Runtime control flow appears in consumer code that includes `dce_11_2_d.h`, selects an address macro for a particular PHY/PLL/transmitter instance, and performs a register read, write, or read-modify-write through AMD display register helpers. A typical flow is:

1. Select the correct instance-specific address, for example a `mmDC_COMBOPHYPLLREGS<n>_FREQ_CTRL*`, `mmDC_DISPLAYPLLREGS<n>_PPLL_*`, or `mmDPCSTX<n>_DPCSTX_*` macro.
2. Use the matching DCE 11.2 field mask/shift definitions from the companion generated mask header when only part of the register is being updated.
3. Write PHY/PLL/transmitter programming values in the order required by display bring-up, link training, clock switching, power transitions, or diagnostics.
4. Poll status/debug registers such as `OBSERVE*`, `DFT_OUT`, `PPLL_STATUS_DEBUG*`, `DPCSTX_REG_ERROR_STATUS`, or `DPCSTX_TX_ERROR_STATUS` when the hardware sequence requires confirmation.

Because this header only supplies addresses, it does not enforce safe sequencing. Ordering constraints such as disabling a transmitter before changing PLL parameters, waiting for PLL lock/update completion, resetting lanes before reprogramming PHY state, or clearing sticky DPCSTX status are owned by display-driver and firmware-facing code outside this file.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes hardware-backed state in display PHY, PLL, and DPCSTX MMIO registers.

The hardware state represented by this chunk includes COMBOPHY per-lane transmitter setup, margin/de-emphasis values, lane-global TX command state, common lane power management, common lane resets, impedance/calibration control, COMBOPHY PLL frequency/bandwidth/calibration/loop parameters, display PPLL mode/frequency/post-divider/update/debug state, and DisplayPort transmitter PHY/clock/control/error/debug/indexed-access state.

Persistence is register-specific. Some values are control settings that remain programmed until a later driver or firmware write, display link reset, PHY reset, PLL update, suspend/resume transition, power-gating transition, or full GPU reset. Other values are status or debug outputs that reflect current hardware state, and error/status registers may be sticky or clear-on-write depending on the matching hardware specification. This address header does not encode read-only, write-one-to-clear, self-clearing, reserved, or power-domain access semantics.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract. It is normally paired with the matching DCE 11.2 mask/shift header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h`, so consumers can combine address macros from this file with field masks and shifts from the companion file.

Direct include points in this source tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`

The practical integration surface is the AMD display core and power-management stack for DCE 11.2/Vega-era hardware. These address constants support display clock programming, PHY/transmitter setup, DisplayPort/HDMI link enablement, lane power/reset sequencing, PLL programming and observation, and debug/error paths. Firmware tables, BIOS/ATOM-derived transmitter settings, and hardware resource discovery can influence which instance macros are used for a particular connector and signal type.

## Risks And Edge Cases

The primary risk is silent MMIO misaddressing. A wrong address macro can compile cleanly while directing a register write to the wrong PHY, PLL, lane, transmitter, or reserved address. In display bring-up this can appear as missing output, unstable link training, wrong pixel clock, incorrect lane voltage swing/de-emphasis, spurious DPCSTX errors, or a hang during power/clock transitions.

Instance and lane repetition is the main source of human and generator-review risk. The chunk contains many near-identical definitions where only the instance number, lane number, RFU slot, or low address nibble changes. Copy or generation errors can be hard to detect by inspection and may only affect one connector mapping, one transmitter instance, or one lane width configuration.

Clock and PLL registers are high impact. Misprogramming `FREQ_CTRL*`, `BW_CTRL_*`, `CAL_CTRL`, `LOOP_CTRL`, `PPLL_FREQ_CTRL*`, `PPLL_POSTDIV`, or update/control registers can produce incorrect display clocks, failed PLL lock, jitter, or broken mode-set behavior. Some PLL fields are likely safe only under strict sequencing with disabled outputs or quiesced links.

PHY and transmitter controls are also sensitive. `MARGIN_DEEMPH_*`, `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, `DPCSTX_PHY_CNTL`, `DPCSTX_TX_CLOCK_CNTL`, and `DPCSTX_TX_CNTL` touch the physical signal path. Incorrect values can break DisplayPort link training, HDMI/TMDS output, lane powerdown, HPD-driven reconfiguration, or resume from low-power states.

Reserved/RFU and debug/DFT registers should be treated conservatively. The `TX_DISP_RFU*`, `COMMON_DISP_RFU*`, `DEBUG*`, `OBSERVE*`, `DFT_OUT`, `DPCSTX_DEBUG_CONFIG`, and `DPCSTX_TEST_DEBUG_DATA` names indicate vendor-reserved, test, or observation surfaces. Production code should avoid writing undocumented debug or RFU locations unless the ASIC programming guide or existing AMD sequence requires it.

The requested range begins mid-family, after earlier lines have already defined lane 0/1 `CMD_BUS_TX_CONTROL` entries, and it ends with the header's include guard close. The merge lane should treat the beginning split as a chunk boundary artifact rather than a real omission in the source file.

## Test Signals

Useful validation signals are mostly build-time plus display hardware behavior:

- AMDGPU builds for DCE 11.2 paths should compile with all included address macros and no missing/renamed register definitions.
- Static register-map checks can compare every address in this generated header against AMD's source register database and the companion mask/shift header.
- Display mode-set tests should validate that pixel clocks, PPLL post-dividers, and link clocks are correct across common resolutions, refresh rates, and connector types.
- DisplayPort link-training tests should cover one-, two-, and four-lane configurations, multiple transmitter instances, hotplug, retraining, suspend/resume, and low-power transitions.
- HDMI/TMDS output tests should exercise `COMMON_TMDP`, common TX controls, and PHY power/reset sequencing through real connector bring-up.
- PLL status/debug checks should confirm lock/update/status behavior through `PPLL_STATUS_DEBUG*`, `PPLL_DIV_UPDATE_DEBUG`, `OBSERVE*`, and related debug registers when available.
- DPCSTX error-path diagnostics should watch `DPCSTX_REG_ERROR_STATUS` and `DPCSTX_TX_ERROR_STATUS` during link bring-up, retraining, and forced fault scenarios.
- Multi-display tests should be included because the instance tables cover eight COMBOPHY/DPCSTX blocks and three display PLLs; errors can be instance-local and invisible on a single default connector.

Regression symptoms from bad constants include blank displays, failed hotplug recovery, modes rejected or programmed with the wrong clock, link training loops, intermittent flicker, reduced lane count or link rate, failures after suspend/resume, unexpected DPCSTX error status, or debug reads returning values from the wrong transmitter/PLL instance.

## Cross-Chunk Notes

Earlier chunks of `dce_11_2_d.h` define the beginning and middle of the DCE 11.2 display register address namespace, including preceding display controller, PHY, and lane-register families. This chunk closes the COMBOPHY TX/common/PLL, display PPLL, and DPCSTX address tables and then terminates the include guard with `#endif /* DCE_11_2_D_H */`. The final per-file research document should present the whole file as generated AMDGPU register-address metadata rather than algorithmic driver code.
