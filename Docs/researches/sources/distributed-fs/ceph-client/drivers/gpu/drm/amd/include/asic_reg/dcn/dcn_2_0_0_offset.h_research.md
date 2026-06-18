# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001603`: lines 1-2677, `Docs/researches/chunks/subset-b-001603_research.md`
- `subset-b-001604`: lines 2678-5241, `Docs/researches/chunks/subset-b-001604_research.md`
- `subset-b-001605`: lines 5242-7775, `Docs/researches/chunks/subset-b-001605_research.md`
- `subset-b-001606`: lines 7776-10411, `Docs/researches/chunks/subset-b-001606_research.md`
- `subset-b-001607`: lines 10412-12940, `Docs/researches/chunks/subset-b-001607_research.md`
- `subset-b-001608`: lines 12941-15538, `Docs/researches/chunks/subset-b-001608_research.md`
- `subset-b-001609`: lines 15539-17539, `Docs/researches/chunks/subset-b-001609_research.md`

## Chunk Research

### subset-b-001603: lines 1-2677

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 1-2677

## Scope And Purpose

This chunk is the opening section of the generated AMD DCN 2.0.0 register offset header. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The exported symbols map symbolic `mm...` register names to numeric MMIO offsets and pair each offset with an `mm..._BASE_IDX` selector that tells AMDGPU/DC register-access helpers which base-address table entry to use.

Within lines 1-2677, the header guard and AMD license are followed by 1,189 non-`BASE_IDX` register offset macros plus matching base-index macros. The visible offset range runs from `mmVGA_MEM_WRITE_PAGE_ADDR` at `0x0000` through the partial `HUBPREQ1` VM-context region ending at `mmHUBPREQ1_DC_VM_CONTEXT0_PAGE_TABLE_END_ADDR_MSB` at `0x071e`. The larger source file continues after this chunk, so this report covers only the address blocks visible in lines 1-2677.

The source tree is a Ceph-client mirror that vendors Linux AMDGPU display-driver code. This file is AMD DCN hardware register metadata, not Ceph distributed-filesystem code. Its purpose is to let DCN 2.0 display, memory-hub, interrupt, audio, writeback, and hub-pipe code use stable names rather than raw register offsets when programming display hardware.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this range. The interface is the macro namespace. Each hardware register normally appears as:

- `mmREGISTER_NAME`, the register offset in the selected register aperture.
- `mmREGISTER_NAME_BASE_IDX`, the register-base index, with this chunk using base index `0` for a few legacy/audio aperture registers, `1` for early display/VGA/DCCG offsets, and mostly `2` for DCN display-decode blocks.

Major visible address-block families are:

- Legacy VGA and VGA interface registers: `mmVGA_*`, `mmD[1-6]VGA_CONTROL`, `mmCRTC8_*`, `mmSEQ8_*`, `mmGRPH8_*`, `mmDAC_*`, `mmGEN*`, `mmATTR*`, `mmVGA_SOURCE_SELECT`, `mmVGA_SRC_SPLIT_CNTL`, and `mmMCIF_*`. These expose compatibility VGA page, render, sequencer, DAC, source-selection, memory-base, interrupt, and MCIF controls.
- DCCG, display clocks, and PLL/perfmon: `mmPHYPLL[A-F]_PIXCLK_RESYNC_CNTL`, `mmDP_DTO*`, `mmOTG[0-5]_PIXEL_RATE_CNTL`, `mmDPPCLK*`, `mmDSCCLK*`, `mmDCCG_*`, `mmDENTIST_DISPCLK_CNTL`, `mmPLL_MACRO_CNTL_RESERVED*`, and `mmDC_PERFMON0/1_*`. These define offsets for pixel-clock resync, DTO phase/modulo registers, clock-gating controls, audio DTOs, vsync latch/counter controls, soft reset, and display perf counters.
- DMU, DCPG, DMCU, and interrupt hub control: `mmRBBMIF_*`, `mmDOMAIN*_PG_CONFIG/STATUS`, `mmDCPG_INTERRUPT_*`, `mmDC_IP_REQUEST_CNTL`, `mmDMCU_*`, `mmMASTER_COMM_*`, `mmSLAVE_COMM_*`, `mmDISP_INTERRUPT_STATUS*`, `mmDC_GPU_TIMER_*`, and `mm*_INTERRUPT_DEST`. These cover display power domains, DMCU firmware/RAM/mailbox/interrupt registers, GPU timer read positions, and interrupt destination routing for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, HPD/I2C/AUX, Azalia, and DSC sources.
- Writeback, converter, scaler, and MCIF writeback: `mmWB_ENABLE`, `mmCNV_*`, `mmWB_DEBUG_*`, `mmWB_SOFT_RESET`, `mmWB_MEM_PWR_*`, `mmWBSCL_*`, `mmDC_PERFMON3_*`, and `mmMCIF_WB0_*` / `mmMCIF_WB1_*`. These offsets describe writeback enable/debug/reset/power, conversion window/source/test CRC, writeback scaler tap/ratio/init/manual-replicate settings, and two MCIF writeback buffer managers with addresses, pitches, status, arbitration, watermark, self-refresh, QoS, security, luma/chroma sizes, high address bits, and per-buffer resolution.
- MMHUBBUB and hubbub VM/return path: `mmWBIF0_*`, `mmMMHUBBUB_*`, `mmDCHUBBUB_SDPIF_*`, `mmDCN_VM_*`, `mmDCHUBBUB_RET_PATH_DCC_CFG*`, `mmDCHUBBUB_CRC*`, `mmDCHUBBUB_ARB_*`, `mmVTG[0-5]_CONTROL`, `mmDCFCLK_CNTL`, `mmDCHUBBUB_CTRL_STATUS`, and `mmDCN_VM_CONTEXT[0-15]_*`. These are the main display memory-hub offsets for VM aperture programming, local HBM aperture, pipe security levels, DCC return-path configuration, CRC readback, arbitration watermarks, self-refresh and DRAM-clock-change policy, global timer, surface-check addresses, VM context page tables, and VM fault reporting.
- Azalia/HDA audio display registers: `mmAZF0STREAM[0-15]_*`, `mmAZF0ENDPOINT[0-7]_*`, `mmAZF0INPUTENDPOINT[0-7]_*`, `mmAZALIA_*`, and `mmAZALIA_F0_*`. These cover indirect stream and codec endpoint index/data windows, controller clock/audio DTO/global capability/payload/CRC/memory power registers, root codec parameters, function controls, converter synchronization, audio port connectivity, and GTC group offsets.
- HUBP0 and the start of HUBP1 scanout fetch pipes: `mmHUBP0_*`, `mmHUBPREQ0_*`, `mmHUBPRET0_*`, `mmCURSOR0_0_*`, `mmDC_PERFMON7_*`, `mmHUBPXFC0_*`, `mmHUBP1_*`, and the first `mmHUBPREQ1_*` offsets. These expose surface config, tiling, viewport, request-size, clock/control/debug, surface pitch/address/meta-address, flip/queue/frame-pacing, in-use and earliest-in-use address latches, TTU QoS programming, per-HUBP VM aperture and context registers, cursor surface/position/DM data registers, HUBP perfmon, XFC buffer and underflow registers, and the beginning of HUBP1's equivalent request block.

## Control Flow And Data Flow

This chunk has no internal runtime control flow. Data flow is compile-time substitution: DCN 2.0 code includes this header, obtains a numeric offset and base index from a register macro pair, combines them with matching field definitions from `dcn_2_0_0_sh_mask.h`, and performs MMIO reads or writes through AMDGPU/DC helper layers.

Representative consumers in this tree include `display/dmub/src/dmub_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, `display/dc/resource/dcn20/dcn20_resource.c`, and `amdgpu/gmc_v10_0.c`. Those call sites do the actual sequencing: select a register, read or write it via register macros or generated register lists, then use the companion mask/shift header to update fields.

The address-block order also reveals intended hardware topology. Early VGA/DCCG blocks set compatibility and clocking state; DMU/DMCU/IHC blocks expose power, firmware, timer, and interrupt routing state; writeback and MCIF blocks provide capture-buffer paths; MMHUBBUB/DCHUBBUB blocks provide display memory arbitration and VM context state; HDA/Azalia blocks support display audio; HUBP/HUBPREQ/HUBPRET/CURSOR/HUBPXFC blocks program per-pipe scanout fetch, cursor, and extended-flow-control state. The header itself does not enforce this order.

## State And Persistence Behavior

The file stores no software state and performs no I/O. The mutable state represented by the constants lives in DCN 2.0 hardware registers. Writes made through these offsets may persist until a later driver write, a modeset or plane update latches new scanout state, an interrupt ack clears sticky state, a DMCU/DMUB or display firmware sequence changes state, a power-gating transition resets a block, or GPU reset/suspend/resume restores display programming.

Important state categories represented in this chunk include legacy VGA compatibility state, display clock and DTO programming, DCCG soft reset and clock gating, perf-counter control/state, display power-domain status, DMCU firmware/RAM/mailbox registers, interrupt status and destination routing, GPU timer snapshots, writeback buffer and scaler programming, MCIF writeback buffer addresses and QoS, MMHUBBUB and DCHUBBUB memory-power state, VM aperture and page-table state, DCHUBBUB watermarks and surface checks, Azalia audio stream/controller/root codec state, HUBP surface/viewport/tiling/pitch/address/flip/cursor state, and HUBP VM/fault-related programming.

Several categories are sequencing-sensitive even though the macros cannot express that. Examples include `*_SOFT_RESET`, `*_MEM_PWR_CTRL/STATUS`, `*_INTERRUPT_STATUS`, `*_INTERRUPT_DEST`, `DMCU_*` firmware/RAM access, `MCIF_WB*` buffer-manager state, `DCHUBBUB_ARB_*` watermarks, `DCN_VM_CONTEXT*` page-table programming, `DCSURF_*` surface-address and flip registers, cursor address/position registers, and writeback/XFC underflow status. Callers must know whether a target register is read-only, write-one-to-clear, latched on update, protected by update locks, or safe only while a display pipe is disabled.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_2_0_0_offset.h` for the complete DCN 2.0 register map and on `dcn_2_0_0_sh_mask.h` for field masks and shifts. It is part of a family of generated DCN headers (`dcn_1_0`, `dcn_2_0_1`, `dcn_2_1_0`, `dcn_3_*`, and later versions) with similar names but generation-specific offsets and sometimes different register coverage.

The direct include sites visible in this repository are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Primary integration surfaces are DRM/KMS modesetting, DCN 2.0 resource construction, clock-manager programming, IRQ source setup and routing, GPIO/display feature registration, DMUB/DMCU display microcontroller access, memory-controller/VM setup for display fetches, writeback capture paths, display audio setup, page-flip and cursor programming, and power-management or reset flows.

`BASE_IDX` is part of the integration contract. The same hex offset can mean a different physical register depending on the base index used by the register-access layer. For example, this chunk uses base index `0` for some legacy VGA/audio descriptor style offsets, `1` for early display decode ranges such as VGA/DCCG, and `2` for most DCN display-decode blocks. Losing or mismatching a base index can send an otherwise correct offset to the wrong aperture.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are accepted by the compiler as integers; a wrong offset or base index can still build cleanly while causing reads or writes to hit the wrong register.

Generation mismatch is a high-risk edge case. DCN 2.0, DCN 2.0.1, DCN 2.1, DCN 3.x, and older DCE/DCN generations share many names such as `mmDCCG_SOFT_RESET`, `mmDMCU_CTRL`, `mmAZALIA_CONTROLLER_CLOCK_GATING`, `mmDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A`, and `mmHUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS`, but the correct file must match the ASIC and field mask header used by the caller.

