# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001777`: lines 1-2680, `Docs/researches/chunks/subset-b-001777_research.md`
- `subset-b-001778`: lines 2681-5260, `Docs/researches/chunks/subset-b-001778_research.md`
- `subset-b-001779`: lines 5261-7902, `Docs/researches/chunks/subset-b-001779_research.md`
- `subset-b-001780`: lines 7903-8471, `Docs/researches/chunks/subset-b-001780_research.md`

## Chunk Research

### subset-b-001777: lines 1-2680

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 1-2680

## Purpose

This chunk is the opening portion of AMD's generated DCN 3.0.3 register-offset header for the display driver. It does not implement executable logic; it supplies preprocessor constants that map display hardware register names to register offsets and base-segment indices. Driver code combines each `mm...` offset with the corresponding `mm..._BASE_IDX` entry and the ASIC base table from `sienna_cichlid_ip_offset.h` to compute absolute MMIO addresses for DCN303 display programming.

The header is guarded by `_dcn_3_0_3_OFFSET_HEADER`, uses the MIT SPDX identifier, and starts the DCN303 address map at the VGA/MMHUBBUB, DCCG, DMU/DMCU/DMCUB, writeback, HDA/Azalia audio, DCHUBBUB, HUBP/HUBPREQ, and DPP0 blocks. The full file is longer, but this chunk ends in the DPP0 color-management register group.

## Important definitions and block coverage

The only public "API" in this chunk is a large set of C macros:

- `mm<REGISTER>`: the register's block-local offset value, for example `mmDCCG_GTC_CNTL`, `mmDMCUB_INBOX0_BASE_ADDRESS`, `mmHUBP0_DCSURF_SURFACE_CONFIG`, and `mmCM0_CM_GAMCOR_LUT_DATA`.
- `mm<REGISTER>_BASE_IDX`: the base segment selector used by helper macros such as `BASE(mm..._BASE_IDX)` or `REG_OFFSET(...)`. In this chunk the values are mainly `0`, `1`, or `2`.

Major register groups covered in lines 1-2680:

- VGA and legacy display decode registers: `mmVGA_*`, indexed DAC/CRTC/SEQ/GRPH names, and per-pipe `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`.
- DCCG display clock generation: PHY pixel-clock resync, DP DTO phase/modulo, DISPCLK/DPPCLK/DSCCLK controls, GTC counters, audio DTOs, vsync latch/counter controls, clock gating, and soft reset.
- DC perfmon instances 0-6: repeated `PERFCOUNTER_CNTL`, `PERFMON_CNTL`, current value, high, and low counter registers for DCCG, DMU, MMHUBBUB, HDA, DCHUBBUB, and HUBP instances.
- DMU/DMCU/DMCUB control: DMCU firmware address/checksum/interrupt/communication registers; DMCUB region offsets and top addresses; code-window region 3 mappings; inbox/outbox queues; scratch registers; GPINT registers; timers; memory/security/fault controls.
- Interrupt hub/control: `mmDISP_INTERRUPT_STATUS*`, GPU timer start/read registers, and interrupt-destination registers for DCCG, DMU, DCHUB, HUBBUB, WB, MPC, OPP, OPTC, OTG, DIG, I2C/DDC/HPD, DCIO, AUX, DSC, and audio.
- MCIF writeback and MMHUBBUB: writeback buffer manager status/control, Y/C buffer addresses and high-address registers, arbitration, watermarks, VMID control, warmup configuration, memory power, clock, soft reset, and VGA interface controls.
- HDA/Azalia audio: stream index/data registers for streams 0-15, endpoint and input-endpoint index/data windows, controller clock/DTO/DMA/RIRB/CORB controls, codec root parameters, CRC registers, cyclic-buffer sync, payload capabilities, and memory power.
- DCHUBBUB memory path: SDPIF configuration and VM aperture registers, return-path DCC/CRC/memory-power registers, hubbub arbitration watermarks A-D, DRAM/self-refresh clock-change controls, timeout detection, surface-check addresses, VTG controls, performance measurement, and VM request context programming for contexts 0-15.
- HUBP/HUBPREQ/HUBPRET and cursor for instances 0 and 1: surface configuration, tiling, viewport dimensions, request sizing, surface pitch, primary/secondary luma/chroma and metadata addresses, flip control/status, TTU/QoS parameters, VM aperture/L1 TLB controls, prefetch/vblank/flip/nominal timing parameters, cursor addresses/position/hot spot/DMDATA, and read-line controls.
- DPP0 front-end processing through the start of CM: DPP top control/reset/CRC, CNVC pixel format, format conversion bias/scale, color keyer, pre-CSC matrices, cursor conversion colors, DSCL coefficient RAM and scaler ratios/inits, line-buffer and output-buffer controls, and CM post-CSC/gamut/gamma-correction LUT registers.

There are a few intentional-looking aliases where multiple symbolic names share the same offset, such as legacy VGA index/data windows and `mmFMON_CTRL`/`mmFMON_CTRL_1`. These allow common helper tables to use semantic names even when the hardware decodes them at the same address.

## Control flow and runtime behavior

This file has no functions, branches, loops, storage, or runtime control flow. Its behavior happens entirely at C preprocessing and compile time.

The runtime register access flow is supplied by including code:

1. DCN303 resource, IRQ, and DMUB sources include this header together with `sienna_cichlid_ip_offset.h` and `dcn_3_0_3_sh_mask.h`.
2. Local macros such as `SR(reg_name)`, `SRI(reg_name, block, id)`, and DMUB's `REG_OFFSET(reg_name)` expand `BASE(mm..._BASE_IDX) + mm...`.
3. `BASE(seg)` expands through `DCN_BASE__INST0_SEG<seg>` from the ASIC IP offset header, producing an absolute register offset for the ASIC instance.
4. The resulting constants initialize register tables, for example hubbub/HUBP/DCCG register structs, DMUB common register offsets, and IRQ source descriptors.
5. Later driver register helpers use those tables with field masks/shifts from the companion `_sh_mask.h` header to perform MMIO reads, writes, interrupt acknowledgement, watermarks, flips, power state changes, and firmware mailbox operations.

## State and persistence

This header stores no driver state and persists nothing by itself. The constants point at hardware stateful registers. Writes by the display driver affect volatile hardware state such as DMCUB mailbox pointers, display VM context page table bases, surface addresses, flip status, memory power controls, clock controls, watermarks, perfmon counters, audio stream windows, and color/scaler LUT/index data. That state lives in GPU display hardware and, for some firmware-facing registers, in DMCUB/DMCU-managed SRAM or queue memory configured elsewhere.

