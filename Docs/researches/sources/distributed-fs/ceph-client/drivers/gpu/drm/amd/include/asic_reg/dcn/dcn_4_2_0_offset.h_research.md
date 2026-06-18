# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002211`: lines 1-2953, `Docs/researches/chunks/subset-b-002211_research.md`
- `subset-b-002212`: lines 2954-5582, `Docs/researches/chunks/subset-b-002212_research.md`
- `subset-b-002213`: lines 5583-8099, `Docs/researches/chunks/subset-b-002213_research.md`
- `subset-b-002214`: lines 8100-10752, `Docs/researches/chunks/subset-b-002214_research.md`
- `subset-b-002215`: lines 10753-13311, `Docs/researches/chunks/subset-b-002215_research.md`
- `subset-b-002216`: lines 13312-15838, `Docs/researches/chunks/subset-b-002216_research.md`
- `subset-b-002217`: lines 15839-17880, `Docs/researches/chunks/subset-b-002217_research.md`

## Chunk Research

### subset-b-002211: lines 1-2953

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 1-2953

## Purpose

This chunk is the opening portion of the generated DCN 4.2.0 register offset header for AMD display hardware. It exports numeric register offsets and indirect-register indices for display core, audio, link, debug, clock, DSC, and USB4/DPIA blocks. The header is pure hardware contract data: consumers include it, combine `reg*` symbols with a base segment selected by each `*_BASE_IDX`, and pair the resulting address with field shifts/masks from `dcn_4_2_0_sh_mask.h`.

The slice starts with the MIT/SPDX banner and include guard, then defines 2,284 preprocessor symbols across 124 address blocks. Of those, 396 are direct `reg*` offset or `reg*_BASE_IDX` definitions and 1,887 are `ix*` indirect indices. The extra counted symbol is the include guard macro. The first major group covers HDA/Azalia controller command and response rings, debug buses, DP/DIG/AUX/HPD debug indices, stream/link encoder debug indices, Azalia audio endpoint and stream indices, DSC/DPIA debug indices, DCE HDA direct offsets, and DCCG clock-generator offsets. The final lines in this chunk enter the Azalia F2 input endpoint codec indirect table and stop at `ixAZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE`.

## Important APIs, Types, And Macros

This file does not define C functions or structs. Its exported API is the preprocessor namespace consumed by AMDGPU display register helper macros.

- `regAZCONTROLLER0_*` and later `regAZENDPOINT0_*`, `regAZINPUTENDPOINT0_*`, `regAZROOT0_*`, and `regAZSTREAM0..7_*` define direct offsets for HDA/Azalia controller, endpoint, root, and stream access registers. Each has a companion `_BASE_IDX` used to choose the DCN base segment.
- `ix*` symbols define indirect register indices for debug buses or codec tables. Examples include `ixDP0_DP_DEBUG_*`, `ixAZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_*`, `ixDSCC_DEBUG_*`, and `ixDPIA_PORT_AUX0_DPIA_PORT_AUX_TEST_DEBUG*`.
- DCCG direct offsets such as `regDCCG_GATE_DISABLE_CNTL*`, `regDPPCLK*_DTO_PARAM`, `regSYMCLK*_CLOCK_ENABLE`, `regDCCG_AUDIO_DTO*_PHASE`, `regDCCG_AUDIO_DTO*_MODULE`, and `regDENTIST_DISPCLK_CNTL` supply the address side of display clock programming.
- The value of `_BASE_IDX` is semantically part of the register address. DCN 4.2 code maps these segment indices through `ctx->dcn_reg_offsets[seg]` or hard-coded `DCN_BASE__INST0_SEG*` constants before adding the raw offset.
- The matching field macros live in `dcn_4_2_0_sh_mask.h`. Consumers normally access these constants through `SR`, `SRI`, `SRI_ARR`, `REG_OFFSET_EXP`, `FD_MASK`, `FD_SHIFT`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and related helper macros rather than spelling the offsets directly.

Representative address-block coverage in this chunk:

- HDA/Azalia controller and codec blocks: `dce_dc_hda_azcontroller_azdec`, `azf0stream0..15_streamind`, `azf0endpoint0..7_endpointind`, `azf0inputendpoint0..7_inputendpointind`, `azendpoint_descriptorind`, `dce_dc_hda_azendpoint_azdec`, `dce_dc_hda_azinputendpoint_azdec`, `dce_dc_hda_azroot_azdec`, `dce_dc_hda_azstream0..7_azdec`, `azroot_f2codecind`, `azendpoint_f2codecind`, and the start of `azinputendpoint_f2codecind`.
- Display/link diagnostics: `dc_perfmon`, `mcif_wb0`, `hubbub`, `odm0..3`, `rbbmif`, `ihc`, `dmu_misc`, `dc_pg`, `dp0..4`, `dig0..4`, `dio_misc`, `apg`, `dcoh_top`, `hpo_top`, HDMI stream/link/FRL debug, DP stream/sym32/link encoder debug, and DP DPHY sym32 debug blocks.
- Connector and sideband diagnostics: `dp_aux0..4`, `hpd0..4`, and `dpia_port0..5`, `dpia_port_ml0..5`, `dpia_port_aux0..5`, plus `dpia_mu0`.
- Compression and clock blocks: `dscc`, `dscc_dispclk`, `dsccif`, `dsc_top`, `dce_dc_dccg_dccg_dispdec`, and `dce_dc_dccg_dccg_dfs_dispdec`.

## Control Flow

There is no executable control flow in the header. The runtime flow is created by consumers that expand register-list macros at compile time:

1. DCN 4.2 resource construction includes this header and `dcn_4_2_0_sh_mask.h`.
2. Resource macros such as `SR`, `SRI`, `SRI_ARR`, and `SR_ARR` add the appropriate base segment to `reg*` offsets and store the results in per-block register tables.
3. Hardware objects such as stream encoders, link encoders, AUX, HPD, HPO encoders, hubbub, DCCG, DPP, HUBP, and DSC receive those tables during resource-pool creation.
4. Runtime paths call generic register helpers through those tables. The helpers operate on the resolved offsets and the matching field shifts/masks.
5. For indirect tables, common code first writes an index register and then reads or writes a data register. `dce_audio.c` uses this pattern for Azalia endpoint codec registers through `AZ_REG_READ()` and `AZ_REG_WRITE()`.

Specific DCN 4.2 consumers found in this tree include `dmub_dcn42.c`, which initializes DMUB register offsets with `REG_OFFSET_EXP`; `dcn42_resource.c`, which builds the main DC resource register tables; `dcn42_clk_mgr.c`, which uses DCN and CLKIP base mappings for clock-manager registers; `hw_translate_dcn42.c`, which translates HPD/DDC GPIO register offsets to DAL GPIO IDs; and `irq_service_dcn42.c`, which includes the same offsets for DCN 4.2 IRQ handling.

## State And Persistence

The header itself is stateless. All persistence is in hardware registers reached through the constants:

- HDA/Azalia controller state includes CORB/RIRB pointers, command status, DMA position base, immediate command/response interfaces, stream descriptors, codec function parameters, endpoint pin controls, audio descriptors, sink info, hotplug control, LPIB snapshots, format-change status, and audio enable/disable interrupt status.
- DCCG state includes clock-gating controls, display/DPP/DSC clock DTO parameters, symbol-clock enables, soft reset, audio DTO source/module/phase, vsync latch values, and Dentist clock divider control.
- AUX, HPD, DP/DIG, HDMI, DPHY, DSC, DPIA, and debug-indirect indices expose diagnostic or sideband state selected through each block's indirect debug mechanism.
- Hardware state survives as long as the relevant IP block remains powered and is otherwise reset or reprogrammed by display mode set, audio setup, DMUB boot/reset, suspend/resume, or power-management sequencing. There is no filesystem persistence.

## Dependencies And Integration Points

The main dependency is strict naming agreement between this generated offset header and the surrounding AMD display macro ecosystem:

- `dcn_4_2_0_sh_mask.h` must provide matching field masks and shifts for the same register names.
- DCN 4.2 resource code maps `_BASE_IDX` values through `ctx->dcn_reg_offsets[]`; standalone code such as GPIO translation and clock manager also defines the base segment constants it needs.
- `display/dmub/src/dmub_dcn42.c` consumes offsets for DMUB initialization, reset, boot options, framebuffer base/offset reads, scratch registers, inbox/outbox pointers, and related DMCUB control registers.
- `display/dc/resource/dcn42/dcn42_resource.c` consumes the header to initialize AUX, HPD, stream encoder, link encoder, HPO stream/link encoder, DPP, HUBP, hubbub, DCCG, DSC, and other register structures.
- `display/dc/dce/dce_audio.c` and `display/dc/dce/dce_audio.h` consume Azalia endpoint/root/function and DCCG audio DTO offsets to configure HDMI/DP audio, write sink audio information, audio descriptors, ACP support, HBR/lipsync, hotplug, and audio DTO clocks.
- `display/dc/gpio/dcn42/hw_translate_dcn42.c` uses the same offset scheme to convert HPD and DDC register addresses into GPIO IDs and line numbers.
- `display/dc/irq/dcn42/irq_service_dcn42.c` integrates the register namespace with HPD, HPDRX, vblank, vline, page-flip, vupdate, and DMCUB outbox IRQ mapping.
- DPIA and AUX constants connect to USB4 DisplayPort tunneling code paths, DMUB DPIA commands, bandwidth allocation notifications, and AUX-over-DPIA transactions.

## Risks

- Offset drift is a hardware-contract failure. A wrong `reg*` value or `_BASE_IDX` can direct a `REG_READ` or `REG_WRITE` to the wrong MMIO address, which may misprogram unrelated display state.
- Indirect index mistakes are difficult to catch at compile time. An incorrect `ixAZF0ENDPOINT*` value can make audio code write the wrong codec node while the C symbols still compile.
- Instance symmetry hides copy errors. DP/DIG/AUX/HPD/DPIA/Azalia endpoint blocks are repeated across instances; a single mismatched instance can only fail on the corresponding connector, stream, audio endpoint, or USB4 tunnel.
- Base segment mismatches are as dangerous as offset mismatches. This chunk uses base indices 0, 1, and 2 in early DCN definitions; consumers must map those to the correct per-ASIC base addresses.
- Debug and diagnostic registers can look low risk but are often used during bring-up, validation, power debugging, and failure triage. Bad debug indices reduce observability and can mask real hardware failures.
- DCCG and audio DTO offsets are timing-sensitive. Wrong values can break display clocks, DPP/DSC clock programming, symbol clocks, HDMI/DP audio clocks, or clock-gating behavior.
- The chunk is generated and broad. Manual edits risk creating local divergence from the ASIC register database and from the paired shift/mask header.

## Test Signals

Useful validation signals include:

- Build coverage with `CONFIG_DRM_AMD_DC_DCN4_2` enabled. Missing or renamed macros should fail in DMUB, resource, GPIO, IRQ, clock-manager, and audio register-table initialization.
- Register-table sanity checks or register dumps comparing resolved DCN 4.2 addresses against the ASIC specification, especially for `*_BASE_IDX` segment handling.
- Display bring-up on DCN 4.2 hardware across all physical connectors: HPD detection, DDC/AUX transactions, DP link training, HDMI stream setup, and mode set.
- HDMI/DP audio tests through every exposed audio endpoint: ELD propagation, channel allocation, audio descriptor programming, HBR/lipsync fields, ACP support, hotplug changes, and suspend/resume audio recovery.
- Clock and power-management tests covering DCCG programming, DPPCLK DTO changes, DSC clocks, symbol-clock enable/disable, clock-gating controls, DMUB reset/boot, and runtime power transitions.
- USB4/DPIA tests across six DPIA instances: AUX-over-DPIA access, HPD interrupt enablement, bandwidth allocation notifications, MST slot allocation, and link fallback behavior.
- DSC and HPO validation with high-bandwidth DP modes, because this chunk includes DSCC/DSC debug indices and HPO/link encoder related debug surfaces.

### subset-b-002212: lines 2954-5582

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 2954-5582

## Scope And Purpose

This chunk is a generated AMD DCN 4.2.0 register-offset map for part of the display controller address space. It is not executable code; it provides C preprocessor constants used by AMDGPU display code to translate symbolic register names into MMIO offsets. The matching `dcn_4_2_0_sh_mask.h` header supplies field shifts and masks, while this file supplies register addresses and per-register base-index selectors.

The requested span starts mid-list with 15 `ixAZALIA_F2_CODEC_INPUT_*` indirect-codec definitions, then covers 65 complete `addressBlock` sections. Those sections describe display performance monitors, display microcontroller and power-gating registers, interrupt/status registers, DMCUB firmware interface registers, display writeback and MMHUBBUB registers, HDA/Azalia audio stream and endpoint registers, DCHUBBUB arbitration/VM registers, and HUBP/HUBPREQ/HUBPRET/CURSOR register sets for HUBP instances 0, 1, and the beginning of instance 2.

The chunk contains 2,369 `#define` lines: 1,192 value macros and 1,177 `_BASE_IDX` macros. Most names use the `reg*` prefix and are consumed through normal display MMIO register tables. The opening 15 `ix*` names are indirect-indexed Azalia codec/performance/debug style registers and do not carry `_BASE_IDX` companions.

## Register Families Covered

The major address-block groups in this span are:

- `dce_dc_dccg_dccg_dcperfmon{0,1}_dc_perfmon_dispdec`: `DC_PERFMON0_*` and `DC_PERFMON1_*` control/state/counter registers.
- `dce_dc_dmu_dc_pg_dispdec`: display power-gating domain configuration/status registers, `DCPG_INTERRUPT_*`, `DC_IP_REQUEST_CNTL`, and `LONO_MEM_PWR_REQ_CNTL`.
- `dce_dc_dmu_*`: DMU misc, IHC interrupt/status, FGSEC, RBBMIF, and a large `dce_dc_dmu_dmcub_dispdec` block for DMCUB control, scratch, inbox/outbox, region, timer, interrupt, debug, and fault registers.
- `dce_dc_mmhubbub_*`: MCIF writeback, MMHUBBUB VM/aperture, memory power, and MMHUBBUB perfmon registers.
- `dce_dc_hda_*`: HDA/Azalia stream, endpoint, controller, root, misc, perfmon, and input endpoint register windows.
- `dce_dc_dchubbubl_*`: HUBBUB SDPIF, return path, global DCHUBBUB arbitration/watermark/self-refresh/clock/power/compression-buffer/VM/FAMS registers, DCHUBBUB perfmon, and VMRQ interface registers.
- `dce_dc_dcbubp{0,1,2}_*`: HUBP, HUBPREQ, HUBPRET, cursor, and per-HUBP perfmon register windows. The chunk includes full register sets for instances 0 and 1 and continues through HUBPREQ2 status registers at line 5582.

Repeated instances are encoded by baking the hardware instance number into the macro name. For example, `regHUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS`, `regHUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS`, and `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS` have separate offset constants, and each has a matching `_BASE_IDX` macro selecting the DCN segment base.

## Important APIs, Types, And Macros

This header exports macros only. There are no C functions, structs, enums, or storage definitions in the chunk.

The important macro forms are:

- `reg<NAME>`: a register offset within a DCN base segment. Example families include `regDMCUB_CNTL`, `regDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A`, `regHUBP0_DCHUBP_CNTL`, and `regHUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS`.
- `reg<NAME>_BASE_IDX`: the segment selector used by register-table initialization. In this span almost all regular DCN registers use base index `2`, while the generated form still preserves the selector for code that computes `BASE(reg..._BASE_IDX) + reg...`.
- `ix<NAME>`: indirect-index constants. In this span these are Azalia F2 codec input converter/pin parameter and control indexes, continuing a list that begins before line 2954.
- `addressBlock` comments and `base address` comments: generated metadata documenting the hardware block and instance spacing. Consumers do not parse these comments at runtime, but they are important review signals when validating offsets against ASIC register specifications.

The register families in this chunk are later projected into typed register-table structs in display code. For example, DCN42 resource code defines helpers such as `SR`, `SRI`, `SRI_ARR`, and related macros that expand a symbolic register name into `BASE(reg..._BASE_IDX) + reg...`. DMUB code similarly uses `REG_OFFSET_EXP(reg_name)` to initialize `dmub_srv_dcn42_regs` offsets from this header.

## Control Flow And Runtime Use

There is no local control flow in the header. Runtime control flow appears in consumers:

1. DCN42-specific modules include `dcn/dcn_4_2_0_offset.h` and `dcn/dcn_4_2_0_sh_mask.h`.
2. During construction/init, modules build register tables by combining the segment base selected by `_BASE_IDX` with the offset value from the `reg*` macro.
3. Generic display register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` use those tables plus the shift/mask tables to perform MMIO reads and writes.
4. Higher-level display code programs the hardware: DMCUB boot/reset/mailbox setup, HUBBUB watermarks and VM configuration, HUBP surface address/pitch/format/deadline programming, cursor and 3D LUT DMA state, flip handling, power gating, audio stream state, and performance monitoring.

Concrete integration examples from nearby code:

- `display/dmub/src/dmub_dcn42.c` includes this header and initializes `dmub->regs_dcn42` with `REG_OFFSET_EXP`. The DMCUB block in this chunk backs reset, boot options, scratch registers, inbox/outbox pointers, region windows, GPINT, timer, and fault/debug reads.
- `display/dc/resource/dcn42/dcn42_resource.c` includes this header and defines the `BASE`, `SR`, `SRI`, and array helpers used by DCN42 resource construction to fill per-block register structs.
- `display/dc/hubp/dcn42/dcn42_hubp.c` operates on HUBP/HUBPREQ/HUBPRET names represented in this chunk. It programs surface formats, DLG/TTU deadline registers, requestor behavior, cursor-related state, fine-grain clock gating, and 3D LUT DMA-related registers.
- `display/dc/hubbub/dcn42/dcn42_hubbub.c` operates on DCHUBBUB registers from this span to program urgent/stutter watermarks, arbitration timing, self-refresh, VM/aperture, and memory-power behavior.
- `display/dc/irq/dcn42/irq_service_dcn42.c` includes the same offset and mask headers for DCN42 interrupt-service mappings, including vblank/vupdate/flip/HPD/DMCUB outbox sources.

## State And Persistence Behavior

The header itself has no mutable state and persists nothing. Its values become part of the compiled driver image and define the MMIO contract for DCN 4.2 hardware.

At runtime, the register names in this chunk control persistent hardware state for the lifetime of the GPU/display session:

- DMCUB scratch, boot-option, inbox/outbox, region-window, reset, interrupt, and timer registers hold firmware communication state and boot/debug state until reset or power loss.
- HUBBUB and HUBPREQ registers hold display memory-fetch programming: surface addresses, metadata addresses, VMID settings, VM aperture bounds, TLB control, TTU/DLG timing, watermarks, arbitration, self-refresh, MALL, clock gating, and memory power state.
- HUBP/HUBPRET/CURSOR registers hold per-pipe presentation state such as pixel format, surface configuration, cursor position/address/control, detile/decompression behavior, 3D LUT DMA configuration, and per-pipe perfmon state.
- HDA/Azalia stream and endpoint registers hold display-audio stream descriptors, link position/status, endpoint configuration, converter/pin state, and controller/root capabilities.
- Perfmon blocks hold counter selection, state, and counter values. These are volatile but user/debug-visible through driver diagnostics or perf tooling.

Because these constants address live MMIO, a wrong offset is not a local logic bug. It can redirect a read or write to another hardware register, causing hangs, display corruption, missed interrupts, incorrect audio behavior, firmware boot failure, or incorrect power-management state.

## Dependencies And Integration Points

This chunk depends on the generated DCN 4.2 ASIC register specification and on the broader AMD display register framework. Important dependencies are:

- `dcn_4_2_0_sh_mask.h`, which must define field masks and shifts for the same symbolic register names.
- DCN base-address setup, exposed in consumers through `ctx->dcn_reg_offsets[...]` or fixed segment base macros. `_BASE_IDX` values are meaningful only with the correct base table for the ASIC instance.
- `reg_helper.h` and display register helper macros, which combine register offsets with shifts/masks for read-modify-write access.
- DCN42 block constructors and register-list macros in HUBP, HUBBUB, MMHUBBUB, DCCG, clock manager, GPIO, IRQ, DIO, resource, and DMUB code.
- Hardware firmware contracts for DMCUB mailbox/scratch/region registers and audio contracts for HDA/Azalia stream/endpoint registers.
- Linux DRM/AMDGPU display initialization and atomic commit paths, which indirectly rely on these constants when programming planes, flips, watermarks, interrupts, clocks, and link/audio state.

The repeated instance spacing is an important integration signal. In this chunk, HDA stream blocks are spaced by `0x8` for streams 0-7 and again at higher offsets for streams 8-15; HDA endpoints are spaced by `0x18`; HDA input endpoints are spaced by `0x10`; HUBP/HUBPREQ/HUBPRET/CURSOR instances are spaced by `0x370` for instances 0, 1, and 2. If a consumer uses array helpers with the wrong instance name or index, the generated offset still compiles but targets the wrong hardware pipe.

## Risks And Edge Cases

- The requested range starts in the middle of an indirect Azalia block and ends in the middle of the HUBPREQ2 block. This chunk is not a standalone semantic unit for the whole header; adjacent chunks are needed for the beginning/end of those generated lists.
- The file is generated hardware data. Manual edits are high risk because register names and offsets must match the ASIC specification and the sibling mask/shift header exactly.
- `_BASE_IDX` values are as important as the offset values. A correct offset with a wrong base index computes a wrong absolute MMIO address.
- Register families with repeated instances are easy to miswire. HUBP0/HUBPREQ0/HUBPRET0/CURSOR0 and HUBP1/HUBPREQ1/HUBPRET1/CURSOR0 share repeated field names but differ in macro prefixes and offsets.
- Several registers represent paired low/high addresses, such as DMCUB region offsets, DCSURF primary/secondary surface addresses, metadata surface addresses, and VM aperture bounds. Missing one half or swapping high/low names breaks 64-bit addressing.
- DMCUB reset and mailbox registers are tightly ordered by firmware protocols. Incorrect offsets can make firmware stop/reset handshakes time out or make GPINT/inbox/outbox state appear corrupt.
- HUBBUB/HUBPREQ timing registers come from DML calculations. A wrong mapping can compile cleanly but produce underruns, flicker, failed flips, or memory-clock/pstate behavior that only appears under bandwidth stress.
- Some register macros in consumers are optional-gated by checking whether a register-table field is nonzero. A generated zero offset may be valid for a register at block base, so optional checks must be interpreted in the context of the surrounding inherited register tables.
- The opening `ixAZALIA_*` constants do not have `_BASE_IDX` companions because they are indirect indexes, not the normal DCN segment-offset form. Treating them like `reg*` macros would be incorrect.

## Test Signals

Useful validation for this chunk is mostly compile-time, register-table, and hardware/driver integration oriented:

- Build the AMDGPU display code with DCN42 enabled and ensure all symbolic names referenced by DCN42 consumers resolve against `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
- Add or run static checks that every `reg*` macro used in DCN42 register-list macros has a matching `_BASE_IDX` macro and matching shift/mask fields where field operations are used.
- Compare generated offsets and base indexes against the authoritative DCN 4.2 ASIC register database, especially DMCUB, DCHUBBUB, HUBP/HUBPREQ instance spacing, and HDA stream/endpoint spacing.
- Exercise DMCUB reset/release and mailbox paths and watch for timeout, scratch-register, GPINT, inbox/outbox, and firmware-version diagnostics.
- Run display atomic modeset/flip tests across multiple pipes to cover `HUBPREQ0`, `HUBPREQ1`, and `HUBPREQ2` surface-address, flip, DLG/TTU, cursor, and perfmon mappings.
- Stress memory bandwidth, self-refresh, MALL, and UCLK pstate transitions to validate DCHUBBUB and HUBPREQ watermark/arbiter register addressing.
- Exercise display audio over HDMI/DP to validate Azalia stream/endpoint/controller/root register mappings and codec input pin/converter indirect indexes.
- Verify interrupt delivery for vblank, vupdate, page flip, HPD/HPDRX, and DMCUB outbox sources on DCN42 hardware.
- Use debug/perf tooling to read DC_PERFMON, MMHUBBUB, HDA, DCHUBBUB, and HUBP perfmon counters and confirm counters increment for the expected block, not a neighboring instance.