Offset/base-index errors in clock, reset, power, and VM registers can produce severe display failures: failed modesets, blank screens, underflow, hangs waiting for power/status bits, memory faults from bad page-table/aperture programming, interrupt storms or missing vblank/HPD/audio events, broken writeback capture, or failed suspend/resume.

HUBP and DCHUBBUB registers are especially sensitive because they point at scanout surfaces and govern memory fetch timing. Bad surface-address, meta-address, pitch, VM, TTU, watermark, or flip-control offsets can fetch from the wrong memory, miss a flip, report wrong in-use state, or produce underflow. Cursor and DM data offsets have similar visible failure modes for hardware cursors or DisplayPort metadata.

The chunk boundary is artificial. It starts at the file header, but it ends in the middle of the `dce_dc_dcbubp1_dispdec_hubpreq_dispdec` address block after `mmHUBPREQ1_DC_VM_CONTEXT0_PAGE_TABLE_END_ADDR_MSB_BASE_IDX`; later lines continue HUBPREQ1 and many additional DCN blocks. The final merged per-file report should not treat this chunk as a complete DCN 2.0 register map.

## Test Signals

There are no meaningful unit tests for this header chunk alone. Useful validation starts with build coverage for DCN 2.0 AMDGPU/DC configurations that include `dcn_2_0_0_offset.h` alongside `dcn_2_0_0_sh_mask.h`.

Generated-header integrity should be checked against AMD's authoritative DCN 2.0 register database or a known-good upstream Linux header. For this chunk, focus comparison on the block boundaries and base-index values for VGA/DCCG, DMU/DMCU/IHC, writeback/MCIF, MMHUBBUB/DCHUBBUB, Azalia, HUBP0, and the partial HUBP1 range.

Runtime validation signals include successful DCN 2.0 modeset and page-flip tests, stable vblank and interrupt delivery, working clock changes, no DCHUBBUB or HUBP underflow/fault status, correct writeback capture into MCIF buffers, working display audio streams and Azalia endpoint access, correct cursor movement and hot-spot behavior, valid VM aperture/page-table programming for display surfaces, and clean suspend/resume or GPU reset recovery.

Targeted diagnostics should exercise DCHUBBUB watermark programming, VM fault reporting, HUBP0/HUBP1 primary and chroma surface address flips, cursor address and position changes, DMCU/DMUB mailbox or firmware-access paths where applicable, writeback scaler/buffer-manager setup, audio DTO/stream configuration, interrupt destination routing, and perfmon counter reads for DCCG, DMU, MMHUBBUB, HDA, writeback, and HUBP blocks.

## Cross-Chunk Notes

This report covers only lines 1-2677 of `dcn_2_0_0_offset.h`. Later chunks complete HUBPREQ1 and define additional DCN 2.0 blocks. The final per-file research document should synthesize all chunk reports into one source-tree-aligned summary that treats the whole header as a generated DCN 2.0 register offset contract.

### subset-b-001604: lines 2678-5241

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 2678-5241

## Scope And Purpose

This chunk is a generated AMD DCN 2.0 register-offset map. It contains only preprocessor constants mapping symbolic display-register names to MMIO offsets plus companion `_BASE_IDX` constants. It has no functions, structs, enums, executable control flow, or local storage.

The covered range starts in the tail of the `HUBPREQ1` block and then covers most of the replicated HUBP/HUBPREQ/HUBPRET/cursor/XFC register groups for display pipes 2 through 5. It then enters the DPP register space, covering DPP0 top, converter/cursor, scaler, and color-manager blocks, DPP0 perfmon, and the beginning of the same DPP1 blocks through `mmCM1_CM_SHAPER_LUT_DATA`. The file continues after this chunk, so DPP1 and later DPP instances are incomplete here and must be reconciled with later chunk reports.

The purpose of these macros is to give DCN 2.0 Display Core code stable register addresses for plane fetch, VM/page-table display reads, cursor fetch, metadata fetch, flip timing, prefetch/watermark programming, line/read diagnostics, DPP format conversion, scaling, color management, LUT programming, CRC, and performance monitoring. This source tree is a Ceph-client mirror that includes Linux AMDGPU display code; this header is hardware register metadata rather than Ceph filesystem logic.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types. The exported interface is the macro namespace. Each `mm...` macro is a register offset and each `mm..._BASE_IDX` macro selects the DCN base segment used by register helper macros such as `SR`, `SRI`, `SRII`, `REG_READ`, `REG_WRITE`, and `REG_UPDATE`.

The HUBP/HUBPREQ/HUBPRET section includes `HUBP2` through `HUBP5`, `HUBPREQ2` through `HUBPREQ5`, `HUBPRET1` through `HUBPRET5`, `CURSOR0_1` through `CURSOR0_5`, `HUBPXFC1` through `HUBPXFC5`, and display perfmons `DC_PERFMON8` through `DC_PERFMON13`. These define per-pipe scanout surface configuration, tiling/address config, luma/chroma primary and secondary viewport registers, request-size config, HUBP control/clock/VMPG/debug registers, DCFCLK/DPPCLK measure-window controls, surface pitches, VMID selection, primary/secondary surface and meta-surface low/high address pairs, flip controls, queue/frame pacing, surface-in-use and earliest-in-use readbacks, DCN TTU/QoS and prefetch parameters, VM aperture and page-table controls, protection-fault/default-address registers, TLB control, blank/destination/timing parameters, nominal delivery parameters, per-line delivery, cursor settings, memory power control/status, HUBPRET read-line controls/status/interrupts, cursor surface and DMDATA controls, and XFC buffer/delay/underflow/slave timing/scaler/MPC controls.

The DPP0 portion defines `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and `DC_PERFMON13`. `DPP_TOP0` covers DPP enable/control, soft reset, CRC values/control, and host-read throttling. `CNVC_CFG0` covers surface pixel format, format/alpha expansion control, floating-point bias and scale, color keyer registers, and the 2-bit alpha LUT. `CNVC_CUR0` covers DPP-side cursor enable/mode/colors/FP scale-bias. `DSCL0` covers scaler coefficient RAM selection/data, scaling mode and taps, 2-tap/manual replicate controls, horizontal/vertical scale ratios and initial phases for luma/chroma, black offset, update/autocal, overscan, OTG blanking, RECOUT/MPC sizes, line-buffer format/control/counters, DSCL memory power, OBUF control, and OBUF memory power. `CM0` covers color-manager control, input CSC matrices, gamut remap matrices, bias, degamma LUT and piecewise region RAM A/B programming, alpha LUTs, 3D LUT mode/index/data/read-write controls, output CSC, output gamma, blend gamma, HDR multiplier, memory power, dealpha, coefficient format, shaper controls/LUTs, test/debug, and readback-current state.

The DPP1 portion begins the replicated instance-1 versions of the same families: `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and the start of `CM1`. It is complete through DPP1 top/CNVC/cursor/DSCL and partial for `CM1`, ending at shaper LUT index/data rather than the whole color-manager block.

## Control Flow And Data Flow

This header has no runtime control flow. Data flow is compile-time macro substitution: DCN 2.0 resource code includes `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`, expands register-list macros, and stores concrete MMIO addresses and field masks in per-block register structures.

The main integration pattern is generated-instance expansion. `display/dc/resource/dcn20/dcn20_resource.c` defines `SR` and `SRI` so a list macro such as `HUBP_REG_LIST_DCN20(id)` or `TF_REG_LIST_DCN20(id)` becomes `.FIELD = BASE(mmBLOCKid_FIELD_BASE_IDX) + mmBLOCKid_FIELD`. The constants in this chunk therefore feed instance-specific HUBP and DPP objects without the driver computing raw offsets by hand.

At runtime, higher-level DC code programs these addresses through block abstractions. HUBP code writes surface pitches, addresses, VM controls, cursor addresses, DMDATA controls, flip controls, TTU/prefetch timing, and read-line controls. DPP code writes format-conversion, scaler, color-key, CSC, degamma/gamma/blend-gamma/shaper/3D-LUT, CRC, and power-control registers. The header does not enforce sequencing; synchronization is done by callers using vblank/update locks, flip status, readback registers, waits, and Display Core state machines.

## State And Persistence Behavior

The file itself stores no mutable state and performs no I/O. The state represented by these offsets is persistent hardware state in the DCN display engine until modeset, page flip, cursor update, color-management update, power-gating transition, suspend/resume restore, GPU reset, or another register write changes it.

Important state classes in this chunk include scanout base addresses and meta-addresses for luma/chroma surfaces, per-pipe VMID and VM aperture/page-table settings, DCC/meta fetch settings, flip and queue state, surface-in-use readbacks, frame pacing, prefetch and TTU watermarks, delivery timing, cursor image and DMDATA addresses, HUBP/HUBPREQ/HUBPRET/CURSOR/DSCL/CM memory power state, scaler coefficients and geometry, DPP input format/alpha/color-key state, cursor palette/control state in CNVC, color matrices, degamma/blend-gamma/shaper/3D LUT RAM contents, HDR multiplier/dealpha state, DPP CRC state, and perfmon counters.