Because the macros are compile-time constants, a wrong offset or base index becomes a persistent binary-level defect: every runtime access through the affected table targets the wrong MMIO address until the driver is rebuilt.

## Dependencies and integration points

Direct companion dependencies:

- `sienna_cichlid_ip_offset.h`: provides `DCN_BASE__INST0_SEG*` base values selected by `_BASE_IDX`.
- `dcn/dcn_3_0_3_sh_mask.h`: provides bit-field masks and shifts for the same register names.
- `dpcs/dpcs_3_0_3_offset.h` and `dpcs/dpcs_3_0_3_sh_mask.h`: included beside this file for DisplayPort/DPCS blocks in DCN303 resource code, although not defined in this chunk.

Observed integration points:

- `display/dc/resource/dcn303/dcn303_resource.c` includes this header and uses `SR`, `SRI`, `SRII`, `DCCG_SRII`, and related macros to populate DCN303 register structures. The resource file advertises `num_timing_generator = 2`, `num_video_plane = 2`, `num_audio = 2`, and `num_vmid = 16`, matching the two HUBP/HUBPREQ instances, two OTG-facing paths, audio support, and VM context range seen in this chunk.
- `display/dmub/src/dmub_dcn303.c` includes this header and expands `REG_OFFSET(...)` into `dmub_srv_dcn303_regs`, especially for DMCUB internal, inbox/outbox, scratch, interrupt, timer, memory, and fault registers.
- `display/dc/irq/dcn303/irq_service_dcn303.c` includes this header and uses `SRI(...)` to build IRQ source metadata. In this chunk, the `HUBPREQ0/1_DCSURF_SURFACE_FLIP_INTERRUPT` offsets back page-flip IRQ entries, while HPD/OTG registers are also resolved through the same base-plus-offset pattern.

## Risks and correctness concerns

- The file is generated-style hardware data. Manual edits are high risk because a single incorrect hex value or `_BASE_IDX` can redirect register access to another block, causing display bring-up failures, hangs, missed interrupts, incorrect flips, firmware mailbox breakage, audio malfunction, or memory/power sequencing bugs.
- The names and companion field masks must stay synchronized. If `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h` come from different register generations, the driver can write valid addresses with invalid field encodings.
- The repeated instance blocks have dense patterns, but they are not safe to infer mechanically without the hardware source: offsets for HUBP0/HUBP1, stream 0-15, endpoints, perfmon instances, and VM contexts must match the ASIC address map exactly.
- Alias definitions are expected for some legacy windows; tools looking for duplicate offsets should distinguish intentional aliases from accidental overlap.
- Registers that program 64-bit addresses are split into low/high pairs. Using only one half or mixing pair order in consumers would corrupt display VM, DMCUB region, cursor, surface, or writeback buffer addresses.
- The chunk includes both control and status/ack registers. Consumer code must preserve hardware write-one-to-clear and polling semantics from the field definitions and block programming guides; the offset header alone does not encode access type.

## Test signals and validation

Useful validation signals for this chunk are mostly build-time and hardware/driver runtime signals:

- Compile the AMD display driver path with DCN303 enabled; failures in register table initialization usually expose missing or renamed macros.
- Check that `dcn303_resource.c`, `dmub_dcn303.c`, and `irq_service_dcn303.c` still compile with this header and the matching `_sh_mask.h`.
- Boot or load the driver on matching DCN 3.0.3 hardware and verify display modeset, page flips, vblank/vupdate IRQs, HPD/HPDRX events, DMCUB firmware communication, audio stream setup, cursor updates, and memory power transitions.
- Exercise multi-plane scanout on both HUBP instances; this stresses `HUBP0/1`, `HUBPREQ0/1`, cursor, flip, prefetch, TTU, and VM context offsets.
- Use debug/perfmon paths to confirm DC perfmon counters and timeout/fault status registers are readable at the expected addresses.
- Compare generated offsets against the vendor register database or adjacent known-good DCN 3.0.x offset headers when updating, while treating DCN303-specific differences as authoritative only if sourced from the correct ASIC data.

### subset-b-001778: lines 2681-5260

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 2681-5260

## Scope

This chunk is a generated DCN 3.0.3 register-offset slice from `dcn_3_0_3_offset.h`. It contains only C preprocessor definitions and address-block comments. There are no functions, structs, enums, local variables, or executable branches in the range. Its job is to expose the MMIO offset map for AMDGPU Display Core code that programs DCN 3.0.3 display pipelines.

The range begins inside the DPP0 color-management block at `mmCM0_CM_GAMCOR_LUT_CONTROL` and ends at `mmDIG1_HDMI_ACR_STATUS_1`. It covers 2,409 `#define mm...` lines: 1,205 register-offset macros and 1,204 matching `_BASE_IDX` macros inside the requested line range. The apparent one-macro imbalance is a chunk-boundary artifact: line 5260 contains `mmDIG1_HDMI_ACR_STATUS_1`, while its `mmDIG1_HDMI_ACR_STATUS_1_BASE_IDX` companion appears on line 5261, outside this work item.

## Purpose And Hardware Surface

The macros in this chunk provide register addresses for the DCN 3.0.3 display datapath. Driver code combines each register offset with a base segment selected by the corresponding `_BASE_IDX` macro. In the DCN303 resource code, helper macros such as `SR`, `SRI`, `SRII`, and `SRI2` expand names like `mmCM1_CM_CONTROL_BASE_IDX` and `mmCM1_CM_CONTROL` into absolute register addresses through `BASE(mm..._BASE_IDX) + mm...`. Companion field definitions in `dcn_3_0_3_sh_mask.h` provide the bit-level `_SHIFT` and `_MASK` values.

Major hardware areas represented in this slice:

