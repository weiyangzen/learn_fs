# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001575`: lines 1-2770, `Docs/researches/chunks/subset-b-001575_research.md`
- `subset-b-001576`: lines 2771-5323, `Docs/researches/chunks/subset-b-001576_research.md`
- `subset-b-001577`: lines 5324-7968, `Docs/researches/chunks/subset-b-001577_research.md`
- `subset-b-001578`: lines 7969-10476, `Docs/researches/chunks/subset-b-001578_research.md`
- `subset-b-001579`: lines 10477-13111, `Docs/researches/chunks/subset-b-001579_research.md`
- `subset-b-001580`: lines 13112-14114, `Docs/researches/chunks/subset-b-001580_research.md`

## Chunk Research

### subset-b-001575: lines 1-2770

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h

Chunk: `subset-b-001575`
Covered source range: lines 1-2770 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

## Purpose

This chunk is the opening section of a generated AMD DCN 1.0 register offset header. It contains C preprocessor constants for memory-mapped display controller register offsets and their register-base index selectors. It is not executable driver logic; its purpose is to provide stable symbolic register addresses for DCN 1.0 display code.

The covered range starts with the file license and include guard `_dcn_1_0_OFFSET_HEADER`, then defines `mm*` register offset macros and matching `mm*_BASE_IDX` macros for several DCN 1.0 hardware blocks:

- legacy HDA/Azalia controller, endpoint, root, input endpoint, and stream descriptor windows;
- VGA compatibility and VGAIF/MMHUBBUB register windows;
- DCCG display clock, DTO, resync, audio DTO, gate-disable, perfmon, and PLL-reserved registers;
- DMU, DMCU, interrupt handler controller, power-gating domains, scratch, RAM access, mailbox, firmware-loading, and perfmon registers;
- display writeback converter/scaler (`CNV0/1`, `WBSCL0/1`), writeback MCIF (`MCIF_WB0/1`), and writeback perfmon registers;
- MMHUBBUB and DCHUBBUB hub, SDPIF, return-path, arbiter, clock/reset, memory-power, CRC, global timer, surface-check, and DC perfmon registers;
- the beginning of HUBP/HUBPREQ plane-fetch register instances for `HUBP0/HUBPREQ0` and `HUBP1/HUBPREQ1`.

The chunk ends in the middle of the `dce_dc_dcbubp1_dispdec_hubpreq_dispdec` address block at `mmHUBPREQ1_VBLANK_PARAMETERS_4`. Later HUBP1 registers and subsequent register blocks are outside this chunk and should be reconciled by the later merge lane.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs defined in this header section. Its public interface is the generated macro naming contract:

- `mm<REGISTER>` gives the register offset within an AMD display register segment.
- `mm<REGISTER>_BASE_IDX` selects the segment base used by helper macros such as `BASE(mm<REGISTER>_BASE_IDX) + mm<REGISTER>`.
- Repeated hardware instances are encoded in the macro name, for example `mmAZSTREAM0_1_*`, `mmCNV0_*`, `mmCNV1_*`, `mmMCIF_WB0_*`, `mmMCIF_WB1_*`, `mmHUBP0_*`, `mmHUBP1_*`, `mmHUBPREQ0_*`, and `mmHUBPREQ1_*`.

Important macro families in this chunk include:

- HDA/Azalia controller command rings and streams: `mmCORB_*`, `mmRIRB_*`, `mmIMMEDIATE_*`, `mmDMA_POSITION_*`, `mmWALL_CLOCK_COUNTER_ALIAS`, `mmAZSTREAM0_1_*` through `mmAZSTREAM7_1_*`, and the F0 codec stream, endpoint, input endpoint, root, and controller index/data registers.
- VGA compatibility offsets: `mmVGA_MEM_WRITE_PAGE_ADDR`, `mmVGA_MEM_READ_PAGE_ADDR`, `mmCRTC8_*`, `mmSEQ8_*`, `mmGRPH8_*`, DAC index/data registers, `mmVGA_*`, and VGA memory/mode control registers.
- DCCG clocks and timing: `mmREFCLK_CNTL`, `mmDENTIST_DISPCLK_CNTL`, `mmDPREFCLK_CNTL`, `mmDCCG_AUDIO_DTO*`, `mmOTG0_PIXEL_RATE_CNTL` through `mmOTG5_PIXEL_RATE_CNTL`, `mmDP_DTO0_*` through `mmDP_DTO5_*`, `mmDCCG_VSYNC_*`, `mmDCCG_GATE_DISABLE_CNTL*`, `mmDCCG_SOFT_RESET`, and clock enable controls for symbol and DVO clocks.
- Perfmon blocks: `mmDC_PERFMON0_*`, `mmDC_PERFMON1_*`, `mmDC_PERFMON2_*`, `mmDC_PERFMON3_*`, `mmDC_PERFMON4_*`, `mmDC_PERFMON5_*`, `mmDC_PERFMON7_*`, and `mmDC_PERFMON8_*`, each exposing counter control, state, current-value interrupt, high, and low value registers.
- DMU/DMCU and power management: `mmDOMAIN0_PG_CONFIG` through `mmDOMAIN15_PG_STATUS`, `mmDCPG_INTERRUPT_*`, `mmDC_IP_REQUEST_CNTL`, `mmDMCU_CTRL`, `mmDMCU_STATUS`, `mmDMCU_RAM_ACCESS_*`, `mmDMCU_FW_START_ADDR`, `mmDMCU_ERAM_*`, `mmDMCU_INTERRUPT_*`, mailbox registers such as `mmMASTER_COMM_*` and `mmSLAVE_COMM_*`, and `mmIHC_*` interrupt routing/control registers.
- Writeback pipeline: `mmCNV0_*` and `mmCNV1_*` for converter/capture window, color space conversion, CRC, warm-up, reset, and input selection; `mmWBSCL0_*` and `mmWBSCL1_*` for scaler coefficients, taps, ratios, clamp, CRC, overflow, and backpressure; and `mmMCIF_WB0_*` and `mmMCIF_WB1_*` for writeback buffer manager, four luma/chroma buffer slots, pitch, arbitration, p-state/watermark, warm-up, self-refresh, QoS, and buffer size registers.
- HUBBUB/DC hub registers: `mmDCHUBBUB_SDPIF_*`, `mmDCHUBBUB_RET_PATH_*`, `mmDCHUBBUB_ARB_*`, `mmDCHUBBUB_GLOBAL_TIMER_CNTL`, `mmSURFACE_CHECK*`, `mmVTG0_CONTROL` through `mmVTG5_CONTROL`, `mmDCHUBBUB_SOFT_RESET`, `mmDCHUBBUB_CLOCK_CNTL`, `mmDCFCLK_CNTL`, performance measurement registers, and test-debug index/data registers.
- HUBP/HUBPREQ plane-fetch registers: `mmHUBP0_DCSURF_*`, `mmHUBPREQ0_DCSURF_*`, `mmHUBPRET0_*`, `mmCURSOR0_*`, `mmHUBP1_DCSURF_*`, and the start of `mmHUBPREQ1_DCSURF_*`, covering surface format/tile/viewports, request sizing, surface addresses, meta addresses, flip control, frame pacing, in-use addresses, TTU QoS controls, VM aperture/context registers, blank offsets, destination dimensions, prefetch settings, and vblank parameters.

The companion `dcn_1_0_sh_mask.h` provides the corresponding field `__SHIFT` and `_MASK` constants. This offset header supplies the register addresses those fields are applied to.

## Control Flow

This chunk has no internal control flow. The preprocessor expands constants into static register tables and register access helper calls during compilation.

The normal runtime control flow in consumers is:

1. A DCN 1.0 translation unit includes `dcn/dcn_1_0_offset.h`, `dcn/dcn_1_0_sh_mask.h`, SoC segment-base headers such as `soc15_hw_ip.h` and `vega10_ip_offset.h`, and `reg_helper.h`.
2. Local macros such as `SR`, `SRI`, `SRII`, and `REG` compute a full MMIO register address from `BASE(mm<REGISTER>_BASE_IDX) + mm<REGISTER>`.
3. Resource construction code stores those computed addresses in per-block register structs.
4. Runtime block code uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, and `REG_GET` against those register structs, combining this file's offset macros with mask/shift fields from the companion header.

Concrete local integration examples:

- `display/dc/resource/dcn10/dcn10_resource.c` includes this header and defines `SR`, `SRI`, and `SRII` macros that add `BASE(mm*_BASE_IDX)` to `mm*`. It builds register tables for DMCU, audio, AUX/HPD, HUBP, HUBBUB, DIO, writeback, stream encoders, timing generators, and related DCN 1.0 blocks.
- The same resource file creates `hubp_regs[]` from `HUBP_REG_LIST_DCN10(id)` and a `hubbub_reg` from `HUBBUB_REG_LIST_DCN10(0)`, so the `HUBP0/1`, `HUBPREQ0/1`, and `DCHUBBUB_*` offsets in this chunk become the runtime addresses used by plane fetch and hubbub code.
- `display/dc/dcn10/dcn10_dwb.h` maps `CNV*` and `MCIF_WB*` offsets through `SRI()` into writeback register structures, then pairs them with field masks for converter enable/reset, MCIF buffer address, pitch, arbitration, p-state, watermark, and interrupt control.
- `display/dc/irq/dcn10/irq_service_dcn10.c` includes this offset header while mapping DCN interrupt source IDs to core DC IRQ sources. The IHC, HUBP flip, HPD, and vupdate register families represented in this file support those interrupt flows.
- `display/dc/gpio/dcn10/hw_factory_dcn10.c` and `display/dc/gpio/dcn10/hw_translate_dcn10.c` include this header and use the same offset plus base-index pattern to construct and decode GPIO, HPD, DDC, and generic pin registers.

Because this file is generated register data, the actual control dependencies live in the consumer orderings: reset before programming, double-buffer or latch semantics for timing-sensitive registers, interrupt ack before re-enable, and writeback or HUBP address programming before enabling fetch/capture.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, read hardware, write hardware, acquire locks, or persist data. Its only persistent effect is that numeric register offsets are compiled into driver objects.

The hardware registers named here represent stateful display controller state until changed by driver writes, firmware, display microcontroller action, power gating, suspend/resume, hotplug events, or GPU reset. Important state categories include:

- HDA/Azalia command ring pointers, immediate command/response registers, stream descriptor positions, cyclic buffer lengths, BDL addresses, codec endpoint/root parameters, and audio wall-clock counters.
- DCCG clock source selection, DTO phase/modulo values, pixel-rate controls, resync controls, symbol clock enables, soft-reset bits, vsync latch values, and clock-gating overrides.
- DMCU firmware control and observability state, including microcontroller reset/start/stop, ERAM/IRAM access, firmware start address, PC/PC start, RAM access data, mailbox messages, interrupt enables, and status registers.
- Display power-gating domain configuration and status for domains 0 through 15, plus global DC IP request and power-gating interrupt control.
- Writeback capture state, including converter mode, capture window, CSC coefficients and clamps, scaler coefficients and ratios, buffer addresses, buffer status, arbitration slices, p-state and watermark settings, self-refresh, warm-up, QoS, and interrupt/overrun indications.
- HUBBUB memory aperture, SDPIF address range, MARC relocation windows, return-path DCC configuration, memory-power state, CRC capture results, arbiter watermarks for urgency/self-refresh/DRAM clock change, global timer state, surface-check addresses, VTG controls, clock/reset state, and performance measurement counters.
- HUBP/HUBPREQ plane state, including surface configuration, tiling, viewport, request sizing, primary/secondary luma and chroma surface addresses, meta-surface addresses, flip control, frame pacing, current/earliest in-use addresses, TTU QoS, VM aperture/context/page-table/protection-fault state, and cursor offsets/settings in the HUBP0 portion.

Several represented registers are read-only status, write-one-to-clear interrupt acknowledgement, latched debug/CRC output, or double-buffered update state in hardware, but this offset header does not encode access type. Consumers must follow the register specification and use the appropriate existing helper sequences.

## Dependencies And Integration Points

Immediate build dependencies are the C preprocessor and the include guard in this file. Practical driver dependencies include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h` for matching field masks and shifts;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_hw_ip.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vega10/vega10_ip_offset.h` for segment base constants such as `DCE_BASE__INST0_SEG*`;
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/reg_helper.h` and related DC register helper macros that consume register addresses and field masks;
- DCN 1.0 block headers that define register-list and mask-list macros, including DMCU, audio, AUX, HPD, HUBP, HUBBUB, DWB, stream encoder, timing generator, and GPIO helpers.

Key local integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn10/dcn10_hubp.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.h`

This file also shares register naming and layout conventions with later DCN offset headers such as `dcn_2_0_0_offset.h`, `dcn_2_1_0_offset.h`, and `dcn_3_0_0_offset.h`. Some symbolic names persist across generations while numeric offsets differ. The resource layer is the intended generation-specific boundary.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are untyped preprocessor values, so a mismatched `mm*` register, `_BASE_IDX`, shift, or mask can compile successfully while directing a read or write to the wrong register or segment.

Base-index correctness is critical. Many early HDA/Azalia and VGA definitions use base index 0 or 1, while most DC display blocks in this chunk use base index 2. If a register-list macro combines an offset with the wrong base segment, the final MMIO address can target a different hardware aperture.

Repeated instance blocks are easy to mix up. `AZSTREAM0..7`, `CNV0/1`, `WBSCL0/1`, `MCIF_WB0/1`, `HUBP0/1`, `HUBPREQ0/1`, endpoint instances, and input endpoint instances have highly similar names and layouts. A copy/paste error can leave one instance accessing another instance's state.

This chunk contains a boundary split. It ends inside the `HUBPREQ1` block at `mmHUBPREQ1_VBLANK_PARAMETERS_4`; a chunk-local completeness check should not assume the block is complete. The final merged file report should verify that the rest of the `HUBPREQ1` register list is covered by later chunks.

Some macros preserve generated spelling, including names such as `mmHUBPREQ0_PREFETCH_SETTINS` and `mmHUBPREQ1_PREFETCH_SETTINS`. Consumers must use the generated spelling consistently; locally "correcting" it would break compilation unless all generated companions and register-list macros are changed together.

Timing and ordering hazards are concentrated in these register families:

- DCCG DTO, pixel-rate, resync, and gate-disable registers affect live display clocks and audio/video synchronization.
- DMCU reset, firmware, RAM access, and mailbox registers can hang or desynchronize firmware communication if touched out of sequence.
- Power-domain and memory-power registers can gate blocks that still have pending register access or memory requests.
- Writeback MCIF buffer addresses, pitch, size, watermark, p-state, and arbitration registers are tied to memory traffic and can cause underrun, overrun, stale capture, or memory faults if programmed inconsistently.
- HUBBUB arbiter watermarks and VM aperture/context registers affect display fetch latency, page-table access, protection fault behavior, self-refresh entry/exit, and DRAM clock-change safety.
- HUBP/HUBPREQ surface address, meta address, flip, in-use, and TTU registers affect page flips, cursor/plane fetch, compression metadata, and VM fault behavior.

Generated register headers can drift from silicon documentation, firmware expectations, or companion `sh_mask` headers. A stale offset may only fail on hardware and may present as display corruption, IRQ storms, blank displays, audio failure, writeback failure, or intermittent suspend/resume issues rather than a compile error.

## Test Signals

Useful validation signals include:

- build coverage for DCN 1.0 translation units that include `dcn_1_0_offset.h`, especially `dcn10_resource.c`, `irq_service_dcn10.c`, DCN10 GPIO factory/translate code, DWB, HUBP, HUBBUB, DMCU, audio, AUX, and stream/timing encoder code;
- generated-header consistency checks confirming each `mm<REGISTER>` has exactly one matching `mm<REGISTER>_BASE_IDX` and that register names used in DCN10 register-list macros exist in this offset header;
- companion consistency checks against `dcn_1_0_sh_mask.h`, ensuring field mask/shift macros are paired with an existing register offset and that instance prefixes line up as expected;
- address regression checks comparing repeated instances, for example stream blocks stepping by the documented stride, `MCIF_WB0` versus `MCIF_WB1`, `CNV0/WBSCL0` versus `CNV1/WBSCL1`, and `HUBP0/HUBPREQ0` versus `HUBP1/HUBPREQ1`;
- boot and modeset smoke tests on DCN 1.0 hardware, covering display bring-up, page flips, vblank/vupdate interrupts, hotplug detection, suspend/resume, and multi-plane scanout;
- DisplayPort/HDMI audio tests that exercise Azalia codec endpoint/root registers, audio DTO programming, stream descriptor state, and wall-clock/link-position readback;
- DMCU tests for firmware load/start, mailbox round trips, ABM/backlight paths that rely on DMCU registers, interrupt delivery, and reset/recovery paths;
- writeback tests that program converter/scaler/MCIF settings, capture luma/chroma buffers, validate pitch/size/address handling, exercise watermark and p-state changes, and observe overrun/interrupt behavior;
- HUBBUB/HUBP stress tests with VM-enabled surfaces, compressed surfaces, cursor updates, rapid flips, p-state and DRAM clock changes, self-refresh entry/exit, and protection-fault reporting;
- debug and perfmon tests that program DC perfmon counter blocks, read high/low counter values, verify current-value interrupt behavior, and confirm debug/CRC readback without perturbing live display state.

### subset-b-001576: lines 2771-5323

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 2771-5323

## Scope And Purpose

This chunk is part 2 of the generated DCN 1.0 register offset header for the AMDGPU display driver. It contains C preprocessor constants mapping DCN display-controller register names to register offsets and base-segment indices. The chunk is not executable code; it is a hardware address contract consumed by AMD Display Core resource construction code to build per-block MMIO register tables.

The visible range starts mid-HUBPREQ1 with a trailing `mmHUBPREQ1_DST_AFTER_SCALER_BASE_IDX` from the previous chunk, then covers the remaining HUBPREQ1 prefetch/timing registers, HUBPRET1, CURSOR1, HUBP/HUBPREQ/HUBPRET/CURSOR instances 2 and 3, DPP instances 0 through most of 3, DSCL scaler blocks, CNVC input pixel/cursor blocks, CM color-management blocks, and DC perfmon blocks up through `mmCM3_CM_DENORM_CONTROL`. The next chunk continues at line 5324 with the rest of the DPP3 CM/perfmon register map.

Within this range there are 2,411 `#define mm...` entries: 1,205 register offset constants and 1,206 `_BASE_IDX` constants. The one-extra base-index definition is caused by the chunk boundary starting at the base index for `mmHUBPREQ1_DST_AFTER_SCALER`, whose offset is in the previous chunk.

## Register Families Covered

The chunk is organized by generated `addressBlock` comments and repeated instance prefixes:

- `HUBPREQ1` tail: prefetch settings, vblank/nominal delivery parameters, per-line delivery, cursor settings, reference-to-pixel frequency conversion, and HUBPREQ memory power control/status.
- `HUBPRET1`, `HUBPRET2`, `HUBPRET3`: request-return/read-line control, read-line values/status, interrupts, and memory power control/status.
- `CURSOR1`, `CURSOR2`, `CURSOR3`: cursor surface address high/low, size, position, hot spot, stereo control, destination offset, and cursor memory power status/control.
- `HUBP2` and `HUBP3`: surface config, address/tiling config, primary/secondary luma/chroma viewports, request-size config, HUBP control/clock, VMPG config, debug registers, and clock measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: surface pitch, primary/secondary luma/chroma addresses, meta-surface addresses, flip/surface control, in-use and earliest-in-use addresses, TLB/VM aperture registers, TTU/QoS programming, blank/destination geometry, prefetch and delivery programming, and memory power control/status.
- `DPP_TOP0` through `DPP_TOP3`: DPP control and host read control.
- `CNVC_CFG0` through `CNVC_CFG3`: format control and surface pixel format.
- `CNVC_CUR0` through `CNVC_CUR3`: cursor color/control and FP scale/bias registers.
- `DSCL0` through `DSCL3`: scaler coefficient RAM selection/data, overscan, output timing blanking, line-buffer format/memory, autocal, tap counts, 2-tap controls, scaler mode, filter ratios/initial conditions, recout/MPC size, and DSCL memory power control/status.
- `CM0`, `CM1`, `CM2`, and most of `CM3`: gamut remap, input/output color-space conversion matrices, degamma and regamma LUT controls, piecewise-linear region descriptors for R/G/B RAM A/B banks, bias/scale, HDR multiplier, clamp/denorm/output controls, shared CM memory power, and debug index/data.
- `DC_PERFMON9` through `DC_PERFMON14`: perfcounter/perfmon control, state, current value, high, and low registers for HUBP and DPP perfmon blocks. The comment for DPP3 perfmon appears just after this chunk, so `DC_PERFMON15` is outside this range except as an integration concern for the next chunk.