Several represented registers are synchronization-sensitive. Surface address low/high pairs, meta-address pairs, cursor address pairs, DMDATA address pairs, flip controls, surface-in-use readbacks, `DSCL_UPDATE`, LUT index/data/write-enable triplets, RAM A/B piecewise gamma regions, memory power control/status pairs, and HUBPRET read-line status require caller-side ordering. The constants do not prevent partially updated address pairs, stale LUT banks, or writes while a block is powered down.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_2_0_0_offset.h` for a complete include-guarded DCN 2.0 register map and on `dcn_2_0_0_sh_mask.h` for bitfield shifts and masks. It is consumed by DCN 2.0 display resource construction, especially `display/dc/resource/dcn20/dcn20_resource.c`, and by register-list declarations in `display/dc/hubp/dcn20/dcn20_hubp.h` and `display/dc/dpp/dcn20/dcn20_dpp.h`.

Integration surfaces include DRM/KMS plane programming, GPU memory scanout through HUBP, VM/page-table display reads, cursor and DMDATA programming, page-flip timing and interrupt handling, Display Mode Library-derived prefetch/watermark/TTU programming, HUBP read-line diagnostics, XFC underflow/status handling, DPP scaler programming, format conversion, color keying, color-management pipelines, HDR and blend-gamma programming, CRC diagnostics, per-block memory power management, and display performance monitoring.

AMDGPU memory-controller code also reads related HUBP/HUBPREQ viewport and pitch registers when estimating active display memory use. That makes the offsets part of both display programming and memory-management diagnostics for DCN-era ASICs.

## Risks And Edge Cases

The main risk is silent hardware misprogramming if any generated offset or base index is wrong. These are integer constants; a wrong value can still compile while programming the wrong pipe, wrong color block, or unrelated register.

This range contains heavily replicated but instance-specific address families. HUBP instance offsets, cursor instance names such as `CURSOR0_5`, perfmon numbering, and DPP/CM register spacing must match the hardware database exactly. Generic code that assumes a single stride across HUBP, HUBPREQ, HUBPRET, cursor, XFC, perfmon, DSCL, and CM blocks can be fragile.

Address-pair and LUT-indexed registers are especially sensitive. Surface, metadata, cursor, DMDATA, and XFC buffer addresses have low/high or LSB/MSB halves. Degamma, blend-gamma, shaper, and 3D LUT paths use index/data/write-enable registers and RAM A/B banked region programming. Programming only part of a pair or switching banks/indexes at the wrong time can cause corrupted scanout, wrong colors, GPUVM faults, cursor corruption, or hangs in display fetch.

Power and timing registers are high-impact. Incorrect HUBP/HUBPREQ/HUBPRET/CURSOR/DSCL/CM memory power control, TTU/QoS/prefetch values, vblank/flip/nominal delivery parameters, or read-line programming can cause display underflow, missed flips, unstable vblank timing, blank screens, bad suspend/resume restore, or diagnostic counters that appear valid but reflect the wrong block.

The chunk starts after the beginning of `HUBPREQ1` and ends before the end of the DPP1 color-manager register map. The final merged report should treat those two edge blocks as partial in this chunk rather than complete descriptions of pipe 1 or DPP1.

## Test Signals

There are no unit tests for this header chunk alone. The first validation signal is build coverage for DCN 2.0 AMDGPU/DC configurations that include both `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`, especially `dcn20_resource.c`, `dcn20_hubp.h`, `dcn20_dpp.h`, and code using `HUBP_REG_LIST_DCN20` and `TF_REG_LIST_DCN20`.

Generated-header integrity should be checked against the authoritative DCN 2.0 register database or a known-good upstream header. Comparisons should focus on instance replication for HUBP2-HUBP5, HUBPREQ2-HUBPREQ5, cursor blocks, XFC blocks, DPP0/DPP1, CM LUT region sequences, `_BASE_IDX` values, and all low/high address-pair registers.

Runtime test signals include successful modesets using multiple pipes, correct page flips and flip-completion timing, stable cursor movement and DMDATA updates, no display underflows, no GPUVM/protection-fault reports from display fetch, correct surface pitch/address/readback behavior, correct scaler output with luma/chroma scaling, correct color conversion/gamut/degamma/blend-gamma/shaper/HDR behavior, stable suspend/resume, and correct memory power transitions.

Diagnostic validation should exercise DPP CRC readback, performance counter readback for the covered perfmon instances, HUBPRET read-line status, surface-in-use and earliest-in-use readbacks, XFC underflow status, LUT programming and bank switching, and stress tests that flip between compressed/uncompressed or luma/chroma surfaces. These signals catch offset and instance-selection mistakes that normal compilation cannot detect.

### subset-b-001605: lines 5242-7775

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 5242-7775

## Scope And Purpose

This chunk is a generated AMD DCN 2.0.0 register-offset header fragment. It contains preprocessor constants only: no C functions, structs, enums, variables, executable control flow, or direct I/O. The exported values map symbolic DCN display-engine register names to MMIO register offsets, with a matching `<REGISTER>_BASE_IDX` macro for the register-base segment used by AMDGPU/DC register helpers.

The source path is under a local `ceph-client` source mirror, but this file is part of the Linux AMDGPU display driver. It does not implement Ceph filesystem behavior. Its job is hardware ABI metadata for DCN 2.0-class display hardware, especially DPP pipes 1-3 and MPC/MPCC color-compositing/output-gamma blocks.

This line range spans 2,534 physical lines and 2,418 `mm*` macro definitions. It starts in the middle of the DPP1 color-management block, at `mmCM1_CM_SHAPER_LUT_WRITE_EN_MASK`, after the previous chunk's CM1 blend-gamma and shaper setup registers. It then covers:

- The tail of `CM1` shaper LUT, shaper RAM A/B region, memory-power, 3D LUT, and CM debug offsets.
- DPP1 perfmon instance `DC_PERFMON14`.
- Full DPP2 and DPP3 top, converter/cursor, scaler, color-management, and perfmon offset groups.
- MPC MPCC instance offsets for `MPCC0` through `MPCC7`.
- MPC output mux offsets for `MPC_OUT0` through `MPC_OUT5`.
- MPC global config, CRC, clock/reset, update/ack/status, stall, and perfmon event-control offsets.
- MPCC output-gamma RAM offsets for `MPCC_OGAM0` through `MPCC_OGAM5`.
- The beginning of `MPCC_OGAM6`, ending at `mmMPCC_OGAM6_MPCC_OGAM_RAMA_REGION_20_21`.

The chunk ends mid-address-block. The rest of `MPCC_OGAM6` and later `MPCC_OGAM7` offsets are in the next file chunk.

## Important APIs, Types, And Macros

There are no callable APIs or C type definitions here. The interface is the generated macro namespace:

- `mm<REGISTER>` gives the DCN 2.0 register offset.
- `mm<REGISTER>_BASE_IDX` gives the base segment index to combine with the offset.
- All macros in this chunk use `BASE_IDX` value `2`, which corresponds to the DCN base segment used by consumers through `BASE(mm..._BASE_IDX)`.

Important macro families:

- `mmCM1_CM_SHAPER_*`, `mmCM1_CM_3DLUT_*`, `mmCM1_CM_MEM_PWR_*`, and `mmCM1_CM_TEST_DEBUG_*` finish the color-management register set for DPP pipe 1. These cover shaper LUT access, split RAM A/B piecewise-linear regions, 3D LUT mode/index/data/control, output normalization/offsets, CM memory-power controls/status, and debug index/data.
- `mmDPP_TOP2_*` and `mmDPP_TOP3_*` define DPP top-level control, soft reset, CRC result/control, and host-read offsets for DPP instances 2 and 3.
- `mmCNVC_CFG2_*` and `mmCNVC_CFG3_*` define surface pixel format, format conversion, floating-point conversion bias/scale, color keyer, and alpha 2-bit LUT offsets. `mmCNVC_CUR2_*` and `mmCNVC_CUR3_*` define cursor control and two cursor color registers.
- `mmDSCL2_*` and `mmDSCL3_*` define scaler offsets: OTG blanking windows, mode, memory power, line-buffer format/control, autocalibration, black offsets, tap controls, coefficient RAM access, 2-tap control, MPC size, scale ratios, phase init, recout start/size, OBUF power/status, and DSCL debug index/data.
- `mmCM2_*` and `mmCM3_*` define the full DPP color-management sets for pipes 2 and 3: gamut remap A/B matrices, input CSC A/B matrices, degamma RAM A/B regions, degamma LUT access/control, CM control, blend-gamma RAM A/B regions, HDR multiplier, dealpha/coefficient format, shaper LUT/RAM, 3D LUT, memory power/status, and CM debug.
- `mmDC_PERFMON14_*`, `mmDC_PERFMON15_*`, and `mmDC_PERFMON16_*` define DPP-local perf counter control, state, current value, high/low counter, and perfmon control offsets.
- `mmMPCC0_*` through `mmMPCC7_*` define MPCC blend/composition offsets: control, top/bottom gain, output size, status, background color components, memory power control/status, mux control, opacity, and SM control.
- `mmMPC_OUT0_MUX` through `mmMPC_OUT5_MUX` define the output mux registers that connect MPCC trees to output processors.
- `mmMPC_*` defines MPC-wide host read, CRC control/results/selection, clock control, soft reset, update acknowledge/status, stall grace window, underflow, idle status, and perfmon event control offsets.
- `mmMPCC_OGAM0_*` through `mmMPCC_OGAM5_*`, plus the first part of `mmMPCC_OGAM6_*`, define MPC output-gamma LUT mode/index/data/control and RAM A/B piecewise-linear start, slope, end, and region offsets.

## Control Flow And Data Flow

This header chunk has no internal runtime control flow. Data flow is compile-time substitution into AMDGPU/DC register tables and MMIO helper calls.

The main inclusion pattern appears in DCN20 code such as `display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dmub/src/dmub_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, and `amdgpu/gmc_v10_0.c`. `dcn20_resource.c` includes both `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`, then defines helpers such as `SR(reg_name)` and `SRI(reg_name, block, id)` that compute absolute register addresses as `BASE(mm..._BASE_IDX) + mm...`.

For DPP registers, `display/dc/dpp/dcn20/dcn20_dpp.h` builds `TF_REG_LIST_DCN20` out of names from this chunk. That list is expanded in resource construction to initialize per-pipe transform/DPP register structs. Runtime functions in `dcn20_dpp.c` then use register-helper macros such as `REG_GET`, `REG_UPDATE`, `REG_SET_2`, and `REG_GET_2` against those tables. Concrete examples include reading `CM_SHAPER_CONTROL`, `CM_3DLUT_READ_WRITE_CONTROL`, `CM_3DLUT_MODE`, and `CM_BLNDGAM_LUT_WRITE_EN_MASK` in `dpp20_read_state()`, powering DPP memory through `CM_MEM_PWR_CTRL`, `OBUF_MEM_PWR_CTRL`, and `DSCL_MEM_PWR_CTRL` in `dpp2_power_on_obuf()`, and programming converter/scaler state through `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `SCL_MODE`, `DSCL_CONTROL`, scale ratios, tap controls, and recout registers.

For MPC/MPCC registers, DC MPC headers and implementations use the same generated-address pattern. `dcn10_mpc.h` and `dcn20_mpc.h` define register lists for `MPCC_CONTROL`, `MPC_OUT_MUX`, and `MPCC_OGAM` instances, while MPC runtime code uses the resulting register arrays to program MPCC blend mode, alpha mode, global alpha/gain, output mux selection, MPCC status, and output-gamma LUT behavior.

No sequencing is encoded by these macros. The ordering lives in the display core and hardware sequencing code that consumes the register tables: modeset programming, plane enable/disable, scaler setup, color pipeline programming, MPCC tree assembly, output mux selection, CRC/debug access, and power-management transitions.

## State And Persistence Behavior

This chunk stores no software state and performs no I/O. It names mutable DCN hardware registers. Runtime state represented by these offsets includes:

- DPP color state: shaper LUT contents, 3D LUT contents/configuration, blend-gamma and degamma RAM regions, gamut remap matrices, input CSC matrices, HDR multiplier, dealpha/coefficient format, and debug selector/data state.
- DPP conversion and scaling state: pixel format, fixed/float conversion bias and scale, color keyer values, alpha LUT, cursor control/color, scaler mode, line-buffer format, coefficient RAM, tap counts, scale ratios, phase initialization, recout window, black offsets, and OTG blanking data.
- DPP and CM power state: shared CM memory power controls/status, DSCL LUT memory power, and OBUF memory power controls/status.
- DPP diagnostics: DPP CRC values/control, DC perfmon counters, scaler/color-management debug index/data registers, and host-read controls.
- MPC/MPCC composition state: MPCC blend mode, alpha blend/multiplied mode, overlap-only behavior, global alpha/gain, top/bottom gain, background color/depth, output size, mux control, opacity, MPCC memory power/status, and SM control.
- MPC-wide state: output mux routing, CRC control/results/selection, update acknowledge/status, clock/reset state, underflow, stall grace window, idle status, and perfmon event control.
- MPCC OGAM state: output-gamma mode, LUT bank/index/data/control, RAM A/B piecewise-linear start/slope/end/region definitions, and the partially covered OGAM6 RAM A range.

Persistence is hardware-defined and not declared in this offset header. Some registers hold programmed mode state until a subsequent modeset, color update, power transition, suspend/resume, GPU reset, or another driver write. Others are live status, sticky status, debug selector/data windows, counters, self-clearing update/acknowledge paths, or read-only hardware state. Names such as `*_STATUS`, `*_PWR_STATUS`, `*_UPDATE_ACK*`, `*_PENDING_TAKEN_STATUS*`, `*_CRC_RESULT*`, `*_PERFCOUNTER_STATE`, `*_SOFT_RESET`, and `*_HOST_READ_CONTROL` indicate likely access semantics, but side effects and clear behavior come from hardware documentation and the matching field masks, not from this file.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_2_0_0_offset.h` for the full include-guarded generated header and on `dcn_2_0_0_sh_mask.h` for field masks and shifts. It is also coupled to DCN 2.0 hardware documentation, SoC base-address headers such as `navi10_ip_offset.h`, and the AMD display `reg_helper` macros.