- DPP0 color management tail: gamma-correction LUT control, RAM A/B piecewise gamma segment start/end/slope/base/offset/region registers, blend gamma, HDR multiplier, memory power, dealpha, coefficient format, shaper LUTs, 3D LUT, and debug index/data registers.
- DPP0 performance monitor: `DC_PERFMON7_*` counter control, state, interrupt/misc, and counter-value readout registers.
- DPP1 pipeline frontend: DPP top control/soft reset/CRC/host read, CNVC pixel format and pre-CSC/pre-degamma/pre-alpha controls, cursor color/control, DSCL scaler/filter/viewport/output sizing/memory-power controls, CM color-management registers mirroring the DPP0 color pipeline, and `DC_PERFMON8_*`.
- OPP0 and OPP1 output processing: formatter clamp, dynamic expansion, bit-depth/dither, side-by-side stereo, 4:2:0 and 4:2:2 controls; display pattern generator controls/status; OPP buffer controls; pipe controls; per-pipe CRC controls/results; common OPP clock and ABM control; DSC forward-config registers for two DSCRM instances; and `DC_PERFMON9_*`.
- OPTC timing/output controls: ODM0/ODM1 input/data format/bytes-per-pixel/width/memory registers, OTG0 and OTG1 timing generator registers, global sync and update-lock controls, vertical interrupt controls, CRC windows/data, dynamic refresh rate controls, DSC start position, pipe-update status, DWB/GSL source select, OPTC memory power, and `DC_PERFMON10_*`.
- DIO/link side registers: DDC/I2C control/arbitration/transactions/data/EDID detect, DIO scratch and power/clock/reset/generic interrupt registers, HPD0/HPD1 status/control/filter/fast-train registers, `DC_PERFMON11_*`, AUX0/AUX1 control/status/data/DPHY/GTC/wake registers, DIG0/DIG1 VPG generic packet and info packet windows, AFMT audio/infoframe/CRC/status/memory-power registers, DME control/memory control, DIG/HDMI packet/audio/ACR/test/CRC/frontend registers, and DP0 transport/link/secondary-data-packet/MST/MSA/MSO/DSC/ALPM/GSP registers.

## Important Definitions

The important API is the macro naming contract, not a callable function interface:

- `mm<REGISTER>` gives the generated register offset within the ASIC's display register space.
- `mm<REGISTER>_BASE_IDX` gives the DCN base segment index used by generated address helpers. In this range the value is consistently `2` for all complete pairs, matching the DCN display segment selected by the including code.
- `// addressBlock: ...` and `// base address: ...` comments document hardware grouping and instance base offsets. They are consumed by humans and generation/reconciliation tools, not by the C compiler.

Representative definition families:

- `mmCM0_*` and `mmCM1_*` define color-management state for DPP instances 0 and 1. The CM families include post-CSC and gamut-remap matrix registers, gamma correction LUT index/data/control, RAM A/B region programming, blend gamma, shaper LUT, 3D LUT, and memory-power/status registers.
- `mmCNVC_CFG1_*`, `mmCNVC_CUR1_*`, and `mmDSCL1_*` define DPP1 input conversion, cursor, and scaler control offsets. These are used when DC builds the DPP1 register table in `dcn303_resource.c`.
- `mmFMT0_*`, `mmFMT1_*`, `mmDPG*`, `mmOPPBUF*`, `mmOPP_PIPE*`, and `mmOPP_PIPE_CRC*` define the output pixel processor surface for two output pipes.
- `mmODM*` and `mmOTG*` define timing-generator and output-data-mapping state for two timing generators. OTG registers include timing totals/blanks/syncs, vertical totals, frame and position counters, update locks, interrupt positions, CRC programming/readout, static-screen and 3D structure state, global sync, DRR, and DSC integration.
- `mmDC_I2C_*`, `mmHPD*`, `mmDP_AUX*`, `mmDIG*`, `mmVPG*`, `mmAFMT*`, `mmDME*`, and `mmDP0_*` define link-side control for DDC/I2C, hotplug, AUX transactions, stream encoding, HDMI/DP packet generation, audio formatting, and DisplayPort transport.
- `mmDC_PERFMON7_*` through `mmDC_PERFMON11_*` define repeated display performance-monitor blocks associated with DPP, OPP, OPTC, and DIO blocks.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime behavior is created by other driver layers that expand these macros into register tables and then perform MMIO read/modify/write operations through AMD Display Core helpers.

The typical flow is:

1. DCN303 initialization includes this header and `dcn_3_0_3_sh_mask.h`.
2. Resource constructors build per-block register tables with macros such as `DPP_REG_LIST_DCN30`, `OPP_REG_LIST_DCN30`, `OPTC_COMMON_REG_LIST_DCN3_0`, `AUX_COMMON_REG_LIST0`, `SE_DCN3_REG_LIST`, `VPG_DCN3_REG_LIST`, `AFMT_DCN3_REG_LIST`, and `I2C_HW_ENGINE_COMMON_REG_LIST`.
3. Block constructors store the resulting addresses in typed register structs for DPPs, OPPs, timing generators, stream encoders, VPG/AFMT, AUX, I2C, HPD, DIO, and related blocks.
4. Runtime display code programs those hardware blocks while setting modes, enabling planes, applying color transforms, setting cursors, training links, sending AUX/I2C transactions, generating HDMI/DP packets, servicing interrupts, or reading CRC/perfmon/debug state.

State represented by this chunk is hardware-backed:

- CM/CNVC/DSCL/DPP registers persist per-plane color conversion, cursor, scaling, memory-power, CRC, and debug state until updated, reset, or power-gated.
- OPP/FMT/DPG/OPPBUF/CRC registers persist output format, dithering/clamping, pattern generation, output buffer, and output CRC state.
- ODM/OTG registers persist timing, update-lock, global sync, dynamic refresh, CRC, DSC, interrupt-position, and pipe-update state for the timing generator.
- DIO/I2C/AUX/HPD/DIG/DP/VPG/AFMT/DME registers persist link-side configuration and expose volatile status for hotplug, AUX/I2C progress, FIFO/CRC/status, audio packet state, DP transport state, and packet-transmission status.
- Perfmon registers persist counter configuration and expose volatile counter values and interrupt status.

The header does not enforce sequencing. Callers must still respect hardware ordering such as locking updates before timing changes, programming scaler/color blocks before enabling a pipe, waiting for AUX/I2C completion, acknowledging or masking HPD/interrupt state appropriately, and avoiding live link/stream packet changes outside safe update windows.

## Dependencies And Integration Points

This offset slice is integrated through several DCN303 paths:

- `display/dc/resource/dcn303/dcn303_resource.c` includes `dcn_3_0_3_offset.h` and uses helper macros to build register tables for DIO, VPG, AFMT, audio, stream encoders, DPPs, OPPs, OPTCs, AUX engines, I2C engines, link encoders, MCIF writeback, MMHUBBUB, MPC, DSC, and hardware sequencing.
- `display/dc/irq/dcn303/irq_service_dcn303.c` includes the same offset and mask headers. It uses generated register names through `SRI` and `IRQ_REG_ENTRY` to describe HPD, vblank, vline, flip, and vupdate interrupt enable/status/ack registers. This chunk directly includes HPD0/HPD1 and OTG0/OTG1 offsets that participate in those tables.
- `display/dmub/src/dmub_dcn303.c` includes this header for common DMUB register offset construction. The DMCUB registers themselves are outside this particular line range, but the integration pattern is the same generated-offset plus generated-mask model.
- Common block headers such as `dcn30_dpp.h`, `dce_opp.h`, `dcn10/dcn10_optc.h`, `dcn20/dcn20_optc.h`, `dce_aux.h`, and `dce_stream_encoder.h` define the register-list macros that expand against this file's `mm...` names.
- Companion generated headers are required: `dcn_3_0_3_sh_mask.h` supplies field masks/shifts, and IP segment headers such as `sienna_cichlid_ip_offset.h` supply the base address macros used by `BASE(mm..._BASE_IDX)`.

The chunk is source-tree-aligned with a DCN303 resource capability of two timing generators, two OPPs, two video planes, two audio instances, two stream encoders, two DDC engines, one DWB, and two DSC instances. That matches the instance coverage visible here for DPP0/DPP1, OPP0/OPP1, OTG0/OTG1, HPD0/HPD1, AUX0/AUX1, DIG0/DIG1, VPG0/VPG1, AFMT0/AFMT1, and DME0/DME1.

## Risks And Maintenance Notes

- Generated-header drift is the primary risk. A wrong offset or stale `_BASE_IDX` value can make otherwise-correct display code write the wrong MMIO register.
- Instance naming is dense and repetitive. Confusing `CM0` with `CM1`, `OTG0` with `OTG1`, `DIG0` with `DIG1`, `HPD0` with `HPD1`, or `AUX0` with `AUX1` can route programming to the wrong pipe or connector.
- Many register families are mirrored but not always contiguous. Code should rely on generated names and register-list macros, not arithmetic assumptions between instances.
- The requested chunk begins and ends mid-block. It starts after earlier DPP0 CM setup definitions and ends before the `mmDIG1_HDMI_ACR_STATUS_1_BASE_IDX` line and later DIG1 registers. Merge/reconciliation should treat this as chunk slicing, not as missing definitions in the source file.
- Several registers control memory power, resets, update locks, CRC/test modes, and link transaction state. Misprogramming these can cause blank displays, stuck AUX/I2C transactions, bad hotplug behavior, link-training failures, incorrect CRC validation, or color/scaler corruption.
- Perfmon and debug registers are low-level diagnostic surfaces. Incorrect use can perturb performance counters or read misleading status if counters are not stopped/sampled in the expected sequence.
- Because these are preprocessor macros, there is no type safety. A register offset from this header can be accidentally paired with a mask or shift from a different register and still compile in generic helper code.

## Test Signals

Useful validation signals are compile-time expansion, register-table sanity, and hardware/display smoke coverage:

- Build AMDGPU DC with DCN303 enabled. This proves the register-list macros in resource, IRQ, stream encoder, DPP, OPP, OPTC, AUX, I2C, HPD, VPG, AFMT, and audio code still resolve every referenced `mm...` symbol.
- Static generated-header checks should verify each complete in-range `mm<REGISTER>` definition has a matching `_BASE_IDX` definition and that all referenced names also have matching field definitions in `dcn_3_0_3_sh_mask.h`.
- Mode-set and page-flip smoke tests should exercise DPP color/scaler setup, OPP formatter setup, OTG timing, update locks, vblank/vline/vupdate, and pipe-update status.
- Color-management tests should apply gamma, degamma, gamut remap, shaper LUT, blend gamma, 3D LUT, CSC, HDR multiplier, and cursor color paths on both available DPP instances.
- Link tests should cover HPD0/HPD1 plug/unplug, DDC/I2C EDID reads, AUX0/AUX1 transactions, DP link training, DP MSA/MST/secondary packet paths, HDMI generic/info/audio/ACR packet programming, and AFMT audio state.
- CRC and diagnostic tests should read DPP, OPP pipe, DIG output, and OTG CRC paths, plus display perfmon counters `DC_PERFMON7` through `DC_PERFMON11`.
- Power-management tests should exercise CM, DSCL, OBUF, OPTC/ODM, DIO, VPG, AFMT, and DME memory-power controls across suspend/resume and display on/off transitions.

## Chunk-Specific Summary

Lines 2681-5260 define a broad DCN 3.0.3 MMIO offset surface for the display pipeline from DPP color/scaler blocks through OPP, OPTC, DIO, AUX/I2C/HPD, stream encoder, HDMI/DP transport, VPG, AFMT, and DME blocks. The slice is not executable code; it is a generated hardware ABI used by AMDGPU Display Core register-table construction. Correctness depends on exact offset/base-index values, consistent instance naming, and matching field masks in the companion sh/mask header.

### subset-b-001779: lines 5261-7902

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 5261-7902

## Scope

This chunk is a generated DCN 3.0.3 register offset slice from `dcn_3_0_3_offset.h`. It contains only preprocessor constants: register-address macros and matching `*_BASE_IDX` macros, plus comment markers for register address blocks. There are no C functions, structs, enums, or executable statements in this range.

The range starts in the tail of the `DIG1` HDMI/TMDS encoder block, covers `DP1`, DCIO, GPIO, DSC0/DSC1, writeback, MPC/MPCC/OGAM, HPO HDMI stream encoder, ABM0/ABM1, HDA/Azalia controller and codec-indexed blocks, VGA indexed registers, Azalia stream-indexed windows 0-15, and Azalia endpoint indexed windows 0-3. The final `azf0endpoint3_endpointind` block is truncated by the chunk boundary at `AUDIO_DESCRIPTOR1`, so the next chunk or file-level merge must account for the rest of that endpoint block.

## Purpose And Hardware Surface

The file is part of the low-level ABI between AMDGPU Display Core and DCN 3.0.3 display hardware. Each `mm*` macro gives an MMIO register offset, each `ix*` macro gives an indirect-index register offset, and each `*_BASE_IDX` macro selects the register base aperture used by AMDGPU register access helpers. The constants are paired with the companion `dcn_3_0_3_sh_mask.h` field definitions so driver code can combine address, mask, shift, and base index for register read/modify/write operations.

