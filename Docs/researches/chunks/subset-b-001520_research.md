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