Direct include consumers found in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Important indirect consumers include DCN20 DPP code (`dcn20_dpp.h` and `dcn20_dpp.c`), common DPP/scaler code inherited from DCN10, and MPC/MPCC code (`dcn10_mpc.*`, `dcn20_mpc.*`) that assembles MPCC trees and output-gamma state.

Practical integration surfaces are DRM/KMS atomic modesets, plane composition, scaling, color management, cursor setup, per-plane and output CRC/debug readback, DC perfmon sampling, underflow detection, output mux routing, power gating/light sleep, suspend/resume reinitialization, DMUB register access, IRQ service mapping, and GPU memory/display interactions on DCN 2.0 ASICs.

## Risks And Edge Cases

- These constants are hardware ABI. An incorrect offset or base index can compile cleanly while reading or writing the wrong hardware register.
- The chunk starts and ends inside larger register families. CM1 shaper state depends on previous-chunk offsets, and OGAM6 is incomplete until the next chunk. Final synthesis should join these boundaries before treating either family as complete.
- Repeated per-instance names are easy to confuse. `CM2` versus `CM3`, `DSCL2` versus `DSCL3`, `MPCC5` versus `MPC_OUT5`, and `MPCC_OGAM5` versus `MPCC_OGAM6` differ only by instance number but target different hardware blocks.
- Base-index pairing matters. Consumers combine `mm..._BASE_IDX` with `mm...`; using a register offset without its generated base segment can address the wrong MMIO aperture.
- DPP color LUT programming is order-sensitive. Shaper, 3D LUT, degamma, blend-gamma, RAM A/B region, LUT index/data, and write-enable/control registers must be sequenced with the field masks from `dcn_2_0_0_sh_mask.h`.
- Scaler and format registers are packed and format-sensitive. Incorrect CNVC/DSCL offsets can produce bad pixel formats, broken cursor colors, incorrect scaling ratios or phase, line-buffer issues, or visual corruption without an obvious crash.
- Power-control offsets affect live display hardware. Misprogramming CM, DSCL, OBUF, or MPCC memory power controls can create black screens, hangs waiting for power-status fields, or resume failures.
- MPC/MPCC routing mistakes are high impact. Wrong MPCC control, mux, update-ack/status, or output mux offsets can attach planes to the wrong output, lose planes, leave stale composition state, or break atomic update synchronization.
- Diagnostics can mask functional issues. CRC, perfmon, debug, host-read, underflow, and idle-status offsets may only be exercised by debugfs or validation tooling, so regressions can escape normal display smoke tests.
- Generated repetition makes manual review brittle. The safest validation is comparison against an authoritative generated DCN 2.0.0 header rather than hand-inspecting every copied offset.

## Test Signals

Validation is mainly compile-time plus hardware behavior:

- Build AMDGPU/DC configurations with DCN 2.0 support enabled. Missing or renamed offsets should fail consumers in `dcn20_resource.c`, `dcn20_dpp.h`, DPP runtime code, MPC/MPCC code, DMUB DCN20 code, IRQ service code, GPIO factory code, clock manager code, and GMC code.
- Compare this range against a known-good upstream `dcn_2_0_0_offset.h` or the authoritative ASIC register database. Focus on instance numbering and offsets for `CM1` tail, DPP2/DPP3, `MPCC0-7`, `MPC_OUT0-5`, MPC global registers, and `MPCC_OGAM0-6`.
- Exercise DCN20 hardware with multiple planes and multiple pipes: plane enable/disable, blending, global alpha, premultiplied alpha, cursor updates, scaling, color keying, and output mux changes.
- Exercise color-management paths: degamma, shaper LUT, 3D LUT, blend/output gamma, gamut remap, HDR multiplier, input CSC, output gamma through MPCC OGAM, LUT bank selection, RAM A/B switching, and suspend/resume after color state is programmed.
- Exercise scaler and converter paths with RGB/YUV formats, 4:2:0 surfaces, scaling up/down, odd source sizes, different tap counts, cursor formats, and recout windows.
- Check power-management transitions around active streams: CM memory power, DSCL LUT memory power, OBUF memory power, MPCC memory power, clock/soft reset, idle status, and resume reprogramming.
- Use CRC/perfmon/debug signals where available: DPP CRC values, MPC CRC results, DC perfmon counters, underflow status, MPCC status, and debug index/data reads can catch wrong offsets that simple modesets miss.
- Watch user-visible regressions: black screen, missing plane, wrong output routing, corrupted scaling, incorrect gamma/color, cursor artifacts, underflow logs, failed page flips, hangs in register waits, or display loss after suspend/resume.

### subset-b-001606: lines 7776-10411

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 7776-10411

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register-offset metadata. It contains no executable C logic. Its purpose is to publish compile-time MMIO register addresses and register base-index selectors for display-core code that programs DCN 2.0 hardware blocks.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The range covers a large display-pipeline section:

- Tail of `MPCC_OGAM6` and full `MPCC_OGAM7` output-gamma LUT/register windows.
- MPC output color-space-conversion register banks for six outputs plus OCSC debug and MPC perfmon 12.
- OPP/formatter/display-pattern/OPP-buffer/OPP-pipe/OPP-pipe-CRC register instances 0 through 5, plus OPP top, DSCRM 0 through 5, and OPP perfmon 18.
- ODM input register instances 0 through 5.
- OTG timing-generator register instances 0 through 5.
- OPTC miscellaneous, ODM memory power, and OPTC perfmon 19 registers.
- DIO global I2C/DDC engine registers, DIO scratch/power/clock/interrupt registers, and the beginning of HPD0 interrupt registers.

Every hardware register macro appears with a companion `_BASE_IDX` macro. In this chunk almost every `_BASE_IDX` is `2`, which selects the register aperture/base used by the generated AMD register access tables.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated preprocessor naming contract:

- `mm<block>_<register>` gives the register offset used by AMDGPU/DC register access helpers.
- `mm<block>_<register>_BASE_IDX` gives the register base-table index used with that offset.
- Matching bit masks, shifts, and field-value definitions live in the corresponding `dcn_2_0_0_sh_mask.h` and enum headers.

Important macro families in this chunk:

- `mmMPCC_OGAM6_*` and `mmMPCC_OGAM7_*`: output-gamma programming windows for MPCC instances. They define LUT index/data/control registers, mode registers, and RAM A/RAM B per-channel start/slope/end/region registers for blue, green, and red channels. The range begins inside the `MPCC_OGAM6` RAMA/RAMB region list and then covers full `MPCC_OGAM7`.
- `mmMPC_OUT*_CSC_*`: output CSC mode and coefficient registers for MPC outputs 0 through 5. Each output has A and B coefficient banks with packed coefficient pairs such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`, plus global `MPC_OUT_CSC_COEF_FORMAT` and OCSC test-debug index/data registers.
- `mmDC_PERFMON12_*`, `mmDC_PERFMON18_*`, and `mmDC_PERFMON19_*`: display performance counter control, state, current-value interrupt/misc, high, and low counter registers for MPC, OPP, and OPTC-related monitor blocks.
- `mmBL1_PWM_*`: backlight/PWM control, period/counter, current/target duty cycle, group registers, user-level/ABM registers, and gamma/lookup-table index/data registers.
- `mmFMT[0-5]_*`: per-OPP formatter clamp, dynamic expansion, format control, bit-depth, dither random seeds, stereo, 4:2:0 memory control, and 4:2:2 control registers.
- `mmDPG[0-5]_*`: display pattern generator control, ramp, dimensions, RGB/YUV color, offset segment, and status registers.
- `mmOPPBUF[0-5]_*`: OPP buffer control and 3D parameter registers.
- `mmOPP_PIPE[0-5]_*` and `mmOPP_PIPE_CRC[0-5]_*`: per-pipe control and CRC control/mask/result registers used for output validation and diagnostics.
- `mmDSCRM[0-5]_*`: per-output descrambler control registers.
- `mmODM[0-5]_*`: OPTC input controls for data source selection, format, bytes per pixel, width, clock control, memory configuration, and spare registers.
- `mmOTG[0-5]_*`: large per-timing-generator banks covering horizontal/vertical totals, blanking and sync windows, variable refresh totals, triggers, flow control, interlace, readback, status counters, update locks, master enable, blank/black colors, vertical interrupts, CRC windows/results/masks, global sync lock/update controls, GSL windows, DRR, DSC start position, pipe update status, and spare registers.
- `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, `mmODM_MEM_PWR_*`, and `mmOPTC_MISC_SPARE_REGISTER`: OPTC-wide source, clock, memory-power, status, and spare controls.
- `mmDC_I2C_*`: global DC I2C/DDC control, arbitration, interrupt, status, six DDC channel status/speed/setup pairs, transaction descriptors, data, VGA DDC setup, EDID-detect, and read-request interrupt registers.
- `mmDIO_*`, `mmDCE_VCE_CONTROL`, and `mmDIG_SOFT_RESET`: DIO scratch registers, DIO memory power/clock controls, power-management control, DIG reset, HDMI RX status timer, PSP/generic interrupt status/clear/message registers.
- `mmHPD0_DC_HPD_INT_STATUS` and `mmHPD0_DC_HPD_INT_CONTROL`: first hotplug-detect block interrupt status/control entries. The remainder of HPD0 continues after this chunk.

## Control Flow

This chunk has no runtime control flow. It is declarative register-address metadata consumed by C code through generated register tables and helper macros such as `SR`, `SRI`, `SRI_ARR`, `SRII`, `REG_READ`, `REG_SET`, `REG_UPDATE`, and `REG_GET`.

Representative runtime flows in local consumers:

- `display/dc/resource/dcn20/dcn20_resource.c` includes `dcn_2_0_0_offset.h` and uses these offsets to populate DCN20 resource register tables for MPC, OPP, OPTC, I2C, GPIO, clock, and DMUB-related blocks.
- `display/dc/mpc/dcn20/dcn20_mpc.h` maps `MPCC_OGAM_MODE` as an indexed `MPCC_OGAM` register, and `display/dc/mpc/dcn20/dcn20_mpc.c` writes `MPCC_OGAM_MODE[mpcc_id]` while enabling, disabling, or selecting output gamma modes.
- `display/dc/optc/dcn10/dcn10_optc.h` and related DCN OPTC code map `OTG_H_TOTAL` and `OPTC_INPUT_GLOBAL_CONTROL`; `dcn10_optc.c` writes timing values, reads timing-generator state, checks underflow status, and clears underflow using fields in the matching mask header.
- `display/dc/opp/dcn20/dcn20_opp.c` reads `OPP_PIPE_CRC_CONTROL` into debug/state snapshots, while generic DCE/OPP code programs formatter clamps, dithering, bit depth, and CRC capture through the per-OPP registers defined here.
- `display/dc/dce/dce_i2c_hw.c` drives hardware DDC transactions through `DC_I2C_CONTROL`, transaction descriptors, `DC_I2C_DATA`, status, speed/setup, reset, and arbitration registers.
- `display/dmub/src/dmub_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include this offset header for DCN20 device-service, IRQ, GPIO, and clock/resource integration.

Because this header only supplies constants, it does not enforce sequencing. Consumers must order operations around OTG update locks and double-buffering, MPC/MPCC gamma RAM access, OPP CRC windows, I2C arbitration and soft reset, ODM memory power control, DIO power/clock controls, and HPD interrupt status/ACK behavior.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe hardware MMIO state.

The represented hardware state spans:

- Gamma/color state in MPCC output gamma LUTs and MPC output CSC coefficient banks.
- Output formatting state in FMT clamp, expansion, bit-depth, dither, 4:2:0, 4:2:2, stereo, and OPP buffer controls.
- Test/diagnostic state in DPG generators, OPP pipe CRC windows/results, MPC/OPP/OPTC perfmon counters, and OTG CRC/readback/status registers.
- Timing-generator state in OTG horizontal and vertical totals, blanking, sync, trigger, interlace, VRR/DRR, global sync lock, update-lock, vertical interrupt, DSC, and pipe-update registers.
- Routing and output-combiner state in ODM input source/format/width/clock/memory registers and OPTC source-selection controls.
- Connector sideband state in DC I2C/DDC engine arbitration, status, transactions, speed/setup, EDID detect, and read-request interrupt registers.
- DIO global state in scratch registers, memory power state, clock controls, DIG soft reset, PSP/generic interrupt registers, and HPD0 interrupt status/control.

Persistence is hardware-specific and not encoded in this file. Some registers are durable programming knobs that remain until modeset, reset, suspend/resume, power-gating transition, or an explicit rewrite. Other registers are read-only status, counters, sticky interrupt status, write-one-to-clear controls, self-clearing requests, or double-buffered values latched at vertical update boundaries. The names hint at behavior (`*_STATUS`, `*_CLEAR`, `*_INT_STATUS`, `*_UPDATE_LOCK`, `*_COUNT_RESET`, `*_SOFT_RESET`, `*_MEM_PWR_STATUS`), but access type, reset value, and side effects require the matching hardware register specification and mask headers.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract for DCN 2.0. It is meaningful together with:

- `dcn_2_0_0_sh_mask.h` for field masks and shifts.
- DCN 2.0 enum/value headers for symbolic register field values.
- AMD display register-access helper macros and per-block register-table structures in `drivers/gpu/drm/amd/display/dc`.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration points are DCN20 resource construction, modeset timing programming, ODM/OPTC routing, multi-display synchronization, output gamma and output CSC programming, DRM color-management application, formatter/dither/bit-depth setup, OPP/OTG CRC validation, underflow detection/clear, display perfmon sampling, EDID/DDC transactions, HPD interrupt handling, DIO power/clock/reset management, and debug state collection.

## Risks And Edge Cases

- Numeric offsets are hardware ABI. A wrong offset or base index can compile cleanly while writing the wrong register block, corrupting unrelated display state, or hanging display hardware.
- The chunk boundary is not semantic. It starts inside the `MPCC_OGAM6` RAM region list and ends immediately after HPD0 interrupt status/control, so readers must merge adjacent chunks for complete MPCC6 and HPD0 coverage.
- Instance-indexed families are highly repetitive. Manual edits to `FMT[0-5]`, `DPG[0-5]`, `OPPBUF[0-5]`, `ODM[0-5]`, `OTG[0-5]`, or `MPC_OUT[0-5]` can introduce off-by-one instance drift that affects only some pipes.
- MPCC OGAM and MPC output CSC registers are color-critical. Bad addresses or mismatched masks can cause wrong gamma, color-space conversion errors, visible banding, or incorrect HDR/SDR output transforms.
- OTG registers are timing-critical. Incorrect `OTG_H_TOTAL`, blanking, sync, update-lock, global-sync, DRR, or DSC start-position offsets can produce black screens, flicker, lost vblank, invalid frame pacing, or multi-display synchronization failures.
- ODM/OPTC state is routing-critical. Wrong source, format, width, clock, memory-power, or underflow-clear registers can break multi-pipe combine/split paths or hide real underflow diagnostics.
- I2C/DDC registers interact with external displays. Arbitration, reset, transaction-count, DDC select, data, and speed/setup mistakes can cause EDID read failures, hotplug instability, or stalled sideband transactions.
- Status, clear, reset, and interrupt registers have side effects not visible in this offset header. Consumers must rely on the matching mask headers and hardware docs to avoid clearing sticky state or triggering resets accidentally.
- This generated header is shared by many display modules. Renaming or moving macros without updating register-table users produces build failures; changing values without regeneration can produce runtime-only regressions that tests may miss unless run on DCN20 hardware.

## Test Signals

Useful validation is compile-time plus hardware/display behavior:

- Build AMDGPU/DC with DCN20 support enabled; missing or renamed macros should fail in DCN20 resource, MPC, OPP, OPTC, I2C, GPIO, IRQ, DMUB, and clock-manager paths.
- Diff generated offsets against adjacent DCN families such as `dcn_2_0_1_offset.h`, `dcn_2_1_0_offset.h`, and `dcn_3_0_0_offset.h` to catch unintended instance or base-index drift where hardware is expected to remain compatible.
- Exercise modesets on DCN20 hardware across all available pipes: single display, multi-display, ODM/split scenarios, blank/unblank, suspend/resume, and hotplug cycles.
- Validate timing behavior: vblank/vline delivery, frame counters, update-lock behavior, global sync lock, DRR/VRR changes, DSC start positioning where supported, and absence of underflow after mode changes.
- Validate color/output programming: output gamma LUT changes, output CSC changes, formatter clamp/bit-depth/dither settings, 4:2:0/4:2:2 output modes, and visible color correctness across SDR/HDR-style configurations.
- Validate diagnostics: OPP pipe CRC results, OTG CRC windows/results, MPC/OPP/OPTC perfmon reads, pattern generator output, and debug register snapshots.
- Validate connector sideband behavior: EDID reads through DDC1-DDC6, I2C soft reset/retry paths, read-request interrupts, HPD0 connect/disconnect interrupt status and control, and DIO power/clock transitions.
- Watch negative signals in kernel logs and display behavior: black screens, stuck modesets, missed vblank/page-flip completion, underflow messages, HPD flapping, EDID failures, color shifts, CRC mismatches, display clock/power transition failures, or resume failures.

### subset-b-001607: lines 10412-12940

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 10412-12940

## Scope And Purpose

This chunk is a generated AMD DCN 2.0 register-offset header slice. It contains preprocessor constants only: no functions, structs, enums, variables, allocation, locking, or executable control flow. The constants define MMIO register offsets and their generated `_BASE_IDX` selector values for DCN 2.0 display I/O, hotplug, AUX, stream encoder, DisplayPort, DCIO, GPIO/DDC, panel power/backlight, and the beginning of UNIPHY0 macro-control space.

The source tree path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The requested range contains 2,421 `#define` entries: 1,211 register-offset macros and 1,210 matching `_BASE_IDX` macros. It covers 27 generated `addressBlock` comments. The range starts in the middle of `dce_dc_dio_hpd0_dispdec`, with `mmHPD0_DC_HPD_CONTROL` through `mmHPD0_DC_HPD_TOGGLE_FILT_CNTL`, and ends in the middle of `dce_dc_dcio_dcio_uniphy0_dispdec`, at `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10`.

Major address-block families in this chunk:

- HPD blocks `HPD0` through `HPD5` for display hotplug detect status, interrupt control, HPD line control, fast training, and toggle filtering.
- `DC_PERFMON20` display performance counter control, state, current-value, high, and low registers.
- `DP_AUX0` through `DP_AUX5` for AUX/I2C-over-AUX controller control, arbitration, software and link-service data/status, DPHY TX/RX controls/status, GTC sync, and PHY wake control.
- `DIG0` through `DIG5` stream-encoder front/back-end and HDMI/AFMT register groups for CRC, HDMI packet controls, infoframes, ACR, audio packets, generic metadata packets, 60958 channel-status words, TMDS controls, AFMT CRC/ramp/status, and force-disable controls.
- `DP0` through `DP5` DisplayPort register groups for link control, pixel/MSA configuration, stream timing, training patterns, DPHY/CRC/scrambling, secondary data packets, audio M/N, MST/MSE allocation/status, MSO, DSC, ALPM, metadata, and double-buffer control.
- DCIO global register groups for generic DC registers, UNIPHY A-F link and channel-crossbar controls, write-command delay, pinstraps, LVTMA panel power sequencing, backlight PWM, genlock/swaplock pads, DCIO clock/reset, and AUX impedance calibration.
- DCIO chip/GPIO groups for generic GPIO, DDC1-DDC6, DDCVGA, genlock, HPD, power-sequence GPIOs, pad strength, AUX controls, RX/pullup enables, and AUX/I2C pad power-good.
- The first 11 `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED<N>` offsets, with their base indices.

## Important APIs, Types, And Macros

There are no callable APIs or C type definitions in this chunk. The exported interface is the generated macro namespace:

- `mm<REGISTER>` gives a register offset in the DCN 2.0 address space.
- `mm<REGISTER>_BASE_IDX` gives the generated base-index selector used by AMDGPU/DC register helper macros to add the correct IP block base.
- Repeated instance names such as `HPD3`, `DP_AUX4`, `DIG2`, and `DP5` identify hardware instances, not C objects.

Important macro families:

- `mmHPD<N>_DC_HPD_*` registers are the hotplug-detect interface used for connector plug/unplug and HPD RX style events. `HPD1` through `HPD5` include status and interrupt-control offsets in this range; `HPD0` status/control begins in the previous chunk, while this chunk contains the latter part of its control group.
- `mmDC_PERFMON20_*` gives one display performance-monitor block with counter control, state, current-value interrupt/misc, high, and low registers.
- `mmDP_AUX<N>_AUX_*` registers are per-AUX-channel controller offsets. They include software control/data/status, arbitration and interrupt control, low-speed data/status, DPHY TX/RX programming and readback, global time counter sync controls/status, and PHY wake control.
- `mmDIG<N>_*` registers represent each digital stream encoder's HDMI/AFMT/TMDS-facing register set. The names cover HDMI metadata and generic-packet controls, ACR values and readback, audio packet controls, AFMT infoframes and generic data slots, IEC 60958 words, CRC controls/results, TMDS pattern/balancer controls, DIG version/lane enable, and force-disable.
- `mmDP<N>_DP_*` registers represent each DisplayPort stream/link block. The names cover link framing, pixel format, MSA colorimetry/timing/VBID, video M/N, DPHY lane training, PRBS/scrambling/CRC, secondary data packet and audio timing, MST/MSE allocation and status, MSO, DSC bytes-per-pixel/control, ALPM, metadata transmission, and double-buffer control.
- `mmUNIPHYA_*` through `mmUNIPHYF_*` identify link control and channel crossbar controls for the six physical transmitter blocks.
- `mmLVTMA_PWRSEQ_*` and `mmBL_PWM_*` cover embedded-panel power sequencing and backlight PWM.
- `mmDC_GPIO_*`, `mmPHY_AUX_CNTL`, `mmDC_GPIO_AUX_CTRL_*`, and `mmAUXI2C_PAD_ALL_PWR_OK` are DCIO chip-level GPIO/DDC/AUX pad offsets used by GPIO, DDC/I2C, HPD, power-sequence, and pad-control code.
- `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED<N>` begins a reserved macro-control array for UNIPHY0. This chunk only includes entries 0 through 10; later entries are in the next chunk.

The field names, bit shifts, and masks are not defined here. They live in sibling generated headers such as `dcn_2_0_0_sh_mask.h`, while higher-level enum and IP-base data come from related DCN/Navi10/SOC15 headers.

## Control Flow And Data Flow

This header chunk has no runtime control flow. Data flow is compile-time substitution:

