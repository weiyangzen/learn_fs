# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001513`: lines 1-4131, `Docs/researches/chunks/subset-b-001513_research.md`
- `subset-b-001514`: lines 4132-7720, `Docs/researches/chunks/subset-b-001514_research.md`
- `subset-b-001515`: lines 7721-11767, `Docs/researches/chunks/subset-b-001515_research.md`
- `subset-b-001516`: lines 11768-15235, `Docs/researches/chunks/subset-b-001516_research.md`
- `subset-b-001517`: lines 15236-17567, `Docs/researches/chunks/subset-b-001517_research.md`

## Chunk Research

### subset-b-001513: lines 1-4131

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 1-4131

## Scope

This chunk covers the opening 4,131 lines of the generated DCE 11.0 register field mask/shift header. The full source file is 17,567 lines, so this report is intentionally a chunk-level artifact for `subset-b-001513`; later chunk reports must cover the rest of the same header before a final per-file synthesis is produced. This span starts at the license and include guard and ends inside the `DC_GPIO_PWRSEQ_Y` field group, after the first GPIO/HPD/PWRSEQ definitions.

## Purpose

`dce_11_0_sh_mask.h` provides C preprocessor constants that describe bit masks and bit shifts for AMD Display Controller Engine 11.0 hardware registers. It contains no executable code, no structs, and no functions. Its purpose is to make register programming code use symbolic names such as `CRTC_H_TOTAL__CRTC_H_TOTAL_MASK` and `CRTC_H_TOTAL__CRTC_H_TOTAL__SHIFT` instead of open-coded bit values.

The chunk is organized as pairs of macros for each register field:

- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask as it appears in a 32-bit MMIO register.
- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used to pack or extract the field.

Consumers combine these with register address headers and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `set_reg_field_value`, or direct mask/shift operations in DCE display code. The values are hardware ABI: changing one constant changes the bits driven into display, clock, memory-interface, link-encoder, GPIO, or power-management registers.

## Important Macro Groups In This Chunk

### File Framing

The chunk begins with the AMD/MIT-style license, `#ifndef DCE_11_0_SH_MASK_H`, and `#define DCE_11_0_SH_MASK_H`. There are no includes and no conditional feature sections in this span. The include guard is not closed in this chunk because the file continues far beyond line 4,131.

### Display Power Gating And PG FSM

The first hardware block covers display pipe and front-end power gating:

- `PIPE0_PG_CONFIG`, `PIPE1_PG_CONFIG`, `PIPE2_PG_CONFIG` expose `PIPE*_POWER_FORCEON`.
- `PIPE*_PG_ENABLE` exposes `PIPE*_POWER_GATE`.
- `PIPE*_PG_STATUS` exposes `PGFSM_READ_DATA`, `DEBUG_PWR_STATUS`, `DESIRED_PWR_STATE`, `REQUESTED_PWR_STATE`, and `PGFSM_PWR_STATUS`.
- `DCFEV0_PG_CONFIG`, `DCFEV0_PG_ENABLE`, and `DCFEV0_PG_STATUS` mirror the same pattern for the virtual display front end.
- `DCPG_INTERRUPT_STATUS` and `DCPG_INTERRUPT_CONTROL` define power-up/down interrupt status, mask, and clear bits for `DCFE0` through `DCFE5`, `DCFEV0`, and `DSI`.
- `DC_IP_REQUEST_CNTL`, `DC_PGFSM_CONFIG_REG`, `DC_PGFSM_WRITE_REG`, and `DC_PGCNTL_STATUS_REG` support IP request enable, PG FSM configuration/write data, and power-gating control status.

These definitions are integration points for display power sequencing and BACO/powerplay flows. Misprogramming clear or mask bits here can leave display power events stuck, masked, or spuriously acknowledged.

### Backlight, ABM, And Panel Power

The early backlight/Adaptive Backlight Management portion includes:

- `BL1_PWM_*` registers for ambient/user/target/current ABM levels, final/minimum duty cycle, ABM control, update sample rate, and group-2 double-buffer lock/update state.
- `DC_ABM1_CNTL`, `DC_ABM1_IPCSC_COEFF_SEL`, `DC_ABM1_ACE_OFFSET_SLOPE_*`, `DC_ABM1_ACE_THRES_*`, `DC_ABM1_ACE_CNTL_MISC`, histogram/lighting sample rate registers, histogram bin shift flags/indexes, and `DC_ABM1_HG_RESULT_*`.
- `DC_ABM1_OVERSCAN_PIXEL_VALUE`, `DC_ABM1_BL_MASTER_LOCK`, and ABM debug index/data.
- Later in the chunk, `LVTMA_PWRSEQ_CNTL`, `LVTMA_PWRSEQ_STATE`, `LVTMA_PWRSEQ_REF_DIV`, and `LVTMA_PWRSEQ_DELAY*` define panel power sequencing fields for target state, `DIGON`, `SYNCEN`, `BLON`, done/state readback, PWM reference divider, and power-up/down delays.
- `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK` define the main panel PWM duty, period, fractional enable, output override, and lock/update behavior.

The ABM and PWM fields are stateful hardware controls. The register-lock and update-pending fields imply double-buffered programming where software must stage values and release locks or wait for frame-start updates. Incorrect masks can cause visible brightness jumps, missed frame updates, or panel power sequencing errors.

### CRTC Timing, Status, Interrupts, And CRC

The CRTC block is dense and central to mode setting:

- Timing geometry: `CRTC_H_TOTAL`, `CRTC_H_BLANK_START_END`, `CRTC_H_SYNC_A/B`, `CRTC_V_TOTAL`, `CRTC_V_TOTAL_MIN/MAX`, `CRTC_V_BLANK_START_END`, `CRTC_V_SYNC_A/B`, and vertical interrupt position/control registers.
- Sync/trigger/control: `CRTC_H_SYNC_A/B_CNTL`, `CRTC_V_SYNC_A/B_CNTL`, `CRTC_TRIGA/B_CNTL`, `CRTC_TRIGA/B_MANUAL_TRIG`, `CRTC_FORCE_COUNT_NOW_CNTL`, `CRTC_FLOW_CONTROL`, `CRTC_VERT_SYNC_CONTROL`, and manual force-vsync controls.
- Status and counters: `CRTC_STATUS`, `CRTC_STATUS_POSITION`, `CRTC_NOM_VERT_POSITION`, frame/VF/HV counters, stereo status, snapshot status/position/frame, and pixel data readback.
- Operational controls: `CRTC_CONTROL`, `CRTC_BLANK_CONTROL`, `CRTC_INTERLACE_CONTROL`, `CRTC_FIELD_INDICATION_CONTROL`, `CRTC_UPDATE_LOCK`, `CRTC_DOUBLE_BUFFER_CONTROL`, `CRTC_MASTER_UPDATE_LOCK`, and `CRTC_MASTER_UPDATE_MODE`.
- Test and validation: `CRTC_TEST_PATTERN_CONTROL`, `CRTC_TEST_PATTERN_PARAMETERS`, `CRTC_TEST_PATTERN_COLOR`, CRC control/window/signature registers, and static screen control.
- Interrupts: `CRTC_INTERRUPT_CONTROL`, `CRTC_V_TOTAL_INT_STATUS`, `CRTC_VSYNC_NOM_INT_STATUS`, and `CRTC_V_UPDATE_INT_STATUS`.

`CRTC_H_TOTAL__CRTC_H_TOTAL_MASK` is used by timing generator code to derive the maximum horizontal total. Many other fields feed mode-set programming, vblank handling, page-flip timing, stereo/3D behavior, CRC capture, and test pattern generation. The field widths in this header effectively define the legal programming range for those higher-level paths.

### DAC, Performance Counter, Reference Clock, And SMU/DMCU

This span includes analog output and instrumentation fields:

- DAC enable/source/CRC/autodetect/force-output/powerdown/comparator/FIFO/debug fields such as `DAC_ENABLE`, `DAC_SOURCE_SELECT`, `DAC_AUTODETECT_*`, `DAC_POWERDOWN`, `DAC_CONTROL`, and `DAC_FIFO_STATUS`.
- `PERFCOUNTER_CNTL`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI/LOW`, and performance debug data.
- `REFCLK_CNTL`, `DPREFCLK_CNTL`, `DCE_VERSION`, `AVSYNC_COUNTER_*`, and DCCG global time counter / deep sleep DTO fields.
- `DMCU_SMU_INTERRUPT_CNTL`, `SMU_CONTROL`, and `SMU_INTERRUPT_CONTROL` for static screen and SMU display interrupts.

These are largely monitoring, legacy analog, and clock-control surfaces. The interrupt ACK/status fields in the perf and SMU blocks are stateful and can lose events if read/modify/write helpers use the wrong field mask.

### DCCG Clocking And Pixel/Audio DTOs

The Display Clock Generator portion covers:

- Clock enable/gate controls: `DAC_CLK_ENABLE`, `DVO_CLK_ENABLE`, `DCCG_GATE_DISABLE_CNTL`, and `DCCG_GATE_DISABLE_CNTL2`.
- Clock gating timing: `DISPCLK_CGTT_BLK_CTRL_REG`, `SCLK_CGTT_BLK_CTRL_REG`, `DPREFCLK_CGTT_BLK_CTRL_REG`, `REFCLK_CGTT_BLK_CTRL_REG`, and `SYMCLK_CGTT_BLK_CTRL_REG`.
- Pixel clock resync/source: `PIXCLK0/1/2_RESYNC_CNTL`, `PHYPLL_PIXCLK_CNTL`, `CRTC0` through `CRTC5_PIXEL_RATE_CNTL`, `DCFEV0_CRTC_PIXEL_RATE_CNTL`, and corresponding `DP_DTO*_PHASE/MODULO`.
- Timebase and ramp controls: `MICROSECOND_TIME_BASE_DIV`, `MILLISECOND_TIME_BASE_DIV`, `DISPCLK_FREQ_CHANGE_CNTL`, and `DENTIST_DISPCLK_CNTL`.
- DCCG performance and debug: `DCCG_PERFMON_CNTL`, `DCCG_PERFMON_CNTL2`, `DCCG_TEST_DEBUG_INDEX/DATA`, `DCCG_TEST_CLK_SEL`, and `DCDEBUG_*`.
- Audio DTO: `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, and `DCCG_AUDIO_DTO0/1_MODULE`.