Major hardware areas in this chunk:

- `DIG1` tail: HDMI audio clock regeneration/status, AFMT control, digital backend enable/control, TMDS control characters, feedback, sync/DC balance, DIG version, lane enable, and force-disable offsets.
- `dce_dc_dio_dp1_dispdec`: DisplayPort link, pixel format, MSA, stream, steer FIFO, DPHY, CRC, fast training, secondary-data packet, audio `M/N`, MSE/MST scheduling, MSO, DSC, metadata, ALPM, and GSP offsets for the DP1 encoder.
- `dce_dc_dcio_dcio_dispdec` and `dce_dc_dcio_dcio_chip_dispdec`: DCIO generic registers, reference clocks, UNIPHY link/xbar, panel power sequencing, backlight PWM, GSL/swaplock pads, DCIO reset, generic/DDC/AUX/HPD GPIO masks/data/enables/readbacks, receive enables, and mutexes.
- `dce_dc_dsc0*` and `dce_dc_dsc1*`: DSC top/control, DSCCIF config, DSCC configuration/status/interrupts, PPS configuration registers 0-22, memory power control, squared-error/max-error/rate-buffer diagnostics, debug index/data buses, and DSC-local perfmon blocks.
- `dce_dc_wb0*`: DWB top controls, flow control, CRC, backpressure, host-read, overflow, soft reset, writeback perfmon, and DWB color-processing registers for HDR multiplier, gamut remap matrices, output gamma LUTs, RAM A/B piecewise regions, and debug access.
- `dce_dc_mpc*`: MPCC0/1 mux/alpha/top/bottom controls, MPCC status, MPCC output gamma and gamut remap banks, MPC global clock/reset/CRC/background/denorm/configuration registers, output CSC, RMU 3D LUT and shaper controls, and MPC perfmon.
- `dce_dc_hpo*`: HPO HDMI AFMT packet/audio/infoframe control, VPG generic packet access/status, DME control/memory control, HPO top clock control, and HPO perfmon.
- `dce_dc_opp_abm0_dispdec` and `dce_dc_opp_abm1_dispdec`: Adaptive backlight management and PWM state for two ABM instances, including ambient/user/target/current levels, final/min duty cycle, ACE slopes/thresholds, luma statistics, histogram controls/results, sample rates, and master lock.
- `dce_dc_hda_*`, `az*`, `azf0stream*`, and `azf0endpoint*`: HDA command/response ring registers, stream/endpoint control windows, codec parameter and converter/pin-control offsets, audio descriptors, sink info, CRC result indices, and per-stream/endpoint indirect register maps.
- `vga_*ind`: legacy VGA sequencer, CRT, graphics, and attribute-controller indirect register offsets.

## Important APIs, Types, And Definitions

There are no callable APIs or types here. The usable surface is the macro naming contract:

- `mmNAME` defines a direct MMIO register offset, for example `mmDP1_DP_LINK_CNTL`, `mmDSCC0_DSCC_CONFIG0`, `mmDWB_ENABLE_CLK_CTRL`, `mmMPC_CLOCK_CONTROL`, or `mmABM0_BL1_PWM_AMBIENT_LIGHT_LEVEL`.
- `mmNAME_BASE_IDX` defines the base-aperture index for that direct register. This chunk uses base index `2` for much of DIO/DCIO/DSC/writeback, base index `3` for MPC/HPO/ABM blocks, and base index `0` for HDA controller-style registers.
- `ixNAME` defines an indirect register index rather than a direct MMIO address. This is used for VGA indexed registers and Azalia codec/stream/endpoint index spaces.
- `// addressBlock:` and `// base address:` comments identify generated register blocks and instance offsets. They are not compiled, but they are important for humans and for comparing the generated header with ASIC register specifications.

Important repeated macro families:

- DP1 offsets include link/stream configuration (`DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`), training/PHY controls (`DP_DPHY_*`, `DP_HBR2_EYE_PATTERN`, fast training status), packet/audio controls (`DP_SEC_*`, `DP_SEC_AUD_N/M`, timestamp), MST/MSE controls (`DP_MSE_*`), DSC/MSO controls (`DP_DSC_CNTL`, `DP_MSO_CNTL*`), and metadata/ALPM/GSP controls.
- DSC0 and DSC1 are parallel instances. Both expose top, DSCCIF, DSCC, `PPS_CONFIG0` through `PPS_CONFIG22`, rate-buffer diagnostics, error counters, debug index/data, and perfmon offsets. Instance 1 has the same logical layout shifted by its block base.
- DWB top and DWBCP offsets split capture plumbing from color processing. The top block handles enable, flow, window/source sizing, CRC, overflow, reset, and backpressure. The DWBCP block contains HDR multiplier, gamut remap matrices, OGAM LUT index/data/control, per-channel RAM A/B slope/base/end/offset/region registers, debug controls, and gamut remap A/B matrix coefficients.
- MPCC0 and MPCC1 contain per-compositor-combiner controls, while MPCC_OGAM0 and MPCC_OGAM1 mirror large output gamma/gamut-remap banks for two MPCC OGAM instances. MPC CFG/OCSC/RMU then provide global composition, output color space conversion, and 3D LUT/shaper state.
- Perfmon blocks use the same register pattern across DSC, writeback, MPC, and HPO: `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`.
- HDA/Azalia direct registers include CORB/RIRB pointers and base addresses, wall clock, codec read/write command/data, stream control/status, CRC controls, and endpoint index/data windows. The `ixAZF0STREAM*` and `ixAZF0ENDPOINT*` families then define the per-stream and per-endpoint codec register indices addressed through those windows.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when included C code uses these offsets through AMDGPU's register helper layer. A typical path is:

1. DCN 3.0.3-specific code includes `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h`.
2. Resource, IRQ, DMUB, or block-specific register tables bind symbolic names to offsets, base indices, shifts, and masks.
3. Runtime code calls helpers such as `REG_GET`, `REG_SET`, or `REG_UPDATE` through per-block register structures.
4. The hardware register state persists in MMIO or indirect-indexed register files until overwritten, acknowledged, power-gated, reset, or changed by firmware/hardware.

The state represented by this chunk is hardware-backed:

- DP1 state controls active link formatting, training, stream timing, MSA/MST/MSO/DSC metadata, audio secondary packets, and diagnostic CRC/training status.
- DCIO/GPIO state controls physical display IO resources: reference clocks, lane routing, panel sequencing, backlight PWM, AUX/DDC/HPD GPIO ownership, and reset/pad behavior.
- DSC state controls display stream compression programming, PPS payloads, memory power, interrupt/status behavior, and compression diagnostics.
- DWB and DWBCP state controls capture/writeback enablement, flow/window sizing, CRC and overflow reporting, output color transforms, and output gamma LUT contents.
- MPC/MPCC/OGAM/OCSC/RMU state controls compositor routing, alpha/blending, output color conversion, output gamma, gamut remap, 3D LUT, CRC, and performance counters.
- HPO/AFMT/VPG/DME state controls high-performance HDMI packet generation, audio/infoframe routing, generic packets, DME memory/control, clocks, and perfmon counters.
- ABM state tracks brightness policy inputs, PWM output levels, luma/histogram samples, ACE configuration, sample rates, and register-lock state.
- HDA/Azalia state includes host command/response rings, stream formatting and routing, endpoint pin/converter controls, audio descriptors, sink information, hotplug/unsolicited response controls, CRC readbacks, and format/audio-enable interrupt statuses.
- VGA and Azalia `ix*` definitions are indirect-indexed state rather than independent direct MMIO registers; callers must select the correct index/data window before reading or writing.

The macros themselves do not encode ordering, locking, range checks, or ownership. Callers must still sequence programming according to the hardware block rules, such as disabling a stream before reprogramming DP link state, respecting panel/backlight power sequencing, loading DSC PPS registers coherently, updating writeback or gamma LUTs at safe update points, and using HDA command/response rings in the expected producer/consumer order.

## Dependencies And Integration Points

This header is consumed by DCN 3.0.3 display code under `drivers/gpu/drm/amd/display`. In this tree it is included by:

- `display/dmub/src/dmub_dcn303.c`, together with `dcn_3_0_3_sh_mask.h`, for DCN303 DMUB register access.
- `display/dc/irq/dcn303/irq_service_dcn303.c`, together with the shift/mask header, for DCN303 IRQ-source register definitions.
- `display/dc/resource/dcn303/dcn303_resource.c`, together with the shift/mask header, for DCN303 resource/block register tables.

The important dependencies are:

- The companion `dcn_3_0_3_sh_mask.h` field macros. Offset macros identify registers; field masks/shifts define how to manipulate bits inside those registers.
- AMDGPU Display Core register helper macros and generated register structures. These helpers combine register offset, base index, field mask, and field shift.
- DC block implementations for DP/DIO, DCIO/GPIO, DSC, writeback, MPC/MPCC, HPO HDMI, ABM, and audio. The blocks rely on stable macro names to initialize per-instance register lists.
- Linux DRM/AMDGPU interrupt, hotplug, modeset, audio, writeback, color-management, and diagnostics paths that indirectly program the registers represented here.
- ASIC register generation inputs. Because this is generated data, the authoritative source is the hardware register specification, not local hand-written logic.

## Risks And Maintenance Notes

- Numeric drift is the main risk. A single wrong offset or base index can make a valid register helper access a different hardware register, which may silently corrupt unrelated display state.
- Instance symmetry is dense. DP, DSC, ABM, MPCC OGAM, stream, and endpoint blocks repeat similar names with instance numbers. Copying an offset or base index across instances without validating the generated value can break only one pipe/stream/endpoint and be hard to isolate.
- Direct `mm*` and indirect `ix*` macros are not interchangeable. Using an `ixAZF0ENDPOINT*` or VGA indexed value as a direct MMIO address would target the wrong aperture.
- The chunk starts and ends mid-logical-block. `DIG1` context begins before line 5261, and endpoint3 continues after line 7902. File-level research must merge neighboring chunks before drawing complete per-block conclusions.
- Address and field definitions are split across headers. Updating an offset without the matching `*_sh_mask.h` field definitions, or vice versa, can compile but produce broken read/modify/write behavior.
- Hardware sequencing is external to this header. The constants allow access to reset, power, clock, panel, PWM, LUT, and audio command registers, but they do not prevent unsafe writes during active scanout, link training, capture, or codec command processing.
- HDA/Azalia and VGA blocks include overlapping index/data windows and legacy-style aliases. Read/write side effects depend on the selected index and on whether the access is through controller, endpoint, stream, or codec-indirect space.
- Many offsets touch visible-output behavior: backlight PWM, ABM, color matrices, gamma LUTs, DSC PPS, stream metadata, and audio routing. Misprogramming can cause black screens, visible color errors, link failures, audio loss, or interrupt storms.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware smoke coverage:

- Build AMDGPU with DCN 3.0.3 support and ensure all DCN303 resource, IRQ, and DMUB register tables compile against these macro names.
- Compare this header and `dcn_3_0_3_sh_mask.h` against the ASIC register source to verify each register has the expected offset, base index, and field layout.
- Exercise DP1 modesets, link training, MST/MSO/DSC paths, audio secondary-data packets, and metadata packet programming while checking for link-training, CRC, or packet-status errors.
- Test DCIO hotplug, AUX/DDC transactions, panel power sequencing, backlight PWM updates, and GPIO ownership/readback paths.
- Run DSC-enabled display modes on both DSC instances and check PPS programming, compression status, underflow/interrupt status, and DSC perfmon readback.
- Exercise writeback capture through DWB, including window/source sizing, overflow reporting, CRC, and DWB color-processing/LUT paths.
- Validate MPC/MPCC color-management paths with blend, OCSC, OGAM, gamut remap, shaper, and 3D LUT programming, including CRC or visual test patterns where available.
- Exercise HPO HDMI AFMT/VPG/DME packet generation and HPO perfmon counters.
- Test ABM0/ABM1 brightness transitions, ambient/user/target level updates, histogram/luma statistics, and register-lock behavior.
- Validate HDA/Azalia audio playback, stream format changes, endpoint pin sense/hotplug, unsolicited responses, audio descriptor/sink-info access, and codec command/response ring behavior.

## Chunk-Specific Summary

Lines 5261-7902 define register offsets and base indices for a broad DCN 3.0.3 display hardware surface rather than executable behavior. The most important responsibilities in this slice are DP1 link/packet/audio state, DCIO/GPIO/panel/backlight control, DSC0/1 compression programming, writeback and DWB color processing, MPC/MPCC color and composition state, HPO HDMI packet generation, ABM brightness policy, and HDA/Azalia/VGA indirect register maps. Correctness depends on exact generated offsets, correct base-index selection, and consistent use with companion shift/mask definitions and block-specific register access sequencing.