Every register offset in the chunk has a matching `_BASE_IDX` value of `2`, indicating that consumers should add the offset to `DCE_BASE__INST0_SEG2` through the DC resource helper macros.

## Important APIs, Types, And Macros

This file only defines preprocessor constants. There are no functions, structs, or runtime control-flow constructs in the chunk. The important "API" is the stable naming convention used by the rest of the display driver:

- Register offsets use `mm<block><instance>_<register>`, for example `mmHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS` or `mmCM3_CM_RGAM_RAMB_REGION_32_33`.
- Address-base selectors use the matching `mm<block><instance>_<register>_BASE_IDX`.
- Consumers combine those constants through resource macros such as `SRI(reg_name, block, id)`, which expands to `BASE(mm ## block ## id ## _ ## reg_name ## _BASE_IDX) + mm ## block ## id ## _ ## reg_name`.
- The sibling `dcn_1_0_sh_mask.h` header supplies the corresponding bit shifts and masks, such as `HUBPREQ0_CURSOR_SETTINS` or `CM0_CM_DGAM_CONTROL` field definitions. This offset header provides address identity; the sh/mask header provides bitfield layout.

Concrete downstream macro lists that rely on names from this chunk include:

- `HUBP_REG_LIST_DCN10(id)` in `display/dc/hubp/dcn10/dcn10_hubp.h`, which references many `HUBP`, `HUBPREQ`, `HUBPRET`, and `CURSOR` offsets from this range.
- `IPP_REG_LIST_DCN10(id)` in `display/dc/dcn10/dcn10_ipp.h`, which uses `CNVC_CFG`, `CNVC_CUR`, `HUBPREQ`, and `CURSOR` register names for input pixel processing and cursor programming.
- `TF_REG_LIST_DCN10(id)` in `display/dc/dpp/dcn10/dcn10_dpp.h`, which uses the `CM`, `DSCL`, `CNVC`, and `DPP_TOP` offsets to initialize DPP color/scaler register tables.
- The `SR`, `SRI`, and `SRII` macros in `display/dc/resource/dcn10/dcn10_resource.c`, which materialize generated offsets into runtime register-address structs.

Several names intentionally preserve generated spelling, including `PREFETCH_SETTINS` and `CURSOR_SETTINS`. These spellings are part of the compile-time token contract; "correcting" them in the offset header without changing all macro-list consumers would break compilation.

## Control Flow And Runtime Use

The header itself has no branches or function calls. Runtime control flow enters indirectly when the DCN 1.0 resource layer constructs hardware object register tables:

1. `dcn10_resource.c` includes `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. It defines `BASE(seg)` and `SRI(reg_name, block, id)` helpers. `BASE(mm..._BASE_IDX)` selects the DCE base segment, and the `mm...` offset is added to produce an absolute register index.
3. It builds arrays such as `hubp_regs[]` for four HUBP instances and `tf_regs[]` for four DPP instances.
4. Constructors such as `dcn10_hubp`, `dpp1_construct`, and `dcn10_ipp_construct` receive those register structs.
5. Later display paths program memory input, cursor, scaler, and color-management hardware via `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers against the precomputed addresses.

Because the register tables are constructed at driver initialization time, an incorrect offset in this header becomes a persistent bad address in the hardware object for the lifetime of the driver instance. There is no runtime validation in this header that the offset matches the ASIC register map.

## State And Persistence Behavior

The constants are compile-time state. They do not allocate memory, mutate software state, or persist data themselves. Their persistence effect is indirect:

- At initialization, resource constructors copy the computed register addresses into static or heap-backed hardware object structs.
- During modesets and page flips, the HUBP/HUBPREQ registers in this chunk point the display engine at framebuffer, chroma, metadata, and cursor surfaces. Bad values can persist across flips until the affected pipe is reprogrammed.
- CM and DSCL registers in this chunk hold display-pipe programming for color conversion, gamma LUT access, scaler coefficients, viewport sizing, and line-buffer state. Those hardware registers retain programmed values until reset or overwritten by later display programming.
- Memory power control/status registers (`*_MEM_PWR_CTRL`, `*_MEM_PWR_STATUS`) affect block SRAM or LUT memory power state; incorrect addressing can leave blocks powered incorrectly or read the wrong status.
- VM/aperture and TLB-related HUBPREQ registers affect display fetch address translation for scanout surfaces. Incorrect programming can produce protection faults, underflow, or blank output.

There is no on-disk persistence and no distributed filesystem interaction despite the repository path prefix. This is Linux DRM/AMDGPU display hardware metadata.

## Dependencies And Integration Points

The direct dependencies are purely preprocessor-level:

- `soc15_hw_ip.h` and ASIC base-address headers provide symbols such as `DCE_BASE__INST0_SEG2`, consumed through `BASE(mm..._BASE_IDX)`.
- `dcn_1_0_sh_mask.h` must stay in sync with this offset header so each address has compatible field shift/mask definitions.
- DCN 1.0 display code under `display/dc/resource/dcn10`, `display/dc/hubp/dcn10`, `display/dc/dpp/dcn10`, and `display/dc/dcn10` depends on the exact generated symbol names.
- Later DCN generation headers follow the same naming shape but different address maps; copy/paste across generations is unsafe unless the consuming resource file includes the matching generation-specific offset and sh/mask headers.

Functional integration points by hardware block are:

- HUBP/HUBPREQ/HUBPRET: surface fetch, VM, viewport, flip timing, TTU/QoS, cursor fetch setup, read-line status, and display memory power control.
- CURSOR and CNVC_CUR: hardware cursor surface, positioning, color, scale/bias, hot spot, and enable state.
- CNVC_CFG: input pixel format and format expansion configuration before DPP processing.
- DSCL: scaler tap programming, line-buffer configuration, overscan, recout sizing, and memory power control.
- CM: gamut remap, input/output CSC, degamma/regamma LUT index/data windows, HDR multiplier, range clamp, denorm, output selection, and CM memory power.
- DC_PERFMON: display block performance counter programming and readback for diagnostics/performance tracing.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are normally generated from ASIC register descriptions, and the compiler can only verify that names exist. It cannot verify that `0x0705` is the right address for `mmHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS`.

High-impact risk areas in this chunk include:

- Surface address registers: bad `DCSURF_*_SURFACE_ADDRESS*` offsets can make scanout fetch from the wrong VRAM location, causing corruption, blank displays, GPU faults, or security-sensitive memory exposure.
- Flip/in-use registers: bad `DCSURF_SURFACE_CONTROL`, `DCSURF_FLIP_CONTROL`, `DCSURF_SURFACE_INUSE*`, or earliest-in-use offsets can break page-flip synchronization and tear-free updates.
- VM registers: incorrect `DCN_VM_*` or TLB offsets can cause display fetch protection faults or mask real address-translation issues.
- Timing and prefetch registers: wrong `VBLANK_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `PREFETCH_SETTINS*`, or TTU/QoS offsets can cause underflow, flicker, or unstable high-resolution modes.
- Cursor registers: cursor offsets span both HUBPREQ cursor settings and CURSOR surface/position registers; cross-instance errors show up as missing cursors, cursors on the wrong pipe, or cursor memory faults.
- DSCL/CM LUT registers: LUT index/data windows and scaler coefficient RAM registers are stateful; wrong offsets can corrupt adjacent DPP state or make color/scaler programming appear to succeed while affecting the wrong register.
- Instance stride assumptions: instances 0-3 are similar but not derived at runtime. Each offset is an explicit constant, so a single generated value can be wrong even if surrounding instances look correct.
- Chunk-boundary risk: this chunk begins and ends inside larger generated register families. Review or regeneration must consider adjacent chunks to avoid orphaning the initial trailing `_BASE_IDX` and the final `CM3` continuation.

## Test Signals

There are no unit tests for this header alone. Useful signals come from build coverage, display bring-up, and hardware validation:

- Compile-time signal: AMDGPU display code must compile with `dcn_1_0_offset.h` and `dcn_1_0_sh_mask.h`; missing or renamed macros are caught by resource-list expansion in files such as `dcn10_resource.c`, `dcn10_hubp.h`, `dcn10_ipp.h`, and `dcn10_dpp.h`.
- Register-table sanity: debug dumps or targeted assertions can compare constructed register addresses for `hubp_regs[]`, `tf_regs[]`, and IPP register tables against the expected DCN 1.0 ASIC register map.
- Display functional tests: modeset, multi-plane scanout, page flip, cursor movement, cursor format changes, rotation/mirroring, scaling, chroma formats, and multi-display use exercise HUBP, CURSOR, CNVC, DSCL, and CM offsets from this chunk.
- Stress signals: high-refresh or high-bandwidth modes, dynamic page flips, cursor updates during flips, VRR-like timing changes, and memory-pressure scenarios are likely to expose prefetch, vblank, in-use, TTU/QoS, or VM-addressing mistakes.
- Color/scaler validation: degamma/regamma LUT programming, gamut remap, CSC, HDR multiplier, range clamp, and scaler coefficient tests can reveal CM/DSCL address mistakes that simple scanout may not catch.
- Power-management signal: suspend/resume, display blank/unblank, DC power gating, and memory power status readback exercise the `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` offsets.
- Diagnostics signal: perfmon tools or driver traces that program `DC_PERFMON9` through `DC_PERFMON14` should return plausible counter values and interrupt/status behavior.

For regression review, the strongest evidence is a combination of successful AMDGPU DCN 1.0 build, hardware modeset on an affected ASIC, cursor/page-flip/scaler/color tests, and comparison against the authoritative generated register database.

### subset-b-001577: lines 5324-7968

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 5324-7968

Chunk: `subset-b-001577`
Covered source range: lines 5324-7968 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

## Purpose

This chunk is a generated AMD DCN 1.0 register offset header slice. It contains preprocessor constants for MMIO register addresses and matching base-index selectors; it is not executable driver logic. In this range every `#define` is an `mm*` address or `mm*_BASE_IDX` macro, for 2,398 macro definitions across 62 generated `addressBlock` sections.

The chunk starts at the tail of the DPP3 color-management block with `mmCM3_CM_CMOUT_CONTROL` through CM memory-power/debug registers, then covers DPP3 perfmon, MPC/MPCC composition, OPP/ABM/output formatting, OPTC/ODM/OTG timing generation, and the beginning of DIO connector-side blocks. It ends inside the DP AUX1 block at `mmDP_AUX1_AUX_LS_DATA_BASE_IDX`; DP AUX1 DPHY/GTC registers and AUX2+ are in the next chunk.

