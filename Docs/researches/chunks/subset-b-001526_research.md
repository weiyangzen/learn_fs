# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 7907-11514

Chunk: `subset-b-001526`
Covered source range: lines 7907-11514 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 11.2 register field mask/shift header segment. It contains no executable C logic; its exported surface is 3,608 preprocessor definitions, forming 1,804 mask/shift constants for DCE 11.2 display-controller register fields.

The constants follow the generated AMD register-header convention:

- `<REGISTER>__<FIELD>_MASK` is the bit mask for a field inside a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` is the corresponding right-shift count.

This chunk covers the tail of DMCU interrupt/status definitions, then DisplayPort stream encoder and AUX-channel fields, DVO output fields, framebuffer compression, formatter/output pixel-processing fields, line-buffer and scaler fields, MVP stereo/video-port fields, and the beginning of color-manager input CSC/prescale fields. The companion address header is `dce_11_2_d.h`; this file supplies field layouts for those register names.

## Important APIs, Types, And Macro Families

There are no functions, structs, typedefs, or enums in this chunk. The effective API is the macro set consumed by AMDGPU/DC register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET_FIELD`, `REG_GET_FIELD`, `set_reg_field_value`, `get_reg_field_value`, `RREG32`, and `WREG32`.

Important macro families in this range:

- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*`: DMCU interrupt occurrence, clear, host mask, microcontroller routing, and IRQ/XIRQ selection fields for DCFE power up/down, DCFEV power events, vblank, static screen, ABM, SCP/MCP, software, and generic DMCU events.
- `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, `DMCU_UC_CLK_GATING_CNTL`, `MASTER_COMM_*`, and `SLAVE_COMM_*`: scratch, interrupt count, firmware checksum sampling, clock-gating, and host/DMCU mailbox fields.
- `DMCU_PERFMON_INTERRUPT_STATUS1..5`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1..5`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1..5`: status, clear, routing, and IRQ selection fields for display pipe perfmon counters across DCFE, DCO, DCP, DMIF, MCIF, ABM, DCPG, and related display blocks.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: DisplayPort receiver-event status and routing fields, including DPRX and DPHY interrupt groups.
- `DP_*`: DisplayPort stream encoder fields for link enable, pixel format, MSA colorimetry/misc/VBID/timing override, video stream control, steering FIFO, DPHY training/scrambling/PRBS/CRC/fast training, secondary data packets, audio M/N readback, MST MSE rate and slot-allocation tables, and DP debug/index/data windows.
- `AUX_*` and `DP_AUX_DEBUG_*`: DisplayPort AUX channel enable/reset, software transaction control/status/data, arbitration, interrupt control, low-speed data/status, DPHY TX/RX controls/status, GTC sync status/error fields, and debug register windows.
- `DVO_*`: DVO enable, source select, output control, CRC, FIFO error status/ack/mask, and debug fields for legacy or external digital-video-output paths.
- `FBC_*`: framebuffer-compression control, source selection, idle-force clear mask, start/stop delay, compression mode/control, indirect LUT entries, CSM region offsets, client region masks, debug CSR access, status, alpha controls, and test-debug fields.
- `FMT_*`: output formatter clamp, dynamic expansion, control, bit-depth truncation/dithering/FRC/randomization, CRC controls/results/masks, side-by-side stereo, YCbCr 4:2:0 hblank early start, and formatter debug/index/data fields.
- `LB_*` and `LBV_*`: line-buffer and virtual/chroma line-buffer data format, memory control/size, desktop height, vline/vblank counters/status, sync reset, black/keyer color controls, buffer levels/urgency/status, no-outstanding-request status, and debug fields.
- `MVP_*` and `DC_MVP_LB_CONTROL`: multi-view/video-port or stereo related controls for AFR flip mode/FIFO, flip-line insertion, line-buffer routing, control/status, in-band capabilities, black keyer, CRC, receive counters, and debug registers.
- `SCL_*`: scaler coefficient RAM selection/data, scaler mode/tap/boundary/replication/automatic ratio controls, horizontal and vertical filter controls/ratios/init values, round offsets, update/pending/taken/lock/coef-complete bits, sharpness, ALU disable, coefficient conflict status, viewport/overscan, mode-change detection, and debug windows.
- `SCLV_*`: virtual/chroma scaler equivalents, including separate luma/chroma horizontal and vertical ratios/init values, viewport and overscan registers for primary and chroma planes, bottom-field init values, update locking, and debug windows.
- `COL_MAN_*`, `INPUT_CSC_*`, and `PRESCALE_*`: start of the color-manager section for input CSC update locking, input CSC mode/type/conversion controls, A/B matrix coefficient registers, and prescale bias/scale for red and green. The blue prescale and output CSC definitions continue in the next chunk.