### subset-b-001780: lines 7903-8471

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 7903-8471

## Scope

This chunk is the closing segment of the generated AMD DCN 3.0.3 register-offset header. It contains preprocessor constants only: symbolic indirect-register indices for Azalia/HD-audio codec endpoint windows. The assigned range spans 569 source lines, with 519 `#define` entries, 335 output-endpoint index definitions, 184 input-endpoint index definitions, 12 visible `addressBlock` comments, and the file's final `#endif`.

The chunk starts inside the `azf0endpoint3_endpointind` output endpoint block, at `AUDIO_DESCRIPTOR2`; the beginning of endpoint3, plus endpoint0 through endpoint2, are in prior chunks. The range then covers full output endpoint blocks 4 through 7, full input endpoint blocks 0 through 7, and closes the include guard.

## Purpose

The purpose of this header segment is to expose hardware-defined Azalia codec endpoint register indices for the DCN 3.0.3 AMDGPU display path. These `ix...` constants are the values written to each endpoint's `AZALIA_F0_CODEC_ENDPOINT_INDEX` or `AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` register before reading or writing the paired endpoint data register.

The covered surface is display-audio related rather than filesystem logic despite the repository path prefix. It describes HDMI/DP audio codec widgets associated with display outputs and input/audio-capture style endpoint windows. The constants let shared DCE/DCN audio helpers address codec verb-like endpoint registers without embedding raw numeric index values in runtime code.

## Address Blocks And Register Surface

Visible output endpoint blocks:

- Tail of `azf0endpoint3_endpointind`: output endpoint 3 pin-control descriptors, sink info, hot-plug/audio enable, LPIB, coding/format status, and interrupt status indices.
- `azf0endpoint4_endpointind` through `azf0endpoint7_endpointind`: complete output endpoint blocks, each with converter parameter/control indices from `0x0001` through `0x000e` and pin-control/status indices from `0x0020` through `0x006e`.

Visible input endpoint blocks:

- `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`: complete input endpoint blocks. Each block has input converter indices `0x0001` through `0x0006`, input pin capability/sense/widget indices `0x0020` through `0x0024`, multichannel/HBR indices `0x0036` through `0x0038`, channel allocation and hot-plug/configuration indices `0x0053` through `0x0056`, LPIB snapshot/readback indices `0x0064` through `0x0066`, and input status/infoframe indices `0x0067` and `0x0068`.

Companion direct MMIO addresses for these indirect windows are defined earlier in the same header. For example, output endpoint 3 through 7 endpoint-index registers are `mmAZF0ENDPOINT3_AZALIA_F0_CODEC_ENDPOINT_INDEX` through `mmAZF0ENDPOINT7_AZALIA_F0_CODEC_ENDPOINT_INDEX`, while input endpoint 0 through 7 endpoint-index registers are `mmAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` through `mmAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX`.

## Important Macros And Register Families

The `ixAZF0ENDPOINT[3-7]_AZALIA_F0_CODEC_CONVERTER_*` constants describe output converter widgets. They include audio widget capabilities, converter format, channel/stream ID, digital converter control, supported stream formats, supported sample sizes/rates, stripe control, ramp rate, GTC embedding, and GTC counter delta/min/max indices. These are per-endpoint offsets within an indirect Azalia endpoint address space, not absolute MMIO addresses.

The `ixAZF0ENDPOINT[3-7]_AZALIA_F0_CODEC_PIN_*` and `...PIN_CONTROL_*` constants describe output pin widgets. The visible families cover pin capabilities and sense, widget control, channel/speaker allocation, audio descriptors 0-13, multichannel enable/mode, lip-sync response, HBR response, sink info 0-8, hot-plug control, unsolicited response force, response configuration default, channel-status override registers 0-8, association info, digital output status, LPIB snapshot/readback, coding type, format-changed status, wireless display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status.

The `ixAZF0INPUTENDPOINT[0-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_*` constants mirror the converter capability and stream-format surface for input endpoints, but the input converter block is smaller: it does not include the output-only stripe, ramp, or GTC delta indices present in the output endpoint blocks.

The `ixAZF0INPUTENDPOINT[0-7]_AZALIA_F0_CODEC_INPUT_PIN_*` constants describe input pin widgets. These include input pin capabilities and sense, widget control, multichannel enables, HBR response, channel allocation, hot-plug control, unsolicited response force, response configuration default, LPIB snapshot/readback, input activity/status control, and audio infoframe readback.

The repeated numeric layout is a key property. Output endpoints use the same indirect index values across endpoint instances, and input endpoints likewise repeat a smaller common layout across input instances. This lets higher-level code combine an endpoint instance's MMIO index/data pair with a common indirect register number.

## Control Flow And Runtime Behavior

There is no executable C control flow in this chunk. Runtime behavior is indirect through register helpers that consume these constants.

The relevant flow in the AMD display code is:

1. DCN 3.0.3 resource construction includes `dcn/dcn_3_0_3_offset.h` and `dcn/dcn_3_0_3_sh_mask.h`.
2. `dcn303_resource.c` builds `audio_regs[]` using `AUD_COMMON_REG_LIST(id)`, which expands through `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)` from `dce_audio.h`.
3. `dcn303_create_audio()` passes the selected register pair plus shift/mask tables into `dce_audio_create()`.
4. `dce_audio.c` performs indirect Azalia access by writing a register index to `AZALIA_F0_CODEC_ENDPOINT_INDEX` and then reading or writing `AZALIA_F0_CODEC_ENDPOINT_DATA`.

The output endpoint `ix...` constants in this chunk are the values that can be written in step 4 for the matching endpoint window. Although the DCN303 resource file creates `audio_regs[]` entries for instances 0 through 6, `res_cap_dcn303.num_audio` is 2, so only the active resource count is normally instantiated by the DC resource pool. The extra endpoint macros still remain part of the generated hardware namespace and may be needed for ASIC variants, diagnostics, or shared generated-header consistency.

Input endpoint constants are not wired by the same `dce_audio` helper path visible in `dcn303_resource.c`, which uses output `AZF0ENDPOINT` windows. They expose the hardware's input endpoint indirect register map for consumers that need capture/status/infoframe surfaces, even if no local DCN303 resource constructor in the inspected code instantiates them directly.

## State And Persistence

