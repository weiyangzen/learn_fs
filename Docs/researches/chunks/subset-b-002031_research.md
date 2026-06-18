# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 10083-12636

Chunk: `subset-b-002031`
Covered source range: lines 10083-12636 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.2.1 register field shift/mask header section. It contains C preprocessor constants used to encode and decode bitfields in display-controller MMIO registers; it does not contain executable driver logic.

The covered range contains 2,107 `#define` entries: 1,054 `__SHIFT` constants and 1,059 `_MASK` constants, grouped under 414 register comments and 11 address-block boundaries. It starts mid-register at the tail of `HUBPREQ3_PREFETCH_SETTINGS`, continues through the rest of several HUBP/DPP instance 3 and DPP instance 0/1 blocks, and ends mid-table inside `CM1_CM_GAMCOR_RAMB_REGION_26_27`.

Major hardware areas covered are:

- `HUBPREQ3` timing, prefetch, vblank, flip, nominal delivery, cursor request, memory power, UCLK p-state force, and status fields.
- `HUBPRET3` detile/read-line control, buffer crossbar, memory power, interrupt, and read-line status fields.
- `CURSOR0_3` cursor surface, size, position, hot spot, stereo, memory power, DMDATA address/control/QoS/status, and software DMDATA fields for HUBP/DPP instance 3.
- `CNVC_CFG0` and `CNVC_CFG1` format-converter fields for surface pixel format, alpha, format expansion, 16-bit conversion, crossbar, floating-point bias/scale, color/luma keying, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0` and `CNVC_CUR1` cursor formatter fields for cursor mode, expansion, enable, pixel inversion, alpha modulation, ROM selection, colors, and FP scale/bias.
- `DSCL0` and `DSCL1` scaler fields for coefficient RAM access, mode, tap count, 2-tap controls, manual replication, horizontal/vertical scaling ratios and initial phases for luma/chroma, black color, update/autocal, overscan, blanking, RECOUT, MPC size, line-buffer format/memory, memory power, OBUF control, and OBUF memory power.
- `CM0` and `CM1` color-management fields for post-CSC matrices, gamut-remap matrices, bias, gamma-correction control and LUT access, gamma RAM A/B region programming, HDR multiplier, memory power, dealpha, coefficient format, and debug index.
- `DPP_TOP0` top-level DPP clock, soft-reset, CRC value/control, and host-read rate fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, or runtime APIs in this chunk. The interface is the generated macro contract shared by AMDGPU Display Core:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the field.
- `//<REGISTER>` comments group fields that belong to one register.
- `// addressBlock: ...` comments mark hardware register-block boundaries.
- The companion offset header, `dcn_3_2_1_offset.h`, supplies matching `reg<REGISTER>` and `reg<REGISTER>_BASE_IDX` address constants.

Important field families in this range include:

- HUBP request timing: `HUBPREQ3_VBLANK_PARAMETERS_*`, `HUBPREQ3_FLIP_PARAMETERS_*`, `HUBPREQ3_NOM_PARAMETERS_*`, `HUBPREQ3_PER_LINE_DELIVERY*`, `HUBPREQ3_REF_FREQ_TO_PIX_FREQ`, and `HUBPREQ3_DST_Y_DELTA_DRQ_LIMIT` describe VM/PTE/meta request timing during vblank, flip, nominal scanout, prefetch, and per-line delivery.
- HUBP power/status: `HUBPREQ3_HUBPREQ_MEM_PWR_CTRL`, `HUBPREQ3_HUBPREQ_MEM_PWR_STATUS`, `HUBPREQ3_UCLK_PSTATE_FORCE`, and `HUBPREQ3_HUBPREQ_STATUS_REG*` expose memory power force/disable/state, UCLK p-state force controls, row/chunk readiness, self-refresh entry/exit, p-state-change allowance, urgent QoS, vblank, pipe recovery/flush, HUBP enable, and flip-active status.
- HUBPRET read-line/detile controls: `HUBPRET3_HUBPRET_CONTROL`, memory power fields, `HUBPRET3_HUBPRET_READ_LINE_CTRL*`, `HUBPRET3_HUBPRET_READ_LINE*`, interrupt fields, read-line value, and status fields support detector-buffer layout, crossbar source selection, read-line capture, and line interrupt behavior.
- Cursor/DMDATA: `CURSOR0_3_CURSOR_*` fields control GPU cursor memory address, dimensions, pitch/mode, enable, x/y position, hot spot, stereo behavior, destination offsets, cursor memory power, and dynamic metadata payload address/control/status/software update semantics.
- CNVC format conversion: `CNVC_CFG0_*` and `CNVC_CFG1_*` fields map surface pixel format, alpha plane, bypass, MSB alignment, clamp, channel crossbar, color-key thresholds, 2-bit alpha LUT, floating-point conversion scale/bias, pre-dealpha, pre-CSC mode/matrix, pre-degamma selection, and pre-realpha controls.
- DSCL scaler programming: `DSCL0_*` and `DSCL1_*` fields cover scaler mode, coefficient RAM selection/phase/filter/tap data, tap counts, 2-tap sharpening, manual replication, luma/chroma scale ratios and init phases, autocal pipe selection, recout/MPC geometry, line-buffer partitioning, clock/memory power, and OBUF controls.
- CM color management: `CM0_*` and `CM1_*` fields cover post-CSC and gamut-remap 3x4 matrix programming, gamma-correction mode/current mode, LUT index/data/control, RAMA/RAMB start/end/offset/region metadata for B/G/R channels, HDR multiplier, GAMCOR memory power, dealpha, coefficient format, and debug index.
- DPP top-level diagnostics and control: `DPP_TOP0_DPP_CONTROL`, `DPP_TOP0_DPP_SOFT_RESET`, `DPP_TOP0_DPP_CRC_*`, and `DPP_TOP0_HOST_READ_CONTROL` control DPP clocks/gating/test clock, CNVC/DSCL/CM/OBUF reset, DPP CRC capture/readback, and host-read pacing.

The repeated-instance pattern matters. The chunk contains full `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and `DPP_TOP0` definitions, then repeats much of the same DPP surface for instance 1. Instance 3 appears for HUBPREQ/HUBPRET/cursor state at the beginning. A macro from the wrong instance usually has the same field meaning but must be paired with the correct register address table.

## Control Flow

This header has no internal control flow. Runtime flow occurs in Display Core consumers that include this file, expand generated register-list macros, and pass the resulting address, shift, and mask tables to hardware object constructors.

The main path in this tree is `display/dc/resource/dcn321/dcn321_resource.c`. That file includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`, defines address-expansion helpers such as `SR` and `SRI`, initializes per-instance register tables, and constructs objects such as HUBP and DPP instances. In particular, `dcn321_hubp_create()` passes `hubp_regs`, `hubp_shift`, and `hubp_mask` into `hubp32_construct()`, while `dcn321_dpp_create()` passes `dpp_regs`, `tf_shift`, and `tf_mask` into `dpp32_construct()`.