These masks are used by clock manager and resource programming code to select reference clocks, enable/disable gates, change display clock dividers, program pixel DTOs, and route audio clocks. Several fields are replicated by pipe index; off-by-one use of register instance and matching field mask would silently program the wrong CRTC clock path.

### DMIF, DVMM, MCIF, DCI, And Memory Power

The memory/display interface portion defines:

- DMIF address and arbitration: `DMIF_ADDR_CONFIG`, `DMIF_CONTROL`, `DMIF_STATUS`, `DMIF_ARBITRATION_CONTROL`, per-pipe `PIPE*_ARBITRATION_CONTROL3`, `DMIF_P_VMID`, `DMIF_URG_OVERRIDE`, `DMIF_STATUS2`, per-pipe `PIPE*_MAX_REQUESTS`, and debug fields.
- DVMM: `DVMM_REG_RD_STATUS`, `DVMM_REG_RD_DATA`, `DVMM_PTE_REQ`, `DVMM_CNTL`, `DVMM_FAULT_STATUS`, `DVMM_FAULT_ADDR`, `DVMM_PTE_PGMEM_CONTROL`, and `DVMM_PTE_PGMEM_STATE`.
- Low-power tiling: `LOW_POWER_TILING_CONTROL`.
- MCIF: `MCIF_CONTROL`, `MCIF_WRITE_COMBINE_CONTROL`, `MCIF_VMID`, `MCIF_MEM_CONTROL`, `MC_DC_INTERFACE_NACK_STATUS`, and related debug fields.
- DCI clock, memory power, soft reset, and misc controls: `DCI_MEM_PWR_STATUS*`, `DCI_CLK_CNTL`, `DCI_CLK_RAMP_CNTL`, `DCI_MEM_PWR_CNTL*`, `DCI_SOFT_RESET`, `DCI_MISC`, `DCI_TEST_DEBUG_*`, `DCI_DEBUG_CONFIG`, and per-pipe `PIPE*_DMIF_BUFFER_CONTROL`.

These fields integrate with memory request scheduling, VMID selection, PTE behavior, low-power memory state, underflow detection, and display/memory-interface resets. They are risk-heavy because they affect memory fetch, underflow recovery, fault diagnosis, and clock/power gating around display memory clients.

### DCIO, UNIPHY, AUX, GPIO, HPD, And Sync Routing

The chunk moves from DCI/DCIO into link, pad, and GPIO definitions:

- Generic clock/debug outputs: `DC_GENERICA`, `DC_GENERICB`, `DC_PAD_EXTERN_SIG`, `DC_REF_CLK_CNTL`, and `DC_GPIO_DEBUG`.
- UNIPHY link control for A through G and low-power A/B: `UNIPHY*_LINK_CNTL` and `UNIPHYLP*_LINK_CNTL` fields for pixel-valid reset, channel inversion, lane stagger delay, and link-enable HPD masks.
- UNIPHY channel crossbars for A through G and low-power A/B: `UNIPHY*_CHANNEL_XBAR_CNTL` maps channel sources and link enable bits.
- Impedance calibration: `UNIPHY_IMPCAL_LINKA` through `LINKF`, `UNIPHY_IMPCAL_PERIOD`, `AUXP_IMPCAL`, and `AUXN_IMPCAL`.
- Global sync and timer routing: `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, `DCIO_GSL0/1/2_CNTL`, `DC_GPU_TIMER_START_POSITION_*`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`.
- DCIO reset/debug: `DCIO_CLOCK_CNTL`, `DCIO_DEBUG*`, `DCO_DCFE_EXT_VSYNC_CNTL`, `DBG_OUT_CNTL`, `DCIO_DEBUG_CONFIG`, `DCIO_SOFT_RESET`, `DCIO_DPHY_SEL`, and `DCIO_TEST_DEBUG_*`.
- GPIO families at the tail: `DC_GPIO_GENERIC_*`, `DC_GPIO_DVODATA_*`, `DC_GPIO_DDC1` through `DDC6`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_SYNCA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, and the beginning of `DC_GPIO_PWRSEQ_*`.

These constants are consumed by link encoder, AUX/DDC, HPD, GPIO factory/translation, and sync-lock paths. The chunk ends before the `DC_GPIO_PWRSEQ_Y` group is complete, so cross-chunk synthesis must treat GPIO/PWRSEQ coverage as partial here.

## APIs, Types, And Functions

This chunk exports no functions, no types, and no variables. Its API surface is the macro namespace itself. Important usage conventions are:

- Every register field normally has exactly two macros: `_MASK` and `__SHIFT`.
- Full-register data fields often use `0xffffffff` mask with shift `0x0`.
- Boolean fields usually use a single-bit mask and matching shift.
- Packed repeated fields use regular spacing, such as pipe/HPD/DDC/channel fields at byte or nibble boundaries.

The macros are compile-time constants and are included by C source files under AMDGPU display and power management. No runtime object is created by this header.

## Control Flow

There is no runtime control flow in this header. The effective control flow exists in consumers:

1. A DCE 11.0 implementation includes the register offset header and this shift/mask header.
2. The implementation selects a register address for a hardware block or instance.
3. It packs values with the field `__SHIFT` and `_MASK`, or passes names into AMD display register helper macros.
4. Hardware observes the resulting MMIO write or returns status bits that software extracts with the same constants.

Because the file is pure macro data, compile-time include order and macro naming are the main flow constraints. Including the wrong ASIC generation's `*_sh_mask.h` can compile but program the wrong hardware layout.

## State And Persistence Behavior

The header itself has no storage or persistence. The state described by the macros lives in hardware registers:

- Power-gating and memory-power fields persist in display hardware state until firmware, driver, reset, or power transitions modify them.
- Interrupt status/clear/ACK fields represent edge or sticky hardware state and often require write-one-to-clear or explicit ACK semantics in consumers.
- CRTC timing, lock, double-buffer, and update-pending fields persist across frame timing until the hardware latch point.
- Backlight/PWM and panel power sequence fields directly affect panel-visible state.
- GPIO/DDC/HPD fields reflect pad output enable, mask, pull, receiver, and hotplug status state.

This makes correct mask/shift definitions more important than normal constant tables: a one-bit error may become persistent hardware misconfiguration.

## Dependencies And Integration Points

Primary include sites found in this tree include:

- `drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.c`
- `drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.c`
- `drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.c`
- `drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.c`
- `drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.c`, `dce110_opp_regamma_v.c`, and `dce110_opp_csc_v.c`
- `drivers/gpu/drm/amd/display/dc/dce110/dce110_compressor.c`
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`
- `drivers/gpu/drm/amd/display/dc/dce/dce_aux.c`
- `drivers/gpu/drm/amd/display/dc/dce/dce_link_encoder.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_translate_dce110.c`
- `drivers/gpu/drm/amd/display/dc/irq/dce110/irq_service_dce110.c`
- `drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.c`
- `drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dce110/dce110_clk_mgr.c`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.c`

Nearby ASIC-generation headers such as `dce_10_0_sh_mask.h` and `dce_11_2_sh_mask.h` carry similar names and layouts. This header must be paired with DCE 11.0 register offsets and DCE 11.0 hardware support code, not with DCE 10.x, DCE 11.2, or DCN layouts unless a consumer deliberately shares compatible fields.

## Risks And Edge Cases

- Generated hardware headers are easy to treat as inert, but every constant is a hardware ABI. Manual edits should be avoided unless regenerated from the authoritative register database.
- Some macro names contain doubled `MASK` tokens, for example fields named `*_MASK` become macros like `DCPG_INTERRUPT_CONTROL__DCFE0_POWER_UP_INT_MASK_MASK`. This is intentional naming, not a typo; code generation and consumers must tolerate it.
- Repeated pipe/channel/link blocks increase copy/paste risk. The register instance, field prefix, and mask/shift pair must all come from the same block.
- Interrupt and ACK fields are particularly sensitive because an incorrect mask can clear the wrong event or fail to clear a sticky condition.
- Clock-gate and soft-reset fields can disable display clocks, reset link encoders, or affect memory clients if used with the wrong bit.
- CRTC total/blank/sync field masks define legal timing ranges. Wrong widths can corrupt mode validation or produce invalid timing programming.
- The assigned chunk ends mid-GPIO/PWRSEQ. Any final per-file report must merge later chunks before making whole-file claims about all GPIO, DDC, HPD, and power-sequence macros.

## Test Signals

There are no unit tests for this header in isolation. Useful validation signals for changes or regeneration include:

- A full AMDGPU build that compiles every include site using `dce_11_0_sh_mask.h`.
- Static comparison against the authoritative DCE 11.0 register database or a known-good generated header.
- Display mode-setting tests that exercise CRTC timing, vblank/vupdate interrupts, page flips, stereo/snapshot/CRC paths, and test patterns.
- Backlight and panel tests that verify PWM duty cycle, ABM update behavior, LVTMA power sequencing, and frame-start double-buffer locks.
- Clock manager tests or hardware smoke tests that change display clocks, pixel DTOs, DP reference clocks, and audio DTOs without FIFO errors.
- Hotplug, DDC, AUX, and GPIO tests across HPD1-HPD6 and DDC1-DDC6/VGA pads.
- Power-management tests covering BACO, display power gating, memory power states, soft resets, and underflow/fault reporting.
- Register readback checks for fields with status or update-pending bits, especially `CRTC_*`, `DCCG_*`, `DMIF_*`, `DCI_*`, `DCIO_*`, and `DC_GPIO_*` groups.