1. A DCN 2.0 consumer includes `dcn_2_0_0_offset.h` and usually the matching `dcn_2_0_0_sh_mask.h`.
2. Helper macros combine a register offset with the base index, for example `BASE(mmREG_BASE_IDX) + mmREG`.
3. The resulting absolute register address is stored in generated register tables or used by `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, IRQ-source tables, AUX/link encoder helpers, and similar AMDGPU/DC register abstractions.
4. The companion mask/shift macros select fields for read-modify-write or status decoding.

Concrete consumers in this tree show that pattern. `display/dc/resource/dcn20/dcn20_resource.c` defines `SR`, `SRI`, `SRIR`, and related macros that expand `mm...` offsets into DCN 2.0 resource register lists. Its resource tables include the AUX, HPD, stream-encoder, DisplayPort, and UNIPHY-style registers represented by this chunk. `display/dc/irq/dcn20/irq_service_dcn20.c` uses `SRI()` to build HPD interrupt enable/status/ack register addresses from `mmHPD<N>_DC_HPD_INT_*` macros. `display/dmub/src/dmub_dcn20.c` and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c` include the same generated header for DCN 2.0 register-table setup, though their direct references are not limited to this chunk. `amdgpu/gmc_v10_0.c` also includes the DCN 2.0 generated headers as part of SOC15/Navi10 register metadata.

The header does not encode programming order. Correct sequencing is imposed by the display core and hardware specifications: HPD interrupts must be masked/acked with the correct polarity, AUX transactions must arbitrate and poll status in the required order, stream encoder and DP link registers must be programmed around link training and modeset transitions, HDMI/AFMT audio packets must match audio stream state, and GPIO/power/backlight registers must be written in panel-safe sequences.

## State And Persistence Behavior

The macros themselves hold no mutable software state and perform no I/O. The mutable state represented by this chunk lives in hardware registers.

State categories described by these offsets include:

- Connector and interrupt state: HPD status, HPD interrupt enable/ack, HPD RX interrupt enable/ack, fast-training controls, and HPD debounce/toggle filtering.
- AUX/DDC transaction state: controller enable/reset, software command/data/status, arbitration ownership, interrupt control, low-speed data/status, AUX DPHY TX/RX tuning/status, GTC sync status, and PHY wake behavior.
- Stream-encoder state: HDMI metadata and infoframes, generic packets, ACR/audio packet generation, AFMT controls, IEC 60958 channel-status words, CRC/ramp diagnostics, TMDS control, lane enable, and DIG force-disable.
- DisplayPort link/stream state: lane/link configuration, pixel format, MSA timing/colorimetry/VBID, video M/N, training patterns, DPHY symbol/CRC/scrambler state, secondary packet framing, DP audio M/N, MST/MSE bandwidth allocation, MSO, DSC, ALPM, metadata transmission, and double-buffer state.
- Physical link and pad state: UNIPHY link/crossbar routing, DCIO pinstraps, genlock/swaplock pads, DCIO clock/reset, AUX impedance calibration, GPIO/DDC/HPD/power-sequence directions and values, pad strengths, AUX controls, pullups, RX enables, and pad power-good.
- Panel state: LVTMA power-sequence control/state/delays and backlight PWM control/period/locking.
- Diagnostics: display perfmon counters, HDMI/AFMT/DP DPHY CRC registers, status/readback registers, and reserved UNIPHY macro-control offsets.

Persistence is register-specific and not stated in the offset header. Some registers are durable control values that remain programmed until a modeset, link retrain, suspend/resume, reset, power transition, or later driver write. Others are live status bits, sticky interrupt flags, write-one-to-clear acknowledgements, hardware counters, self-clearing commands, read-only capabilities/status, or reserved registers whose semantics are intentionally opaque in this generated file.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 ASIC register database. The numeric offsets and `_BASE_IDX` values are meaningful only with the matching base-address definitions and field metadata:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h` for field masks and shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_0_offset.h` and `dpcs_2_0_0_sh_mask.h` for paired DPCS register metadata used by DCN 2.0 link resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/soc15/navi10_ip_offset.h` and SOC15 base-address helpers used by `BASE(mm..._BASE_IDX)`.
- Register-helper macros in AMD display code, including `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, and IRQ resource-list builders.

Direct include consumers found in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration surfaces are DRM/KMS connector detection, HPD interrupt handling, AUX/DDC transactions and EDID reads, DP link training, DP MST/MSE bandwidth programming, HDMI and DisplayPort stream encoder setup, HDMI/DP audio packet generation, DSC/MSO/ALPM modes, panel power and backlight control, GPIO/DDC/HPD pad translation, genlock/swaplock pad configuration, DCIO reset/clock control, and low-level debug/CRC/perf-counter workflows.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong offset or base index can compile cleanly while reading or writing the wrong register, causing black screens, missed hotplug, bad AUX/DDC transactions, broken link training, audio failures, interrupt storms, or unintended reset/power effects.
- The chunk begins and ends mid-address-block. `HPD0` status and interrupt-control offsets are in the previous chunk, and most of the `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED<N>` array is in the next chunk. The final per-file synthesis must stitch those boundaries together.
- Instance repetition increases review risk. `AUX0`-`AUX5`, `DIG0`-`DIG5`, `DP0`-`DP5`, and `HPD0`-`HPD5` are nearly regular, but a one-instance offset or base-index error can affect only one connector or stream.
- `_BASE_IDX` values are as important as the visible offsets. Most values in this range are `2`; using the wrong base segment with a numerically correct offset still addresses the wrong IP aperture.
- AUX registers mix command, data, arbitration, interrupt, DPHY tuning, wake, and status surfaces. Incorrect ordering or ack/mask semantics can hang AUX transfers, misread EDID/DPCD, or break HPD RX paths.
- Stream encoder and DP link programming is timing-sensitive. Bad DIG/DP constants can disturb link training, MSA timing, MST allocation, DSC/MSO, ALPM, HDMI infoframes, audio packets, or CRC diagnostics.
- GPIO/DDC/HPD/panel power registers are physical-pad controls. Misprogramming direction, output value, pullups, pad strength, AUX controls, or panel power/backlight sequencing can produce connector detection failures, I2C failures, panel flicker, backlight faults, or unsafe panel transitions.
- Reserved UNIPHY macro controls should not be inferred from names alone. Their offsets may be needed for generated tables or debug paths, but behavior must come from AMD's hardware database, not from the `RESERVED` names.
- Names such as `*_STATUS`, `*_ACK`, `*_INT_CONTROL`, `*_RESET`, `*_WAKE`, `*_LOCK`, `*_CRC_RESULT`, and `*_READBACK` signal possible side effects or volatility, but the offset header does not define access type or write semantics.

## Test Signals

Useful validation is a mix of generated-header comparison, build coverage, and hardware behavior:

- Build AMDGPU/DC configurations that include DCN 2.0/Navi10 paths. Missing or renamed constants should surface in `dcn20_resource.c`, `irq_service_dcn20.c`, `dcn20_clk_mgr.c`, `dmub_dcn20.c`, and `gmc_v10_0.c`.
- Compare all offsets and `_BASE_IDX` values in lines 10412-12940 against AMD's authoritative DCN 2.0 register database or a known-good upstream `dcn_2_0_0_offset.h`.
- Exercise all connector instances, not just connector 0: HPD plug/unplug, HPD RX events, EDID reads, DPCD reads/writes, DP link training, HDMI modes, DP modes, MST where available, suspend/resume, GPU reset, and repeated modeset cycles.
- Validate AUX/DDC behavior through successful EDID/DPCD access, sane AUX timeout/error handling, and no stuck arbitration or interrupt state after failed transactions.
- Validate DP link behavior with lane-count/rate changes, training-pattern transitions, MSA timing, secondary data packets, audio M/N readback, MST/MSE allocation, DSC/MSO/ALPM paths where supported, and DP DPHY CRC/debug readback.
- Validate HDMI/AFMT behavior with infoframes, generic metadata packets, ACR generation, audio packet control, IEC 60958 channel-status programming, audio CRC/status readback, and audio playback across common rates/channel counts.
- Validate GPIO/DDC/HPD/panel paths by checking DDC bus operation on all ports, HPD GPIO state translation, panel power-on/off sequencing, backlight PWM changes, suspend/resume backlight restoration, and pad power-good/pullup behavior.
- Monitor logs and hardware counters for regression signals: absent connectors, missed or repeated HPD interrupts, AUX timeouts, bad EDID, DPCD failures, link-training failure, no HDMI/DP audio, wrong audio format/channel map, underflow/flicker, black screen after resume, panel backlight stuck on/off, or unexpected DCIO reset effects.

## Cross-Chunk Notes

Adjacent chunks are required for a full-file report. This chunk continues an HPD0 block that began before line 10412 and stops partway through the UNIPHY0 reserved macro-control block. During reconciliation, describe this range as the DCN 2.0 DIO/DCIO offset section spanning HPD, perfmon, AUX, DIG, DP, DCIO, GPIO, panel power/backlight, and the beginning of UNIPHY0, not as a standalone complete header.

### subset-b-001608: lines 12941-15538

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 12941-15538

## Scope

This chunk is a generated register-offset portion of the AMD DCN 2.0.0 ASIC register map. It contains only C preprocessor constants: `mm...` register offset macros and matching `mm..._BASE_IDX` segment-index macros. The slice starts inside the `dce_dc_dcio_dcio_uniphy0_dispdec` block at `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10_BASE_IDX` and ends inside the `dce_dc_dpp5_dispdec_dscl_dispdec` block at `mmDSCL5_SCL_MODE`; both boundary blocks are partial and require neighboring chunks for the full per-file view.

The file-level contract supplied by this chunk is address resolution, not executable logic. Consumers combine `BASE(mmREG_BASE_IDX)` with `mmREG` to produce absolute MMIO offsets for DCN 2.0 display hardware.

## Purpose

The macros in this range map DCN 2.0 display sub-block registers for:

- UNIPHY display PHY macro reserved controls for PHY instances 0-6.
- Display Stream Compression instances DSC0-DSC5, including top-level DSC, DSC CIF, DSCC configuration/PPS/error/rate-buffer registers, and per-DSC performance monitors.
- DMCUB display microcontroller address windows, interrupts, inbox/outbox mailboxes, scratch/status registers, GPINT registers, and timers.
- MMHUBBUB writeback and XFC/XFCP buffer-control blocks.
- DPP4 and the beginning of DPP5: top control, CNVC format/cursor, scaler, color-management/gamma/3D LUT, and perfmon offsets.

Each non-`_BASE_IDX` macro is a register offset, for example `mmDMCUB_INBOX1_WPTR 0x3280`. Each paired `_BASE_IDX` macro identifies the SoC register-base segment to use with the offset, almost always `2` in this chunk.

## Important APIs, Types, And Macros

This header defines no functions, structs, enums, or storage. Its public API is the macro namespace consumed by AMD display code:

