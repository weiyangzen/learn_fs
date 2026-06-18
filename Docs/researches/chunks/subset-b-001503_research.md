# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 1-4129

## Scope And Purpose

This chunk is the first portion of the generated DCE 10.0 register field header for AMD display hardware. It defines C preprocessor constants for bit masks and bit shifts used to access fields inside display-engine registers. The paired address header, `dce_10_0_d.h`, names the MMIO registers (`mmPIPE0_PG_CONFIG`, `mmCRTC_CONTROL`, `mmDCCG_GATE_DISABLE_CNTL`, and so on); this file names the fields inside those registers.

The chunk covers the header guard, copyright/license block, and 4,104 `#define`s across 589 register names. The definitions are almost entirely mask/shift pairs in the form:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

These constants are not executable code by themselves. They are the hardware contract consumed by the legacy `amdgpu` DCE paths, Display Core DCE 10.0 resource/hardware sequencing code, power-management code, and generic register helper macros that compose MMIO read-modify-write values.

The largest field groups in this chunk are CRTC timing/control, display GPIO/DDC/HPD/power-sequence pads, UNIPHY link/impedance controls, DCI/DMIF memory interface controls, DCCG clock controls, ABM/backlight controls, DCIO resets/debug, and per-pipe power-gating/status fields.

## Register Field API Surface

There are no functions, structs, enums, or storage declarations in this chunk. The API surface is the set of public macro constants included by C files that perform register access. Important groups include:

- `PIPE0_PG_*` through `PIPE5_PG_*`: per-display-pipe power gating force, enable, FSM readback, debug power status, requested/desired state, and power-status fields.
- `DC_IP_REQUEST_CNTL`, `DC_PGFSM_*`, `DC_PGCNTL_STATUS_REG`, and `DCPG_TEST_DEBUG_*`: display core power-gating request/FSM/debug fields.
- `BL1_PWM_*`, `DC_ABM1_*`, and `ABM_TEST_DEBUG_*`: backlight PWM, ambient backlight management, histogram/gain/luma statistics, ACE thresholds/slopes, double-buffer locks, missed-frame flags, and ABM debug indexing/data.
- `CRTC_*`: timing generator and scanout control, including DCFE clock gating, horizontal/vertical totals and blanks, sync A/B timing, triggers, flow control, stereo, master enable, blanking, interlace, counters, snapshots, start-line prefetch, interrupts, update locks, test patterns, overscan/blank/black colors, vertical interrupts, CRC windows/data, external timing sync, static-screen detection, 3D structure, and global-swap-lock fields.
- `MASTER_UPDATE_*`: master update lock and mode fields used to coordinate display-register updates.
- `DCCG_*`, `DISPCLK_*`, `SCLK_*`, `DPREFCLK_*`, `REFCLK_*`, `PIXCLK*_RESYNC_CNTL`, `CRTC[0-5]_PIXEL_RATE_CNTL`, and `DP_DTO[0-5]_*`: display clock generator, clock gating, clock turn-on/off delays, DTO phase/modulo, pixel-rate selection, add/drop pixel controls, FIFO error reporting, frequency-change ramping, and performance monitor fields.
- `SYMCLK[A-F]_CLOCK_ENABLE`, `DPDBG_CLK_FORCE_CONTROL`, `DVOACLK*`, and `DCCG_AUDIO_DTO*`: link symbol clock enables/force sources, debug clock forcing, DVO skew/clock selection, and audio DTO source/phase/module control.
- `CPLL_MACRO_CNTL_RESERVED*`, `PLL_MACRO_CNTL_RESERVED*`, `DAC_MACRO_CNTL_RESERVED*`, and `UNIPHY_MACRO_CNTL_RESERVED*`: full-register reserved macro-control fields retained for low-level programming sequences or compatibility with generated register tables.
- `DENTIST_DISPCLK_CNTL`: display clock and DP reference clock divider/change-toggle/done-toggle fields.
- `DCDEBUG_*`, `DBG_OUT_*`, `DCIO_DEBUG*`, `DCCG_TEST_DEBUG_*`, `DCI_TEST_DEBUG_*`, and `DCIO_TEST_DEBUG_*`: test muxes, debug bus selection, debug output pins, and index/data debug windows.
- `DMIF_*`, `DCI_*`, `PIPE[0-5]_DMIF_BUFFER_CONTROL`, `LOW_POWER_TILING_CONTROL`, and memory power status/control groups: display memory interface address layout, arbitration, chunk request accounting, underflow recovery, stutter/watermark status, buffer allocation, DCI clock gating, memory power forcing/disable/mode/status, and soft resets.
- `DC_GENERICA`, `DC_GENERICB`, `DC_PAD_EXTERN_SIG`, `DC_REF_CLK_CNTL`, and `DC_GPIO_DEBUG`: generic signal routing, clock/debug output selection, and DisplayPort receiver loopback/debug controls.
- `UNIPHYA` through `UNIPHYG` link/channel xbar controls and `UNIPHY_IMPCAL_LINK[A-G]`, `AUXP_IMPCAL`, `AUXN_IMPCAL`: physical-link pixel-valid reset, channel inversion, lane stagger, link enable masks, channel crossbar sources, impedance calibration enable/status/error/value/override controls, and AUX impedance calibration fields.
- `DC_GPU_TIMER_READ_CNTL`: display-domain start-position selection for GPU timer reads relative to display vblank events.
- `DCIO_*`: DCIO clock gating/ramp disable, external vsync muxing, soft resets for UNIPHY/DSYNC/DAC/DCRXPHY/DPHY blocks, DPHY lane selection, and DVO debug signals.
- `DC_GPIO_*`: generic GPIO, DVO data/control/clock, DDC1-DDC6, DDCVGA, sync, genlock/swaplock, HPD1-HPD6, panel power sequence, pad strength, AUX pad, I2C pad, DVO strength/vref/skew, and associated `MASK`, `A`, `EN`, and `Y` register fields.