### subset-b-001514: lines 4132-7720

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 4132-7720

## Scope

This chunk covers lines 4132-7720 of the AMD DCE 11.0 register mask header. It is a generated/declarative C preprocessor header region, not executable code: the content is a dense catalog of `#define` constants for register field masks and their corresponding shift counts. The chunk contains 3,589 macro definitions. Each field generally appears as a pair:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

The constants are consumed by the AMDGPU display stack when composing read-modify-write values for DCE 11.0 display controller registers, decoding status registers, clearing interrupt bits, programming color pipelines, managing graphics plane addresses, configuring display encoders, and routing DMCU microcontroller interrupts.

## Purpose

The purpose of this chunk is to expose bit layout metadata for several DCE 11.0 hardware blocks:

- GPIO, AUX, DDC, DVO, DAC, UNIPHY, DCRX PHY, and DPHY pad/macro control fields.
- The graphics plane (`GRPH_*`) fetch, format, tiling, flip, address, compression, DFQ, interrupt, underflow, stereo, and counter fields.
- Color-management fields for prescale, input CSC, output CSC, common matrices, denorm, clamp, keying, degamma, gamut remap, dither, LUT, and regamma programming.
- DIG, HDMI, AFMT, and TMDS front-end/back-end encoder and packet/audio fields.
- DMCU control, firmware address, internal memory access, event trigger, interrupt, static-screen, power-gating, vblank, and performance-monitor interrupt fields.

The header lets C code avoid hard-coded bit numbers while still using raw MMIO register programming. For example, a driver can mask/shift `GRPH_CONTROL__GRPH_FORMAT`, `DIG_BE_CNTL__DIG_MODE`, `HDMI_CONTROL__HDMI_DEEP_COLOR_DEPTH`, or `DMCU_INTERRUPT_STATUS__VBLANK1_INT_CLEAR` with symbol names tied to the hardware register manual.

## Important APIs, Types, and Functions

This chunk defines no C functions, structs, enums, or storage objects. Its public API is the macro namespace itself. Important macro families include:

- `DC_GPIO_PWRSEQ_Y`, `DC_GPIO_PAD_STRENGTH_1`, `DC_GPIO_PAD_STRENGTH_2`, `PHY_AUX_CNTL`, `DC_GPIO_I2CPAD_*`: GPIO, power-sequencing, HPD/sync, AUX, DDC, I2C pad enable, receive, pull-down, and drive strength fields.
- `DVO_VREF_CONTROL`, `DVO_SKEW_ADJUST`: digital video output reference voltage and skew tuning fields.
- `DAC_MACRO_CNTL_RESERVED*`, `UNIPHY_MACRO_CNTL_RESERVED*`, `DCRX_PHY_MACRO_CNTL_RESERVED*`, `DPHY_MACRO_CNTL_RESERVED*`: full-register reserved windows. Each reserved macro has a full `0xffffffff` mask and shift `0`, preserving access to reserved macro-control register slots when a caller or table needs symbolic coverage.
- `GRPH_ENABLE`, `GRPH_CONTROL`, `GRPH_SWAP_CNTL`, `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_SECONDARY_SURFACE_ADDRESS`, `GRPH_PITCH`, `GRPH_UPDATE`, `GRPH_FLIP_CONTROL`, `GRPH_DFQ_*`, `GRPH_INTERRUPT_*`, `GRPH_COMPRESS_*`, `GRPH_XDMA_*`, `GRPH_STEREOSYNC_FLIP`, `HW_ROTATION`: primary graphics plane format, tiling, memory address, flip, compression, synchronization, and fault/underflow controls.
- `PRESCALE_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `COMM_MATRIX*`, `DENORM_CONTROL`, `OUT_*`, `KEY_*`, `DEGAMMA_CONTROL`, `GAMUT_REMAP_*`, `DCP_SPATIAL_DITHER_CNTL`, `DC_LUT_*`, `REGAMMA_*`, `ALPHA_CONTROL`: color-processing and blending register fields.
- `DCP_CRC_*`, `DIG_OUTPUT_CRC_*`, `AFMT_AUDIO_CRC_*`: CRC control/result fields used as display and audio test or validation hooks.
- `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_FIFO_STATUS`, `DIG_DISPCLK_SWITCH_*`, `DIG_LANE_ENABLE`, `DIG_TEST_PATTERN`, `DIG_RANDOM_PATTERN_SEED`: digital encoder front-end/back-end selection, test-pattern, FIFO, lane, and clock-switch metadata.
- `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_*`, `HDMI_*_PACKET_CONTROL*`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GC`: HDMI data scrambling, deep color, AVMUTE, ACR, VBI, generic packet, and infoframe control bits.
- `AFMT_*`: audio formatter packet control, IEC 60958 channel status fields, generic and AVI/MPEG/audio infoframe payload fields, ISRC payload bytes, audio source selection, DTO debug, ramp/test, status, and CRC fields.
- `TMDS_*`: TMDS control character generation, feedback, debug, DC balancer, CTL bit generation, stereo sync, and sync pattern fields.
- `DMCU_*`: display microcontroller reset/enable/status, firmware and PC addresses, IRAM/ERAM access, software/internal events, interrupt status/clear, interrupt masks to host/uC, XIRQ selection, static-screen events, and perfmon interrupt routing.

Consumers normally combine these with register offset headers, ASIC-specific register accessor macros, and AMDGPU display helper macros such as field update/read helpers in the surrounding driver tree.

## Control Flow

There is no local runtime control flow. The practical control flow is imposed by callers:

1. Driver code chooses a DCE 11.0 register offset from a companion register header.
2. It composes a value by shifting a field value by `<FIELD>__SHIFT` and constraining it with `<FIELD>_MASK`.
3. It writes the register, or reads a register and extracts a field by applying the same mask/shift pair.
4. For status/interrupt registers, code may write a matching `*_CLEAR` or `*_ACK` field back to clear a latched condition.

The chunk itself therefore behaves as a hardware contract. Bugs are not branch bugs in this file; they are bitfield mapping bugs that propagate into all display initialization, modeset, flip, audio, interrupt, or power-management paths using these symbols.

## State and Persistence Behavior

The macros do not allocate or persist software state. They describe persistent or latched state inside DCE hardware registers:

- `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_SECONDARY_SURFACE_ADDRESS`, high address, pitch, tiling, compression, and update-lock fields persist graphics plane programming until the next modeset or flip sequence changes them.
- `GRPH_UPDATE`, `GRPH_FLIP_CONTROL`, `GRPH_INTERRUPT_STATUS`, `GRPH_XDMA_CACHE_UNDERFLOW_DET_STATUS`, `DCP_CRC_*`, `DIG_FIFO_STATUS`, `HDMI_STATUS`, `AFMT_STATUS`, and many `DMCU_INTERRUPT_STATUS*` fields represent transient, pending, latched, or ack/clear state.
- `DC_LUT_*`, `REGAMMA_*`, CSC, gamut, degamma, denorm, clamp, key, alpha, dither, and prescale fields represent programmed color pipeline state.
- `DMCU_ERAM_*`, `DMCU_IRAM_*`, firmware checksum/address, event, and interrupt-mask fields control the display microcontroller and its memory access windows.
- Full-register reserved macros expose opaque hardware state. Drivers should treat them carefully because reserved fields can have undocumented side effects across ASIC revisions.

## Dependencies

The direct dependency is the C preprocessor. There are no includes visible in this chunk, but the macros depend on the rest of the AMD ASIC register infrastructure for meaning:

- Companion offset headers for DCE 11.0 register addresses.
- AMDGPU display MMIO helpers that use mask/shift constants to read and write bitfields.
- Hardware programming tables and block-specific code for DCP, DIG, HDMI, AFMT, DMCU, DCRX, DPHY, and UNIPHY.
- DCE 11.0 hardware documentation or generated register database that must match these constants.

The macro names encode dependencies on display block naming conventions: `DCP` for display controller pipe, `DIG` for digital encoder, `AFMT` for audio formatter, `DMCU` for display microcontroller, and `GRPH` for graphics plane registers.

## Integration Points

Likely integration points in the broader driver are:

- Plane programming and page-flip code uses `GRPH_*` address, tiling, format, pitch, flip, update, interrupt, DFQ, XDMA, and stereosync fields.
- Color-management code uses `INPUT_CSC_*`, `OUTPUT_CSC_*`, `GAMUT_REMAP_*`, `REGAMMA_*`, `DC_LUT_*`, `DEGAMMA_CONTROL`, `PRESCALE_*`, and clamp/denorm/dither fields.
- Display CRC and validation paths use `DCP_CRC_*`, `DIG_OUTPUT_CRC_*`, and `AFMT_AUDIO_CRC_*`.
- HDMI and DVI/TMDS encoder setup uses `DIG_*`, `HDMI_*`, and `TMDS_*` fields for link mode, packet generation, deep color, scrambling, infoframes, test patterns, and lane enables.
- Audio-over-HDMI/DP setup uses `AFMT_*`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_*`, and IEC 60958 channel status fields.
- Power, backlight, static-screen, vblank, and microcontroller integration uses `DMCU_*` control, event, memory, interrupt, and perfmon routing fields.
- Board/connector bring-up paths use GPIO, HPD, AUX, DDC/I2C pad, DVO, DAC, UNIPHY, DCRX PHY, and DPHY macro fields.

## Risks

- Incorrect mask or shift values can silently corrupt adjacent fields during read-modify-write operations. High-risk examples include `GRPH_CONTROL` tiling/format bits, `DIG_BE_CNTL` encoder routing, `HDMI_CONTROL` deep-color/scrambling bits, and DMCU interrupt masks.
- Many interrupt status fields define both `*_OCCURRED` and `*_CLEAR` with the same mask. Callers must know whether a field is read-only status, write-one-to-clear, or an enable mask; the macro names alone do not enforce safe access.
- `*_MASK_MASK` names, such as interrupt mask fields, can be visually confusing because the first `MASK` is part of the hardware field name and the second is the generated suffix. This increases review risk in manual updates.
- The long `DCRX_PHY_MACRO_CNTL_RESERVED0` through `DCRX_PHY_MACRO_CNTL_RESERVED379` range and similar reserved windows have full-register masks. Accidental writes through these definitions can touch undocumented register space.
- Address fields such as `GRPH_PRIMARY_SURFACE_ADDRESS`, `GRPH_COMPRESS_SURFACE_ADDRESS`, and XDMA recovery addresses mask off low bits and split high bits. Callers must preserve alignment and high-address programming for large GPU addresses.
- Color pipeline fields pack signed, fixed-point, segmented LUT, and matrix coefficients into 16- or 18-bit ranges. Incorrect signedness or scaling in caller code will not be caught by these macros.
- This header is generated-style hardware metadata. Manual edits are risky unless they are synchronized with register offset headers and the authoritative ASIC register database.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Compile coverage: all macros referenced by DCE 11.0 display code resolve with no duplicate/conflicting definitions.
- Static checks: every used field has a matching `_MASK` and `__SHIFT`; each mask aligns with its shift; full-register masks use shift `0`; no field pairs overlap unexpectedly within a register unless they intentionally alias status/clear semantics.
- Display bring-up: modeset tests across HDMI/DVI/DP paths, including deep color, scrambling, audio, and infoframe programming.
- Plane tests: page flips, primary/secondary surface selection, pitch/tiling modes, compression, rotation, stereo sync, and XDMA underflow recovery.
- Color tests: LUT/regamma/degamma, CSC, gamut remap, dithering, clamping, keying, and alpha blending checks.
- Interrupt tests: vblank, page flip, DMCU, static-screen, perfmon, HDMI/AFMT status, FIFO error, and underflow interrupt acknowledge paths.
- CRC tests: DCP output CRC, DIG output CRC, and AFMT audio CRC paths can detect incorrect field extraction or programming.

## Chunk Notes for Merge

This chunk starts mid-header at `DC_GPIO_PWRSEQ_Y` fields and ends within the DMCU perfmon interrupt-to-uC mask definitions. Cross-chunk reconciliation should merge this with earlier/later DCE 11.0 register definitions to produce a whole-file view. The final per-file report should not treat this chunk as owning register offsets or executable behavior; it supplies mask/shift metadata for the code that includes this header.

### subset-b-001515: lines 7721-11767

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 7721-11767

## Purpose

This chunk is a large middle section of the generated AMD DCE 11.0 shift/mask header. It defines preprocessor constants for packed bit fields in display-controller registers: each exported symbol is a `REGISTER__FIELD_MASK` or `REGISTER__FIELD__SHIFT` value used by AMDGPU display code to compose or decode 32-bit MMIO register values without hard-coding bit positions.

The range covers several major DCE hardware surfaces:

- DMCU interrupt routing for display perfmon events and DisplayPort receiver events.
- DisplayPort link, video stream, MSA/VBID, secondary-data-packet, MST, DPHY training/CRC, and AUX channel control/status.
- DVO output and FIFO/CRC diagnostics.
- Frame buffer compression (FBC), formatter (FMT), line buffer (LB/LBV), multi-VPU/MVP, scaler (SCL/SCLV), and color-management blocks.
- Underlay graphics (UNP) surface, tiling, DVMM/PTE, flip, interrupt, CRC, and rotation controls.
- Legacy VGA sequencer/CRTC/graphics/attribute registers and VGA display mux/control state.
- Pixel/display PLL and VGA PPLL fields, plus the beginning of UNIPHY transmitter and power-control fields.

This file does not implement policy or algorithms. Its purpose is to preserve the ASIC register layout as C macros so higher-level display, power, hotplug, AUX/I2C, color, flip, and clock code can perform read-modify-write operations against the correct hardware bits.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this chunk. The important interface is the generated macro namespace:

- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK*` and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*`: enable and IRQ-route perfmon counter/off interrupts for DCI, DCO, DCCG, DCFE0-5, WB, DCRX, and DCFEV paths.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: status/clear, microcontroller enable, and XIRQ selection fields for DPRX stream events, DPHY errors, AUX/I2C/CPU events, and AUX message timeouts.
- `DP_*`: DisplayPort link and video stream fields, including `DP_LINK_CNTL`, pixel format/colorimetry, lane configuration, M/N video timing, framing, HBR2 pattern, VBID/MSA placement, stream-disable interrupt, DPHY training pattern/symbol/8b10b/PRBS/scrambler/CRC/fast-training state, secondary packet/audio timestamp controls, MST rate and slot allocation, and DP debug windows.
- `AUX_*` and `DP_AUX_DEBUG_*`: AUX transaction control, software and low-speed status/data, arbitration, interrupt enables, DPHY TX/RX timing/status, GTC sync control/status/data, phase override, and debug readback registers.
- `DVO_*`: digital video output enable, source select, output/clock/sync/color format, FIFO error calibration/status, CRC, and debug fields.
- `FBC_*`: frame buffer compression enable/source/coherency/clock gating, compression modes and LUTs, CSM region offsets, privileged/address-translation debug controls, decompression error handling, and status.
- `FMT_*`: clamp, dynamic expansion, pixel encoding/subsampling/source selection, truncation, spatial and temporal dithering, programmable dither matrices, CRC collection/masks/results, and debug fields.
- `LB_*` and `LBV_*`: primary and video line-buffer data format, memory sizing, desktop height, vline/vblank interrupt/status, sync reset, keyer colors, buffer level/urgency/empty/full status, and debug fields. `LBV_*` adds chroma counters and video-plane variants.
- `MVP_*`: multi-VPU/mixer controls, AFR flip, FIFO watermarks/status, slave timing counters, in-band control, CRC, flow/swap-lock debug, and async FIFO debug fields.
- `SCL_*` and `SCLV_*`: scaler coefficient RAM indexing/data, mode/tap/filter controls, horizontal/vertical ratios and init phases, update locking, sharpening, viewport/overscan, mode-change detection, host-conflict status, and video/chroma variants.
- `COL_MAN_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `GAMMA_CORR_*`, and `INPUT_GAMMA_*`: color-management update locks, input/output CSC matrices, prescale, denorm clamps, gamma/PWL region definitions, LUT access/autofill, FIFO error flags, and input gamma controls.
- `UNP_*`: underlay enable, tiling/depth/banking/format, surface addresses and in-use addresses, pitch, source rectangles, update locking, DVMM PTE controls/arbitration, flip interrupts, stereosync flips, CRC, rotation, outstanding request limits, and debug fields.
- `GEN*`, `SEQ*`, `CRT*`, `GRA*`, `ATTR*`, and `VGA_*`: legacy VGA miscellaneous, DAC, sequencer, CRTC, graphics controller, attribute controller, render/memory/cache/HDP/control/status/interrupt/test fields, and per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`.
- `BPHYC_*`, `PLL_*`, `VGA25_PPLL_*`, `VGA28_PPLL_*`, `VGA41_PPLL_*`, `DISPPLL_BG_CNTL`, `PPLL_*`: DAC analog controls, PLL dividers, spread-spectrum/delta-sigma settings, ID clock, reset/power/calibration/lock status, analog and regulator trims, update/debug state, and VGA-specific PLL triplets.
- `UNIPHY_TX_CONTROL1` through `UNIPHY_TX_CONTROL4` and the first `UNIPHY_POWER_CONTROL` fields: transmitter pre-emphasis, voltage swing, pull-down/drive trim, operating point, bandgap power-down, logic reset, and bias reference selection.

The companion register-address constants are in the matching generated DCE 11.0 register definition headers, typically `dce_11_0_d.h` and related generated AMD ASIC headers. Consumers pair those register offsets with these masks/shifts through AMDGPU register helpers.

## Control Flow

This header has no runtime control flow. Its operational flow is compile-time macro expansion:

1. A DCE 11.0 display, power, AUX, or diagnostic source file includes the generated register address and shift/mask headers.
2. The source chooses a register offset such as a DP, AUX, FMT, LB, UNP, VGA, PLL, or UNIPHY register.
3. It uses a `*_MASK` constant to isolate or clear the target field and the matching `*__SHIFT` constant to align a field value.
4. The resulting value is read from or written to hardware through AMDGPU MMIO helpers such as direct register access, indexed register access, or higher-level display helper macros.

Runtime sequencing is owned by callers. For example, a caller programming a mode would coordinate surface addresses, underlay update locks, line-buffer/scaler settings, formatter bit depth, DP stream enablement, and PLL/PHY state. This chunk only provides the bit encodings that make those sequences target the intended hardware fields.

Several field families imply hardware handshakes that callers must respect:

- `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, and `*_UPDATE_TAKEN` fields gate atomic or double-buffered updates in scaler, color-management, underlay, and PLL blocks.
- `*_ACK`, `*_CLEAR`, and `*_OCCURRED` fields implement interrupt/status clear protocols for DMCU/DPRX, DP stream disable, AUX/GTC sync, line-buffer, MVP, FMT/UNP CRC, FIFO errors, and VGA interrupts.
- PLL and link-training fields such as `PLL_LOCKED`, `PLL_CALIB_DONE`, DPHY fast-training status, and DP stream status are state machines that must be polled or observed by higher layers.

## State And Persistence Behavior

The chunk stores no software state, allocates no memory, and performs no MMIO by itself. It is a declarative mapping from hardware field names to masks and shifts.

When used by callers, the affected state is persistent device register state:

- Display mode state: DP stream enable, pixel format, M/N timing, MSA/VBID, MST slot allocation, formatter pixel encoding, dither/truncation mode, line-buffer memory, scaler ratio/taps/coefficients, viewport/overscan, and color-management matrices/LUTs.
- Surface and flip state: underlay tiling/depth/address/pitch/source rectangles, primary/secondary/bottom surface pending bits, update locks, page-flip interrupt masks/types, DVMM PTE buffering, and rotation.
- Error and diagnostic state: sticky interrupt/status bits, CRC enable/result fields, FIFO underflow/overflow status, FBC decompression errors, DPRX DPHY/AUX timeouts, and debug mux/index/data windows.
- Link and clock state: AUX channel arbitration/status/data, DPHY training and test patterns, PLL reset/power/divider/spread-spectrum/lock/update state, VGA PLL settings, and UNIPHY transmitter drive/power trims.
- Legacy compatibility state: VGA sequencer, CRTC, graphics, attribute, DAC, memory base, cache/HDP, render, and per-pipe mux controls.

Most register values persist until overwritten, reset by a block-level reset, power-gated, or lost during GPU reset/suspend. Status and interrupt bits may be write-one-to-clear or acknowledge-driven depending on the register; the paired `*_ACK`/`*_CLEAR` masks in this chunk are the only local clue, so caller-side protocol must match the hardware programming guide.

## Dependencies

This chunk depends on the surrounding generated AMD register ecosystem:

- The top-level include guard, license text, and prior/later DCE 11.0 definitions in `dce_11_0_sh_mask.h`.
- Matching DCE 11.0 register-address headers that define `mm*` or indexed register constants for these field names.
- AMDGPU display and power-management register-access helpers that understand mask/shift pairs and perform 32-bit MMIO read-modify-write operations.
- DCE 11.0 hardware semantics for display pipes, DIG/DP/AUX, DMCU, FBC, FMT, LB, SCL, color management, underlay, VGA, PLL, and UNIPHY blocks.
- Linux DRM/AMDGPU call paths that decide when to program mode state, hotplug/AUX transactions, page flips, gamma/CSC updates, power transitions, and display clock/PHY changes.

The chunk also has implicit dependency on ASIC register-generation correctness. A stale or mismatched mask can compile cleanly while causing silent hardware misprogramming.

## Integration Points

The main integration point is the AMDGPU DCE 11.0 display stack. These macros are consumed by code that sets modes, programs display planes, services vblank/vline/page-flip interrupts, performs AUX/I2C/DP link operations, controls power states, and handles diagnostics.

Specific integration surfaces include:

- DisplayPort encoder/link handling: `DP_*`, `AUX_*`, and `DMCU_DPRX_*` fields support link training, stream enable/disable, AUX transactions, MST slot allocation, audio/SDP packets, CRC/debug tests, and receiver-side event routing.
- Display pipe programming: `FMT_*`, `LB_*`, `LBV_*`, `SCL_*`, `SCLV_*`, and color-management fields support DRM mode-setting, plane format conversion, scaling, overscan, dithering, gamma/CSC, CRC capture, and vblank/vline timing behavior.
- Surface update and flip handling: `UNP_*` fields expose underlay/overlay-like surface addresses, tiling metadata, update locks, DVMM request behavior, flip interrupt control, stereosync flips, and in-use readback state.
- Power and clock management: `PLL_*`, `PPLL_*`, `DISPPLL_BG_CNTL`, `BPHYC_*`, and `UNIPHY_*` fields connect display mode programming to pixel-clock generation, analog calibration, PHY transmitter settings, and suspend/resume or BACO-style power sequences.
- Legacy boot/console compatibility: VGA register macros allow early display, VGA arbitration, console handoff, and compatibility paths to program or inspect legacy VGA state.
- Diagnostics and validation: CRC, debug index/data, status, error, and FIFO fields are integration points for bring-up, hardware validation, debugfs-like inspection, and automated display test flows.

The chunk starts in the middle of the larger DMCU perfmon/DPRX region and ends in the middle of `UNIPHY_POWER_CONTROL`. The per-file reconciliation lane must merge adjacent chunks for a complete register-family view.

## Risks And Edge Cases

- Mask/shift mistakes are high impact because many callers use read-modify-write operations. A wrong field definition can corrupt adjacent control bits while still compiling.
- Status and clear bits often share masks, as seen in the DPRX status/clear pattern. Callers must distinguish read status from write-clear semantics; treating clear bits like ordinary writable state can drop interrupts.
- Update-lock fields must be used coherently. Programming scaler, color-management, underlay, or PLL fields without honoring pending/taken/lock semantics can produce tearing, partial mode updates, or clock glitches.
- DP/AUX and DPHY fields are timing-sensitive. Wrong timeout, training, PRBS, scrambler, fast-training, or AUX arbitration settings can break link training, EDID/DPCD access, MST, or HDCP-related AUX traffic.
- FMT/FBC/LB/SCL/color-management fields are visually sensitive. Incorrect dither depth, truncation, clamp range, CSC/gamma region, viewport, tap coefficient, or line-buffer memory setting can cause banding, color shifts, underruns, blanking artifacts, or scaling defects.
- UNP surface and DVMM fields include address, tiling, privileged access, translation enable, PTE buffering, and outstanding request controls. Bad values can fetch from the wrong memory, fault display reads, or expose stale/wrong pixels.
- PLL/UNIPHY and analog fields are hardware-sensitive. Incorrect reset, power-down, divider, spread-spectrum, calibration, voltage swing, or pre-emphasis programming can cause no-display, unstable links, EMI problems, or suspend/resume regressions.
- Legacy VGA fields overlap compatibility behavior. Incorrect VGA memory base, sequencer reset, CRTC timing, cache/HDP, or per-pipe VGA mux values can break firmware console handoff or multi-display boot paths.
- Several repeated register families (`LB` versus `LBV`, `SCL` versus `SCLV`, VGA25/28/41 PPLLs, D1-D6 VGA controls) are copy-patterned. Generation drift or suffix confusion can map a valid-looking field to the wrong block variant.
- This chunk is part of a generated header. Manual edits risk divergence from the hardware register database and should be avoided unless regenerating or applying a verified ASIC-header update.

## Test Signals

Useful validation signals for this chunk are build-time, static, display-functional, and hardware-observable:

- Kernel/AMDGPU builds including DCE 11.0 register headers should compile without missing macro or duplicate-definition errors.
- Static generation checks should verify each `REGISTER__FIELD_MASK` has the matching `REGISTER__FIELD__SHIFT`, masks do not unintentionally overlap within a register, and repeated families preserve expected field positions.
- Register read-modify-write unit or simulator tests should confirm that helper macros using these constants change only intended bits for representative DP, AUX, FMT, LB, SCL, UNP, VGA, PLL, and UNIPHY fields.
- Display mode tests should cover multiple pixel formats, bit depths, RGB/YCbCr range/colorimetry, dithering/truncation modes, scaling ratios, viewport/overscan settings, gamma/CSC programming, and FBC enable/disable.
- DP tests should exercise AUX DPCD/EDID reads, hotplug/disconnect, link training at multiple rates/lane counts, HBR2 patterns, MST slot allocation, stream disable interrupts, audio/SDP packet programming, and CRC/debug paths.
- Flip and vblank tests should verify page-flip completion interrupts, vblank/vline status/ack behavior, underlay in-use surface readback, stereosync/stack-interlace flip modes, and update-lock sequencing.
- Error-path tests should induce or simulate AUX timeouts, DPHY errors, FIFO underrun/overflow, FBC decompression errors, line-buffer empty/full events, and scaler coefficient host conflicts, then confirm status/ack fields behave as expected.
- Clock/PHY tests should validate PLL lock/calibration/readback, spread-spectrum settings, PPLL update state, suspend/resume, power-gating/BACO paths, and UNIPHY voltage-swing/pre-emphasis programming across supported connector types.
- VGA compatibility tests should include firmware console handoff, fbcon/simpledrm to amdgpu transition, VGA disable/enable paths, and multi-pipe VGA source selection on DCE 11.0 ASICs.

### subset-b-001516: lines 11768-15235

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 11768-15235

## Purpose

This chunk is a generated AMD DCE 11.0 register shift/mask header section. It does not implement runtime logic; it publishes preprocessor constants that describe packed bit fields for display-engine MMIO and indirect registers. Driver code combines these `*_MASK` and `*__SHIFT` definitions with register addresses from the companion `dce_11_0_d.h` header and with AMDGPU/DC register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and audio endpoint accessors.

The covered range starts in the middle of `UNIPHY_POWER_CONTROL`, after the first power/reset fields that are in the prior chunk, and ends in the middle of `DISP_INTERRUPT_STATUS_CONTINUE3`, before the later CRTC3 vertical-interrupt and continuation fields. Within those boundaries it defines several major DCE 11.0 hardware areas:

- `UNIPHY_*` PHY, PLL, spread-spectrum, BIST, test-pattern, TMDS/DP analog, and debug fields.
- `DPG_*`, `DPGV0_*`, and `DPGV1_*` display-pipe memory arbitration, urgent watermark, stutter/self-refresh, DPM, and NB p-state-change fields.
- Large Azalia/HD-audio blocks, including root/function parameters, codec converter and pin widgets, HDMI/DP audio descriptors, stream descriptors, CORB/RIRB command rings, DMA position, CRC/debug/latency counters, clock gating, memory power control, and both F0 and F2 endpoint views.
- `BLND_*`, `WB_*`, and `CNV_*` blender, writeback, converter, CSC, update, underflow, debug, and test CRC fields.
- `DCFE_*` and `DCFEV_*` clock, reset, debug, memory power, DMIFV, and miscellaneous display frontend fields.
- `DC_HPD_*` hot-plug-detect status, control, fast-training, and debounce/toggle filter fields.
- `DCO_SCRATCH*`, `DCE_VCE_CONTROL`, and display interrupt status chain fields through part of `DISP_INTERRUPT_STATUS_CONTINUE3`.

The chunk is therefore a declarative hardware ABI surface for DCE 11 display, audio, power, and interrupt programming. Its correctness matters because users of these macros normally perform read-modify-write operations against hardware registers; a wrong bit position can change a different hardware control without any compiler warning.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this chunk. The exported interface is the generated macro namespace. The recurring pattern is:

- `REGISTER__FIELD_MASK`: a constant with the field's bit mask in the 32-bit register value.
- `REGISTER__FIELD__SHIFT`: a constant with the field's least-significant bit position.