### subset-b-002213: lines 5583-8099

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 5583-8099

## Purpose

This chunk is part of the generated AMDGPU DCN 4.2.0 register-offset header. It defines C preprocessor constants that map display hardware register names to numeric offsets, plus a paired `_BASE_IDX` constant for each register. The values are consumed by DCN 4.2 display code to compute MMIO addresses as `BASE(reg..._BASE_IDX) + reg...`, using the matching `dcn_4_2_0_sh_mask.h` field definitions when individual bitfields are read or written.

The range contains constants only. There are no functions, structs, enums, branches, loops, allocation paths, or direct persistence operations in these lines. Its behavioral role is nevertheless critical: it is the register-address contract for the third HUBP pipe, all visible DPP pipes 0-2, and the beginning of DPP pipe 3.

The requested boundaries are not semantic boundaries. The chunk starts at the tail of `HUBPREQ2`, after earlier `HUBPREQ2` surface and timing registers, and ends inside the `CM3` gamma-correction RAM A sequence at `regCM3_CM_GAMCOR_RAMA_OFFSET_B`; later `CM3` gamma, histogram, memory-power, and debug registers are outside this chunk.

## Covered Register Blocks

The chunk defines 1,197 register-offset constants and 1,196 paired `_BASE_IDX` constants. Every paired base index visible in this range is `2`, meaning the register offset must be resolved through DCN base segment index 2. The only unpaired offset at the exact chunk end is `regCM3_CM_GAMCOR_RAMA_OFFSET_B`, because its `_BASE_IDX` line falls after line 8099.

- Tail of `HUBPREQ2`: `regHUBPREQ2_FLIP_PARAMETERS_5`, `regHUBPREQ2_FLIP_PARAMETERS_6`, `regHUBPREQ2_UCLK_PSTATE_FORCE`, and `regHUBPREQ2_HUBPREQ_STATUS_REG0..2`.
- `HUBPRET2` at address block `dce_dc_dcbubp2_dispdec_hubpret_dispdec`, base `0x6e0`: HUBP return control, memory-power control/status, read-line control, interrupt, read-line value, and status.
- `CURSOR0_2` at address block `dce_dc_dcbubp2_dispdec_cursor0_dispdec`, base `0x6e0`: cursor control, address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power/status, DMDATA programming, and HUBP 3D LUT address/control/DLG parameter registers.
- `DC_PERFMON8` at address block `dce_dc_dcbubp2_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`, base `0x2154`: performance-counter control, state, counter-value, high, and low registers for the pipe-2 HUBP/perfmon block.
- `HUBP3`, `HUBPREQ3`, `HUBPRET3`, `CURSOR0_3`, and `DC_PERFMON9`: the corresponding pipe-3 fetch, request, return, cursor, DMDATA, 3D LUT, and performance-monitor register blocks. `HUBPREQ3` is the largest HUBP block in this chunk, covering surface pitch, VMID, primary/secondary and chroma luma/meta addresses, flip control, in-use/earliest-in-use readbacks, TTU/QoS, VM aperture/TLB controls, prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor settings, memory power, UCLK pstate force, and status registers.
- DPP pipe 0 through pipe 2 complete visible groups: `DPP_TOP0..2`, `CNVC_CFG0..2`, `CM_CUR0..2`, `DSCL0..2`, `CM0..2`, and `DC_PERFMON10..12`.
- DPP pipe 3 partial groups: complete `DPP_TOP3`, `CNVC_CFG3`, `CM_CUR3`, and `DSCL3`, followed by the beginning of `CM3` through gamma-correction RAM A offset B.

## Important APIs, Types, and Macros

There are no callable APIs or types in this header slice. The important interface is the generated macro namespace:

- `reg<block>_<register>` expands to a register offset. Examples include `regHUBPREQ3_DCSURF_PRIMARY_SURFACE_ADDRESS`, `regDSCL2_SCL_MODE`, `regCM0_CM_GAMCOR_LUT_DATA`, and `regCM3_CM_CONTROL`.
- `reg<block>_<register>_BASE_IDX` expands to the base segment selector. In this chunk the visible base index value is consistently `2`.
- Address-block comments such as `// addressBlock: dce_dc_dpp2_dispdec_dscl_dispdec` and `// base address: 0xb58` document the generated hardware block grouping but do not create C symbols.
- DCN 4.2 consumers include `display/dmub/src/dmub_dcn42.c`, `display/dc/resource/dcn42/dcn42_resource.c`, `display/dc/irq/dcn42/irq_service_dcn42.c`, `display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and DCN 4.2 GPIO translation/factory code, all of which include this offset header with the companion shift/mask header.

The broader AMD display code uses helper macros such as `REG_OFFSET_EXP(reg_name) (BASE(reg##reg_name##_BASE_IDX) + reg##reg_name)` and service macros in `dm_services.h` to translate these generated constants into MMIO addresses for register reads, writes, and masked updates.

## Control Flow and Runtime Use

This chunk has no local control flow. Runtime behavior appears when DCN resource construction and block-specific programming tables paste logical register names onto these generated symbols:

1. A DCN 4.2 component includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Register-list macros or per-block register structs select an instance, such as HUBP3, DSCL1, or CM2.
3. The register access helper combines `BASE(reg..._BASE_IDX)` with the `reg...` offset and writes fields using masks from the shift/mask header.
4. Hardware consumes the resulting MMIO programming on update, flip, clock, memory-power, or vblank boundaries, depending on the block.

The most important programming sequences represented by this range are:

- HUBP fetch setup: surface format and tiling are partly outside this chunk for pipe 2, but pipe 3 includes surface address, pitch, viewport, request sizing, VM/TLB, flip, TTU, prefetch, and status addresses needed to fetch scanout surfaces and cursor/DMDATA payloads.
- Cursor setup: `CURSOR0_2` and `CURSOR0_3` provide cursor surface addresses, dimensions, position, hot spot, stereo, and memory-power status offsets.
- DPP conversion and cursor color setup: `CNVC_CFG*` registers cover pixel format, fixed-point bias/scale, color keying, alpha LUTs, pre-dealpha, pre-CSC matrix A/B, coefficient format, pre-degamma, and pre-realpha. `CM_CUR*` covers cursor color and cursor matrix registers inside the DPP color path.
- Scaling and sharpening: `DSCL0..3` cover coefficient RAM access, scaler mode, tap control, 2-tap/manual replicate controls, luma/chroma ratios and initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer data/memory/counter registers, scaler and output-buffer memory power, EASF modes and ring-estimator controls, bilateral-filter PWL segments, image-sharpening mode/delta/noise/LBA controls, and sharpen delta LUT memory power.
- Color management: `CM0..2` are complete in this chunk for post-CSC, bias, gamma-correction LUT and RAM A/B region metadata, HDR multiplier, memory-power/status, dealpha, coefficient format, test-debug, and histogram control/data/status/interrupt registers. `CM3` begins the same pattern but stops during gamma-correction RAM A.
- Perfmon: `DC_PERFMON8..12` expose performance-counter control, state, current value, high, and low registers for HUBP and DPP instances represented here.

## State and Persistence Behavior

The macros themselves are compile-time constants and hold no state. They describe hardware state locations:

- Surface state lives in HUBP/HUBPREQ registers: current and earliest in-use surface addresses, flip-control registers, VM aperture/TLB registers, and timing parameters.
- Cursor and DMDATA state lives in cursor address/control/status registers and may reference GPU memory through programmed addresses.
- Memory-power state is controlled and observed through `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` registers for HUBPREQ, HUBPRET, cursor, DSCL, OBUF, CM, and sharpen LUT memories.
- DPP color and scaler state is stored in hardware registers and indexed LUT memories. Gamma-correction LUT, CM histogram, DSCL coefficient RAM, EASF PWL, and sharpen delta controls must be reprogrammed after hardware reset or power gating if the hardware does not retain them.
- Perfmon counters are transient hardware counters; offset mistakes affect observability rather than persistent storage.

No filesystem or driver-private persistent data is created by this header. Persistence across suspend/resume depends on higher-level DCN state reconstruction using these addresses.

## Dependencies and Integration Points

This file depends on the generated DCN base-address model used by AMD display register helpers. The `_BASE_IDX` constants must match `DCE_BASE` segment definitions and the ASIC's register aperture layout. A wrong base index can redirect otherwise-correct offsets into the wrong MMIO segment.

The field-level interpretation depends on `dcn_4_2_0_sh_mask.h`. Offset and mask headers must be generated from the same register database; mixing DCN 4.2 offsets with a different generation's masks can compile but program incorrect fields.

Integration points include:

- DCN 4.2 DMUB register tables in `display/dmub/src/dmub_dcn42.c`.
- DCN 4.2 display resource construction in `display/dc/resource/dcn42/dcn42_resource.c`.
- DCN 4.2 interrupt, clock manager, and GPIO code that include this header for register access.
- Shared display block implementations for HUBP/HUBPREQ/HUBPRET, DPP top, CNVC, CM cursor, DSCL, CM, and perfmon that are parameterized by generated register tables.
- The Linux AMDGPU display mode-setting path, which ultimately exercises these constants through plane updates, flips, cursor movement, scaling, color management, power management, and debug/perfmon paths.

## Risks and Edge Cases

- Chunk-boundary incompleteness is significant. The first six lines are only the tail of `HUBPREQ2`; the end omits the `_BASE_IDX` for `regCM3_CM_GAMCOR_RAMA_OFFSET_B` and all later `CM3` registers. The merge lane must combine adjacent chunks before making whole-block claims.
- Repeated instance families invite generator or manual-review errors. `HUBP3` must stay paired with `HUBPREQ3`, `HUBPRET3`, `CURSOR0_3`, and `DC_PERFMON9`; DPP instances must keep `DPP_TOPn`, `CNVC_CFGn`, `CM_CURn`, `DSCLn`, `CMn`, and `DC_PERFMON10+n` aligned.
- Offset gaps are intentional in generated hardware maps, for example gaps in `HUBPREQ3` around `DCSURF_FLIP_CONTROL2` to `DCSURF_SURFACE_FLIP_INTERRUPT` and VM aperture/TLB ranges. Treating the list as densely sequential can create false positives in validation scripts.
- Address reuse across logical subregister names is possible elsewhere in the file and should not be normalized away. This chunk primarily presents one offset per visible register symbol, but the generated style relies on symbol identity, not just numeric uniqueness.
- A bad surface-address, pitch, or VM offset can cause scanout corruption, GPU VM faults, black screens, stale flips, or failures isolated to pipe 3.
- A bad scaler, CNVC, or CM offset can produce wrong scaling, clipped or shifted image geometry, bad color conversion/gamma, broken cursor color conversion, histogram readback errors, or DPP CRC mismatches.
- A bad memory-power offset can cause hangs waiting for status convergence, lost LUT contents after power gating, or resume-only display failures.
- A wrong perfmon offset can silently corrupt diagnostics by reading counters from the wrong block.

## Test Signals

Useful validation signals for changes touching these constants include:

- Build coverage for DCN 4.2 display code with both `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h` included, catching missing symbols such as an omitted `_BASE_IDX`.
- Register-table sanity checks that every `reg...` used by DCN 4.2 resource, DMUB, IRQ, clock, GPIO, HUBP, DPP, DSCL, CM, and perfmon code has a matching base index in the full file.
- Plane modeset and page-flip tests on configurations that use HUBP/DPP instance 3, including luma/chroma formats, meta surfaces, VM-backed scanout, SubVP/MALL paths, vblank flips, and UCLK pstate transitions.
- Cursor tests on pipes 2 and 3 covering movement, hot spot, large cursor sizes, stereo fields where supported, and cursor memory power transitions.
- Scaling tests across DPP0-3, including luma/chroma scaling, tap changes, overscan, recout/MPC sizing, line-buffer partitioning, EASF/sharpening paths, and suspend/resume after scaler memory power transitions.
- Color-management tests for DPP0-2 complete CM blocks and the early CM3 path: pre/post CSC, gamma-correction LUT programming, HDR multiplier, dealpha, coefficient-format changes, histogram readback/interrupts, and DPP CRC comparison against expected output.
- Perfmon smoke tests that program `DC_PERFMON8..12`, read low/high/current counter values, and verify counters correspond to the expected HUBP/DPP instance.

### subset-b-002214: lines 8100-10752

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 8100-10752

## Scope

This chunk is a middle slice of the generated AMD DCN 4.2.0 register offset header. It contains only preprocessor metadata: 2,369 `#define` lines, including 1,184 register-offset macros and 1,185 `_BASE_IDX` macros. The one extra base-index macro is the opening boundary line for `regCM3_CM_GAMCOR_RAMA_OFFSET_B_BASE_IDX`; its matching offset macro is immediately before this chunk. All visible `_BASE_IDX` values in this range select DCN base segment `2`.

The range starts inside the `CM3` color-management gamma-correction RAM definitions and ends on the `dce_dc_dio_dig1_dme_dme_dispdec` address-block comment/base-address pair. The actual `DME1` register definitions begin in the following chunk.

## Purpose

The file gives DCN 4.2 display code symbolic names for memory-mapped display ASIC register offsets and the SOC/DCN base segment used to form absolute register addresses. Runtime code combines `regFOO_BASE_IDX` with `ctx->dcn_reg_offsets[]` or compile-time `DCN_BASE__INST0_SEG*` constants and the `regFOO` offset through helper macros such as `SR`, `SRI`, `REG_OFFSET_EXP`, `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

This chunk covers several display-output-facing hardware areas:

- Tail of DPP3 color management: `CM3_CM_GAMCOR_RAMA/RAMB_*`, HDR multiplier, coefficient format, histogram lock/index/data/status, debug registers, and CM memory power/status.
- DPP3 display-performance monitoring through `DC_PERFMON13_*`.
- Display Core Output Hub sideband plumbing: DisplayPort AUX instances `DP_AUX0`-`DP_AUX4`, HPD instances `HPD0`-`HPD4`, DPIA mux instances `DPIA_MUX0`-`DPIA_MUX5`, PHY mux instances `PHY_MUX0`-`PHY_MUX4`, and DCOH top-level control/status registers.
- OPP/output formatting for pipes 0-3: `FMT<n>`, `DPG<n>`, `OPPBUF<n>`, `OPP_PIPE<n>`, `OPP_PIPE_CRC<n>`, OPP top registers, DSCRM instances, and `DC_PERFMON14_*`.
- Output timing/combine control: `ODM0`-`ODM3`, full `OTG0`-`OTG3` timing-generator register sets, OPTC miscellaneous registers, and `DC_PERFMON15_*`.
- DIO common, I2C/DDC, stream-mapper, and performance-monitor registers.
- DIG0 stream encoder and DP0 link encoder registers for HDMI, TMDS, DisplayPort main-link, secondary-data/audio packets, MSA, MST/MSE, MSO, ALPM, GSP, symbol counters, panel replay, and fast training.
- Start of DIG1 sideband/audio packet blocks: `VPG1` generic/ISRC packet registers and `APG1` audio-packet generator registers.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable statements in this range. The exported interface is the generated macro convention:

- `reg<REGISTER>`: the register offset used by DCN 4.2 register helpers.
- `reg<REGISTER>_BASE_IDX`: the index into the DCN base-address table. In this chunk, the value is consistently `2`.

Important macro families include:

- `regCM3_CM_GAMCOR_RAMA/RAMB_*`, `regCM3_CM_HDR_MULT_COEF`, `regCM3_CM_HIST_*`, and `regCM3_CM_MEM_PWR_*` for DPP pipe 3 color/gamma RAM programming, histogram access, and memory power state.
- `regDP_AUX<n>_*` for AUX software transactions, arbitration, interrupt control, low-speed status/data, AUX PHY transmit/receive control, wake control, and wake status.
- `regHPD<n>_DC_HPD_*` for hotplug interrupt/status/filter/toggle and RX interrupt/status registers.
- `regDPIA_MUX<n>_DPIA_MUX_CNTL` and `regPHY_MUX<n>_*` for USB4/DPIA and PHY routing selection/status.
- `regFMT<n>_*`, `regDPG<n>_*`, `regOPPBUF<n>_*`, `regOPP_PIPE<n>_*`, and `regOPP_PIPE_CRC<n>_*` for output formatter clamping, bit depth, dithering seeds, 4:2:0/4:2:2 handling, display-pattern generation, OPP buffering, and CRC capture/readback.
- `regODM<n>_ODM_*` and `regOTG<n>_*` for output data merger state and timing generator totals, sync/blanking, triggers, stereo/interlace, status counters, snapshots, update locks, vertical interrupts, CRC windows/results, static-screen, global sync, vstartup/vupdate/vready, dynamic refresh rate, request control, p-state, and encryption state.
- `regDC_I2C_*` and `regDIO_*` for DDC/I2C transactions, arbitration, DIO power/status/debug, and stream mapping.
- `regDIG0_*` and `regDP0_*` for DIG0 HDMI/TMDS and DP0 DisplayPort link programming, including HDMI info/audio/generic packets, ACR, DP DPHY training/scrambling/CRC, transfer-unit control, secondary-data/audio packet timing, MST/MSE, MSO, ALPM, GSP, symbol counters, and panel replay hooks.
- `regVPG1_*` and `regAPG1_*` for DIG1 generic video packets, ISRC access, audio packet control/debug, IEC 60958 debug registers, audio CRC, ramp generation, and APG memory power/status.

## Control Flow

This header has no local control flow. Runtime sequencing is imposed by AMDGPU display code that token-pastes these macro names into per-block register tables:

1. DCN42 resource, IRQ, GPIO, clock-manager, and DMUB files include `dcn_4_2_0_offset.h` together with `dcn_4_2_0_sh_mask.h`.
2. Register-list macros in block-specific headers are expanded by `SR`, `SRI`, `SRI_ARR`, `REG_OFFSET_EXP`, and related helpers to compute absolute MMIO addresses from `BASE(reg*_BASE_IDX) + reg*`.
3. Higher-level display paths use the generated register tables to program link discovery, AUX/DDC transactions, hotplug handling, timing generators, OPP formatting, stream encoders, DP/HDMI packets, audio packets, CRC diagnostics, and performance counters.

The macros themselves do not express ordering. Consumers must still sequence display clocks, resets, mux selection, AUX/HPD enablement, OPP/OTG update locks, stream-encoder programming, DP link training, HDMI/DP infoframe/audio setup, and interrupt acknowledgement according to DCN 4.2 hardware rules.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It names hardware-backed state in the display engine:

- `CM3` gamma/histogram registers hold color pipeline programming and histogram/debug state for DPP pipe 3 while that block is powered.
- AUX, HPD, DDC/I2C, mux, and DIO registers expose live connector-side control/status, interrupt, arbitration, wake, routing, and transaction state.
- FMT/DPG/OPPBUF/OPP/CRC registers hold output formatter, pattern generation, buffering, CRC capture, and memory-power state for OPP pipes 0-3.
- ODM/OTG/OPTC registers hold live timing state: totals, sync windows, blanking, trigger windows, counters, frame counts, vblank/vline interrupts, update locks, CRC windows/results, DRR parameters, global sync, p-state, and static-screen controls.
- DIG0/DP0/VPG1/APG1 registers hold stream-encoder state for HDMI/TMDS/DisplayPort link formatting, training, secondary-data packets, audio packets, MST/MSO allocation, ALPM/panel replay, symbol counters, and audio-packet diagnostics.
- `DC_PERFMON13`, `DC_PERFMON14`, `DC_PERFMON15`, and DIO perfmon registers expose performance-counter control and readback state.

Persistence is hardware-defined. Configuration fields generally remain until modeset, link retraining, stream disable/enable, suspend/resume, power gating, GPU reset, or driver reinitialization. Status, interrupt, CRC, counter, wake, and transaction fields may be read-only, sticky, self-clearing, write-one-to-clear, double-buffered, or valid only while relevant display clocks and power domains are active. This offset header does not encode those access semantics; the matching shift/mask header and consuming block drivers supply them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h`, which provides field shifts and masks for these offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes this header and expands register lists for DCN42 hardware blocks using `BASE(reg*_BASE_IDX) + reg*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, which uses these offsets and masks for HPD, vblank, vline, vupdate, page-flip, and DMUB outbox interrupt descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c` and `hw_translate_dcn42.c`, which use DCN42 register metadata for GPIO, HPD, DDC, and AUX translation/factory wiring.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which includes the generated DCN42 metadata for clock-manager register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which initializes DMUB register offsets through `REG_OFFSET_EXP`; most DMUB-critical registers are in other chunks, but this file verifies the whole generated header participates in DCN42 DMUB support.

Functional integration points include connector discovery and hotplug, AUX/DDC EDID and DP sideband transactions, USB4/DPIA routing, pipe output formatting, timing generator programming, vblank/vline/DRR behavior, CRC diagnostics, HDMI/DP stream-encoder setup, DP link training, MST/MSO bandwidth allocation, audio/infoframe packet delivery, ALPM/panel replay behavior, and display performance monitoring.

## Risks And Edge Cases

- Offset/base-index macros are untyped preprocessor constants. A wrong value can compile cleanly while directing the driver to a valid but incorrect MMIO address.
- Because every visible `_BASE_IDX` is `2`, an accidental segment change in this range would be suspicious and high impact; it would route register helpers through a different DCN base segment.
- This is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching shift/mask file, firmware expectations, and silicon documentation.
- The chunk begins with a boundary-only `regCM3_CM_GAMCOR_RAMA_OFFSET_B_BASE_IDX` line. Whole-register pair validation must include the previous chunk for that register.
- The chunk ends on the `DME1` address-block comment/base-address pair without the actual `regDME1_*` macros. The following chunk owns those offsets.
- Repeated per-instance families are copy-sensitive. AUX0-4, HPD0-4, FMT/DPG/OPP/OTG0-3, and the DIG/DP instance layout can look structurally identical while carrying instance-specific offset deltas.
- OTG timing, update-lock, vblank/vline interrupt, CRC, and DRR registers are sequencing-sensitive. A misplaced offset can produce blanking errors, missed interrupts, visible timing jitter, bad CRC diagnostics, or failures that appear only during modeset, variable refresh, or suspend/resume.
- AUX/DDC/HPD offsets are connector-discovery critical. Mistakes can appear as failed EDID reads, broken DP link training, missed HPD/HPDRX events, or broken USB4/DPIA routing.
- Stream-encoder packet and audio offsets can cause HDMI/DP sinks to receive bad infoframes, ACR/N/M values, secondary-data packets, MST allocation state, or audio packets without necessarily causing a build failure.
- Perfmon and status registers mix control, sticky status, and readback semantics. Wrong offsets can clear unrelated events or produce misleading diagnostics.

## Test Signals

Useful validation for this chunk combines generated-header consistency checks with DCN42 display behavior:

- Build AMDGPU display with DCN42 enabled. Missing or renamed macros should fail in resource construction, IRQ service, GPIO translation/factory, clock-manager, DMUB, OPP, OPTC, DIO, AUX/I2C, stream-encoder, and audio register-table setup.
- Mechanically verify every `reg*` offset in this range has exactly one matching `reg*_BASE_IDX`, allowing the expected boundary exception for `regCM3_CM_GAMCOR_RAMA_OFFSET_B`.
- Cross-check offset values and base indexes against AMD's DCN 4.2.0 generated register source and compare repeated families against adjacent DCN 4.x headers where the layout should match.
- Exercise connector workflows: HPD/HPDRX interrupts, AUX native transactions, EDID reads over DDC/I2C, USB4/DPIA mux routing, link retraining, wake/status paths, and unplug/replug across suspend/resume.
- Exercise OPP/OTG paths on four pipes: modesets, vblank/vline interrupts, page flips, update locks, static-screen entry/exit, interlace/stereo where supported, CRC capture/readback, DRR/VRR changes, and multi-display synchronization.
- Exercise HDMI and DisplayPort stream-encoder behavior on DIG0/DP0: TMDS and DP link training, MSA programming, secondary-data/infoframe delivery, audio ACR/N/M programming, MST/MSE/MSO allocation, ALPM/panel replay, symbol counters, and fast-training status.
- Monitor kernel logs, IRQ counters, EDID/AUX traces, display CRCs, link-training traces, sink audio enumeration, perfmon readback, and suspend/resume logs for missed interrupts, failed transactions, invalid packets, wrong timing, or resume-only register-restore failures.

## Cross-Chunk Notes

The previous chunk owns the matching offset macro for the first line's `regCM3_CM_GAMCOR_RAMA_OFFSET_B_BASE_IDX` and the earlier `CM3` gamma-control setup. This chunk owns the remaining visible `CM3` gamma/histogram tail, DCOH/AUX/HPD/mux, OPP/OTG, DIO, DIG0/DP0, and DIG1 VPG/APG macro groups. The next chunk begins with the actual `DME1` register macros and continues DIG1/DIO families. The final merged file report should reconcile these boundaries before making complete claims about all DCN 4.2.0 offset families in this header.

### subset-b-002215: lines 10753-13311

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 10753-13311

## Purpose

This chunk is a generated AMD DCN 4.2.0 register offset header slice. It contains no executable C logic; it exports preprocessor constants that map symbolic display-controller register names to MMIO register offsets and base-index selectors. AMDGPU display code pairs these offset macros with the matching `dcn_4_2_0_sh_mask.h` field definitions and generic register helpers to build per-block register tables.

The requested range contains 2,384 `#define` lines: 1,192 register offset macros and 1,192 matching `_BASE_IDX` macros. It starts at the tail of the DIO DME1 block, covers legacy-style DIG/DP encoder instances 1 through 4, covers DSC instances 0 through 3 and their perfmon blocks, covers writeback instance 0, covers DCHVM registers, and then enters the first high-performance DP 2.x output path: HPO stream encoder 0, APG5/DME5/VPG5, DP_SYM32 encoder 0, link encoder 0, and the beginning of DP_DPHY_SYM320.

Although this path is under a local `ceph-client` source mirror, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro naming convention:

- `reg<INSTANCE>_<REGISTER>`: the register's generated offset value.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX`: the register's base-index selector, `2` for every register in this chunk.

Major register groups in this chunk:

- `DME1`: the tail of DIO metadata engine instance 1, with DME control and memory-control offsets.
- `DIG1` through `DIG4`: front-end/back-end digital encoder and HDMI/TMDS register offsets, including FE/BE control, clocks, enable, output CRC, test/random patterns, FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, GC, DB control, ACR values/status, audio control, TMDS control/sync/DC-balancer registers, and DIG version.
- `DP1` through `DP4`: DisplayPort stream/link encoder offsets for each DIO instance, including link control, pixel format, MSA colorimetry/misc/timing, video stream control, steering FIFO, DPHY training/symbol/8b10b/PRBS/scramble/CRC controls and results, TU control, secondary-data/audio/timestamp/packet controls, MSE/MST rate and slot-allocation controls/status, HBLANK, MSO, ALPM, AUX-less ALPM, symbol counters, panel replay, and fast-training registers.
- `VPG2` through `VPG5`: generic packet access/data, GSP frame/immediate update controls, status, memory power, and ISRC access/data windows.
- `APG2` and `APG3`: full audio packet generator control/debug/audio CRC/ramp/memory-power blocks. `APG4` and `APG5` are shorter HPO-adjacent groups with APG control/control2/debug and memory-power offsets.
- `DME2` through `DME5`: metadata-engine control and memory-control offsets.
- `DSC_TOP0` through `DSC_TOP3`, `DSCCIF0` through `DSCCIF3`, and `DSCC0` through `DSCC3`: display stream compression top/interface/compressor offsets for four DSC instances.
- `DC_PERFMON17` through `DC_PERFMON21`: perf-counter and perfmon register offsets attached to DSC and DWB blocks.
- `DWB` and `FC`: writeback top, frame-capture/window, CRC, output, backpressure, host-read, overflow, reset, debug, HDR multiplier, gamut-remap, OGAM LUT, and OGAM RAM A/B curve-region offsets.
- `DCHVM`: display hub virtual-memory control, clock, memory, RIOMMU control, and RIOMMU status offsets.
- `DP_STREAM_ENC0`: HPO DP stream encoder 0 clock, input mux, audio, clock-ramp FIFO status, and spare offsets.
- `DP_SYM32_ENC0`: 32-bit-symbol HPO stream encoder video FIFO, MSA, pixel-format double-buffer, SDP/GSP, audio SDP, metadata packet, stream/VBID/panel replay, CRC, symbol-count, ALPM, memory-power, and spare offsets.
- `DP_LINK_ENC0`: HPO DP link encoder clock-control and spare offsets.
- `DP_DPHY_SYM320`: the beginning of HPO DP DPHY symbol32 lane/VC/eDP/ALPM metadata, through `DP_DPHY_SYM32_ALPM_SLEEP_CONFIG0`.

The DSC compressor groups are dense and user-visible. Each `DSCCn` block exposes configuration/status/interrupt offsets, `DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`, memory-power controls, squared-error and max-absolute-error readbacks, output/rate-buffer fullness readbacks, and debug index/data registers. These offsets are consumed with field masks from the companion shift/mask header to program DSC picture parameter sets and monitor compression health.

The DIO DP groups are structurally repeated across `DP1` through `DP4`. Each instance describes the legacy DP stream/link surface used for link training, main stream attribute programming, secondary-data packets, audio, MST/MSE scheduling, panel replay, ALPM, symbol counting, and PHY diagnostics.

## Control Flow

This header has no runtime control flow. Runtime use follows the AMD display register-table pattern:

1. DCN 4.2 code includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Resource headers and block constructors use token-pasting helpers such as `SR`, `SRI_ARR`, `SRI2_DWB`, `SRI_ARR_DWB`, and `SE_SF`-style field macros to bind generic block register names to generated offsets, base indices, shifts, and masks.
3. Constructed display objects store those tables for encoders, DSC, DWB, HPO stream/link encoders, IRQ/GPIO, clock, and DMUB-facing code.
4. Runtime paths use register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables during modeset, link training, audio/packet setup, DSC programming, writeback capture, hotplug/IRQ handling, and power-management transitions.

The macros themselves do not encode programming order. Sequencing for stream disable/enable, DP link training, DSC PPS updates, DWB update locking, writeback memory programming, DCHVM setup, HPO stream/link allocation, DPHY lane setup, ALPM, and interrupt/status acknowledgement is supplied by consuming driver code and the hardware programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It names hardware-backed state surfaces:

- Digital encoder state for FE/BE enable, clocks, FIFOs, HDMI/TMDS packet generation, audio packets, ACR values, test patterns, and CRC readbacks.
- DisplayPort stream/link state for pixel format, MSA timing/colorimetry, video stream enable, DPHY training/patterns, secondary-data packets, audio timestamps/N/M values, MST/MSE allocation, MSO, ALPM, panel replay, and symbol-count diagnostics.
- Packet and metadata state in VPG/APG/DME blocks, including generic packets, GSP updates, ISRC payload windows, audio packet generation, metadata-engine memory power, and related debug registers.
- DSC state for compressor configuration, status, interrupt registers, PPS payload, memory-power controls, error counters, buffer-fullness counters, and debug buses.
- Perfmon state for attached DSC/DWB performance counters and current-value readbacks.
- DWB/frame-capture state for enable/clock/memory, capture windows, output format, CRC, backpressure counters, host-read controls, overflow state, reset/debug, HDR/gamut remap, and output gamma RAM/LUT programming.
- DCHVM state for display virtual-memory and RIOMMU control/status.
- HPO DP 2.x stream/link state for stream muxing, audio, 32-bit symbol encoder video MSA/pixel/SDP/CRC/ALPM/memory-power controls, link encoder clocks, DPHY enable/status, stream VC rates, slot allocation table entries, eDP ASSR, and initial ALPM sleep configuration.

Persistence and side effects are hardware-defined. Configuration fields usually remain until modeset, block disable, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, CRC, counter, update-pending, overflow, error, and debug fields may be read-only, latched, self-clearing, write-one-to-clear, or valid only while the relevant block is powered and clocked. This generated offset file does not express those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and its companion shift/mask header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h` supplies the matching field positions and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes this header and constructs DCN42 resource tables, including DIG/link encoder mapping, HPO stream encoders, DWB resources, and register/mask/shift tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines the register-list macros that directly expect names from this chunk, including the DIG HDMI/FE list and `DCN42_HPO_DP_STREAM_ENC_REG_LIST_RI(id)` for `DP_STREAM_ENC`, `DP_SYM32_ENC`, and related HPO stream registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c` reads HPO DPHY status, control, slot allocation, and VC-rate registers whose offsets are in the `DP_DPHY_SYM320` portion of this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h` provides the shared HPO link encoder mask/shift list shape that expects `DP_DPHY_SYM320_*` register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h` and DCN42 resource glue consume the DWB/FC offset names through DWB common register-list macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` include the DCN42 generated headers for interrupt/GPIO translation, clock management, and DMUB register access.

Behaviorally, this range is part of several display paths: legacy DIO HDMI/DP stream encoding, DSC compression, writeback capture/color processing, display VM setup, and HPO DP 2.x stream/link encoding. The repeated instance numbering must align with resource-pool capabilities and engine identifiers used by DCN42 resource construction.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index can compile cleanly and only fail as bad MMIO at runtime.
- The file is generated. Manual edits risk divergence from AMD's authoritative register database, the companion shift/mask header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The range starts after the address-block comment for DME1 and only includes its last two registers. It ends inside `DP_DPHY_SYM320`; ALPM wake/control and test-pattern registers continue in the next chunk.
- Repeated instances are copy-sensitive. DIG/DP instances 1-4 and DSC instances 0-3 are structurally similar; an offset error can affect only one connector, one stream encoder, or one DSC pipe.
- Legacy DIO DP and HPO DP 2.x registers coexist in this slice. Consumers must use the right register list for the selected encoder type; mixing `DPn_*` and `DP_SYM32_ENC0`/`DP_DPHY_SYM320` offsets can produce plausible but wrong hardware access.
- DSC PPS offsets must align exactly with the shift/mask definitions. A mismatch can corrupt compressed stream parameters, causing blank displays, decompressor mismatch, underrun/overflow status, or mode-specific visual corruption.
- DWB update, overflow, CRC, OGAM, and backpressure registers are sequencing-sensitive. Bad offsets can silently break capture output, color conversion/gamma, or diagnostics while normal display scanout still works.
- DCHVM and RIOMMU control/status registers are low-level display memory integration points. Incorrect offsets can appear as page faults, blank display after resume, writeback failures, or DMUB/display-memory handoff issues.
- HPO DPHY VC-rate and SAT registers are link-bandwidth critical. Wrong offsets can break MST/USB4-style stream allocation, link bring-up, ALPM, panel replay, eDP ASSR handling, or only high-bandwidth DP modes.
- Base-index selectors are all `2` in this range. A generator or merge error that changes an offset without the correct base index would route generic register helpers to the wrong address aperture.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display coverage:

- Build AMDGPU display with DCN42 enabled. Missing or renamed macros should fail in DCN42 resource, HPO, IRQ, GPIO, clock-manager, DMUB, DSC, or DWB table construction.
- Mechanically verify every `reg...` offset in this chunk has exactly one adjacent matching `reg..._BASE_IDX` definition and that all base-index values are `2`.
- Cross-check this offset range against `dcn_4_2_0_sh_mask.h` and AMD's DCN 4.2.0 register database so every consumed register has matching field definitions.
- Compare repeated instance layouts for `DIG1-4`, `DP1-4`, `VPG2-5`, `DME1-5`, `DSC_TOP0-3`, `DSCCIF0-3`, and `DSCC0-3`, allowing only intentional offset spacing and HPO-specific truncation.
- Exercise HDMI and legacy DP connectors backed by DIG/DP instances in this range: modeset, audio, infoframes, CRC/test patterns, link training, secondary-data packets, MST/MSO where supported, panel replay, fast training, suspend/resume, and hotplug.
- Exercise DSC on all four instances with modes that require compression. Expected signals are successful modesets, valid PPS programming, no stuck update-pending state, no unexpected DSCC interrupt/status errors, and sane error/fullness readbacks.
- Exercise DWB capture with different source sizes, windows, output formats, CRC checks, gamut-remap/OGAM programming, backpressure monitoring, overflow interrupt/status handling, and suspend/resume.
- Exercise DCHVM/RIOMMU paths under display memory pressure and resume/reset scenarios; watch for page-fault, RIOMMU status, blanking, or DMUB/display handoff errors.
- Exercise HPO DP 2.x stream/link encoder 0 with high-bandwidth DP modes, MST allocation, eDP ASSR where applicable, ALPM, panel replay, symbol-count/CRC diagnostics, and DPHY status polling. Expected signals are stable link training, correct VC-rate/SAT programming, no stuck rate/SAT update-pending bits, and no cross-encoder register aliasing.

## Cross-Chunk Notes

The previous chunk owns the earlier DME1 address-block context and register families before `DME_CONTROL`. This chunk owns the DME1 tail, complete DIG/DP instances 1-4, DSC instances 0-3, DWB0, DCHVM, and the first HPO DP stream/link encoder 0 sections through `DP_DPHY_SYM32_ALPM_SLEEP_CONFIG0`. The next chunk continues the `DP_DPHY_SYM320` block with ALPM wake/control and test-pattern registers, so the final per-file report should merge these boundaries before making whole-block claims about HPO DP DPHY support in `dcn_4_2_0_offset.h`.

### subset-b-002216: lines 13312-15838

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 13312-15838

## Purpose

This chunk is a generated AMD DCN 4.2.0 register-offset header slice. It exports preprocessor constants that name MMIO register offsets and matching `_BASE_IDX` values for two DCN address spaces:

- HPO DisplayPort stream/link/DPHY register blocks use `_BASE_IDX` value `2`.
- MPC/MPCC compositor and color-management register blocks use `_BASE_IDX` value `3`.

The range contains 2,391 `#define` lines: 1,196 register-offset macros and 1,195 `_BASE_IDX` macros. It starts in the tail of the HPO DP DPHY SYM32 instance 0 block, covers HPO DP stream/link/DPHY instances 1 through 3, then transitions into the MPC block: MPCC instances 0 through 3, MPCC OGAM instances 0 through 3, MPC output CSC/denorm controls, MPC RMCM instances 0 and 1, MPC perfmon registers, and the beginning of MPCC MCM instance 0. The chunk ends in the middle of `MPCC_MCM0`, so adjacent chunks are required for whole-file conclusions about all MCM registers.

Although this source tree is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or runtime APIs in this header chunk. The exported interface is the generated macro namespace consumed by DCN 4.2 display code:

- `reg<REGISTER>` expands to the generated register offset.
- `reg<REGISTER>_BASE_IDX` selects the base segment used by token-pasting register helpers.
- DCN 4.2 resource and DMUB code resolve final addresses as `ctx->dcn_reg_offsets[reg..._BASE_IDX] + reg...`.
- Field-level access is supplied by the sibling `dcn_4_2_0_sh_mask.h`; this offset header only names addresses.

Important register families in this slice:

- HPO DP stream encoder instances 1-3: `regDP_STREAM_ENC1_*`, `regDP_STREAM_ENC2_*`, and `regDP_STREAM_ENC3_*` provide stream clock control, input muxing, audio control, clock-ramp FIFO status/control, and spare registers.
- HPO DP APG/DME/VPG packet sub-blocks: `regAPG6-8_*`, `regDME6-8_*`, and `regVPG6-8_*` expose audio packet generator control/debug/memory power, metadata engine control/memory power, generic packet access/data, GSP frame/immediate update, generic status, memory power, and ISRC access/data registers. These APG/VPG instance numbers correspond to HPO DP stream instances rather than the legacy DIG instance numbering.
- HPO DP SYM32 stream encoders 1-3: `regDP_SYM32_ENC1-3_*` cover stream enable/control, video FIFO, MSA and pixel-format double buffering, MSA payload words, hblank handling, 15 SDP/GSP controls, audio SDP controls, metadata packet control, VBID, panel replay, video CRC control/results/status, symbol counters, ALPM sleep/wake/request/ready/hardware-mode/status/start/interrupt controls, memory power, and spare registers.
- HPO DP link encoders 1-3: `regDP_LINK_ENC1-3_*` expose clock control and spare registers.
- HPO DP DPHY SYM32 instances 1-3 plus the preceding instance-0 tail: `regDP_DPHY_SYM320-*` and `regDP_DPHY_SYM321-323_*` include DPHY control/status, stream VC rate controls, stream allocation table updates, SAT VC slots and status, eDP/ASSR configuration, ALPM sleep/wake/control, test-pattern configuration, PRBS seeds, custom pattern registers, error status, and symbol counters.
- MPCC compositor instances 0-3: `regMPCC0-3_*` define top/bottom mux selection, OPP routing, control/control2, stereo-mix control, update-lock selection, blend gains, movable color-management location control, background color channels, memory-power control, and status.
- MPCC OGAM instances 0-3: `regMPCC_OGAM0-3_*` provide output gamma control, LUT index/data/control, RAMA/RAMB piecewise-linear start/slope/base/end/offset/region registers for RGB channels, and gamut-remap coefficient format/mode/matrix coefficients for banks A and B.
- MPC output CSC/denorm: `regMPC_OUT0-3_*` exposes output mux and denormalization controls/clamps. The shared output CSC block contains coefficient format, CSC mode, and matrix coefficients for outputs 0-3, including banked A/B coefficient sets.
- MPC RMCM instances 0-1: `regMPC_RMCM0-1_*` expose shaper control, offset/scale, shaper LUT index/data/write mask, RAMA/RAMB shaper regions, 3D LUT mode/index/data/read-write/out-normalization/out-offset, gamut remap format/mode/matrix coefficients, memory power, 3D LUT fast-load select/status, control, and test/debug access.
- MPC perfmon: `regDC_PERFMON16_*` provides perfmon control, counter, test-debug index/data, and clear registers for the MPC block.
- MPCC MCM instance 0 start: `regMPCC_MCM0_*` begins a large per-MPCC movable color-management block with shaper control/offset/scale/LUT programming, shaper RAMA/RAMB region tables, 3D LUT programming, 1D LUT control/data, 1D LUT RAMA/RAMB piecewise-linear programming, and the first gamut-remap controls.

## Control Flow

This header has no executable control flow. Runtime behavior is created by consumers that include this generated metadata:

1. DCN 4.2 resource construction includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Register-list macros in `dcn42_resource.c` and `dcn42_resource.h` token-paste names such as `regDP_SYM32_ENC1_DP_SYM32_ENC_CONTROL`, `regDP_DPHY_SYM321_DP_DPHY_SYM32_STATUS`, `regMPCC0_MPCC_CONTROL`, or `regMPC_RMCM0_MPC_RMCM_3DLUT_DATA`.
3. Helpers such as `SR`, `SRI`, `SR_ARR`, and `SRI_ARR` compute final offsets from `ctx->dcn_reg_offsets[segment] + generated_offset`.
4. Constructed hardware objects use those tables through `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`.

The macros do not encode sequencing. The HPO DP code must still perform link enable/disable, lane/mode programming, stream allocation table programming, test-pattern setup, ALPM transitions, panel replay state handling, SDP/audio/metadata setup, and DPHY status polling in the correct order. The MPC/MPCC code must still acquire/update locks where required, power memories before programming LUTs, select the correct RAM bank, program PWL regions and LUT entries consistently, switch color-management modes at a safe time, and preserve pipe topology while changing muxes or blend state.

## State And Persistence Behavior

The header stores no software state. It identifies hardware registers whose state is owned by DCN 4.2 display blocks:

- HPO DP stream state includes stream encoder clock/input/audio configuration, packet generator state, generic packet memories, SDP/GSP controls, MSA and pixel-format double-buffered values, VBID/panel replay controls, video CRC state, ALPM state, memory-power state, and symbol counters.
- HPO DP link/DPHY state includes DPHY reset/enable/mode/lane state, VC rate programming, stream allocation table slots, eDP ASSR state, ALPM configuration, test-pattern and PRBS seeds, error status, and link symbol counters.
- MPCC state includes per-compositor topology selection, OPP routing, blending mode and gains, background color, update-lock selection, memory-power state, and status.
- MPCC OGAM, MPC RMCM, and MPCC MCM state includes color pipeline mode, shaper LUTs, 1D/3D LUT memories, bank selection, gamut-remap matrices, coefficient formats, fast-load status, and debug index/data state.
- MPC output state includes output mux routing, denormalization/clamp configuration, output color-space conversion matrices, and perfmon counter/control state.

Persistence is hardware-defined. Programming generally survives until a modeset, plane update, color-management update, link retrain, panel replay/ALPM transition, power-gate cycle, suspend/resume, driver reset, or ASIC reset. Status, interrupt, counter, CRC, error, perfmon, debug, and memory-power state registers may be read-only, sticky, self-clearing, write-one-to-clear, or meaningful only while the corresponding block is powered and clocked. This offset header does not describe those access semantics; consumers must rely on the shift/mask header and ASIC programming rules.

## Dependencies And Integration Points

This generated header must remain synchronized with AMD's DCN 4.2 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h`, which provides field shifts and masks for the same symbolic register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes this header and resolves offsets through `ctx->dcn_reg_offsets`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h`, which defines DCN 4.2 register-list macros, including `DCN42_HPO_DP_STREAM_ENC_REG_LIST_RI(id)`, `DCN42_HPO_DP_LINK_ENC_REG_LIST_RI(id)`, and `VPG_DCN42_REG_LIST_RI(id)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c`, which reads DPHY status, lane count, mode, stream allocation slots, and VC rates through the HPO DP link encoder register table.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c`, which uses the MPC/MPCC register tables for MPCC blending, RMCM shaper/3D LUT power, PWL programming, LUT programming, gamut remap, and hardware state readback.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which also includes `dcn_4_2_0_offset.h` and computes DMUB-visible register offsets via `REG_OFFSET_EXP`.

The chunk's HPO DP registers integrate with DCN 4.2 stream encoders, link encoders, DCCG HPO clocks, DMUB commands that carry HPO stream/link instance identifiers, DisplayPort 2.x link training, MST allocation, eDP ALPM/ASSR, panel replay, audio SDP, and VPG/DME/APG metadata packet paths. The MPC registers integrate with resource pool construction, plane composition, OPP routing, color management, 3D LUT and shaper programming, HDR/gamut remap paths, perfmon diagnostics, and debug-state readback.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong offset or base index can compile cleanly while directing MMIO to the wrong block or segment.
- This chunk has mixed base segments. HPO DP registers use base index `2`, while MPC/MPCC registers use base index `3`; accidental cross-segment substitution would produce plausible-looking but wrong final addresses.
- The chunk boundaries are artificial. It starts after the beginning of DPHY instance 0 and ends before the end of `MPCC_MCM0`, so complete block-level review requires adjacent chunks.
- HPO DP instance names are copy-sensitive. Stream/link/DPHY instances 1-3 are nearly identical, and APG/DME/VPG numbering uses `6`, `7`, and `8`; an instance-number mismatch can connect packets, stream encoders, link encoders, or DPHY state to the wrong HPO path.
- DPHY and SAT/VC-rate registers are central to DP 2.x operation. Misaddressing can break link enablement, lane/mode reporting, MST bandwidth allocation, throttled VCP size programming, training/test patterns, eDP ASSR, ALPM, or symbol/error diagnostics.
- Stream encoder and packet registers affect visible output metadata. Bad offsets can cause blanking, incorrect MSA or pixel format, missing audio SDP, stale HDR or ISRC packets, invalid panel replay signaling, or misleading CRC/symbol-counter reads.
- MPCC control and mux registers define pipe composition topology. Wrong values can route a plane to the wrong output, corrupt blending, break update-lock behavior, or leave the compositor in a stale state across modesets.
- MPCC OGAM, RMCM, and MCM blocks are LUT-heavy and banked. Incorrect offsets or bank selection can cause color corruption, gamma discontinuities, HDR/gamut-remap errors, hangs while programming powered-down memories, or failed fast-load transitions.
- Memory-power registers are operational, not just metadata. Programming LUT or packet memories while their memory-power state is off or transitioning may fail silently or produce transient display corruption.
- Perfmon and debug index/data registers can be misleading if the wrong block is selected, if counters are not cleared, or if reads happen while clocks/power are gated.

## Test Signals

Useful validation combines generated-header consistency with DCN 4.2 hardware behavior:

- Build AMDGPU display code with DCN 4.2 enabled. Missing or renamed macros should fail in `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_mpc.c`, `dcn42_hpo_dp_link_encoder.c`, `dmub_dcn42.c`, or register-list expansion.
- Mechanically compare this range against `dcn_4_2_0_sh_mask.h` and the generated register database, checking that every consumed offset macro has a matching `_BASE_IDX` macro and that field definitions exist for all programmed fields.
- Diff equivalent HPO DP and MPC/MPCC blocks against nearby ASIC headers such as `dcn_4_0_1_offset.h`, DCN 3.6 headers, and later DCN headers to catch unintended instance swaps, base-index changes, or register omissions.
- Exercise DP 2.x and HPO paths on DCN 4.2 hardware: hotplug, cold boot, modesets, high-bandwidth modes, MST, DSC-over-DP where applicable, link retraining, test patterns, ALPM, eDP ASSR, panel replay, audio SDP, metadata packets, CRC reads, symbol counters, suspend/resume, and HPD storms.
- Exercise composition and color paths: multi-plane blending, alpha and global gain, OPP routing, update-lock changes, background color, output CSC/denorm, SDR/HDR modes, gamma/degamma updates, shaper LUTs, 1D/3D LUTs, gamut remap, fast-load paths, and repeated plane enable/disable.
- Monitor kernel logs and display diagnostics for failed `REG_WAIT` loops, DPHY status mismatches, SAT/VC allocation errors, link training failures, blank or flickering displays, missing audio or metadata, panel replay/ALPM failures, color corruption, memory-power warnings, perfmon anomalies, and resume-only regressions.

## Cross-Chunk Notes

This is a middle chunk of `dcn_4_2_0_offset.h`. The previous chunk contains the beginning of HPO DP instance 0 and likely the first stream/link/DPHY blocks. The next chunk continues `MPCC_MCM0` and the remaining generated register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all HPO DP instances, all VPG/APG mappings, all MPCC/MPC color-management blocks, or the full DCN 4.2 register surface.

### subset-b-002217: lines 15839-17880

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 15839-17880

## Purpose

This chunk is the final line range of AMD's generated DCN 4.2.0 register-offset header. It contains C preprocessor constants, not executable logic. Each `reg...` macro gives a register offset and each adjacent `reg..._BASE_IDX` macro gives the register-base selector used by AMD display register-access tables. In this range every visible base index is `3`, so consumers combine these offsets with the fourth MMIO base in the generated DCN 4.2.0 register-base table.

The chunk starts at an artificial boundary inside the `MPCC_MCM0` first gamut-remap definition: the offset for `regMPCC_MCM0_MPCC_MCM_FIRST_GAMUT_REMAP_MODE` is immediately before this range, while its `_BASE_IDX` line is the first line here. It then completes the tail of `MPCC_MCM0`, contains the complete `MPCC_MCM1`, `MPCC_MCM2`, and `MPCC_MCM3` blocks, and ends at the file terminator after Azalia stream 7 output-descriptor offsets.

The covered hardware surface is broad:

- MPC/MPCC MCM color-management offsets for shaper LUTs, 3D LUTs, 1D LUTs, first and second gamut-remap matrices, memory power control, and fast 3D-LUT load status for MPCC MCM instances 0-3.
- MPC configuration, CRC, pending status, vupdate lock-set, per-HUBP 3D-LUT fast-load configuration, and DWB mux offsets.
- HPO HDMI stream, TMDS/transport block, APG, VPG, DME, link encoder, FRL encoder, HPO top, DP stream mapper, and DC perfmon 23 offsets.
- OPP ABM0-ABM3 adaptive backlight and histogram/luma-statistic offsets.
- DPIA MU/glue/performance-counter offsets for DisplayPort-over-USB-C infrastructure.
- HDA/Azalia controller, endpoint/root immediate command aliases, and output stream descriptor offsets for audio streams 0-7.

Although the repository path sits under a `ceph-client` source mirror, this header is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, variables, or includes in this chunk. The public interface is generated macro naming:

- `reg<REGISTER>` expands to a numeric register offset, for example `regMPCC_MCM1_MPCC_MCM_SHAPER_CONTROL`, `regHDMI_TB_ENC_PACKET_CONTROL`, `regABM0_DC_ABM1_LS_SUM_OF_LUMA`, `regDPIA_MU_INTERRUPT_STATUS`, or `regAZSTREAM0_1_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`.
- `reg<REGISTER>_BASE_IDX` expands to the base-address table index paired with the offset.
- Address-block comments such as `dce_dc_mpc_mpcc_mcm1_dispdec`, `dce_dc_hpo_hdmi_tb_enc0_dispdec`, `dce_dc_opp_abm0_dispdec`, `dce_dpia_dpia_mu0_dpiadec`, and `dce_dc_hda_azcontroller_azdec` preserve the generated register database grouping.

Important macro families in this chunk:

- `regMPCC_MCM{1,2,3}_MPCC_MCM_*` and `regMPCC_MCM{1,2,3}_MPC_MCM_*` repeat a large color pipeline layout: shaper control/offset/scale/index/data/write-enable; shaper RAM A/B start, end, and 34 region registers; 3D LUT mode/index/data/read-write/out offset; 1D LUT control/index/data and RAM A/B curve registers; first and second gamut-remap coefficient-format, mode, and matrix coefficient registers; memory power control; and fast-load select/status.
- The tail of `regMPCC_MCM0_*` completes first and second gamut remap, memory power, and 3D-LUT fast-load status for instance 0.
- `regMPC_*`, `regADR_*`, `regCFG_*`, `regCUR_*`, and `regHUBP{0..3}_3DLUT_FL_*` cover global MPC clock/reset/CRC/status, vertical-update lock sets 0-3, and per-HUBP fast-load 3D-LUT bias/scale and config.
- `regHDMI_STREAM_ENC_*`, `regHDMI_TB_ENC_*`, `regAPG9_*`, `regVPG9_*`, `regDME9_*`, `regHDMI_LINK_ENC_*`, `regHDMI_FRL_ENC_*`, `regHPO_TOP_*`, and `regDP_STREAM_MAPPER_CONTROL*` cover the HPO HDMI/DP output path.
- `regDC_PERFMON23_*` covers performance-counter control, state, current value, and high/low counter latches for HPO perfmon 23.
- `regABM{0..3}_*` repeats the OPP adaptive backlight module layout: PWM levels, ABM control, ACE/PWL controls, histogram/luma-stat readouts, sample rates, histogram-bin shift flags/indices, result index/data, and backlight master lock.
- `regDPIA_*` and `regDPIA_MU_*` cover DPIA MU clock/reset per port, TPI status per port, interrupt status/control/ack, RBBM timeout/status, microsecond reference control, adapter status, glue control, and indexed performance counters.
- `regGLOBAL_*`, `regINTERRUPT_*`, `regCORB_*`, `regAZCONTROLLER1_*`, `regAZENDPOINT1_*`, `regAZINPUTENDPOINT1_*`, `regAZROOT1_*`, and `regAZSTREAM{0..7}_1_*` cover DCN HDA/Azalia controller global registers, CORB/RIRB rings, immediate command/response paths, DMA position base, wall-clock alias, endpoint/root aliases, and stream descriptor registers.

## Control Flow

This chunk has no local control flow. Runtime flow is created when DCN 4.2 display code includes this header with the matching `dcn_4_2_0_sh_mask.h` file and token-pastes register names into tables consumed by AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed variants.

Typical flow using these offsets is:

1. DCN 4.2 resource, IRQ, DMUB, audio, link, color, ABM, or HPO code selects the DCN 4.2 offset and shift/mask headers.
2. Register-list macros expand symbolic names into offset/base-index pairs and field shift/mask pairs.
3. Runtime display programming writes or polls hardware through those generated tables.
4. The numeric offsets in this chunk decide which hardware register receives each write or read.

Examples of indirect sequencing affected by this chunk include programming MPCC MCM LUT and gamut-remap state during color pipeline updates, locking MPC vertical-update domains around atomic plane updates, configuring HDMI/FRL/VPG/APG/DME packet paths during modeset, collecting ABM luma histograms and updating backlight PWM levels, resetting or monitoring DPIA ports during USB-C/DP tunnel activity, and programming Azalia command rings or output stream descriptors for HDMI/DP audio.

## State And Persistence Behavior

The header itself stores no software state and persists nothing to disk. It describes hardware-backed state:

- MPCC MCM state persists in color-management hardware: shaper LUT entries, 1D LUT curves, 3D LUT entries, output offsets, first/second gamut-remap matrices, memory power settings, and fast-load selection/status.
- MPC state includes clock/reset controls, CRC selection/results, DPP and miscellaneous pending state, vertical-update lock groups, HUBP fast-load configuration, and DWB mux routing.
- HPO HDMI/DP state includes stream encoder clocks, input muxing, audio control, packet control, ACR values/status, generic-packet line selection, data-buffer control, metadata control, active/blank timing, CRC, encryption, mode, FIFO status, FRL configuration, and stream-mapper routing.
- ABM state includes user/ambient/target/current/final/min PWM levels, ABM control, ACE/PWL table access, histogram/luma readouts, sample-rate programming, bin shift settings, and backlight master locks.
- DPIA state includes per-port clocks/resets/status, interrupt status/control/ack, timeout status, timing reference, adapter status, and performance counter index/data state.
- Azalia state includes controller global status/control, wake/status/interrupt registers, CORB/RIRB base addresses and pointers, immediate command/response state, DMA position base address, wall clock, and per-stream descriptor control, position, cyclic buffer length, last valid index, FIFO/format, BDL base, and position alias.

The access semantics are not encoded here. Many target registers are hardware latches, read-only status, sticky interrupt status, write-one-to-clear bits, indexed windows, or values only valid while a related clock/power domain is enabled. The matching shift/mask header and consuming driver code must supply field-level semantics and ordering.

## Dependencies And Integration Points

Direct dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h` must define fields for the register names listed here. Offsets without matching field definitions, or field definitions without matching offsets, break register-table construction or produce incomplete accessors.

Important integration points visible in the tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`, so DMUB DCN 4.2 support depends on the generated offset namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c` includes both generated headers for DCN 4.2 interrupt register setup.
- AMD display register helpers and component register-list macros depend on stable `reg...` names and `_BASE_IDX` companions.
- HDMI transport-block enum values in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h` describe semantic values for several `HDMI_TB_ENC_*` registers whose offsets are in this chunk.
- ABM, HPO, DPIA, Azalia/audio, color-management, and MPC code from adjacent DCN generations can share naming conventions. That makes the generated names look reusable, but the offsets must remain generation-specific for DCN 4.2.0.

## Risks And Edge Cases

- The chunk starts in the middle of a register pair. `regMPCC_MCM0_MPCC_MCM_FIRST_GAMUT_REMAP_MODE_BASE_IDX` is present here, but the corresponding offset line is in the previous chunk. Any per-chunk validator must account for that boundary exception.
- This is untyped generated metadata. A wrong offset or base index can compile cleanly and route a valid-looking register access to the wrong hardware address.
- The repeated `MPCC_MCM1`, `MPCC_MCM2`, and `MPCC_MCM3` blocks are copy-sensitive. A single instance offset error may only affect one pipe or plane color path and can be missed if testing exercises only instance 0.
- HPO HDMI/FRL, APG/VPG/DME, and DP stream-mapper offsets sit in adjacent but distinct blocks. Mixing similarly named stream, transport, link, FRL, packet, and mapper registers can cause black screens, invalid infoframes, bad ACR/audio behavior, or link-training failures.
- ABM offsets are repeated for four OPP instances with regular spacing. Misindexing can drive the wrong panel/backlight path or read the wrong histogram/luma statistics.
- DPIA MU registers include interrupts, timeout handling, and per-port reset/clock controls. Wrong offsets can leave a USB-C/DP tunnel port stuck, miss an interrupt, or acknowledge the wrong event.
- Azalia controller and stream descriptor registers share offsets for aliased subregisters such as version/capability fields, payload capability fields, wake/status, CORB/RIRB fields, immediate-command data/index, and stream FIFO/format. Consumers must use matching field masks to disambiguate aliases.
- Several status and clear registers are timing-sensitive. Reads while clocks are gated, writes before reset release, or acknowledgements with stale masks can produce intermittent display, audio, or hotplug failures.
- The file ends at this chunk. Merge tooling should not expect following lines after the `#endif`, but it must still reconcile the previous boundary line for a complete per-file report.

## Test Signals

Useful validation signals include:

- Build AMDGPU display support with DCN 4.2 enabled. Missing or renamed macros should fail in DCN 4.2 DMUB, IRQ, resource, audio, ABM, HPO, DPIA, or color register-table compilation.
- Mechanically verify every `reg...` offset macro in this range has a paired `_BASE_IDX` macro and that all visible base indexes are intentional for DCN 4.2.0. Allow the first-line boundary where only a `_BASE_IDX` half of the previous register appears in this chunk.
- Cross-check this offset range against AMD's authoritative DCN 4.2.0 register database and the matching `dcn_4_2_0_sh_mask.h` names.
- Exercise color-management paths on all MPCC MCM instances: shaper LUT load, 1D LUT load, 3D LUT load/fast load, first and second gamut-remap programming, memory power transitions, and multi-plane composition.
- Exercise modeset and atomic update paths that use MPC CRC, vupdate locks, pending status, HUBP fast-load configuration, and DWB mux routing.
- Exercise HDMI/DP output through the HPO path: stream encoder input mux/clock, HDMI transport packet and ACR programming, APG/VPG generic packets, DME, link encoder, FRL configuration, stream mapper, CRC, metadata packets, encryption mode, and suspend/resume.
- Exercise ABM on all available OPP instances: PWM level programming, ambient/user/target transitions, luma-stat/histogram collection, ACE/PWL table access, result index/data reads, and backlight lock behavior.
- Exercise DPIA ports 0-3 where hardware exposes them: clock/reset, TPI status, interrupt status/ack, timeout paths, adapter status, microsecond reference, and performance counter readback.
- Exercise HDMI/DP audio: HDA controller reset/interrupt, CORB/RIRB ring setup, immediate command/response, DMA position base, wall-clock reads, and stream descriptor programming for streams 0-7 including FIFO/format aliases and link-position aliases.