## Control Flow And Usage Pattern

This header has no runtime control flow. Its values participate in control flow indirectly when driver code reads, modifies, or polls hardware registers.

The typical usage pattern is:

1. Include `dce_10_0_d.h` for register addresses and `dce_10_0_sh_mask.h` for field masks/shifts.
2. Use raw accessors such as `RREG32`/`WREG32`, or higher-level helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, and `REG_SET`, to compose values.
3. Apply a field mask to preserve unrelated register bits and use the shift constant to position the requested field value.
4. Poll status fields or write clear bits for interrupts, power-state transitions, update locks, missed-frame flags, CRC status, HPD/DDC/AUX pad state, and underflow/debug conditions.

Representative consumers include `amdgpu/dce_v10_0.c`, which includes this header next to `dce_10_0_d.h` and `dce_10_0_enum.h`, and Display Core DCE 10.0 files such as `display/dc/resource/dce100/dce100_resource.c` and `display/dc/hwss/dce100/dce100_hwseq.c`. Related VI-era paths in `gfx_v8_0.c`, `gmc_v8_0.c`, `vi.c`, BACO handlers, and SMU managers also include the same generated field header when they need shared display/DC bit definitions.

## State And Persistence Behavior

The file itself is stateless and produces no persistent data. The persistent state affected by these constants lives in hardware registers and hardware-managed latches:

- Power-gating fields can force, request, enable, or report display-pipe and memory power states.
- CRTC fields hold active timing, blanking, sync, stereo, trigger, CRC, snapshot, interrupt, static-screen, and update-lock state until driver code or hardware events change them.
- ABM/backlight fields hold PWM duty-cycle inputs/outputs, ambient/backlight source selection, histogram/luma readbacks, ACE thresholds/slopes, and double-buffer lock/update-pending state.
- DCCG/DCI/DCIO fields control clock gating, clock dividers, soft resets, debug routing, DTO accumulators, and memory power state.
- GPIO/DDC/AUX/HPD fields expose pad masks, enables, observed input values, pull/power behavior, AUX mode/polarity, and panel power-sequence outputs.

Several fields are edge- or event-oriented rather than simple configuration bits. Examples include `*_CLEAR`, `*_OCCURRED`, `*_UPDATE_PENDING`, `*_MISSED_FRAME`, `*_READ_IN_PROGRESS`, `*_CHGTOG`, `*_DONETOG`, and interrupt status/type/mask fields. Incorrect mask or shift values can leave state uncleared, clear the wrong event, or make polling loops wait forever.

## Dependencies And Integration Points

The primary dependency is the matching generated register-address file, `dce_10_0_d.h`. Register address macros and field mask/shift macros must stay synchronized: a correct field applied to the wrong `mm*` address is just as dangerous as a wrong mask.