The most important macro families in this range are:

- `UNIPHY_POWER_CONTROL`, `UNIPHY_PLL_FBDIV`, `UNIPHY_PLL_CONTROL1`, `UNIPHY_PLL_CONTROL2`, `UNIPHY_PLL_SS_STEP_SIZE`, and `UNIPHY_PLL_SS_CNTL`: PHY bandgap/bias selection, PLL feedback divider, enable/reset/clock controls, loop-filter/bandwidth controls, reference-clock selection, post-divider and reference-divider fields, VCO mode, and spread-spectrum modulation parameters.
- `UNIPHY_DATA_SYNCHRONIZATION`, `UNIPHY_REG_TEST_OUTPUT`, `UNIPHY_ANG_BIST_CNTL`, `UNIPHY_TMDP_REG0` through `UNIPHY_TMDP_REG6`, `UNIPHY_TPG_CONTROL`, `UNIPHY_TPG_SEED`, and `UNIPHY_DEBUG`: synchronization status, PLL lock/unlock test fields, BIST control/error reporting, TMDS/DP analog impedance calibration controls, TX/RX bias and calibration status, test-pattern generation, and debug selects.
- `DPG_PIPE_ARBITRATION_CONTROL*`, `DPG_WATERMARK_MASK_CONTROL`, `DPG_PIPE_URGENCY_CONTROL`, `DPG_PIPE_DPM_CONTROL`, `DPG_PIPE_STUTTER_CONTROL`, `DPG_PIPE_NB_PSTATE_CHANGE_CONTROL`, and `DPG_PIPE_STUTTER_CONTROL_NONLPTCH`: pipe memory timing, watermark masks, urgent thresholds, memory-clock-change policy, stutter/self-refresh behavior, and NB p-state transitions for the base DPG block.
- `DPGV0_*` and `DPGV1_*`: duplicated DPG field layouts for virtual/display-pipe instances 0 and 1, including arbitration, urgency, stutter, DPM, p-state change, repeater, debug, and check/preprocessor controls.
- `AZROOT_*`, `AZENDPOINT_*`, `AZALIA_*`, `AZALIA_F0_*`, and `AZALIA_F2_*`: HD-audio controller and codec register fields. These cover immediate command input/output interfaces, global capability/control/status, interrupt control/status, CORB/RIRB rings, DMA position and output stream descriptors, audio DTO/SCLK controls, memory power controls, CRC engines, latency counters, stream-indexed debug/data registers, and endpoint codec widgets.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` and `AZALIA_F0/F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR*`: HDMI/DP short audio descriptor fields such as maximum channel count, coding type, supported frequencies, sample sizes, max bit rate, and descriptor copy-to-verb controls.
- `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`, `AZALIA_F0/F2_CODEC_PIN_CONTROL_SINK_INFO*`, and related manufacturer/product/port/speaker/allocation fields: sink identity and audio-capability reporting fields exposed through the codec pin controls.
- `AZALIA_F0/F2_CODEC_*_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `*_PARAMETER_CAPABILITIES`, `*_CONTROL_CONVERTER_FORMAT`, `*_CONTROL_DIGITAL_CONVERTER`, `*_MULTICHANNEL*`, `*_HBR`, `*_LIPSYNC`, `*_UNSOLICITED_RESPONSE`, and `*_RESPONSE_CONFIGURATION_DEFAULT`: codec function, converter, pin, input converter, and input pin widget fields. These are used by display audio code to advertise audio capabilities, program channel layouts, set stream IDs, enable HBR, report pin sense, and handle hot-plug or format-change responses.
- `BLND_CONTROL`, `BLND_CONTROL2`, `BLND_UPDATE`, `BLND_UNDERFLOW_INTERRUPT`, `BLND_V_UPDATE_LOCK`, and `BLND_REG_UPDATE_STATUS`: blender enable/bypass/global alpha, update locking, pending update status, and data-underflow interrupt fields.
- `WB_ENABLE`, `WB_EC_CONFIG`, `WB_DEBUG_CTRL`, `WB_DBG_MODE`, `WB_HW_DEBUG`, and `WB_SOFT_RESET`: writeback block enable, error-concealment/configuration, debug, and reset fields.
- `CNV_MODE`, `CNV_WINDOW_START`, `CNV_WINDOW_SIZE`, `CNV_UPDATE`, `CNV_SOURCE_SIZE`, `CNV_CSC_*`, `CNV_TEST_*`, and `CNV_INPUT_SELECT`: converter mode, source/window geometry, update, color-space conversion coefficients/clamps/rounding, CRC test output, and input selection fields.
- `DCFE_CLOCK_CONTROL`, `DCFE_SOFT_RESET`, `DCFE_MEM_PWR_CTRL`, `DCFE_MEM_PWR_CTRL2`, `DCFE_MEM_PWR_STATUS`, `DCFEV_*`, and `DCFEV_DMIFV_*`: display frontend clock enable/selection, resets, memory power control/status for line buffers and related memories, vertical-pipe variant controls, and DMIFV clock/memory/debug fields.
- `DC_HPD_INT_STATUS`, `DC_HPD_INT_CONTROL`, `DC_HPD_CONTROL`, `DC_HPD_FAST_TRAIN_CNTL`, and `DC_HPD_TOGGLE_FILT_CNTL`: HPD sense, delayed sense, interrupt status/ack/enable/polarity, RX interrupt handling, connection timers, AUX/fast-training delay controls, and connect/disconnect debounce timers.
- `DCO_SCRATCH0` through `DCO_SCRATCH7`: full-width scratch register masks.
- `DCE_VCE_CONTROL`: video and audio pipe selection fields for VCE/display integration.
- `DISP_INTERRUPT_STATUS`, `DISP_INTERRUPT_STATUS_CONTINUE`, `DISP_INTERRUPT_STATUS_CONTINUE2`, and the beginning of `DISP_INTERRUPT_STATUS_CONTINUE3`: chained display interrupt summary bits for SCL mode changes, blender underflows, line-buffer vline/vblank events, CRTC snapshot/trigger/vsync/DRR events, DIG fast-training or stream-disable events, HPD/RX HPD, AUX completion, I2C completion, DMCU, ABM, writeback/scaler conflicts, external timing sync, and continuation bits.

The matching register address constants are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h`. Examples from that companion file include `mmUNIPHY_POWER_CONTROL`, `mmDPG_PIPE_STUTTER_CONTROL`, `mmDC_HPD_INT_STATUS`, and `mmDISP_INTERRUPT_STATUS_CONTINUE3`. Many Azalia endpoint registers use indirect/indexed register names such as `ixAZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`, which are accessed through audio endpoint helpers rather than plain MMIO offsets.

## Control Flow

This chunk has no executable control flow. Its operational behavior is compile-time macro substitution:

1. A DCE 11 display, audio, GPIO, AUX, clock, IRQ, or power-management translation unit includes `dce/dce_11_0_sh_mask.h`.
2. The source selects a register address from `dce_11_0_d.h` or an indexed Azalia register.
3. The source uses `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, usually indirectly through `REG_SET_FIELD` or `REG_GET_FIELD`, to insert or extract a field.
4. The resulting value is written to or read from hardware through AMDGPU/DC register access helpers.

Several control-flow-sensitive hardware concepts are encoded by these constants even though the header itself is declarative:

- Display audio setup code can sequence Azalia converter and pin programming by selecting endpoint registers, reading/writing stream IDs and converter formats, advertising ELD-derived audio descriptors, enabling audio on hot plug, and acknowledging unsolicited/format-change status.
- IRQ code can traverse the display interrupt chain by checking continuation bits: `DISP_INTERRUPT_STATUS` points at `DISP_INTERRUPT_STATUS_CONTINUE`, which points at `CONTINUE2`, which points at `CONTINUE3`. This range contains the chain through part of `CONTINUE3`.
- Power and clock-management paths can gate or ungate DPG, DCFE/DCFEV, Azalia, and memory sub-blocks by setting enable, force-on, shutdown, power status, and reset fields.
- HPD handling code can read `DC_HPD_INT_STATUS__DC_HPD_SENSE_MASK` and acknowledge or enable related interrupt bits in `DC_HPD_INT_CONTROL`.

The chunk boundaries matter: the first line is only the shift for `UNIPHY_POWER_CONTROL__UNIPHY_BIASREF_SEL`, with that field's mask immediately before this chunk; the last line is only the shift for `DISP_INTERRUPT_STATUS_CONTINUE3__CRTC3_EXT_TIMING_SYNC_INTERRUPT`, with more fields for the same register immediately after this chunk. The later merge lane must combine neighboring chunks for complete per-register descriptions.

## State And Persistence Behavior

The header stores no software state. It defines constants that describe hardware state locations. State becomes persistent only when another component writes registers using these definitions:

- `UNIPHY_*` fields persist in PHY/PLL hardware until the PHY block is reprogrammed or reset. Incorrect PLL divider, reference-clock, bandgap, impedance calibration, or spread-spectrum fields can prevent link lock, create unstable clocks, or break analog display output.
- `DPG*` watermark, stutter, DPM, and p-state fields persist as display memory-service policy. These values affect underrun risk, memory power saving, stutter/self-refresh entry and exit, and whether memory clock or NB p-state changes are allowed during scanout.
- `AZALIA_*` controller, codec, stream, and endpoint fields persist as the display-audio programming model. CORB/RIRB pointers, stream descriptor status, codec capabilities, endpoint descriptor content, hot-plug controls, and unsolicited-response fields are stateful at the audio controller or codec-emulation level.
- `BLND_*`, `WB_*`, and `CNV_*` fields persist in the display pipe. Update-lock and pending-update bits coordinate when new blender/converter/writeback state takes effect relative to scanout timing.
- `DCFE/DCFEV_*` fields persist as frontend clock/reset/memory-power state. These settings can power down local memories or gate clocks, so consumers must respect hardware sequencing and status bits.
- `DC_HPD_*` fields persist in HPD debounce, interrupt, and fast-training state. Ack bits are transient write-to-clear style controls in the consumer logic even though this header only provides masks.
- `DISP_INTERRUPT_STATUS*` fields represent latched or summary interrupt state. Some are read-only status and some are interpreted with separate control/ack registers outside this exact family.
- `DCO_SCRATCH*` fields are full 32-bit scratch values and may be used by firmware, BIOS, driver, or diagnostics depending on platform conventions.