Major hardware surfaces in this range are:

- DPP3 color management and `DC_PERFMON15`.
- Four MPCC instances plus MPC global config, output muxes, update-lock sets, and `DC_PERFMON16`.
- Two ABM instances for backlight/PWM, histogram/local statistics, ACE curves, and master-lock state.
- Six OPP/FMT/OPPBUF/OPP pipe instances, OPP top clock control, and `DC_PERFMON17`.
- Six ODM input blocks and six OTG timing generators, followed by OPTC misc and `DC_PERFMON18`.
- DIO DAC, DOUT I2C, generic I2C, scratch/power/reset/interrupt registers, six HPD blocks, `DC_PERFMON19`, and the first two DP AUX register groups.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is the generated macro namespace:

- `mm<REGISTER>` gives the register offset value used by AMDGPU/DC register helpers.
- `mm<REGISTER>_BASE_IDX` selects the SOC15 base segment to add to that offset. All macros in this chunk use base index `2`.
- Repeated instance prefixes such as `MPCC0..3`, `FMT0..5`, `OPPBUF0..5`, `ODM0..5`, `OTG0..5`, `HPD0..5`, and `DP_AUX0..1` encode physical display block instances.
- Field shifts and masks are not defined here; they live in the companion `dcn_1_0_sh_mask.h`.

Important macro families include:

- `CM3_CM_*`: DPP3 color output control, dither/random seeds, memory power, and test-debug index/data.
- `DC_PERFMON15..19_*`: performance counter control, current-value compare, counter state, and high/low counter value registers for DPP3, MPC, OPP, OPTC, and DIO.
- `MPCC0..3_MPCC_*`: MPC compositor plane selection, OPP routing, blend/control state, stereo/multiplane controls, update-lock selection, offsets, background color, stall status, and busy/idle status.
- `MPC_*`, `MPC_OUT0..3_MUX`, `ADR_*_VUPDATE_LOCK_SET*`, and `CUR*_*_VUPDATE_LOCK_SET*`: global MPC clock/reset/CRC/perf/event/mux controls and vupdate lock routing for address and cursor updates.
- `ABM0..1_*`: backlight PWM levels, sample rates, histogram/statistics controls, ACE offset/slope/threshold programming, debug/capture controls, and ABM memory power/master lock.
- `FMT0..5_*`, `OPPBUF0..5_*`, and `OPP_PIPE0..5_*`: output pixel formatting, dither/clamp/dynamic expansion, 4:2:0 memory controls, output buffer sizing/segmentation, 3D parameters, pipe clock control, and OPP pipe CRC.
- `ODM0..5_OPTC_INPUT_*`: OPTC input global control, control, clock control, and spare registers for output data merge paths.
- `OTG0..5_OTG_*`: horizontal/vertical totals, blanking and sync, startup/update/ready windows, master/global update locks, double buffering, stereo/3D, dynamic refresh, trigger/manual flow controls, static-screen detection, frame/status counters, CRC windows/results, vertical interrupts, GSL, memory power, clock control, and spare registers.
- `DAC_*`, `DOUT_I2C_*`, `GENERIC_I2C_*`, `DIO_*`, `HPD0..5_*`, and `DP_AUX0..1_*`: display I/O configuration for analog DAC, I2C engines, DIO scratch/power/reset/interrupts, hot-plug detect status/control/filtering, and DP AUX software transaction/PHY/GTC registers.

## Control Flow

This header chunk has no internal control flow. The runtime flow is created by consumers that include `dcn_1_0_offset.h` with `dcn_1_0_sh_mask.h`:

1. Resource construction code builds generation-specific register tables from macro lists such as `MPC_COMMON_REG_LIST_DCN1_0`, `TG_COMMON_REG_LIST_DCN1_0`, `OPP_REG_LIST_DCN10`, `AUX_COMMON_REG_LIST`, and ABM register-list macros.
2. The register-table macros expand `mm*` and `mm*_BASE_IDX` names into SOC15 MMIO addresses, commonly through `SR`, `SRI`, `SRII`, or related helpers.
3. Hardware objects such as MPC, OPP, OPTC, AUX, HPD, GPIO, and ABM objects use those table entries with mask/shift metadata to read, write, update, or poll registers.
4. Sequencing, locking, interrupt acknowledgement, and polling behavior live in the DC display code, not in this generated offset header.

Concrete local integration examples include:

- `display/dc/resource/dcn10/dcn10_resource.c`, which builds `mpc_regs`, `tg_regs`, `opp_regs`, and `aux_engine_regs` from the DCN 1.0 offset namespace.
- `display/dc/mpc/dcn10/dcn10_mpc.h`, where `MPC_COMMON_REG_LIST_DCN1_0` maps `MPCC*` and `MPC_OUT*` names in this chunk into the MPC compositor object.
- `display/dc/optc/dcn10/dcn10_optc.h`, where `TG_COMMON_REG_LIST_DCN1_0` maps OTG timing, CRC, update-lock, GSL, and test-pattern registers.
- `display/dc/opp/dcn10/dcn10_opp.h`, where `OPP_REG_LIST_DCN10` maps FMT, OPPBUF, and OPP pipe registers.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and `display/dc/resource/dcn10/dcn10_resource.c`, which use DP AUX and HPD register-list macros for link encoder/AUX resources.
- `display/dc/irq/dcn10/irq_service_dcn10.c` and `display/dc/gpio/dcn10/hw_translate_dcn10.c`, which include this header for IRQ source handling and GPIO register-address translation.

## State And Persistence Behavior

The header itself is stateless. It allocates no memory, performs no I/O, takes no locks, and persists nothing outside the compiled constants.

The hardware registers addressed by these macros do represent persistent GPU display state until later programming, block reset, power-gating transition, suspend/resume restore, firmware intervention, or full GPU reset. State represented by this chunk includes:

- MPC/MPCC blending topology, output routing, background color, update-lock routing, compositor busy/idle status, and MPC CRC/perfmon state.
- ABM backlight/PWM state, histogram/local-statistics sampling, ACE curve programming, and ABM memory-power/master-lock state.
- OPP formatter state, output buffer segmentation, pipe clocks, pipe CRC capture, and OPP top clock state.
- ODM input routing and OTG timing-generator state, including mode timings, vstartup/vupdate/vready windows, update locks, DRR limits, stereo/3D controls, CRC windows/results, vertical interrupts, GSL synchronization, clock gating, and memory-power state.
- DIO state for DAC/I2C/AUX/HPD engines, hot-plug sense and interrupt latches, DIO scratch registers, soft resets, memory power, and generic interrupt messages.
- Perfmon counter configuration and values across multiple display blocks.

Access type is not encoded. Some addressed registers are control registers, some are status/readback registers, and some status or interrupt bits are acknowledged through companion fields in the mask header. Callers must rely on the block implementation and hardware spec for ordering, double-buffering, write-one-to-clear behavior, and safe polling.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor and AMD's generated ASIC register database. Practical dependencies include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h` for matching field shifts and masks.
- SOC15 base-address helpers and generation base tables such as `soc15_hw_ip.h` and `vega10_ip_offset.h`, which resolve `*_BASE_IDX` into an MMIO base.
- AMD DC register-helper macros and hardware-object register tables in the display core.

This chunk is integrated with DCN10 resource construction and hardware programming for:

- MPC/MPCC composition and output muxing.
- OPP/FMT output formatting, dither/clamp/4:2:0 handling, OPPBUF, and OPP pipe CRC.
- OPTC/OTG timing, vblank/vline/vupdate interrupts, CRC, dynamic refresh, update locks, stereo, and GSL.
- AUX/HPD/link-encoder and GPIO paths used for connector detection, DPCD/EDID access, and DP link training.
- ABM/backlight and adaptive brightness logic via shared DCE/DC ABM helpers.
- DC perfmon diagnostics for DPP, MPC, OPP, OPTC, and DIO blocks.

The file path is under a local `ceph-client` source mirror, but this chunk is AMDGPU display hardware metadata and has no Ceph filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These are untyped preprocessor constants; a wrong offset, base index, or instance prefix can compile cleanly while reads and writes target the wrong MMIO register.

Repeated instance blocks are a major review hazard. OTG0-5, FMT0-5, OPPBUF0-5, HPD0-5, and related blocks are nearly identical but have different offsets. A copy or generator error can affect only one display pipe or connector, so single-pipe testing may not catch it.

Chunk boundaries are incomplete. The first lines continue DPP3 CM definitions that began in the previous chunk, and this range ends in the middle of DP AUX1. The final per-file reconciliation should merge these with adjacent chunks before describing the full file.

Several addressed blocks are timing-sensitive or externally visible:

- OTG timing, double-buffer, DRR, GSL, and vertical interrupt registers can cause blank output, flicker, missed vblank, or bad multi-display synchronization when misprogrammed.
- MPCC and MPC mux registers define compositor topology; stale or wrong addresses can route planes to the wrong OPP or leave blend state busy.
- OPP formatter and output buffer registers affect color depth, dithering, 4:2:0 handling, segmentation, CRC, and final scanout formatting.
- HPD and AUX registers affect connector detection, interrupt storms/loss, DP AUX transactions, DPCD/EDID reads, MST sideband traffic, and link training.
- ABM/PWM registers can produce incorrect panel brightness or unstable adaptive-backlight transitions.
- Perfmon and CRC registers are often used for diagnostics; bad offsets may hide real hardware problems by reading plausible values from a different block.

All macros in this chunk use base index `2`. Later DCN generations have similar register names with different offsets and sometimes different base indexes, so cross-generation reuse must go through the intended generation-specific register-list macros rather than hard-coded addresses.

## Test Signals

Useful validation signals include:

- Build coverage for DCN10 users that include `dcn_1_0_offset.h`, especially `dcn10_resource.c`, `irq_service_dcn10.c`, `hw_translate_dcn10.c`, `hw_factory_dcn10.c`, MPC, OPTC, OPP, ABM, and link-encoder translation units.
- Generated-header consistency checks that every `mm<REGISTER>` has a matching `mm<REGISTER>_BASE_IDX`, and that consumed registers have corresponding field definitions in `dcn_1_0_sh_mask.h`.
- MMIO table validation that `SR`/`SRI`/`SRII` expansion resolves expected SOC15 base plus offset values for MPC, OPP, OTG, HPD, and AUX instances.
- Multi-pipe display tests across all available OTGs/OPPs/MPCCs, covering modeset, vblank/vline/vupdate IRQs, page flips, update locks, DRR, stereo/GSL where supported, CRC readback, and suspend/resume restore.
- Plane composition tests that exercise MPCC selection, OPP routing, background color, alpha/blend modes, and busy/idle polling.
- Output formatting tests for bit depth, dithering, clamp, dynamic expansion, 4:2:0 paths, OPPBUF segmentation, and OPP pipe CRC.
- Hot-plug and AUX tests across every connector: HPD connect/disconnect, delayed sense, RX IRQ, debounce/filter programming, EDID/DPCD reads, DP link training, AUX timeout/error handling, and MST sideband traffic.
- ABM/backlight tests for user level, target/current level readback, PWM update sample rate, histogram/ACE programming, master-lock handling, and panel suspend/resume.
- Perfmon tests that program event selection, start/stop counters, read high/low values, and verify interrupts or compare values without disturbing adjacent display block registers.

## Cross-Chunk Notes

Earlier chunks own the beginning of `dcn_1_0_offset.h`, including the full DPP0-3 and DPP3 CM context leading into the first lines here. Later chunks complete DP AUX1, AUX2+, DIG/link encoder, DP PHY, audio, clock-source, and remaining DCN 1.0 offset definitions. The merge lane should present the full source file as generated DCN 1.0 MMIO address metadata paired with `dcn_1_0_sh_mask.h`, not as algorithmic driver code.

### subset-b-001578: lines 7969-10476

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h

Chunk: `subset-b-001578`
Covered source range: lines 7969-10476 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

## Purpose

This chunk is part of a generated AMD DCN 1.0 MMIO register offset header. It contains preprocessor constants only; there are no executable functions, structs, enums, or storage objects. Its purpose is to publish register addresses and register-base-index selectors used by AMDGPU display code when programming DCN 1.0 display I/O, stream encoder, link encoder, AUX, and DCIO global hardware blocks.

The source tree path is under a local `ceph-client` mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The covered range starts inside the `dce_dc_dio_dp_aux1_dispdec` address block. Lines 7969-7986 provide the tail of `DP_AUX1` DPHY and GTC sync offsets; the earlier `DP_AUX1_AUX_CONTROL`, software-control, arbitration, interrupt, status, and data offsets are in the previous chunk. The range then covers:

- complete DisplayPort AUX instance blocks `DP_AUX2` through `DP_AUX6`;
- DIO digital/HDMI/audio-format/TMDS blocks `DIG0` through `DIG6`;
- DisplayPort link/stream/secondary-packet blocks `DP0` through `DP6`;
- the global `DCIO` block containing generic display I/O controls, UNIPHY crossbar/link controls, LVTMA power sequencing, backlight PWM, genlock/swaplock pads, impedance calibration, DPCS interrupts, semaphores, and USB-C flip selection.

The chunk ends cleanly at `mmDCIO_USBC_FLIP_EN_SEL_BASE_IDX`. The next chunk begins after this DCIO block.

## Important APIs, Types, And Macros

There are no C APIs in this header section. The public interface is the generated offset macro convention:

- `mm<REGISTER>` gives the register's MMIO offset within the selected ASIC register aperture.
- `mm<REGISTER>_BASE_IDX` gives the base-segment selector used by SOC15 register helpers. Every macro in this chunk uses base index `2`.
- Register prefixes identify repeated hardware instances: `DP_AUX1..6`, `DIG0..6`, `DP0..6`, `UNIPHYA..G`, and global `DC`, `DCIO`, `LVTMA`, `BL`, `AUXP`, and `AUXN` registers.

Important macro families in this chunk include:

- `mmDP_AUX1_AUX_DPHY_*` and `mmDP_AUX1_AUX_GTC_SYNC_*`: the tail of AUX instance 1, covering DPHY TX/RX control/status and GTC sync status/control offsets.
- `mmDP_AUX2..mmDP_AUX6_AUX_*`: full AUX controller instance offsets for software transaction control/status/data, AUX arbitration, interrupts, line-status capture, DPHY TX/RX tuning/status, and GTC sync controller/error/status registers.
- `mmDIG0..mmDIG6_DIG_*`: digital encoder front-end and back-end control, output CRC, clock/test/random patterns, FIFO status, version, lane enable, and DIG back-end enable/control offsets.
- `mmDIG0..mmDIG6_HDMI_*`: HDMI control/status, audio packet, ACR packet and CTS/N values, VBI packet controls, infoframe controls, generic packet controls, GCP/AVMUTE, data-block control, and related status offsets.
- `mmDIG0..mmDIG6_AFMT_*`: audio-format and infoframe packet metadata, ISRC packets, MPEG/generic packet payload/header registers, audio info/channel-status registers, audio CRC, ramp controls, audio source selection, and VBI/infoframe packet-control offsets.
- `mmDIG0..mmDIG6_TMDS_*`: TMDS control, control-character, sync-character pattern, stereosync, generated control bits, feedback, and DC balancer offsets.
- `mmDP0..mmDP6_DP_*`: DisplayPort link control, pixel format, MSA colorimetry/timing/misc/VBID, stream control, timing M/N values, link framing, DPHY control/training/scrambler/CRC/fast-training, secondary-data packet controls, audio M/N/readback, timestamp, MST stream allocation table registers, MSO, DSC, data-block control, and extended secondary-packet controls.
- `mmDC_*`, `mmDCIO_*`, `mmUNIPHY*`, `mmLVTMA_*`, and `mmBL_*`: global display I/O controls for reference clocks, GPIO debug, pin straps, DVO data, panel power sequencing, backlight PWM, genlock/swaplock pads, clocking, soft reset, DPHY selection, impedance calibration, DPCS interrupts, eight DCIO semaphores, and USB-C flip enable selection.

The matching field masks and shifts are in the companion `dcn_1_0_sh_mask.h` header. Consumers pair these offset macros with field macros through AMD display register helper tables.

## Control Flow

This chunk has no internal control flow. Every meaningful line is a `#define` consumed by C preprocessor substitution.

Runtime control flow is in the AMD display code that builds register tables from these macros:

1. DCN 1.0 modules include `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. Table-building macros such as `SRI(...)` concatenate a block name, instance id, and register name, then add the SOC15 base segment selected by `mm..._BASE_IDX`.
3. Object constructors store the resulting offsets in typed register tables such as `struct dcn10_link_enc_registers`, `struct dcn10_link_enc_aux_registers`, and `struct dcn10_stream_enc_registers`.
4. Runtime paths call register helpers such as `dm_read_reg`, `generic_reg_update`, and related DC helper macros to read, modify, write, or poll hardware registers.

Concrete local integration paths include:

- `display/dc/dio/dcn10/dcn10_link_encoder.h` builds AUX, DIG, TMDS, and DP link-encoder register lists using `SRI(AUX_CONTROL, DP_AUX, id)`, `SRI(DIG_BE_CNTL, DIG, id)`, `SRI(DP_LINK_CNTL, DP, id)`, `SRI(DP_DPHY_CNTL, DP, id)`, `SRI(DP_MSE_SAT*, DP, id)`, and related macros defined in this chunk.
- `display/dc/dio/dcn10/dcn10_link_encoder.c` programs output setup, DP link training patterns, lane settings, MST allocation tables, PSR fast training, secondary packets, AUX receiver controls, and output disable/enable paths through the register tables derived from this chunk.
- `display/dc/dio/dcn10/dcn10_stream_encoder.h` maps DIG/HDMI/AFMT and DP stream registers such as `DIG_FE_CNTL`, `DIG_FIFO_STATUS`, `HDMI_CONTROL`, `AFMT_*`, `DP_PIXEL_FORMAT`, `DP_SEC_CNTL*`, `DP_VID_M/N`, `DP_MSA_*`, `DP_MSE_RATE_*`, and `DP_DB_CNTL`.
- `display/dc/irq/dcn10/irq_service_dcn10.c` includes this offset header with the companion mask header and uses the same base-index/address convention while mapping DCN 1.0 interrupts to DAL IRQ sources.
- Resource construction in DCN 1.0 display code uses these register-list macros to instantiate per-link and per-stream hardware objects for up to seven digital link encoders.

The header itself does not express sequencing. Consumers must perform the correct hardware order around stream enable, link training, AUX transactions, HPD/link ownership, PLL/PHY setup, packet update pending bits, resets, and power-domain state.

## State And Persistence Behavior

The header is stateless. It does not allocate memory, perform I/O, or persist data. Its macros become compile-time constants in driver objects.

The hardware registers addressed by these macros represent state that persists in GPU display hardware until changed by driver writes, firmware, hotplug activity, link retraining, power management, display block reset, suspend/resume, or GPU reset. State categories represented in this chunk include:

- AUX controller state: software transaction buffers, transaction start/control, arbitration ownership, interrupt state, line-status/error capture, DPHY TX/RX tuning and status, and GTC sync status.
- DIG and HDMI state: front-end source/start, back-end enable/mode, clock/test patterns, FIFO status, lane enable, HDMI packet generation, deep color, data scrambling, generic packets, infoframes, AVMUTE, and audio packet controls.
- AFMT/audio state: audio source selection, channel status words, 60958 data, audio CRC, ISRC/MPEG/generic packet contents, ramp controls, VBI packet state, and frame/immediate packet update behavior.
- DP link and stream state: link training completion/status, lane configuration, DPHY training pattern/symbol/scrambler/CRC/fast-training controls, video stream enable/status, M/N timing generation, MSA timing/colorimetry/VBID values, secondary packet scheduling, audio M/N values, MST stream allocation table slots/status, DSC/MSO controls, and data-block controls.
- DCIO global state: reference-clock and clock-control selection, soft reset, DPHY selection, UNIPHY crossbar routing, panel power sequencing, backlight PWM timing/lock state, impedance calibration controls, DPCS interrupt latches, global semaphores, and USB-C flip routing.

Access type and side effects are not encoded here. Some registers are durable configuration bits; others are read-only status, sticky interrupt/status bits, write-one-to-clear/acknowledge bits, self-clearing update requests, or power-domain-gated registers. The generated names hint at behavior (`*_STATUS`, `*_CONTROL`, `*_CNTL`, `*_INTERRUPT`, `*_READBACK`, `*_UPDATE`, `*_SOFT_RESET`, `*_SEMAPHORE`), but callers must rely on the register specification and existing DC helper sequences.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor and the AMD generated-register naming scheme. Practical dependencies include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h` for the bit masks and shifts matching the offsets in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_hw_ip.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_ip_offset.h` for SOC15 base segment metadata used with `_BASE_IDX`.
- AMD display register helpers and table macros, especially `SRI`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `dm_read_reg`, and generic register update/read helpers.
- DCN 1.0 DIO/link/stream encoder code under `display/dc/dio/dcn10/`.
- DCN 1.0 IRQ service under `display/dc/irq/dcn10/`.

The instance layout is a key integration contract. The chunk defines seven DIG/DP instances (`0..6`) with regular 0x100 register-spacing in the generated offsets, and seven AUX-visible instance numbers across the file (`0..6`, with this chunk containing the tail of `1` and full `2..6`). Consumers often write field/mask tables against instance `0` names, then use `SRI` and instance ids to select the matching offset. If the repeated offsets drift, generic per-instance code can silently program the wrong physical encoder or link.

The `DCIO` block integrates across several display subsystems rather than one stream: UNIPHY link routing, DPHY selection, panel/backlight sequencing, genlock/swaplock pad control, impedance calibration, DPCS interrupt reporting, semaphores, and USB-C flip routing affect link encoders, GPIO/HPD routing, panel power, and low-level PHY bring-up.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong offset or base index can compile cleanly while reading or writing an unrelated MMIO register.
- The chunk starts mid-block. `DP_AUX1` is incomplete here; final file-level reconciliation must merge this chunk with the previous chunk before treating AUX1 as fully described.
- The repeated `DIG0..6`, `DP0..6`, and `DP_AUX2..6` definitions are highly regular. A single copied instance number, address, or base-index error can affect only one connector path and may appear as a port-specific black screen, AUX timeout, audio failure, MST failure, or bad link-training behavior.
- `DIG` and `DP` blocks share an instance id and base address comments, but they are separate register families. Mixing a DIG address with a DP mask/field table, or vice versa, is not type-checked by C.
- AUX DPHY and DP DPHY controls are timing- and board-sensitive. Incorrect offsets can cause intermittent EDID/DPCD failures, link-training failures, PSR failures, MST sideband instability, or hotplug/link recovery problems that are hard to reproduce.
- HDMI/AFMT packet registers are protocol-sensitive. Wrong offsets can corrupt infoframes, audio channel status, ACR values, generic packet payloads, AVMUTE behavior, or deep-color/scrambling setup while the display link otherwise appears active.
- DP secondary-packet, MSA, M/N, MST allocation, MSO, and DSC registers are mode-sensitive. Misprogramming can break high-bandwidth modes, audio, MST topologies, DSC-enabled modes, or data-block-disable behavior without affecting simpler modes.
- DCIO global registers have broad blast radius. Soft reset, DPHY selection, UNIPHY crossbar, impedance calibration, panel power sequencing, PWM, semaphores, and USB-C flip selection can affect multiple connectors or the whole display I/O fabric.
- The header does not encode register access restrictions, locking, reserved bits, reset values, or power-domain requirements. Callers must use established helper paths rather than ad hoc MMIO writes.

## Test Signals

Useful validation signals include:

- compile coverage for DCN 1.0 display code that includes `dcn_1_0_offset.h`, especially `irq_service_dcn10.c`, `dcn10_link_encoder.c`, `dcn10_link_encoder.h`, `dcn10_stream_encoder.c`, `dcn10_stream_encoder.h`, and DCN 1.0 resource construction files;
- generated-header consistency checks ensuring every `mm<REGISTER>` used by `SRI` register-list macros exists with a matching `_BASE_IDX`, and every referenced field in `dcn_1_0_sh_mask.h` has a matching address macro in this offset header;
- per-instance duplicate-pattern checks across `DIG0..6`, `DP0..6`, and `DP_AUX2..6` to verify intended register spacing and to catch a single bad copied address;
- hardware smoke tests across every physical connector path, including modeset, blank/unblank, stream enable/disable, suspend/resume, and rapid hotplug;
- DisplayPort tests for DPCD/EDID AUX reads, link training at all supported link rates/lane counts, test patterns, scrambler/training-pattern changes, PSR fast training, MST stream allocation, audio over DP, DSC/MSO modes where supported, and link recovery after disconnect;
- HDMI/DVI tests for TMDS output, deep color, scrambling, audio packets, ACR values, AVI/audio/vendor/generic infoframes, AVMUTE, and mode switches between common pixel formats;
- debug/readback checks for FIFO status, DPHY CRC/status, MSE SAT status, audio M/N readback, AFMT status, DPCS interrupts, DCIO semaphores, backlight PWM readback, and panel power sequencing state;
- negative signals in logs or display behavior: AUX timeouts, HPD/RX IRQ anomalies, link-training retries, black screens, missing audio, corrupted infoframes, MST payload failures, underflow/FIFO errors, stuck packet-update pending bits, bad backlight/panel sequencing, or failures limited to one encoder instance.

### subset-b-001579: lines 10477-13111

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 10477-13111

## Scope

This chunk covers lines 10477-13111 of the generated AMD DCN 1.0 register offset header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable control flow. The chunk starts at the `dce_dc_dcio_dcio_chip_dispdec` address block with DC GPIO offsets and ends inside the `azinputendpoint_f2codecind` indexed Azalia input endpoint block after the first input pin configuration-default register.

The slice contains 2635 source lines, 2404 `#define` lines, and 32 named `addressBlock` sections. Most direct MMIO-style macros are paired with a `_BASE_IDX` macro, while indexed register blocks use `ix*` names without `_BASE_IDX`. The exported surface is therefore an ABI-like set of symbolic register addresses for DCN 1.0 display, GPIO, PHY, VGA, and Azalia audio code.

## Purpose

The macros map hardware register names to DCN 1.0 offsets or indexed-register addresses. Driver code combines these constants with ASIC base-address data and companion shift/mask headers to program display I/O hardware.

The major hardware areas in this chunk are:

- DCIO GPIO register groups for generic GPIO, DVO data, DDC1-DDC6, DDC VGA, sync, genlock/swaplock, HPD, power sequencing, pad strength, AUX/I2C pads, DVO strength/reference/skew control, I2S/SPDIF, AUX control, RX enable, and pull-up control.
- DAC and UNIPHY reserved macro-control windows, including four large repeated `DCIO_UNIPHY{0..3}_UNIPHY_MACRO_CNTL_RESERVED{0..159}` blocks.
- Four COMBOPHY instances, each split into common/fuse/RFU registers, TX lane command/DFE/RFU registers, and PLL frequency/spread-spectrum/RFU/wrapper-control registers.
- ZCAL macro-control, compensation enable, auto-calibration control, and fuse offsets.
- Indexed VGA sequencer, CRT controller, graphics controller, and attribute-controller registers.
- Indexed Azalia F2 codec output endpoint registers, audio descriptor and sink-info tables, CRC result windows, and the beginning of the Azalia input endpoint register map.

## Important Macro Families

Direct MMIO offset macros in this chunk follow a paired pattern:

- `mmREGISTER` gives the register offset within its hardware address segment.
- `mmREGISTER_BASE_IDX` selects the base segment index used by local register helper macros such as `BASE(mmREGISTER_BASE_IDX) + mmREGISTER`.

Indexed-register macros follow an `ixREGISTER` form. These values are not simple direct MMIO offsets in the same way as `mm*` macros; they are indices or codec verb-style node/register addresses for indirect VGA and Azalia access paths.

The `dce_dc_dcio_dcio_chip_dispdec` block has 148 defines. It exposes the DC GPIO hardware that DCN GPIO translation code maps to software GPIO IDs: generic pins, DDC lines, HPD lines, sync pins, genlock/swaplock pins, DVO data, power sequencing, and I2C/AUX related pads. Representative macros include `mmDC_GPIO_GENERIC_MASK`, `mmDC_GPIO_DDC1_A`, `mmDC_GPIO_DDC6_Y`, `mmDC_GPIO_DDCVGA_A`, `mmDC_GPIO_SYNCA_A`, `mmDC_GPIO_GENLK_A`, `mmDC_GPIO_HPD_A`, `mmDC_GPIO_PWRSEQ_A`, `mmDC_GPIO_I2CPAD_A`, `mmDC_GPIO_AUX_CTRL_0`, `mmDC_GPIO_RXEN`, and `mmDC_GPIO_PULLUPEN`.

The `dce_dc_dcio_dcio_dac_dispdec` block is a small reserved DAC macro-control window: `mmDAC_MACRO_CNTL_RESERVED0` through `mmDAC_MACRO_CNTL_RESERVED3`, each with base index 2.

The UNIPHY blocks are highly regular. `dce_dc_dcio_dcio_uniphy0_dispdec`, `...uniphy1...`, `...uniphy2...`, and `...uniphy3...` each provide 160 reserved macro-control offsets and 160 base-index macros. These appear as `mmDCIO_UNIPHYN_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` for N = 0..3. They reserve a broad register-address surface for PHY macro internals without exposing field-level meaning in the offset header.

Each COMBOPHY instance has three related address blocks:

- `dce_dc_combophy_dc_combophycmregsN_dispdec` exposes common registers, fuse registers, spare/RFU control, and display RFU offsets such as `COMMON_FUSE1`, `COMMON_FUSE2`, `COMMON_TXCNTRL`, `COMMON_RXCNTRL`, `COMMON_TXCNTRL2`, `COMMON_ZCALCODE_CTRL`, and `COMMON_DISP_RFU0` through `COMMON_DISP_RFU7`.
- `dce_dc_combophy_dc_combophytxregsN_dispdec` exposes per-lane TX registers for four lanes, including `CMD_BUS_TX_CONTROL_LANE{0..3}`, `TX_CONTROL_LANE{0..3}`, `TX_DISP_RFU0_LANE{0..3}` through `TX_DISP_RFU12_LANE{0..3}`, and DFE/RFU lane registers.
- `dce_dc_combophy_dc_combophypllregsN_dispdec` exposes PLL registers such as `FREQ_CTRL0`, `FREQ_CTRL1`, spread-spectrum control, observation/RFU registers, and `PLL_WRAP_CNTRL`.