The macros themselves hold no state and allocate no storage. They name persistent hardware registers inside indirect endpoint address spaces. When driver code writes through an endpoint index/data pair, the target state persists in the audio codec/display hardware until changed by another write, reset, power transition, suspend/resume reinitialization, or mode-set/audio reprogramming.

Important state classes represented by this chunk:

- Audio format and stream state: converter format, stream ID, digital converter, supported formats/rates, coding type, and format-changed status control how the endpoint advertises and tracks the active audio stream.
- Sink capability state: audio descriptor registers, sink info registers, speaker/channel allocation, HBR capability, lip-sync response, and response configuration default represent EDID/ELD-derived or hardware-exposed capabilities that userspace and the audio stack depend on.
- Hot-plug and unsolicited response state: hot-plug control, pin sense, unsolicited response, and forced unsolicited response indices participate in connector/audio-jack change reporting.
- Runtime position state: LPIB snapshot control, LPIB, and LPIB timer snapshot expose link-position and timing state. Snapshot lock and timer semantics are defined by companion shift/mask registers and hardware documentation, not by this offset file alone.
- Interrupt/status state: audio enabled, disabled, and format-changed interrupt status indices expose latched events for output endpoints; input status control and infoframe indices expose activity and channel-layout changes for input endpoints.
- Channel-status override state: output endpoint channel-status override indices 0-8 are persistent hardware registers that can affect the channel-status bits sent with digital audio.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_3_0_3_offset.h` for the direct MMIO addresses of the endpoint index/data windows, and on `dcn_3_0_3_sh_mask.h` for the bitfields inside both the direct index/data registers and the indirect endpoint registers. It is included by at least the DCN303 resource, IRQ, and DMUB source files, although the audio endpoint constants are most directly relevant to the resource/audio path.

Primary integration points:

- `display/dc/resource/dcn303/dcn303_resource.c`: includes the generated DCN 3.0.3 headers, declares `res_cap_dcn303.num_audio = 2`, constructs `audio_regs[]`, and creates DCE audio objects through `dce_audio_create()`.
- `display/dc/dce/dce_audio.h`: defines `AUD_COMMON_REG_LIST(id)` and the shift/mask table layout used for endpoint index/data access.
- `display/dc/dce/dce_audio.c`: implements indirect Azalia register access by writing `AZALIA_ENDPOINT_REG_INDEX` and then reading/writing `AZALIA_ENDPOINT_REG_DATA`.
- `display/dc/irq/dcn303/irq_service_dcn303.c` and `display/dmub/src/dmub_dcn303.c`: include the same generated offset/mask headers for DCN303 register table construction, though this particular chunk has no obvious IRQ or DMUB-specific endpoint consumer in the inspected source.
- Companion generated enum headers such as `soc21_enum.h`, `soc24_enum.h`, `navi10_enum.h`, and `vega10_enum.h` define symbolic enum values for related Azalia input endpoint fields.

Because this is a generated public include inside AMDGPU, compile-time consumers depend on exact macro spelling. A missing or renamed `ix...` definition can break register-table builds; an incorrect value can silently redirect an indirect read/write to the wrong Azalia endpoint register.

## Risks And Edge Cases

- Generated-header drift is the main risk. If an `ix` value is wrong, audio code can program the wrong indirect endpoint register while all C code still compiles.
- The assigned range starts mid-block. Endpoint3 converter, capability, pin sense, widget control, channel speaker, and descriptor0/descriptor1 definitions are above line 7903. The final per-file report must merge adjacent chunks before treating endpoint3 as complete.
- The range ends at `#endif`. There is no following chunk for this source file's include guard, but there may be adjacent chunks that complete the earlier endpoint blocks.
- Output and input endpoint families look similar but are not identical. Input endpoints omit several output-only converter controls and audio descriptor/sink-info/channel-status override families. Scripts that assume a single common endpoint layout across both families may produce invalid accesses.
- Numeric index reuse is intentional across endpoint instances. A deduplication tool must preserve the endpoint instance prefix (`AZF0ENDPOINT4`, `AZF0INPUTENDPOINT4`, etc.) because the same index value targets different hardware windows depending on which direct MMIO index/data pair is used.
- DCN303 exposes more generated endpoint definitions than the resource pool normally instantiates (`num_audio = 2`). Reviewers should distinguish generated hardware addressability from runtime resource count.
- Indirect register programming is sequencing-sensitive. The offset header does not encode whether a target register is read-only, write-one-to-clear, self-clearing, sticky, or safe only while audio is disabled.
- Status and interrupt registers can interact with hot-plug, audio enable/disable, and format-change handling. Incorrect polling or acknowledgement behavior may cause missed audio state changes or repeated interrupts even when the index constants are correct.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage for the DCN303 display resource path, especially `dcn303_resource.c`, `dce_audio.h`, and `dce_audio.c`, to catch missing endpoint index/data register macros and shift/mask names.
- Generated-header consistency checks verifying that endpoint blocks 4-7 have identical output indirect index layouts, input endpoint blocks 0-7 have identical input layouts, index values remain within the expected `0x0001`-`0x006e` range, and every indirect register with bitfields has corresponding entries in `dcn_3_0_3_sh_mask.h`.
- HDMI/DP audio mode-set tests that exercise audio enable, stream format programming, channel/speaker allocation, audio descriptors, HBR support, lip-sync fields, and hot-plug audio state.
- ELD/sink-capability tests that compare descriptor and sink-info programming/readback against monitor EDID/ELD expectations.
- Suspend/resume and GPU reset tests that verify audio endpoint state is restored and stale format-change or enable/disable status does not survive incorrectly.
- Interrupt/status tests for audio enabled, disabled, and format-changed events, plus unsolicited response and pin-sense behavior across display hot-plug.
- Diagnostic readback tests for LPIB snapshot/timer values and input endpoint activity/infoframe fields if input endpoint surfaces are used on the target ASIC.

## Open Questions For Merge Lane

- Merge the previous chunk to recover the start of `azf0endpoint3_endpointind` and confirm endpoint3 has the same full output layout as endpoints 4-7.
- Confirm whether endpoint7 output and input blocks represent usable DCN303 hardware on all supported ASICs or are generated superset definitions beyond the normal `num_audio = 2` resource count.
- Identify any non-DC resource or firmware diagnostic path that uses the `AZF0INPUTENDPOINT[0-7]` indirect indices, since the inspected `dce_audio` path is output-endpoint oriented.