Because this file is generated hardware metadata, the persistence risk is not memory lifetime inside C code; it is keeping bit layouts synchronized with the ASIC register database and with the register addresses in the companion header.

## Dependencies

This chunk depends on the surrounding AMDGPU/DC generated-register ecosystem:

- The file-level include guard `DCE_11_0_SH_MASK_H`, license block, and earlier macro definitions in `dce_11_0_sh_mask.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h` for corresponding MMIO and indexed register address definitions.
- AMDGPU/DC register helper macros that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- DCE 11 display code that includes this header, including DCE 11 IRQ service, GPIO factory/translation, AUX, audio, link encoder, timing generator, compressor, vertical display-pipe blocks, hardware sequencing, clock manager, and resource setup.
- Power-management code that includes this header for BACO or display/power interactions on DCE 11-era ASICs.
- Hardware contracts for Azalia/HD-audio, HDMI/DP audio descriptors, HPD/AUX behavior, display-pipe watermarks, DCFE memory power, and display interrupt routing.

Search results in this tree show direct consumers of related names in older DCE files as well, for example `dce_v10_0.c` and `dce_v6_0.c` use `DISP_INTERRUPT_STATUS_CONTINUE3__LB_D4_VBLANK_INTERRUPT_MASK`, `DC_HPD_INT_STATUS__DC_HPD_SENSE_MASK`, and Azalia pin-control fields. DCE 11-specific DC files include this header and follow the same generated macro convention.

## Integration Points

Primary integration points are low-level display hardware programming paths:

- Display IRQ routing: `DISP_INTERRUPT_STATUS*` masks map hardware summary bits to vblank, vline, HPD, AUX, DIG, DMCU, ABM, writeback/scaler, and external timing events. The `*_CONTINUE*` continuation bits let interrupt handling proceed to later summary registers.
- Hot-plug detection and link handling: `DC_HPD_INT_STATUS`, `DC_HPD_INT_CONTROL`, `DC_HPD_CONTROL`, `DC_HPD_FAST_TRAIN_CNTL`, and `DC_HPD_TOGGLE_FILT_CNTL` integrate with connector detection, HPD RX, AUX wakeups, and fast training for DisplayPort links.
- Display audio: Azalia root/function/converter/pin/control fields integrate with `dce_audio.c` and related endpoint helpers. They encode HDMI/DP audio capabilities, stream assignment, channel/speaker allocation, HBR capability, lip-sync, ELD/sink data, hot-plug audio enable, and unsolicited responses.
- Power management: DPG and DPGV watermarks/stutter/DPM/p-state fields integrate with display clock and memory clock policy. DCFE/DCFEV memory-power fields integrate with display block gating and power-state transitions.
- Display pipeline programming: BLND, CNV, and WB fields integrate with blender configuration, color-space conversion, writeback, update locking, underflow interrupts, and CRC/debug paths.
- Link encoder and PHY programming: UNIPHY fields integrate with PHY/PLL setup, TMDS/DP transmitter calibration, PLL lock tests, BIST, test pattern generation, and debug selection.
- Firmware/diagnostic scratch use: `DCO_SCRATCH*`, test debug, CRC, latency, and stream-debug fields provide register-level observability and platform coordination points.

The integration is entirely by name and bit layout. This header must stay in lockstep with DCE 11 address headers and with any generated offset tables used by DC code.

## Risks And Edge Cases

- The chunk has split-register coverage at both ends. The `UNIPHY_POWER_CONTROL__UNIPHY_BIASREF_SEL_MASK` definition is outside this range, while its shift is inside; the end of `DISP_INTERRUPT_STATUS_CONTINUE3` continues in the next chunk. A per-file report must reconcile adjacent chunks before claiming full register coverage.
- Wrong shifts or masks silently corrupt hardware programming. For example, bad `DC_HPD_INT_CONTROL` masks can acknowledge or enable the wrong HPD interrupt, and bad `DISP_INTERRUPT_STATUS_CONTINUE3` masks can route or classify the wrong display event.
- Many fields are duplicated across repeated instances (`DPGV0`/`DPGV1`, F0/F2 codecs, input/output pins, audio descriptors, sink-description bytes, and interrupt continuation registers). Generation drift can leave a copied field name or bit position that compiles cleanly but breaks one instance.
- Several fields use the high bits of a 32-bit register, including masks such as `0x80000000`. Callers must use unsigned 32-bit values and helper macros that avoid sign-extension or undefined shifts.
- Audio endpoint registers mix global HD-audio controller state with codec-emulation and endpoint-specific state. Writing the correct field to the wrong endpoint index can advertise incorrect capabilities, break HDMI/DP audio enumeration, or mis-handle format-change/hot-plug events.
- CORB/RIRB, DMA position, stream descriptor, and immediate command fields represent hardware queues and command paths. Bad masks can cause command ring stalls, wrong buffer pointers, or incorrect interrupt acknowledgment.
- DPG/DPGV and DCFE/DCFEV fields affect active scanout power behavior. Incorrect watermarks, stutter settings, or memory power controls can cause visible underflow, flicker, missed p-state transitions, or hangs around clock-gating transitions.
- HPD debounce and fast-training timing fields are timing-sensitive. Incorrect timer masks or shifts can produce noisy connector detection, missed disconnects, delayed hot-plug, or unreliable fast training.
- Interrupt status registers contain continuation bits. If a consumer misinterprets continuation masks, later interrupt status registers may not be inspected, causing lost events for pipes 2, 3, 4, or related AUX/HPD/DIG sources.
- Generated headers are broad include dependencies. A malformed macro or accidental edit here can break many display translation units even though the file contains no C statements.

## Test Signals

Useful validation is primarily compile-time, static, and hardware-integration oriented:

- Build AMDGPU/DC translation units that include `dce/dce_11_0_sh_mask.h`; failures will expose missing, duplicate, or malformed macro definitions.
- Run static consistency checks that pair every `REGISTER__FIELD_MASK` with a matching `REGISTER__FIELD__SHIFT` and confirm that every expected address exists in `dce_11_0_d.h`.
- Compare repeated layouts across instances: `DPG` versus `DPGV0/DPGV1`, F0 versus F2 codec families, audio descriptors 0-13, sink-description bytes, CRC channel arrays, and `DISP_INTERRUPT_STATUS_CONTINUE*` chains.
- Validate mask overlap within each register: fields should not overlap unless explicitly reserved or aliased, and high-bit fields should remain within 32-bit values.
- Exercise display IRQ handling on DCE 11 hardware or emulation by checking vblank/vline, HPD/HPD RX, AUX done, DIG fast-training/stream-disable, underflow, DMCU, ABM, and continuation-register paths.
- Exercise connector hot plug and unplug with debounce and fast-training enabled, verifying `DC_HPD_INT_STATUS` sense/status fields and `DC_HPD_INT_CONTROL` ack/enable behavior.
- Exercise HDMI/DP audio enumeration and playback, including ELD-derived descriptor programming, HBR-capable formats, channel allocation, pin sense, hot-plug audio enable, and unsolicited-response paths.
- Verify CORB/RIRB or immediate-command paths if display audio codec verbs are used, including read/write pointer behavior and response interrupt status.
- Exercise power-management transitions involving stutter/self-refresh, memory-clock changes, NB p-state changes, and DCFE/DCFEV memory power gating while monitoring for underflow, blanking, or clock-gating regressions.
- Use register readback tests around `REG_SET_FIELD` and `REG_GET_FIELD` for representative low, middle, and high-bit fields such as HPD ack bits, audio descriptor fields, watermark thresholds, and continuation interrupt bits.

### subset-b-001517: lines 15236-17567

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 15236-17567

## Purpose

This chunk is the tail of the generated AMD DCE 11.0 shift/mask header. It defines the bitfield masks and shifts used to compose and decode display-controller MMIO register values for the final DCE register groups in the file, then closes the `DCE_11_0_SH_MASK_H` include guard.

The covered range spans several hardware blocks:

- `DISP_INTERRUPT_STATUS_CONTINUE3` through `DISP_INTERRUPT_STATUS_CONTINUE10`, which extend the display interrupt-status chain for later CRTC/DIG/AUX/HPD/perfmon events.
- DCO memory-power, clock-gating, soft-reset, stereo-sync, debug, and power-management fields.
- DC I2C and Generic I2C/DDC control, status, transaction, speed, setup, interrupt, pin, and EDID-detection fields.
- `BLNDV_*` virtual blender controls and `CRTCV_*` virtual CRTC timing, status, trigger, stereo, CRC, test-pattern, update-lock, vertical-interrupt, and GSL synchronization fields.
- `XDMA_*` display cross-DMA master/slave, tiling, interrupt, power, debug, performance, cache, surface-address, urgent/stall, nack, and read-latency fields.

The file does not implement behavior directly. Its purpose is to keep register field layout in one generated source of truth so AMDGPU display code can avoid hard-coded bit constants at call sites.

## Important APIs, Types, And Functions

There are no C functions, structs, or runtime types in this chunk. The exported interface is preprocessor constants following the generated AMD register-header convention:

- `REGISTER__FIELD_MASK` gives the packed bit mask for a field in a 32-bit register value.
- `REGISTER__FIELD__SHIFT` gives the right-shift amount for that same field.

Important macro families include:

- `DISP_INTERRUPT_STATUS_CONTINUE*__*`: status bits for chained display interrupts, including mode-change, blender underflow, line-buffer vline/vblank, CRTC snapshot/trigger/vsync/vertical interrupts, DisplayPort fast-training and stream-disable events for DIGE/DIGF/DIGG/DIGLPA/DIGLPB, HPD/AUX events, GTC sync lock/error events, BUFMGR interrupts, DCCG/DCI/DCO/DCFE/WB perfmon counter interrupts, and continuation bits linking status registers 4 through 10.
- `DCO_MEM_PWR_STATUS*`, `DCO_MEM_PWR_CTRL*`, `DCO_CLK_CNTL*`, `DCO_SOFT_RESET`, `DIG_SOFT_RESET*`: DCO memory power-state and force/disable controls, clock gate-disable bits for display, AFMT, TMDS, DIG, and low-power DIG clocks, plus reset bits for DCO, DIG front/back ends, audio, formatter, MVP, ABM, DVO, and DP debug blocks.
- `DPDBG_*`, `DCO_POWER_MANAGEMENT_CNTL`, `DCO_TEST_DEBUG_*`: DisplayPort debug, DCO power-management, and indexed debug-data fields.
- `DC_I2C_*`: the main display I2C/DDC engine fields, including transaction start/stop/read-write/count descriptors, DDC1-DDC6 and DDCVGA status/setup/speed fields, software and hardware completion interrupts, EDID detection control, arbitration between software and DMCU/hardware users, indexed data FIFO access, and read-request interrupt acknowledgment/masking.
- `GENERIC_I2C_*`: a second generic I2C engine with go/reset/enable, completion and DDC read-request interrupts, status/error bits, speed/setup/transaction/data fields, and pin selection/debug controls.
- `BLNDV_*`: virtual blender gain, blend mode, stereo mode, alpha mode, feedthrough, update lock/status, underflow interrupt, debug, and test-debug fields.
- `CRTCV_*`: virtual CRTC timing registers for totals, blanking, syncs, VBI, vertical total min/max control, nominal-vsync and vertical-update interrupts, trigger A/B controls, force-count/force-vsync controls, stereo and AV sync, master enable, blank/interlace/field status, pixel readback, counters, snapshot, double buffering, test patterns, CRC windows/data, static-screen detection, GSL synchronization, color constants, vertical interrupt windows, and debug access.
- `XDMA_*`: XDMA MC/PCIe client config, local tiling, interrupts, clock/memory power, BIF/status/error, RBBMIF timeout, power-gating mailbox/status, always-on debug, master and slave enable/reset/status, surface addresses and dimensions, local/remote/cache base addresses, urgent/stall tuning, nack clearing, GSL checks, cache and pipe control, performance measurement, latency accounting, and slave channel/remote GPU address fields.
- `#endif /* DCE_11_0_SH_MASK_H */`: closes the header guard opened at the top of the file.

The matching register-address constants live in `dce_11_0_d.h` as `mmDCO_MEM_PWR_CTRL`, `mmDC_I2C_CONTROL`, the `mmCRTCV_*` sequence, and the corresponding `mmXDMA_*` entries. This chunk provides field layout; the companion `_d.h` header provides register offsets.

## Control Flow

This header has no executable control flow. Its operational flow is compile-time expansion:

1. A DCE 11.0 display implementation includes the generated register offset and shift/mask headers.
2. The implementation chooses an MMIO register offset from `dce_11_0_d.h`.
3. It clears, inserts, or extracts a field using the `*_MASK` and `*__SHIFT` constants from this header.
4. The composed value is passed to an AMDGPU register access helper, or a read value is decoded into driver state.

The chunk also describes implicit hardware control sequences. For I2C/DDC, callers typically program speed/setup and transaction fields, write data/index fields, assert `*_GO`, then poll or handle done/status/error bits. For CRTC and blender changes, callers can use update-lock and double-buffer fields so timing-sensitive changes land during a safe update point. For XDMA, callers configure memory clients, tiling, surface addresses, dimensions, cache/pipe state, urgent levels, and enable/reset bits before observing active/flush/flip/status fields.

## State And Persistence Behavior

The macros store no software state. Hardware state changes only when other driver code uses these definitions to read or write DCE registers.

Stateful hardware surfaces represented here include:

- Interrupt status, mask, type, clear, and acknowledge bits. Some fields are latched until an explicit clear or ACK bit is written.
- DCO and XDMA clock-gating, memory-power, power-gating, and reset controls. These persist in the display block until reprogrammed or reset.
- DC I2C and Generic I2C transaction state, including pending requests, done bits, abort/timeout/NACK status, hardware DDC request ownership, EDID-detection counters, and indexed data FIFO contents.
- CRTC timing registers, counters, trigger occurrence bits, stereo/3D state, CRC configuration/data, static-screen status, vertical interrupt positions, and update-lock/double-buffer state.
- XDMA master/slave state such as enable/reset, surface addresses, pitches, cache settings, active/flush/flip-pending flags, urgent/stall controls, nack tags, latency counters, and performance measurement counters.

Because this is a generated bit-layout header, persistence correctness depends on synchronization with the ASIC register database. A stale field definition compiles cleanly but can cause a caller to corrupt adjacent hardware fields.

## Dependencies

The chunk depends on the surrounding AMDGPU generated register ecosystem:

- The file-level license and `DCE_11_0_SH_MASK_H` include guard defined earlier in `dce_11_0_sh_mask.h`.
- Register-address definitions in `drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h`.
- AMDGPU display register helper conventions that pair `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` constants with read/modify/write helpers.
- DCE 11.0 hardware semantics for display interrupts, DCO power and clocks, I2C/DDC engines, virtual CRTC/blender pipelines, and XDMA.
- Higher-level display code responsible for choosing legal timing, I2C, power, reset, and DMA values before writing registers.

There are no direct Linux kernel library dependencies in this chunk beyond the C preprocessor.

## Integration Points

These definitions integrate with DCE 11.0 display bring-up, modeset, interrupt handling, hotplug/DDC, diagnostics, and low-level register programming.

Important integration paths are:

- Display interrupt dispatch can decode continuation status bits to route CRTC, HPD, AUX, DisplayPort, perfmon, GTC sync, BUFMGR, and XDMA events.
- DCO power-management code can gate or ungate clocks, force memory states, assert resets, and inspect power status when enabling or suspending display blocks.
- I2C/DDC code can program DDC bus timing, select DDC instances, issue multi-transaction transfers, read EDID-detection state, and handle read-request or done interrupts.
- CRTC programming code can set virtual timing, sync, blanking, total-min/max, trigger, stereo, CRC, test-pattern, color, and update-lock fields during modeset and validation.
- XDMA code can configure cross-GPU/display DMA surfaces, memory client attributes, local tiling, cache, master/slave channels, urgent watermarks, and performance diagnostics.
- The final `#endif` makes this chunk structurally important to every translation unit including `dce_11_0_sh_mask.h`; a truncation here breaks the generated header globally.

## Risks And Edge Cases

- Incorrect masks or shifts silently target the wrong hardware bits. This is especially risky for packed control registers such as `DCO_CLK_CNTL*`, `CRTCV_INTERRUPT_CONTROL`, `DC_I2C_READ_REQUEST_INTERRUPT`, and `XDMA_MSTR_PIPE_CNTL`.
- Several fields use high bits, including `0x80000000` masks. Callers must compose values using unsigned 32-bit operations to avoid sign-extension or overflow bugs.
- Fields with names ending in `_MASK_MASK` represent a hardware field whose name includes `MASK`, not a duplicate typo. Callers and scripts should not normalize these away.
- Interrupt fields often split occurrence/status, mask, type, ack, and clear bits. Writing a clear or ACK bit when trying to set a mask can lose events.
- DCO clock-gate and reset fields can disable clocks or reset active display sub-blocks. Ordering with modeset, audio, DisplayPort, and I2C activity matters.
- I2C/DDC fields include arbitration with DMCU/hardware users and status reset/abort controls. Misusing ownership or abort bits can hang EDID or AUX/DDC flows.
- CRTC timing fields commonly use 14-bit coordinate/count fields. Values must be range-checked by higher-level timing code before shifting into these masks.
- Update-lock and double-buffer fields can leave pending changes unapplied if locks are not released, or can tear timing changes if bypassed at the wrong time.
- XDMA surface address, pitch, tiling, VMID/privilege, urgent, nack-clear, and cache invalidation fields affect memory access. Bad values can produce display corruption, bus errors, or hard-to-debug cross-GPU transfer failures.
- This chunk starts in the middle of the `DISP_INTERRUPT_STATUS_CONTINUE3` register family and is the last chunk of the file. Per-file reconciliation should combine it with previous chunks for a complete interrupt-map view.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware integration checks:

- Kernel or driver builds including `dce_11_0_sh_mask.h` should pass without unterminated include-guard, duplicate macro, or missing macro errors.
- Generated-header validation should compare this chunk against the DCE 11.0 register database and the companion `dce_11_0_d.h` offsets.
- Static checks can verify each `REGISTER__FIELD_MASK` has a matching `REGISTER__FIELD__SHIFT`, that masks do not overlap unexpectedly within a register, and that continuation interrupt bits progress consistently.
- Register read/modify/write unit tests or bring-up diagnostics should confirm that setting one field changes only its masked bits.
- Display hotplug and EDID tests should exercise `DC_I2C_*`, `GENERIC_I2C_*`, DDC read-request interrupts, NACK/timeout handling, and EDID-detection status.
- Modeset and vblank/vertical-interrupt tests should exercise `CRTCV_*` timing, update-lock, vertical interrupt, snapshot, trigger, and vsync status paths.
- CRC and test-pattern validation should observe stable `CRTCV_CRC*` data and expected test output when corresponding fields are programmed.
- Power-management tests should suspend/resume display while checking DCO memory/clock/reset state and ensuring no lost HPD/AUX/CRTC interrupts.
- XDMA diagnostics should validate master/slave enable, address, pitch, tiling, cache invalidate, urgent interrupt, nack-clear, latency, and performance-measurement behavior on ASICs that use these registers.