- `mmDCIO_UNIPHY<n>_UNIPHY_MACRO_CNTL_RESERVED<m>` and `_BASE_IDX`: 48 reserved control offsets per complete UNIPHY instance. This chunk contains UNIPHY0 reserved 10-47 and complete UNIPHY1-6 reserved 0-47 blocks.
- `mmDSC_TOP<n>_*`, `mmDSCCIF<n>_*`, and `mmDSCC<n>_*`: offsets for DSC top control/debug, CIF config, DSCC config/status/interrupt, 23 PPS config registers, memory power control, squared and absolute error counters, rate-buffer fullness, rate-control fullness, and debug bus rotation for DSC instances 0-5.
- `mmDC_PERFMON21_*` through `mmDC_PERFMON27_*`: per-block display performance counter control/state/value registers. PERFMON21-26 align with DSC0-5; PERFMON27 aligns with DPP4.
- `mmDMCUB_*`: DMCUB region offset/top/base registers, region3 CW0-CW7 windows, interrupt enable/ack/status/type, fault addresses, security/memory control, inbox/outbox ring descriptors, timers, scratch registers, `DMCUB_CNTL`, GPINT data, memory power, and processor ID.
- `mmMCIF_WB2_*`: MCIF writeback instance 2 buffer manager, buffer addresses/status, pitch, arbitration, watermark, clock gating, self-refresh, QoS, luma/chroma sizes, high address bits, and buffer resolution offsets.
- `mmXFCP<n>_MMHUBBUB_XFC_*` and `mmMMHUBBUB_XFC*`: six XFC pipe windows plus global XFC memory power, surface/write config, VM init, GPU base addresses, and XFC monitor counters.
- `mmDPP_TOP4_*`, `mmCNVC_CFG4_*`, `mmCNVC_CUR4_*`, `mmDSCL4_*`, `mmCM4_*`: DPP4 top, converter, cursor, scaler, output buffer, color matrix, degamma, blend gamma, shaper, 3D LUT, memory power, and debug registers.
- `mmDPP_TOP5_*`, `mmCNVC_CFG5_*`, `mmCNVC_CUR5_*`, and partial `mmDSCL5_*`: the beginning of equivalent DPP5 definitions.

The key integration macros are defined in consumers rather than here. For DCN20 resource construction, `SR(reg_name)` expands to `.reg_name = BASE(mm ## reg_name ## _BASE_IDX) + mm ## reg_name`; instance macros such as `SRI(reg_name, block, id)` do the same for `block id` register names. DMUB uses `REG_OFFSET(reg_name) (BASE(mm##reg_name##_BASE_IDX) + mm##reg_name)` through `dmub_reg.h`.

## Address-Block Inventory

Complete address blocks in this chunk:

- `dce_dc_dcio_dcio_uniphy1_dispdec` through `uniphy6`, base addresses `0x360`, `0x6c0`, `0xa20`, `0xd80`, `0x10e0`, `0x1440`, each with 48 reserved register offsets and 48 `_BASE_IDX` entries.
- `dce_dc_dsc0` through `dce_dc_dsc5` groups. Each instance includes a top block, DSCCIF block, DSCC block, and a DC perfmon block. DSC instance base comments progress by `0x170`; perfmon base comments progress from `0xc140` to `0xc870`.
- `dce_dc_dmu_dmcub_dispdec`, base `0x0`, 216 macro definitions covering DMCUB register offsets from `0x3238` through `0x32a9`.
- `dce_dc_mmhubbub_mcif_wb2_dispdec`, base `0xc6b8`, 108 macros covering writeback instance 2 offsets `0x3460` through `0x3496`.
- `dce_dc_mmhubbub_xfcp0_dispdec` through `xfcp5`, plus global `dce_dc_mmhubbub_xfc_dispdec`, covering per-pipe XFC control/config/size and global XFC memory/monitor registers.
- `dce_dc_dpp4_dispdec_*` blocks for DPP top, CNVC config, cursor, DSCL, color management, and perfmon.
- `dce_dc_dpp5_dispdec_dpp_top_dispdec`, `cnvc_cfg`, and `cnvc_cur`.

Partial blocks:

- UNIPHY0 is continued from the previous chunk. This slice begins after `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10`.
- DPP5 DSCL continues into the next chunk. This slice includes only tap select, tap data, and `SCL_MODE` plus the first two `_BASE_IDX` pairs before stopping at line 15538.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time macro expansion:

1. A DCN20-specific C file includes `dcn_2_0_0_offset.h`, `dcn_2_0_0_sh_mask.h`, and a SoC IP offset header such as `navi10_ip_offset.h`.
2. Register-list macros in display blocks name logical registers without hardcoding offsets.
3. Resource initialization macros expand each logical name to `BASE(mm..._BASE_IDX) + mm...`.
4. Runtime helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, and `REG_UPDATE` use the computed offsets to touch MMIO registers.

Examples visible in the tree include `dmub/src/dmub_dcn20.c`, `dc/resource/dcn20/dcn20_resource.c`, `dc/gpio/dcn20/hw_factory_dcn20.c`, `dc/irq/dcn20/irq_service_dcn20.c`, and `dc/clk_mgr/dcn20/dcn20_clk_mgr.c`.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. It describes hardware state locations. The represented hardware registers do hold volatile state:

- DMCUB region, mailbox, scratch, GPINT, interrupt, timer, and fault registers track firmware boot, command transport, interrupt handling, and debug state across driver operations and hardware resets.
- DSCC and DSC_TOP registers hold stream-compression configuration, PPS values, error counters, rate-buffer telemetry, memory-power state, and interrupt status.
- MCIF_WB2 and XFC registers hold display writeback buffer descriptors, watermarks, QoS, VM initialization, monitor counters, and memory-power state.
- DPP4/DPP5 CNVC, DSCL, and CM registers hold pipe-local pixel format, cursor color, scaling, color-space conversion, gamma, shaper, 3D LUT, and memory power state.

Because these are MMIO offsets, persistence semantics come from the hardware and driver reset paths. The header must match the ASIC register spec exactly; stale or shifted constants cause reads and writes to hit the wrong hardware location.

## Dependencies And Integration Points

Primary dependencies:

- `navi10_ip_offset.h` supplies segment base constants such as `DCN_BASE__INST0_SEG2`, used by `BASE(mm..._BASE_IDX)`.
- `dcn_2_0_0_sh_mask.h` supplies field masks and shifts for the same register names.
- AMD display register helpers (`reg_helper.h`, `dmub_reg.h`, and related block headers) provide `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_UPDATE`, `SR`, `SRI`, and DMUB register table construction.

Integration signals in this chunk:

- `dmub/src/dmub_dcn20.c` builds `dmub_srv_dcn20_regs` from this header and uses DMCUB offsets for reset, mailbox pointer zeroing, firmware boot, GPINT, scratch, timer, and fault/debug access.
- `dc/resource/dcn20/dcn20_resource.c` imports this header when constructing DCN20 resources, including DSC, DPP, DWB/MMHUBBUB, GPIO, IRQ, and clock objects.
- `dc/irq/dcn20/irq_service_dcn20.c` imports this header and uses address macros through IRQ register-list expansion.
- Sibling generated headers for DCN 2.1 and 3.x carry similar macro names with sometimes different offset values, so consumers must include the ASIC-matched offset header.

## Risks

- Register-map correctness is high risk. An incorrect numeric offset or `_BASE_IDX` can silently redirect MMIO access to a different register, causing display corruption, hangs, firmware mailbox failure, bad interrupt handling, or memory writeback faults.
- Boundary chunks are easy to mismerge. UNIPHY0 and DPP5 DSCL are incomplete in this slice and must be reconciled with adjacent chunk reports before writing the final per-file report.
- The repeated instance patterns invite copy/paste or generator errors. DSC0-5 and XFCP0-5 should maintain consistent stride and register ordering unless the hardware spec intentionally diverges.
- Most macros in this chunk use `_BASE_IDX 2`; any exception would be significant. Mechanical validation should catch accidental segment-index drift.
- Reserved UNIPHY macro names are opaque. They should not be inferred as safe to program without matching field definitions and ASIC documentation.
- DMCUB mailbox and region-window offsets are especially sensitive because the firmware command channel and memory windows depend on correct base/top/offset pairing.

## Test And Validation Signals

Useful validation for this chunk is mostly compile-time and hardware/integration oriented:

- Compile all DCN20 display objects that include `dcn_2_0_0_offset.h`; macro-name mismatches are caught as build failures.
- Build with corresponding `dcn_2_0_0_sh_mask.h`; register names used by `REG_GET`/`REG_UPDATE` must have both offset and field mask/shift definitions.
- Run display bring-up tests on DCN2.0/Navi10-class hardware: modeset, hotplug, vblank/vupdate IRQs, DSC-enabled modes, cursor display, scaling, color-management/gamma programming, and display writeback.
- Exercise DMUB boot/reset and mailbox paths: DMCUB soft reset, inbox/outbox pointer reset, GPINT command/ack, scratch register status, timer reads, and debug fault collection.
- Check register-map generator consistency: paired `mm...` and `mm..._BASE_IDX` definitions, monotonic offsets inside repeated blocks, correct instance strides for DSC and XFCP, and no duplicate or missing macros relative to the ASIC source data.
- Runtime failures likely surface as `REG_READ`/`REG_WRITE` timeouts, display pipe programming failures, missing interrupts, DMCUB firmware non-response, DSC visual corruption, or writeback buffer/address errors.

## Research Notes

This chunk contains 2,402 `#define` lines in the requested range. The first line is the `_BASE_IDX` for `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10`, confirming a previous-chunk boundary. The last requested line is `#define mmDSCL5_SCL_MODE 0x3762`, and the next source line outside scope supplies its `_BASE_IDX`, confirming a next-chunk boundary.

### subset-b-001609: lines 15539-17539

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 15539-17539

## Scope

This chunk covers the final 2,001 lines of the generated-style AMD DCN 2.0 register offset header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable statements. The range starts in the middle of the `DSCL5` scaler block, covers the full `CM5` color-management block, a DPP5 performance monitor, the HDA/Azalia controller and stream descriptor maps, legacy VGA indexed-register indices, Azalia codec/endpoint indirect register indices, and ends at the file's closing `#endif`.

The source region contains 1,762 `#define` entries. `mm*` names are MMIO register offsets paired with `*_BASE_IDX` macros; `ix*` names are indirect register indices used through index/data windows such as Azalia endpoint and VGA indexed access paths. Most DPP5/DCN display offsets in this chunk use base index `2`, Azalia controller/stream registers mainly use base index `0`, and some aliases such as wall-clock/LPIB readback use base index `1`.

## Purpose

The macros provide the address constants consumed by DCN 2.0 display and audio code when programming hardware blocks:

- Tail of DPP5 display scaler (`DSCL5`): scaler mode, tap control, horizontal/vertical fixed-point ratios and phases for luma/RGB and chroma, black offset, update/autocal controls, overscan, OTG blanking mirrors, recout and MPC sizes, line-buffer format/control/status, DSCL memory power status/control, and output-buffer control.
- DPP5 color management (`CM5`): input color-space conversion, gamut remap, biases, degamma/blend-gamma/shaper LUT index/data/write-enable registers, RAM A/B region/start/slope/end controls, HDR multiplier, coefficient format, memory power controls, 3D LUT programming, output normalization/offset, and debug index/data.
- `DC_PERFMON28`: a DPP5 performance counter/perfmon register set with control, state, selected counter value, and high/low readback offsets.
- HDA/Azalia controller MMIO: CORB/RIRB command-response ring controls, immediate command/response registers, DMA position buffer base addresses, wall-clock alias, endpoint/root immediate command windows, and output stream descriptor registers for streams 0-7.
- VGA indirect indices: sequencer, CRTC, graphics-controller, and attribute-controller index values for legacy VGA paths.
- Azalia codec and endpoint indirect indices: F2 codec pin, descriptor, sink-info, input/output CRC result, root, stream latency, endpoint, and input-endpoint register spaces.
- Repeated F0 output endpoints 0-7 and input endpoints 0-7: converter parameters/controls, stream IDs, digital converter controls, pin parameters, widget controls, multichannel/HBR/channel allocation, hotplug, unsolicited response, configuration defaults, LPIB/status/infoframe, sink/audio descriptor fields, codec status overrides, and audio enable/format-change interrupt status.

## Important Macro Families

`mmDSCL5_*` continues a DPP instance that began before this chunk. The first line is the `mmDSCL5_SCL_MODE_BASE_IDX` companion for the preceding `mmDSCL5_SCL_MODE` offset. The remaining DSCL5 macros cover scaler setup and memory/output-buffer control from offsets `0x3763` through `0x3781`, all in base index `2`.