The ZCAL region is split between five reserved macro-control offsets in `dce_dc_dcio_dcio_zcal_dispdec` and functional ZCAL registers in `dce_dc_zcal_dc_zcalregs_dispdec`: `mmCOMP_EN_CTL`, `mmCOMP_MISC_CTL_0`, and `mmZCAL_FUSES`.

The VGA blocks expose legacy indexed register numbers: sequencer `ixSEQ00` through `ixSEQ04`, CRT controller `ixCRT00` through selected higher registers including `ixCRT18`, `ixCRT1E`, `ixCRT1F`, and `ixCRT22`, graphics controller `ixGRA00` through `ixGRA08`, and attribute controller `ixATTR00` through `ixATTR14`.

The Azalia output endpoint block `azendpoint_f2codecind` maps F2 codec converter and pin-control register indices. It includes converter format/channel/digital-converter/stripe/ramp/GTC registers, converter capability parameters, pin widget control, unsolicited response, pin sense, configuration defaults, speaker and channel allocation, downmix, audio descriptor selection/data, multichannel enables, lipsync, HBR, audio sink info index/data, IEC 60958 channel-status override registers, association info, digital output status, LPIB snapshot registers, coding type, format-change reporting, wireless display identification, remote keepalive, and pin capability parameters.

The `azendpoint_descriptorind` and `azendpoint_sinkinfoind` blocks expose indexed audio descriptor slots `ixAUDIO_DESCRIPTOR0` through `ixAUDIO_DESCRIPTOR13` and sink-info fields such as manufacturer/product IDs, sink description length, port IDs, and `ixSINK_DESCRIPTION0` through `ixSINK_DESCRIPTION17`.

The Azalia CRC blocks provide eight channel result indices each for input CRC0, input CRC1, output CRC0, and output CRC1.

The final `azinputendpoint_f2codecind` block begins the input endpoint map. Within this chunk it covers input converter format/channel/digital-converter fields, input converter capability parameters, input pin widget control, unsolicited response, pin sense, and the first input pin configuration-default register. The rest of the input endpoint block continues after this chunk.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this source slice. The macro names are the interface.

Typical consumers use helper macros like the DCN10 GPIO code's `REG(reg_name)`, which expands `BASE(mmREG_BASE_IDX) + mmREG`. The same source files include `dcn/dcn_1_0_offset.h`, `dcn/dcn_1_0_sh_mask.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`; the offset header supplies register locations, the shift/mask header supplies field layout, and SoC/IP offset headers supply base address selection.

Observed local include users include:

- `display/dc/gpio/dcn10/hw_translate_dcn10.c`, where `mmDC_GPIO_*_A` offsets are translated to logical GPIO IDs and DDC/HPD/generic line IDs.
- `display/dc/gpio/dcn10/hw_factory_dcn10.c`, where GPIO, DDC, HPD, and generic register tables are assembled using DCN 1.0 offset and shift/mask macros.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes the offset header as part of DCN10 interrupt service construction.
- `display/dc/resource/dcn10/dcn10_resource.c`, which includes the generated DCN 1.0 register data for resource setup.
- Powerplay BACO command tables for older ASIC managers (`ci_baco.c`, `fiji_baco.c`, `polaris_baco.c`, `tonga_baco.c`) that reference `mmDC_GPIO_GENERIC_MASK` directly for power-transition scripting.

## Control Flow

The header itself has no runtime control flow. It shapes driver control flow by naming the hardware registers that register helper code reads and writes:

1. Select the correct macro family for the hardware domain: `mmDC_GPIO_*` for GPIO/DDC/HPD, `mmDCIO_UNIPHYN_*` or `mmDC_COMBOPHYN_*` for PHY-related registers, `ixSEQ*`/`ixCRT*`/`ixGRA*`/`ixATTR*` for VGA indexed registers, or `ixAZALIA_*` for Azalia codec/register windows.
2. For direct MMIO registers, add the address segment base chosen by the paired `_BASE_IDX` macro to the `mm*` offset.
3. For field-level programming, combine this offset header with `dcn_1_0_sh_mask.h` so software can preserve reserved bits and update only the intended field.
4. For indexed windows, write/select the `ix*` index through the appropriate VGA, Azalia, descriptor, sink-info, or CRC access path rather than treating it as a normal `mm*` offset.
5. Read back state or status where required by the hardware flow, such as HPD/DDC GPIO state, sink/audio endpoint information, CRC channel results, or PHY/calibration state.

The most sequencing-sensitive runtime flows implied by this chunk are display hotplug/DDC GPIO access, AUX/I2C pad control, PHY/PLL bring-up or diagnostics, ZCAL programming, legacy VGA access, and Azalia endpoint/audio descriptor/sink-info programming. The offset macros do not encode ordering rules; those must come from the hardware programming model and the caller's register access helpers.

## State and Persistence

This header stores no software state and has no persistence. It names hardware state that persists in registers until reset, power transition, firmware/hardware action, or driver writes change it.

State domains visible in this chunk include:

- GPIO state for input/output value, output enable, mask, and active-state registers across generic GPIO, DDC, DDC VGA, sync, genlock, HPD, power-sequence, and I2C pad groups.
- Pad and electrical-control state for GPIO pad strength, DVO strength/reference/skew, AUX control, RX enable, pull-up enable, and I2S/SPDIF pins.
- Reserved or low-level PHY macro state for DAC, UNIPHY0-3, COMBOPHY common/TX/PLL, and ZCAL macro-control windows.
- Calibration/fuse state through ZCAL compensation enable, misc control, and fuse offsets.
- Legacy VGA indexed state in sequencer, CRT, graphics, and attribute controller registers.
- Azalia output endpoint state for converter format, channel/stream ID, digital converter controls, GTC embedding, pin widget behavior, unsolicited responses, pin sense, speaker/channel allocation, audio descriptors, multichannel and HBR/lipsync controls, sink info, IEC channel-status overrides, LPIB snapshots, coding type, format-change reporting, wireless display identification, and remote keepalive.
- Azalia CRC result state for eight channels in four CRC result windows.
- Partial Azalia input endpoint state for input converter and input pin control.

Because many of these registers are hardware-facing latches, status windows, or indirectly indexed tables, software must preserve reserved bits, use the correct access path, and coordinate with power-management state. The `_BASE_IDX` value of 2 is repeated across the direct DCIO/PHY/ZCAL offsets in this chunk and is part of that addressing contract.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is meaningful only with the rest of the AMDGPU display register ecosystem:

- `dcn_1_0_sh_mask.h` supplies field shifts and masks for many of the offsets defined here.
- `soc15_hw_ip.h` and `vega10_ip_offset.h` provide base segment constants such as the `DCE_BASE__INST0_SEG*` values used by DCN10 helper macros.
- DCN10 GPIO factory/translation code maps these offsets to `enum gpio_id`, DDC line IDs, HPD IDs, sync IDs, and generic GPIO instances.
- HPD, DDC, and generic GPIO register table headers use the same offset/shift/mask naming conventions to populate register structs.
- Power-management BACO scripts depend on at least `mmDC_GPIO_GENERIC_MASK` remaining stable for direct read/modify/write command tables.
- Display audio code and diagnostics depend on the Azalia `ix*` endpoint, descriptor, sink-info, and CRC indices matching the hardware codec/register windows.
- Cross-generation generated headers reuse many names with different offsets or identical indexed values; callers must include the header for the active ASIC generation rather than mixing DCN/DCE generations.

The repeated instance structure is an important integration signal. UNIPHY and COMBOPHY instance numbers are encoded in macro names, while GPIO lines and Azalia channel slots are represented by repeated adjacent macro families. Callers should select these symbolically rather than deriving raw offsets by arithmetic unless a local register-table abstraction already proves the layout.

## Risks

The primary risk is silent hardware misaddressing. An incorrect offset or base index can compile cleanly while causing driver writes to touch the wrong GPIO, PHY, ZCAL, VGA, or Azalia register. Symptoms would likely be display hotplug failure, DDC/I2C probing failure, broken AUX or pad behavior, PHY/PLL bring-up instability, audio endpoint misconfiguration, missing sink descriptors, bad CRC diagnostics, or power-transition failures.

Direct and indexed register spaces are easy to confuse. `mm*` macros in this chunk are direct offsets paired with `_BASE_IDX`; `ix*` macros are indexed values for VGA or Azalia windows. Treating an `ix*` value as an MMIO offset, or adding a base index to it, would address the wrong hardware path.

Generated reserved/RFU blocks are still part of the hardware contract. The UNIPHY `RESERVED0..159`, COMBOPHY RFU, DAC reserved, and ZCAL reserved offsets may be used by firmware, diagnostics, bring-up code, or later local patches even though the names do not document field semantics. Renaming or pruning them would break generated-header compatibility.

Repeated instance blocks carry copy/generation risk. A one-register drift among UNIPHY0-3 or COMBOPHY0-3 would be hard to catch by normal compilation and could affect only one physical link, lane group, or connector.

GPIO offsets are tied to logical pin translation. The DCN10 translation code switches on offsets such as `REG(DC_GPIO_DDC1_A)` and uses shift/mask macros to identify pins. A mismatch between offset and mask headers can make the driver classify a pin incorrectly even if both headers compile.

Power-management interaction is sensitive. BACO tables use `mmDC_GPIO_GENERIC_MASK` directly, so changes in this region can affect low-power entry/exit behavior outside the display core.

The chunk boundary is not a semantic boundary. It starts cleanly at a DCIO address block, but it ends in the middle of `azinputendpoint_f2codecind`; the remaining input endpoint, Azalia root, and later stream blocks continue in following lines. Final per-file reconciliation must merge adjacent chunks before presenting the Azalia input endpoint as complete.

## Test Signals

Useful validation signals for this chunk are mostly static, build-time, and hardware-smoke oriented:

- Build coverage for DCN10 display code that includes `dcn_1_0_offset.h`, especially GPIO factory/translation, IRQ service, and resource setup.
- Static generated-header checks that each direct `mm*` macro in these address blocks has the expected paired `_BASE_IDX`, that base indices match the generated ASIC database, and that no duplicate macro names collide.
- Cross-generation regeneration diffs against the authoritative DCN 1.0 register source, with attention to repeated UNIPHY0-3 and COMBOPHY0-3 layouts.
- GPIO smoke tests for DDC1-DDC6, DDC VGA, HPD1-HPD6, generic GPIO A/B, sync, genlock/swaplock, I2C pad, and power-sequence pin access.
- Display connector tests that exercise EDID reads, hotplug interrupts, AUX/DDC probing, and low-power entry/exit paths that touch DC GPIO masks.
- PHY bring-up or diagnostics that verify COMBOPHY common/TX/PLL and ZCAL offsets are reachable on all exposed instances and that reserved/RFU offsets are not accidentally shifted between instances.
- Legacy VGA access tests for sequencer, CRT, graphics, and attribute indexed register selection if the platform uses the VGA path.
- HDMI/DP audio tests that read/write Azalia endpoint converter/pin controls, audio descriptor slots, sink-info strings, multichannel/HBR/lipsync controls, IEC channel status overrides, LPIB snapshot state, and CRC channel result windows.
- Negative/static tests that keep `ix*` indexed-register constants out of direct `REG()` style MMIO expansion paths.