Generated names ending in a hardware field called `*_MASK` produce identifiers such as `DMCU_INTERRUPT_TO_HOST_EN_MASK__UC_INTERNAL_INT_MASK_MASK`. This is expected: the first `MASK` is part of the hardware register or field name, and the final `_MASK` is the generated mask suffix.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to consumers that perform register programming and polling.

Typical runtime usage is:

1. A DCE 11.2 component constructor builds a register table from `dce_11_2_d.h` addresses and this file's mask/shift constants.
2. The component reads a register through DC register helpers or AMDGPU MMIO helpers.
3. The caller clears or extracts a field with the `*_MASK` macro.
4. The caller shifts a new value with the matching `__SHIFT` macro or delegates that to `REG_UPDATE`/`set_reg_field_value`.
5. Hardware latches, reports, clears, or routes the state according to the register semantics.

Concrete consumers in this tree include:

- `display/dc/resource/dce112/dce112_resource.c`, which includes this header and builds DCE 11.2 register/mask tables for timing generators, stream encoders, hardware sequencer, memory inputs, transforms, OPPs, AUX, I2C, and clock sources.
- `display/dc/hwss/dce112/dce112_hwseq.c`, which includes this header for DCE 11.2 hardware sequencer register programming.
- `display/dc/dce112/dce112_compressor.c`, which programs `FBC_*` fields, including `FBC_CNTL`.
- `display/dc/clk_mgr/dce112/dce112_clk_mgr.c`, which uses the same DCE 11.2 register header family for clock-management programming.
- Shared DCE code such as `display/dc/dce/dce_dmcu.c`, `dce_aux.c`, `dce_stream_encoder.c`, `dce_transform.c`, `dce_opp.c`, and `dce110_opp_csc_v.c`, where these fields shape DMCU interrupt routing, AUX transactions, DP secondary packets/MST rates, scaler/line-buffer state, formatter bit depth, and input CSC programming.

The effective sequencing is controlled by hardware side effects. Examples include interrupt `*_CLEAR` bits, AUX transaction start/done/status bits, DMCU mailbox command/byte count fields, `SCL_UPDATE` pending/taken/lock/coef-complete bits, FBC enable and invalidation controls, FIFO error ack bits, CRC result/status fields, and color-manager update locks.

## State And Persistence Behavior

The header itself stores no mutable state and has no persistence. Its constants are compiled into display driver objects.

The registers represented by these fields are hardware state:

- DMCU interrupt status, clear, routing, mailbox, scratch, and clock-gating fields represent state shared between host driver code and the display microcontroller firmware. Status/clear bits are transient and may be write-one-to-clear or otherwise edge-sensitive.
- DP stream encoder, DPHY, secondary packet, MST, and MSA fields persist as link/stream configuration until the encoder is reprogrammed, disabled, reset, power-gated, or restored after suspend/resume.
- AUX fields represent transaction state. `AUX_SW_DONE`, reply byte counts, timeout/invalid-receive bits, HPD-disconnect status, DPHY status, and GTC sync status are transient observations used by AUX/DDC flows.
- FBC fields persist compressed-framebuffer configuration, CSM offsets, client masks, debug CSR indices/data, and compression enable/status until the compressor is disabled or the display/GPU is reset.
- FMT, LB/LBV, SCL/SCLV, viewport, overscan, input CSC, and prescale fields persist as part of the active scanout pipeline and affect displayed pixels until a modeset, plane update, color update, or reset changes them.
- Debug and test-index/data fields can alter what internal state is observed or written through indexed debug windows; those fields should be treated as hardware diagnostics, not general persistent driver state.

## Dependencies And Integration Points

Direct dependencies are the C preprocessor and AMDGPU/DC register helper conventions. The semantic companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h`

Primary include/use sites in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`

The macro families integrate with several shared DCE/DC subsystems:

- DMCU and link encoder code uses interrupt-routing fields to route static-screen, vblank, power-gating, and other display events to firmware.
- AUX code uses `AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_SW_STATUS`, `AUX_SW_DATA`, and DPHY status fields to run DP AUX/I2C-over-AUX transactions and classify timeout, HPD-disconnect, and invalid-reply failures.
- Stream encoder code uses `DP_SEC_CNTL`, `DP_MSE_RATE_CNTL`, MSA/MST, and DP DPHY fields for infoframes, DP audio packet flow, MST slot/rate programming, link training, and stream enablement.
- Compressor code uses `FBC_*` fields for DCE 11.2 framebuffer compression power-up, enable/disable, LPT support, compressed surface programming, and invalidation triggers.
- Transform/scaler code uses `LB_*`, `SCL_*`, `SCLV_*`, viewport, overscan, and update fields for scaling ratios, coefficient RAM programming, line-buffer format, update locking, and virtual/chroma plane support.
- OPP/color code uses `FMT_*`, `COL_MAN_*`, `INPUT_CSC_*`, and `PRESCALE_*` fields for output bit depth, dithering/truncation, CRC, input color-space conversion, and prescale programming.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped numeric constants; the compiler cannot verify that a mask belongs to the register being updated, that the matching shift is used, or that the value fits within the field width.

This assigned range has two chunk-boundary artifacts:

- It starts at `DMCU_INTERRUPT_STATUS__DCPG_IHC_DCFE0_POWER_UP_INT_CLEAR_MASK`; the matching preceding occurrence fields and earlier DMCU interrupt fields are in the previous chunk.
- It ends at `PRESCALE_VALUES_G__PRESCALE_BIAS_G__SHIFT`; the matching green scale field and the blue/output CSC fields continue in the next chunk.

Interrupt fields require careful semantics. Many `*_OCCURRED`, `*_CLEAR`, `*_MASK`, and `*_TO_UC_EN` fields share the same bit position for status and clear behavior. Treating clear bits as ordinary persistent state can lose interrupts, and misrouting DMCU/UC interrupts can break DMCU-assisted power, ABM/backlight, static-screen, vblank, or perfmon workflows.

DP and AUX fields are protocol-visible. Bad link, training, MSA, MST, secondary packet, or audio M/N values can cause blank displays, link-training failures, wrong colorimetry, broken audio, MST allocation errors, or compliance failures. AUX transaction fields are also timing-sensitive; incorrect done/reset/status handling can turn EDID reads and DPCD transactions into intermittent failures.

FBC fields affect memory layout and display fetch/compression behavior. Incorrect compression enable/source selection, CSM offsets, LPT settings, client masks, or invalidation triggers can corrupt scanout, cause stale frames, increase memory traffic, or interact badly with suspend/resume.

SCL/SCLV, LB/LBV, viewport, overscan, FMT, input CSC, and prescale fields directly affect the visible image. Wrong ratios, init values, coefficient RAM selection, update locking, line-buffer pixel format, color matrices, bit-depth controls, or clamp/dither settings can produce scaling artifacts, color shifts, underflow, tearing, or partial updates.

Generated `*_MASK_MASK` names are easy to mishandle in scripts. Pairing checks and documentation tools must separate the hardware field name from the generated suffix to avoid false positives.

## Test Signals

Useful validation signals are a mix of generated-header consistency, build coverage, and hardware behavior:

- Build coverage for AMDGPU configurations that include DCE 11.2 display support, PowerPlay VegaM paths, and shared DCE/DC components that consume generated register tables.
- Header consistency checks that pair every `*_MASK` with its corresponding `__SHIFT`, while accounting for the two chunk-boundary artifacts and hardware fields that naturally end in `_MASK`.
- DCE 11.2 display bring-up on Polaris/VegaM-class hardware, including modeset, page flip, vblank, suspend/resume, hotplug, and GPU reset recovery.
- DP link-training and stream tests covering MSA colorimetry/misc fields, secondary packets, DP audio, MST slot/rate programming, DPHY CRC/debug status, and fast-training paths.
- AUX/DDC tests across all AUX engines, including EDID reads, DPCD reads/writes, HPD disconnect during AUX, timeout handling, reset sequencing, and GTC sync status behavior.
- DMCU-assisted feature tests for static-screen interrupts, vblank routing, display power-gating events, mailbox communication, firmware interrupt masks, perfmon interrupts, and DMCU clock gating.
- FBC enable/disable, compressed-surface address/pitch programming, LPT enable/disable, invalidation trigger, suspend/resume, and visual corruption checks.
- Scaler and line-buffer tests for luma/chroma scaling, interlaced/bottom-field init, coefficient RAM update, viewport/overscan changes, virtual scaler paths, underflow/status, and update-lock sequencing.
- Formatter/color tests for truncation, spatial/temporal dithering, CRC capture, 4:2:0 timing, input CSC matrices, prescale bias/scale, and visible color correctness.

## Chunk Boundary Notes

This report covers only lines 7907-11514. Earlier chunks contain the start of the DMCU interrupt definitions and other DCE 11.2 field families. Later chunks continue the color-manager prescale/output CSC section and the remaining register field definitions. The final per-file report should merge those adjacent reports before drawing file-wide conclusions.