The field naming convention is also a dependency. AMD register helper macros derive names by token pasting. A call that names register `CRTC_CONTROL` and field `CRTC_MASTER_EN` expects `CRTC_CONTROL__CRTC_MASTER_EN_MASK` and `CRTC_CONTROL__CRTC_MASTER_EN__SHIFT` to exist with exactly those spellings. Generated names with repeated words such as `*_MASK_MASK` are intentional where the hardware field name itself ends in `MASK`.

Integration points include:

- Legacy `amdgpu` DCE code for mode setting, vblank/vline/HPD interrupt handling, display enable/disable, CRTC master enable, scanout state, and atomic-style register programming.
- Display Core DCE 10.0 resource construction and hardware sequencing, which pass register lists, shifts, and masks into reusable DCE blocks such as timing generators, link encoders, stream encoders, memory input, transforms, output pixel processors, panel control, AUX, I2C, DMCU, and ABM.
- VI-era power management and BACO/SMU paths that need DCE field definitions while entering low-power states, managing display clocks, or coordinating static-screen/display events with the SMU.
- Adjacent generated headers for DCE 8.0, DCE 11.x, DCE 12.0, DCN, and DPCS blocks. Many field names are shared across hardware generations, so mismatches can produce compile-time errors in shared code or subtle behavior changes when a generation-specific include is selected.

## Risks And Edge Cases

The highest risk is silent hardware misprogramming. These macros are constants, so most errors compile cleanly while causing display failures at runtime.

Specific risks include:

- Mask/shift mismatch: a stale shift paired with a new mask can write neighboring fields in the same register.
- Width errors: fields such as CRTC counters, CRC window coordinates, DMIF request limits, GPIO drive strength, and ABM histogram/luma data have nonuniform widths; truncation or over-wide masks can corrupt adjacent configuration.
- Register-generation drift: DCE 10.0 shares many names with DCE 8.0, DCE 11.x, DCE 12.0, and DCN headers, but offsets and available fields vary. Copying a field across generations without validating the generated table can break only one ASIC family.
- Event clear/status confusion: interrupt, snapshot, force-vsync, trigger, static-screen, sync-loss, and missed-frame fields frequently pair status and clear bits in the same register. A bad definition can leave interrupts stuck or accidentally acknowledge events.
- Power/reset sequencing hazards: `PIPE*_PG_*`, `DCI_MEM_PWR_*`, `DCCG_*_GATE_DISABLE`, `DCIO_SOFT_RESET`, `DCCG_SOFT_RESET`, and `DCI_SOFT_RESET` fields affect clocked hardware domains. Wrong values can make subsequent register access unreliable.
- GPIO/DDC/AUX/HPD pad control hazards: duplicated `MASK`, `A`, `EN`, and `Y` layouts are easy to mix up. Incorrect masks can break monitor detection, AUX transactions, panel power sequencing, genlock/swaplock, or DVO output.
- Generated-name pitfalls: fields whose names end in `MASK` generate macros like `DC_GPIO_DDC1_MASK__DC_GPIO_DDC1CLK_MASK_MASK`; consumers must use the exact generated name rather than simplifying it.

## Test Signals

There are no unit tests for this header alone. Useful signals are build-time and hardware/driver behavior:

- Compile coverage of `amdgpu`, `amd/display`, and `pm/powerplay` users catches missing or misspelled generated macros, especially token-pasted `REG_*` field references.
- Display bring-up on DCE 10.0/VI hardware catches gross CRTC, DCCG, DCIO, UNIPHY, GPIO, and power-gating field errors through black screens, failed modesets, clock failures, or hung polling loops.
- DRM/KMS tests that exercise modeset, vblank, CRC capture, DPMS, hotplug, DDC/EDID reads, DisplayPort AUX, backlight/ABM, suspend/resume, and multi-display synchronization are the strongest behavioral checks.
- Power-management tests for BACO, clock gating, display idle/static-screen, and suspend/resume can reveal bad DCI/DCCG/DCIO memory-power and soft-reset fields.
- Register readback/debug tools are useful for comparing expected field placement against hardware documentation: read a register, apply the generated mask/shift, and confirm the decoded field changes only when the intended hardware setting changes.

Because the file is generated register metadata, review should focus on whether this header matches the authoritative DCE 10.0 register specification and remains paired with the correct `dce_10_0_d.h` address table. Normal code-level tests cannot prove every bit position without hardware or generated-table validation.