## Cross-Chunk Notes

This is an interior slice of a large generated register offset header. The previous lines cover earlier DCIO, power, backlight, impedance-calibration, interrupt, semaphore, and USB-C flip-selection offsets immediately before the DC GPIO block. The following lines continue the Azalia input endpoint block, then Azalia root and stream indexed blocks. The final merged per-file research should treat this document as the DCIO GPIO/PHY/VGA/Azalia-endpoint slice, not as the complete DCN 1.0 offset-header story.

### subset-b-001580: lines 13112-14114

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h lines 13112-14114

## Scope And Purpose

This chunk is the tail of the generated AMD DCN 1.0 register-offset header. It contains no executable driver logic; it publishes C preprocessor constants for indirect Azalia/HDA audio codec register offsets used by AMDGPU display code. The requested range has 869 `#define` entries and 33 generated `addressBlock` group comments.

The range starts in the middle of the `AZALIA_F2` codec input-pin/root codec indirect namespace, covering response configuration defaults, channel allocation, multichannel enable controls, high-bit-rate audio, LPIB snapshots, input status/infoframe, channel status, and root/function parameters. It then defines 16 stream-indirect blocks, `AZF0STREAM0` through `AZF0STREAM15`, each with FIFO size and latency counter registers. Most of the chunk is repeated output endpoint metadata for `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, followed by input endpoint metadata for `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`. The chunk ends with the header guard `#endif`.

Although the repository path is under `ceph-client`, this file is AMDGPU Linux kernel hardware metadata for DCN 1.0 display/audio blocks. It has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, classes, or local variables in this chunk. The public interface is the generated macro namespace:

- `ixAZALIA_F2_CODEC_*` macros describe function group 2 codec root/function/input-pin indirect offsets. They include vendor/device ID, revision, subordinate-node count, power state, subsystem ID response words, converter synchronization, reset, supported size/rates, stream formats, and power states.
- `ixAZF0STREAM<N>_AZALIA_*` macros, for streams 0 through 15, expose the five common per-stream indirect offsets: FIFO size control, latency counter control, worst-case latency count, cumulative latency count, and cumulative request count.
- `ixAZF0ENDPOINT<N>_AZALIA_F0_CODEC_CONVERTER_*` macros, for endpoints 0 through 7, describe output converter capability, format, stream/channel ID, digital converter, supported formats/rates, stripe/ramp/GTC embedding controls, and GTC counter delta/min/max offsets.
- `ixAZF0ENDPOINT<N>_AZALIA_F0_CODEC_PIN_*` and `ixAZF0ENDPOINT<N>_AZALIA_F0_PIN_CONTROL_*` macros describe output pin capability, unsolicited response, pin sense, widget control, channel speaker, audio descriptors 0-13, multichannel enable/mode, lipsync/HBR responses, sink info 0-8, hot-plug control, configuration default, channel-status override words, LPIB snapshots, coding type, format change, wireless display identification, remote keepalive, audio enable state, and audio enabled/disabled/format-changed interrupt status.
- `ixAZF0INPUTENDPOINT<N>_AZALIA_F0_CODEC_INPUT_*` macros, for input endpoints 0 through 7, provide the smaller input converter/pin set: audio widget capabilities, converter format, channel stream ID, digital converter, stream formats, supported size/rates, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel enable controls, HBR response, channel allocation, hot-plug and force unsolicited response, configuration default, LPIB snapshot registers, input status control, and infoframe.

The `ix` prefix denotes indirect-register offsets rather than flat `mm...` MMIO addresses. Consumers must combine these constants with the appropriate Azalia indirect access mechanism and address-block selection; the header itself does not encode the access method.

## Control Flow

This header chunk has no runtime control flow. Each line is declarative metadata consumed by AMD display/audio driver code or register-description tables.

The implied consumer flow is:

1. Select the relevant Azalia root, stream, output endpoint, or input endpoint instance.
2. Use the matching `ix...` macro as the indirect register index for the hardware operation.
3. Access the register through AMDGPU/DC Azalia register helpers or generated register-table plumbing.
4. For status or interrupt-like registers, read, poll, snapshot, acknowledge, or mask according to the hardware programming guide and companion mask/shift definitions.

The chunk does not describe sequencing requirements. Correct order is external to this file: audio format programming must line up with stream IDs and converter state, endpoint hot-plug/unsolicited-response behavior must match connector events, LPIB snapshots must be captured consistently, and interrupt/status fields must be interpreted with the hardware-defined polarity.

## State And Persistence Behavior

The macros have no mutable software state, locking, allocation, reference ownership, or persistence. They are compile-time numeric constants.

The hardware state identified by these offsets is persistent only in the DCN/Azalia hardware registers. Examples include codec function power/reset state, supported-format and capability readbacks, per-stream latency counters, converter format and digital converter controls, stream/channel routing, endpoint audio descriptors, multichannel and HBR state, pin sense and hot-plug controls, sink info, channel-status override data, LPIB snapshots, audio enable status, and input endpoint status/infoframe data.

Persistence and volatility are register-specific and not encoded here. Some registers are static capabilities, some are live counters or snapshots, some are control fields that remain programmed until modeset/audio reconfiguration/suspend/resume/GPU reset, and some status bits may be sticky, write-one-to-clear, self-clearing, or read-only. The offset header does not communicate those access semantics.

## Dependencies And Integration Points

This file depends on AMD's generated DCN 1.0 ASIC register database. The numeric values must match the hardware indirect register map and the companion DCN 1.0 mask/shift and enum headers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/`.

In this source tree, `dcn_1_0_offset.h` is directly included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`, which uses generated offset and mask metadata to map DCN 1.0 interrupt sources. Other practical consumers may reach these constants through generated register tables or shared AMD display/audio include paths rather than explicit direct textual references to every macro.

The chunk also mirrors Azalia endpoint families visible in adjacent AMD DCE offset headers, so it is part of a larger generated convention spanning display IP generations. Integration surfaces include HDMI/DisplayPort audio enablement, HDA codec enumeration, audio stream setup, ELD/sink information handling, hot-plug and unsolicited response handling, HBR/multichannel audio configuration, latency/counter diagnostics, and DCN interrupt/status plumbing.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. A wrong `ix...` value can compile cleanly while reading or writing the wrong indirect register, producing broken HDMI/DP audio, incorrect codec capability reporting, missed hot-plug or unsolicited events, bad stream routing, disabled audio, bogus LPIB/latency diagnostics, or interrupt storms.

The range is highly repetitive. Streams 0-15 and endpoints 0-7 share near-identical register layouts, while input endpoints use a smaller but similarly repeated set. Generator mistakes, copy/paste edits, or manual review errors can affect only one stream or endpoint instance, so tests that exercise only the first connector or first stream may miss instance-specific defects.

The chunk begins mid `AZALIA_F2_CODEC_INPUT_PIN` family and ends at the file guard, so neighboring chunk context is needed before making whole-file claims about all DCN 1.0 Azalia offsets. The final merge lane should treat the initial `AZALIA_F2` lines as a continuation from the previous chunk, not as the beginning of that logical block.

Names such as `*_INT_STATUS`, `*_UNSOLICITED_RESPONSE_FORCE`, `*_HOT_PLUG_CONTROL`, `*_RESET`, `*_POWER_STATE`, `*_LPIB_SNAPSHOT_CONTROL`, and `*_FORMAT_CHANGED` expose hardware conventions, not high-level boolean APIs. Callers must not infer ack polarity, reset side effects, or snapshot timing only from macro names.

Output and input endpoints differ. Output endpoints include audio descriptors, sink info, channel-status overrides, lipsync, coding type, format-change, wireless-display, remote-keepalive, and audio enable/disable status registers. Input endpoints omit most of that surface and instead use input-pin sense/status/infoframe offsets. Treating the two families as layout-compatible would misprogram later offsets.

## Test Signals

Useful validation is mostly generated-header comparison, build coverage, and hardware/display-audio behavior:

- Build AMDGPU/DCN 1.0 targets and ensure all generated offset users compile without missing, duplicated, or mismatched macro names.
- Compare the 869 constants in this range against AMD's source register database and against sibling DCE/DCN generated headers where the Azalia layout is expected to match.
- Exercise HDMI/DisplayPort audio enumeration so codec root/function parameters, subordinate node counts, supported rates, stream formats, power states, and endpoint capabilities are read correctly.
- Test all available endpoint instances, not only endpoint 0, with hotplug, audio enable/disable, format changes, HBR, multichannel modes, and sink-info updates.
- Run audio playback/format tests covering common PCM rates, channel counts, HBR-capable formats, stream/channel ID programming, and repeated modesets.
- Check LPIB snapshot and latency counter behavior for streams 0-15 where supported, watching worst-case and cumulative latency/request counters for sane monotonic behavior.
- Validate interrupt/status paths for audio enabled, audio disabled, format changed, hot-plug, and unsolicited response events, including masking/acknowledgement behavior in the DCN 1.0 IRQ service.
- Include suspend/resume, GPU reset, connector unplug/replug, and display mode changes while audio is active to catch stale register state or missed reprogramming.

Regression symptoms from bad constants include absent HDMI/DP audio devices, wrong supported audio formats, no sound despite video output, audio dropouts after modeset or hotplug, incorrect multichannel/HBR behavior, stale LPIB snapshots, implausible latency counters, persistent format-change status, or endpoint-specific failures limited to higher-numbered streams/connectors.

## Cross-Chunk Notes

Previous chunks own the earlier DCN 1.0 offset header content and the beginning of the Azalia F2 input-pin block. This chunk completes the file. During reconciliation, the full file should be described as generated DCN 1.0 register-offset metadata, not as algorithmic code, with this range specifically representing the final Azalia stream and endpoint indirect-register namespaces.
