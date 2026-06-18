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