The generated fields in this chunk are then consumed indirectly by common register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_WAIT`. Typical runtime sequences are:

1. Resource construction builds per-instance HUBP/DPP register tables using `reg<REGISTER>` offsets and this chunk's masks/shifts.
2. Plane setup programs HUBP timing/prefetch/vblank/flip fields and DPP format-converter/scaler/color-management fields for each active pipe.
3. Cursor updates program `CURSOR0_3_*` and `CNVC_CUR*` fields for cursor memory, geometry, format, colors, and metadata.
4. Scaling and viewport updates program DSCL coefficient RAM, tap counts, mode, ratios, phase init, recout geometry, line-buffer settings, and autocal fields.
5. Color pipeline updates program CNVC pre-CSC/pre-degamma/pre-alpha, CM post-CSC, gamut remap, gamma LUT and RAMA/RAMB region fields.
6. Power-management paths force or release HUBPREQ, HUBPRET, DSCL, OBUF, cursor, and GAMCOR memory power states and poll matching status fields.
7. Diagnostics use DPP CRC, HUBPREQ status, HUBPRET read-line status, DSCL memory status, DMDATA status, and CM/DPP debug fields to verify programmed state.

## State And Persistence Behavior

The header itself is stateless. It allocates no memory, has no locks, performs no I/O, and persists nothing outside compiled constants.

The represented state is GPU display hardware register state. Programmed values remain in registers until overwritten by the driver or firmware, reset by a display-block reset, affected by power gating, lost across suspend/resume or ASIC reset, or reprogrammed during modeset/plane/cursor/color updates.

Persistent programmed state includes:

- HUBP request scheduling for vblank, flip, nominal delivery, prefetch, per-line delivery, cursor request offsets, and p-state force controls.
- HUBPRET crossbar, detile/read-line configuration, memory power control, and line-interrupt configuration.
- Cursor surface addresses, high addresses, dimensions, pitch/mode, enable, position, hot spot, stereo, destination offset, metadata buffer addresses, metadata size/repeat/update policy, and software metadata payload data.
- CNVC surface format, alpha handling, channel crossbar, color-key ranges, pre-dealpha/re-alpha, pre-CSC coefficients, pre-degamma mode, FP conversion bias/scale, and cursor formatter colors.
- DSCL scaling mode, coefficient RAM contents, tap configuration, luma/chroma scaling ratios and init phases, overscan, RECOUT/MPC sizes, line-buffer memory layout, autocal parameters, OBUF controls, and memory power settings.
- CM post-CSC/gamut-remap matrices, gamma-correction mode, LUT index/data/control, RAMA/RAMB region descriptors, HDR multiplier, dealpha behavior, and coefficient format.
- DPP clock/gating controls, soft resets, CRC capture controls, and host-read throttling.

Volatile readback state includes HUBPREQ status registers, HUBPRET read-line interrupt/status/value, cursor and DMDATA completion/status, current pre-CSC/post-CSC/gamut/gamma mode fields, memory power states for HUBPREQ/HUBPRET/DSCL/OBUF/GAMCOR/cursor memories, DPP CRC values, CRC pending/status-like bits, and line-buffer counters.

Some fields are side-effecting or access-sensitive even though the header does not encode access type. Examples include interrupt enable/status/ack fields in `HUBPRET3_HUBPRET_INTERRUPT`, reset fields in `DPP_TOP0_DPP_SOFT_RESET`, update/trigger bits such as `DMDATA_UPDATED` and `DMDATA_SW_UPDATED`, memory power force/disable fields, coefficient/LUT host-select/write controls, and CRC one-shot/pending controls. Consumers must use the existing register helper conventions and the hardware programming sequence for each block.

## Dependencies And Integration Points

Immediate dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which supplies matching register offsets and base indexes.

Primary local integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` includes this header and constructs DCN321 resource objects from the generated register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.h` extends the HUBP mask/shift list with DCN32 fields such as `HUBPREQ0_UCLK_PSTATE_FORCE`; through instance expansion in DCN321 resource construction, the same field lists map onto the per-instance generated macros in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h` provides the common HUBP mask/shift list for prefetch, vblank, flip, cursor, HUBPRET read-line, and VM/request scheduling fields represented by the `HUBPREQ3`, `HUBPRET3`, and `CURSOR0_3` macros in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h` defines DPP register and mask/shift lists for CNVC, CNVC cursor, DSCL, CM, DPP top, gamma, gamut, CSC, and memory-power fields represented by the `CNVC_CFG*`, `CNVC_CUR*`, `DSCL*`, `CM*`, and `DPP_TOP*` macros in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c`, `dcn10_dpp_dscl.c`, and `dcn10_dpp_cm.c` contain shared DPP programming routines that consume the generated DPP shift/mask tables through register helpers for format, cursor, scaler, and color-management programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.c` and older HUBP implementations consume HUBP register tables for cursor, p-state, MALL, buffering, and initialization behavior.

The chunk also depends on generated consistency with nearby DCN 3.2.x and DCN 3.x headers. Many DPP/HUBP field names are intentionally shared across generations and instances, but small numeric differences can be generation-specific. Copying masks from `dcn_3_2_0_sh_mask.h` or other ASIC headers without checking the authoritative DCN 3.2.1 register database can silently misprogram hardware.

## Risks And Edge Cases

- The chunk starts mid-register: only the `DST_Y_PREFETCH` shift and `VRATIO_PREFETCH`/`DST_Y_PREFETCH` masks for `HUBPREQ3_PREFETCH_SETTINGS` are present here; earlier fields are in the previous chunk.
- The chunk ends mid gamma-table family at `CM1_CM_GAMCOR_RAMB_REGION_26_27`; later RAMB regions and any following CM1 fields are in the next chunk. File-level reconciliation must merge adjacent chunks before claiming complete CM1 coverage.
- Generated mask/shift errors compile cleanly. A wrong bit position in HUBP prefetch/vblank/flip scheduling can cause underflow, flicker, missed flips, p-state stalls, or bandwidth failures only under specific modes.
- Repeated instance prefixes are easy to mix. `DSCL0` and `DSCL1`, `CNVC_CFG0` and `CNVC_CFG1`, `CM0` and `CM1`, and `CURSOR0_3` must be matched to the correct register offsets for the pipe being programmed.
- Power-control fields are timing-sensitive. Incorrect HUBPREQ/HUBPRET/DSCL/OBUF/cursor/GAMCOR memory power masks can leave SRAM blocks forced on, forced off, or stuck waiting for a state transition.
- Cursor and DMDATA address/control fields touch GPU memory-backed surfaces and metadata. Wrong high-address, mode, pitch, size, repeat, update, or QoS masks can produce corrupt cursors, stale dynamic metadata, or memory fetch faults.
- DSCL coefficient RAM and tap/phase fields are visually sensitive. Incorrect masks can produce blurring, chroma misalignment, bad 4:2:0 behavior, incorrect viewport/recout geometry, or scaler underflow.
- Color-management tables are large and repetitive. Gamma RAMA/RAMB region start/end/slope/base/offset fields and LUT host-select/write fields are vulnerable to off-by-one, wrong-channel, or wrong-RAM-bank programming mistakes that may only appear in HDR, color-managed, or high-bit-depth modes.
- DPP soft-reset and CRC controls are side-effecting. Incorrect masks can reset the wrong sub-block, leave reset asserted, miss CRC one-shot completion, or read meaningless CRC values.
- High-bit masks such as `0xFFFF0000L`, `0x70000000L`, and similar values should remain in unsigned 32-bit register-helper paths; ad hoc signed arithmetic can create subtle packing bugs.

## Test Signals

Useful validation should combine build-time generated-header checks with hardware-visible DCN321 behavior:

- Build AMDGPU Display Core with DCN321 enabled and ensure all `dcn321_resource.c`, HUBP, DPP, DIO, IRQ, DMUB, clock-manager, GPIO, and resource users resolve the generated DCN 3.2.1 mask/shift names.
- Run generated-register consistency checks over the complete `dcn_3_2_1_sh_mask.h`: every field should have a paired shift/mask except at intentional chunk boundaries; masks should stay within 32 bits; fields in one register should not overlap unexpectedly; and every register should have a matching offset in `dcn_3_2_1_offset.h`.
- Exercise multi-plane modes across all available DCN321 pipes, especially pipes using DPP0/DPP1 and HUBP instance 3, while checking for underflow, missed flips, p-state-change failures, and visual corruption.
- Validate HUBP timing by testing page flips, vblank-heavy workloads, cursor movement, high refresh rates, memory-clock p-state changes, SubVP/MALL-related scenarios where applicable, suspend/resume, and hotplug modesets.
- Validate cursor paths with different cursor sizes, pitches, pixel formats, stereo settings, hot spots, negative/edge positions, dynamic metadata updates, and rapid enable/disable transitions.
- Validate DSCL paths with scaling up/down, 4:4:4 and 4:2:0 formats, chroma scaling, fractional ratios, viewport/recout changes, overscan, tap changes, coefficient RAM reloads, and line-buffer memory pressure.
- Validate CNVC and CM paths with RGB/YCbCr formats, alpha-plane use, pre/post CSC, gamut remap, SDR/HDR switching, degamma/gamma LUT programming, color-keying, dealpha/re-alpha, and high-bit-depth formats.
- Validate DPP diagnostics by enabling DPP CRC one-shot and continuous modes before and after color/scaler/cursor changes, comparing stable CRC values, and checking CRC pending/readback fields.
- Validate memory power behavior by toggling DSCL, OBUF, HUBPREQ, HUBPRET, cursor, and GAMCOR power controls through normal plane enable/disable, idle, blank/unblank, and suspend/resume paths, then polling matching state fields.

## Chunk-Specific Summary

Lines 10083-12636 define DCN 3.2.1 bit shifts and masks for the tail of HUBP request instance 3, HUBPRET instance 3, cursor instance 3, complete DPP0 format/scaler/color/top control blocks, and the beginning-to-mid section of DPP1 format/scaler/color blocks. The chunk is generated register ABI data, not executable logic. Correctness depends on exact numeric masks, pairing with `dcn_3_2_1_offset.h`, safe handling of side-effecting reset/interrupt/update/power fields, and validation across plane flips, cursor updates, scaler programming, color-management LUTs/matrices, DPP CRC diagnostics, and memory-power transitions.