`mmCM5_*` spans offsets `0x3790` through `0x3860` under `dce_dc_dpp5_dispdec_cm_dispdec`. The block includes paired matrix coefficient registers for ICSC and gamut remap, A/B RAM layouts for degamma and blend gamma, larger region tables for shaper RAMs, `CM_3DLUT_*` programming registers, and memory power/status registers. These offsets are instance-specific for DPP/color-management pipe 5.

`mmDC_PERFMON28_*` maps a compact perfmon register set at offsets `0x389a` through `0x38a2`, also base index `2`. It follows the standard DC perfmon pattern: counter control, secondary control, state, perfmon control, selected counter-value interrupt/misc state, and high/low counter data.

`mmCORB_*`, `mmRIRB_*`, `mmIMMEDIATE_*`, `mmDMA_POSITION_*`, `mmAZENDPOINT_*`, `mmAZROOT_*`, and `mmAZSTREAM0_*` through `mmAZSTREAM7_*` describe HDA/Azalia controller and output stream descriptor MMIO. Stream descriptor offsets advance by the HDA stream stride, with control/status, LPIB, cyclic buffer length, last valid index, FIFO/format, BDL pointer low/high, and LPIB alias registers.

`ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` are legacy VGA indexed-register numbers, not direct MMIO offsets. They are meaningful only through VGA index/data accessors.

`ixAZALIA_F2_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, `ixAZALIA_INPUT_CRC*`, `ixAZALIA_CRC*`, `ixAZALIA_F2_CODEC_INPUT_*`, and `ixAZALIA_F2_CODEC_ROOT_*` are indirect Azalia codec/control indices. They describe codec verbs/registers for pin capabilities, multichannel setup, LPIB snapshotting, channel status, root/function parameters, sink description strings, and CRC result channels.

`ixAZF0STREAM0_*` through `ixAZF0STREAM15_*` expose per-stream FIFO sizing and latency counters. Each stream has the same five indices: FIFO size control, latency counter control, worst-case latency count, cumulative latency count, and cumulative request count.

`ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` repeat a 71-index output endpoint layout. Each endpoint has converter controls, pin parameters, 14 audio descriptor slots, multichannel and HBR controls, sink info slots, hotplug and unsolicited response controls, configuration defaults, codec channel-status overrides, LPIB snapshot/readback, coding/format-change controls, wireless display/keepalive, and audio enable/disable/format-change interrupt status indices.

`ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` repeat a smaller 23-index input endpoint layout for input converter and input pin programming: converter capabilities/format/stream ID/digital converter, stream format and supported-rate parameters, input pin capabilities, unsolicited response and sense, widget control, multichannel/HBR/channel allocation, hotplug, configuration defaults, LPIB snapshot/readback, input-status control, and infoframe.

## APIs, Types, and Functions

There are no callable APIs or C types in this chunk. The macros are the hardware-facing address API for generated ASIC register tables:

- `mmREGISTER` constants give register offsets for direct MMIO or register-helper access.
- `mmREGISTER_BASE_IDX` selects the register base aperture/table used by the AMD display register access macros.
- `ixREGISTER` constants give indices for indirect register windows, especially VGA and Azalia endpoint/codec spaces.

Consumers pair these offsets with companion DCN 2.0 shift/mask headers and with AMDGPU display register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and indirect index/data helpers. The header is included by DCN 2.0 display resource setup, IRQ service, GPIO factory code, clock manager code, DMUB DCN 2.0 code, and `gmc_v10_0.c`.

## Control Flow

The header has no runtime control flow. Hardware programming flow is implied by the register groups:

1. Select the intended hardware instance and access path: direct MMIO for `mm*`, indexed VGA for `ixSEQ`/`ixCRT`/`ixGRA`/`ixATTR`, or Azalia index/data windows for `ixAZALIA*`, `ixAZF0ENDPOINT*`, and `ixAZF0INPUTENDPOINT*`.
2. For scaler/color management, program `DSCL5` ratios/phases/taps and `CM5` matrices/LUTs/3D LUT while respecting update, LUT index/data, RAM A/B, memory-power, and display-pipe timing rules.
3. For perfmon, select events and controls, start/stop or clear counters, then read state and high/low counter values from `DC_PERFMON28`.
4. For Azalia controller output, set up CORB/RIRB or immediate-command paths, configure stream descriptors and BDL pointers, program endpoint converter/pin registers through indirect indices, and monitor LPIB/status/interrupt fields.
5. For sink and audio capability reporting, read or populate descriptor/sink-info endpoint indices and codec parameter indices.
6. For status and diagnostics, read CRC result indices, stream latency counters, audio enable/disable/format-change interrupt status, and input endpoint status/infoframe indices.

Sequencing-sensitive areas include scaler coefficient and update latching, CM LUT/3D-LUT index-data programming, Azalia command ring pointer updates, stream descriptor enable/BDL programming, codec endpoint indirect access, LPIB snapshot timing, and any clear-on-write or latched status behavior in audio interrupt/status registers.

## State and Persistence

The file stores no software state. It describes hardware state that persists until explicit driver writes, reset, display modeset teardown, audio stream teardown, suspend/resume, firmware intervention, or power-gating transitions.

Important state domains in this chunk include:

- DSCL5 display scaling state: tap selection, fixed-point scale ratios, filter phases, overscan, recout/MPC geometry, line-buffer format and memory control, and DSCL/OBUF power state.
- CM5 color pipeline state: conversion/remap matrices, degamma/blend/shaper LUT contents and RAM regions, HDR multiplication, shaper scaling/offsets, 3D LUT contents and normalization/output offsets, coefficient format, debug selection, and CM memory power state.
- DPP5 perfmon state: active/counting configuration, event selection, latched state, overflow/interrupt status, and counter values.
- HDA controller state: CORB/RIRB ring pointers and control/status, immediate command status, DMA position buffer address, wall-clock readback, output stream descriptor registers, stream format, buffer descriptor pointers, and LPIB aliases.
- Azalia codec/endpoint state: converter formats and stream IDs, pin widget/hotplug/unsolicited response controls, audio descriptors, sink info, multichannel/HBR/channel allocation, channel status overrides, LPIB snapshots, format-change/audio-enable status, root/function power/reset and capability parameters, CRC results, and latency counters.
- Legacy VGA indexed state: sequencer, CRTC, graphics, and attribute registers reachable through the VGA access path.

Because these are raw hardware offsets and indices, callers must use the correct base index and access path. An `ix*` index used as direct MMIO, or an `mm*` offset used through an indirect endpoint window, would compile but address the wrong hardware surface.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is useful only with the rest of AMD's DCN 2.0 generated register data:

- The companion `dcn_2_0_0_sh_mask.h` field definitions provide the bit positions/masks for these offsets.
- DCN 2.0 display resource code includes this header to construct register tables for DPP/scaler/color-management and other display blocks.
- DCN 2.0 IRQ, GPIO, and clock-manager code include it for interrupt source mapping, DDC/GPIO translation, and clock/power register access.
- DMUB DCN 2.0 code includes it for firmware-facing display register programming.
- Audio integration code uses the Azalia/HDA offsets and indirect indices to drive HDMI/DP audio stream setup, endpoint capability reporting, sink info, channel allocation, LPIB/status tracking, and interrupt handling.
- Shared register-helper infrastructure supplies the accessors that combine `mm*` offsets, `*_BASE_IDX` values, and field masks/shifts.

The repeated endpoint and input-endpoint layouts are a major integration signal. Driver code should select endpoint instances through tables or generated macros rather than constructing names or assuming all ASIC generations preserve the same endpoint count and stride.

## Risks

The primary risk is silent hardware misprogramming. Incorrect offsets or base indices compile cleanly but can write or read the wrong register aperture, causing display pipe corruption, bad color transforms, broken scaler state, perfmon readback failures, audio stream setup failures, or incorrect endpoint capabilities.

Chunk-boundary risk exists at the beginning. The slice starts on `mmDSCL5_SCL_MODE_BASE_IDX`; the matching `mmDSCL5_SCL_MODE` offset is immediately before the requested range. The final per-file reconciliation should merge the preceding chunk before describing the full DSCL5 scaler map.

Direct-vs-indirect access is a recurring hazard. `ix*` names are register indices for VGA/Azalia windows, not direct MMIO addresses. Treating them like `mm*` offsets, or using the wrong endpoint index/data pair, can touch unrelated registers or return misleading zeros.

The color-management and LUT families are order-sensitive. Programming LUT index/data/write-enable registers or RAM A/B region controls without the expected update protocol can leave partial degamma, blend-gamma, shaper, or 3D LUT contents active on a live pipe. That would show up as incorrect color, HDR errors, or transient artifacts.

HDA/Azalia controller registers have side effects and ordering constraints. CORB/RIRB pointer/control updates, immediate command status, stream descriptor enable, BDL pointer programming, and LPIB snapshots must follow HDA hardware rules. Incorrect sequencing may hang audio commands, report stale positions, underrun/overrun streams, or break HDMI/DP audio enumeration.

Status and interrupt-like endpoint indices require hardware semantics beyond the offset value. Audio enable/disable/format-change status, unsolicited responses, hotplug controls, CRC result indices, and input status fields may be latched, write-one-to-clear, or snapshot-based; blind read/modify/write can lose events or clear diagnostics unexpectedly.

Instance mix-ups are easy because endpoint and stream blocks repeat with near-identical register names. Mixing `AZSTREAMn`, `AZF0STREAMn`, `AZF0ENDPOINTn`, and `AZF0INPUTENDPOINTn` namespaces can wire the wrong stream to the wrong endpoint or read unrelated latency/status counters.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for all translation units that include `dcn_2_0_0_offset.h`, catching duplicate/missing macros and malformed generated definitions.
- Generated-header consistency checks that every `mm*` register has the expected `*_BASE_IDX`, repeated endpoint/input-endpoint/stream blocks preserve equivalent layouts, and offset progressions match the authoritative DCN 2.0 register database.
- Static checks that `mm*` offsets are consumed by direct register helpers and `ix*` indices are consumed only through the intended indexed accessors.
- Modeset and scaling tests on pipe/DPP instance 5, covering scaler ratios/phases, overscan, recout/MPC size, line-buffer state, DSCL update/autocal behavior, and memory-power transitions.
- Color-management tests for DPP5 that program ICSC, gamut remap, degamma, blend gamma, shaper LUTs, HDR multiplier, and 3D LUT paths, then verify output through CRC, readback, or visual/colorimetry validation.
- Perfmon tests that start, stop, clear, and read `DC_PERFMON28` counters and verify high/low counter behavior and state bits.
- HDMI/DP audio tests covering HDA CORB/RIRB or immediate command operation, stream descriptor setup, BDL/LPIB behavior, endpoint converter format and stream ID, hotplug/unsolicited response, channel allocation, multichannel/HBR, and format-change events.
- Sink capability tests that verify audio descriptor and sink-info indices are populated/read correctly across endpoints 0-7.
- Input audio/endpoint tests for input endpoints 0-7, including input converter format, pin sense, input status control, LPIB snapshot, and infoframe handling.
- Suspend/resume and runtime power tests that verify CM5/DSCL5 memory power states and HDA/Azalia stream/endpoint state are restored coherently.

## Cross-Chunk Notes

This is the terminal slice of `dcn_2_0_0_offset.h`. The final per-file research document should merge it with the previous chunk for the start of the `DSCL5` block and with earlier chunks that define the matching DPP, HDA, VGA, and Azalia index/data access registers. Treat this chunk as a generated register-map tail, not as a standalone module with local algorithms.
