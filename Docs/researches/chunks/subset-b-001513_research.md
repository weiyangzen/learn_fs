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
