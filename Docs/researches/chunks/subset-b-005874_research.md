# sources/distributed-fs/ceph-client/include/linux/mfd/arizona/registers.h lines 4706-8160

## Scope

This chunk covers the final 3,455 lines of the Arizona MFD register-definition header. The range starts in the tail of the SLIMbus TX enable bitfield definitions and continues through the end of the file. It defines C preprocessor constants only: register field values, masks, shifts, and widths for Wolfson/Cirrus Arizona-family audio codec blocks. There are no C functions, structs, variables, allocations, locks, or executable branches in this chunk.

The covered register families are:

- SLIMbus RX/TX port status and the end of SLIMbus TX enable fields.
- IRQ polarity/output configuration, GPIO debounce, GP switch mode, and miscellaneous pad pull-up/pull-down controls.
- Primary interrupt status, interrupt mask, secondary IRQ status/mask, raw interrupt status, IRQ pin status, and ADSP IRQ handoff fields.
- Always-on-domain wake and jack-detect interrupt/status/debounce fields.
- Audio effects, equalizer, dynamic range control, low/high-pass filter, ASRC, ISRC, clock-control, ANC source, ADC reformatter, and DSP1 control/status fields.

## Purpose

This header is the hardware bitfield ABI consumed by the Arizona MFD, ASoC codec, IRQ, clocking, jack-detect, DSP, and audio-processing drivers. Each field is represented with a regular macro set:

- `ARIZONA_<FIELD>` for single-bit or field value masks when the field is named directly.
- `ARIZONA_<FIELD>_MASK` for isolating or updating the bitfield.
- `ARIZONA_<FIELD>_SHIFT` for the low bit position.
- `ARIZONA_<FIELD>_WIDTH` for field width.

Driver code pairs these macros with register addresses defined earlier in the same header and uses regmap-style read, write, and update operations to compose 16-bit register values. This chunk does not implement policy itself; it provides stable symbolic names for policy implemented in the Arizona MFD core and child drivers.

## Important Macro Families

### SLIMbus and Pad/IRQ Configuration

The chunk starts with `ARIZONA_SLIMTX[1-4]_ENA` definitions and then declares `ARIZONA_SLIMRX[1-8]_PORT_STS` and `ARIZONA_SLIMTX[1-8]_PORT_STS` fields for `SLIMbus RX Port Status` and `SLIMbus TX Port Status`. These are one-bit fields mapped to bits 0 through 7, exposing whether the individual SLIMbus audio ports are active or present.

Low-level interrupt and pad configuration includes:

- `ARIZONA_IRQ_POL` and `ARIZONA_IRQ_OP_CFG` in `IRQ CTRL 1`, controlling interrupt pin polarity/output behavior.
- `ARIZONA_GP_DBTIME_MASK` for a 4-bit GPIO debounce time field.
- `ARIZONA_SW1_MODE_MASK` for GP switch mode selection.
- Miscellaneous pad controls such as `LDO1ENA_PD`, `MCLK1_PD`, `MCLK2_PD`, `MICD_PD`, `ADDR_PD`, `RSTB_PU`, `DMICDAT[1-4]_PD`, and AIF1/AIF2/AIF3 BCLK, RXDAT, and RXLRCLK pull-up/pull-down fields.

These definitions are integration points for board-specific pin state, low-power pin biasing, clock pins, digital microphone pins, reset/address pins, and external interrupt wiring.

### Primary Interrupt Status and Masks

Registers `0xD00` through `0xD0D` define the first interrupt output domain. Status registers expose latched event bits with the `_EINT1` suffix; mask registers use the `IM_..._EINT1` prefix. The event families include:

- GPIO interrupts `GP1_EINT1` through `GP4_EINT1`.
- DSP RAM-ready and DSP IRQ events, including full DSP1-DSP4 RAM-ready fields in the first status layout.
- Speaker thermal, shutdown, and speaker/headphone short-circuit events.
- Headphone detect, microphone detect, write-sequencer done, DRC signal detect, ASRC lock, FLL lock, FLL clock OK, boot done, DCS done, and clock-generation fault events.
- Audio-interface, control-interface, mixer dropped-sample, ISRC/ASRC configuration, system-clock-low, and async-clock-low error events.

This chunk also captures alternate-layout definitions with the `ARIZONA_V2_` prefix for later devices. These alternate macros remap moved status or mask fields, especially AIF/control-interface/mixer/clock/ISRC/ASRC error bits in status 4 and status 5. Any driver selecting between normal and V2 layouts must use the correct macro family for the device revision, since the same logical event can live at a different bit position.

One visible source-quality signal is a likely comment typo: `ARIZONA_SPK_OVERHEAT_WARN_EINT1_MASK` uses the value for speaker overheat warning but its trailing comment says `SPK_OVERHEAD_WARN_EINT1`. The macro name, value, shift, and width are consistent with the surrounding field.

### Secondary IRQ Status and Masks

Registers `0xD10` through `0xD1F` mirror much of the interrupt topology for a second IRQ output domain with `_EINT2` and `IM_..._EINT2` fields. The secondary domain includes GPIO, selected DSP IRQ/RAM-ready fields, thermal and short-circuit events, clock and audio-processing fault events, DCS/FLL/boot events, alternate V2 layouts, and `ARIZONA_IM_IRQ2` in `IRQ2 Control`.

The `IRQ Pin Status` register provides `ARIZONA_IRQ1_STS` and `ARIZONA_IRQ2_STS`, letting software observe the physical interrupt line state rather than only latched per-source status. `ADSP2 IRQ0` exposes `ARIZONA_DSP_IRQ1` and `ARIZONA_DSP_IRQ2`, connecting DSP-originated interrupt lines into the same shared register map.

The primary and secondary IRQ domains are structurally similar but not byte-for-byte identical. Some EINT1 status blocks include DSP2-DSP4 RAM-ready and DSP IRQ3-DSP IRQ8 fields where corresponding secondary blocks in this range expose only DSP1 RAM-ready and DSP IRQ1/2. Consumers should not blindly generate one domain from the other without checking the defined fields.

### Raw Interrupt Status and Clock Fault Diagnostics

Registers `0xD20` through `0xD28` define raw status fields without the EINT1/EINT2 latching suffix. These include raw DSP, thermal, jack/mic detect, DRC, ASRC, FLL, clock-generation, AIF/control-interface, boot/DCS, and short-circuit statuses. They also expose detailed overclocked and underclocked source diagnostics:

- `PWM`, `FX_CORE`, `DAC_SYS`, `DAC_WARP`, `ADC`, `MIXER`, `AIF[1-3]_ASYNC`, `AIF[1-3]_SYNC`, and `PAD_CTRL` overclocked status.
- `SLIMBUS_SUBSYS`, `SLIMBUS_ASYNC`, `SLIMBUS_SYNC`, `ASRC_*`, `ADSP2_1`, and `ISRC[1-3]` overclocked status.
- `SPDIF`, `AIF[1-3]`, `ISRC[1-3]`, `FX`, `ASRC`, `DAC`, `ADC`, and `MIXER` underclocked status.

These raw fields are useful for diagnostic paths that need to distinguish a latched/masked interrupt from the instantaneous hardware condition. They are also sensitive integration points for clock-tree programming: wrong sysclk, FLL, ASRC, ISRC, or AIF settings can surface as the clock fault bits defined here.

### Always-On Domain and Jack Detect

The always-on-domain block at `0xD50` through `0xD56` defines wake and trigger fields for jack-detect and microphone-clamp activity:

- Trigger-status bits for MICD clamp fall/rise, GP5 fall/rise, JD1 fall/rise, and JD2 fall/rise.
- AOD IRQ1/IRQ2 event bits and matching IRQ mask fields.
- Raw AOD status bits for `MICD_CLAMP_STS`, `GP5_STS`, `JD2_STS`, and `JD1_STS`.
- Jack-detect debounce enable bits for MICD clamp, JD2, and JD1.

These fields bridge low-power wake detection and the audio accessory/jack-detection stack. The wake trigger bits are stateful hardware observations; the mask and debounce fields are persistent register settings until changed by driver power-management or accessory-detect code.

### Effects, EQ, DRC, and Filters

The audio-processing section defines control and coefficient fields:

- `FX_Ctrl1` and `FX_Ctrl2` provide `ARIZONA_FX_RATE_MASK` and `ARIZONA_FX_STS_MASK`.
- EQ1 through EQ4 each expose an enable bit, band gain fields for bands 1 through 5, a band-1 mode bit, and coefficient/program-gain registers for the filter sections. Most coefficient fields are full 16-bit masks named `EQn_Bm_A`, `EQn_Bm_B`, `EQn_Bm_C`, or `EQn_Bm_PG`.
- DRC1 and DRC2 provide signal detection thresholds, peak/RMS selection, noise-gate enable, signal-detect mode/status, knee controls, quick-release, anticlip, left/right enables, attack/decay, min/max gain, noise-gate expansion, compression ratios, and knee input/output settings.
- LHPF1 through LHPF4 expose mode and enable bits plus 16-bit coefficient fields.

These definitions are persistent audio DSP configuration state rather than transient events. ALSA controls, DAPM routes, firmware loaders, or tuning paths can update these fields to change audio processing behavior. Full-width coefficient masks are particularly sensitive to byte order, fixed-point format, and the surrounding regmap helper used to write 16-bit registers.

### ASRC, ISRC, Clock Control, ANC, and ADC Reformatters

The sample-rate conversion and clocking section includes:

- `ASRC_ENABLE` bits for ASRC1/ASRC2 left and right channels.
- `ASRC_RATE1` and `ASRC_RATE2` 4-bit rate fields.
- ISRC1, ISRC2, and ISRC3 control registers with high/low sample-rate fields, clock-source selection, interpolator enables `INT0` through `INT3`, decimator enables `DEC0` through `DEC3`, and notch enables.
- `Clock Control` set/clear bits for left/right/noise-gate clock enables and external noise-gate selection.
- `ANC SRC` receive source selectors for left and right ANC paths.
- `FCL/FCR ADC Reformatter Control` microphone mode select fields.

These macros are integration points between clock-framework code, audio interface setup, sample-rate conversion paths, active-noise-cancellation routing, and ADC data formatting. Many fields are multi-bit selectors with hardware-specific encodings not defined in this chunk; call sites must use the codec documentation or companion driver tables to map user-facing rates and routes onto these bit values.

### DSP1 Control and Status

The final register family covers DSP1:

- `DSP1 Control 1` defines `DSP1_RATE`, `DSP1_MEM_ENA`, `DSP1_SYS_ENA`, `DSP1_CORE_ENA`, and `DSP1_START`.
- `DSP1 Clocking 1` defines a 3-bit `DSP1_CLK_SEL`.
- `DSP1 Status 1` exposes `DSP1_RAM_RDY`.
- `DSP1 Status 2` exposes `DSP1_PING_FULL`, `DSP1_PONG_FULL`, and an 8-bit `DSP1_WDMA_ACTIVE_CHANNELS` field.

These fields are used by DSP firmware/control paths to sequence memory power, system/core enable, start, clock selection, RAM readiness, and DMA buffer activity. Incorrect ordering or unchecked status polling in consuming code could lead to failed firmware boot or stalled DSP data movement, though the sequencing logic itself is outside this header.

## Control Flow and State Behavior

This chunk has no executable control flow. The operational flow is encoded by the register model it describes:

1. Drivers configure persistent fields such as pad pulls, debounce, masks, audio-processing coefficients, DRC settings, ASRC/ISRC routing, clock enables, and DSP start/clock controls.
2. Hardware updates status fields such as SLIMbus port status, raw interrupt status, IRQ pin state, AOD trigger status, clock fault status, DSP RAM ready, and DSP DMA activity.
3. IRQ handlers read latched status bits, apply mask bits, dispatch child interrupt handlers, and may clear or acknowledge events using register semantics defined outside this chunk.
4. Power-management and runtime audio paths restore persistent configuration after suspend, reset, or regcache synchronization.

The macros themselves do not persist state, but they name hardware-backed persistent and volatile state. Persistent configuration includes masks, enables, coefficients, selectors, pulls, debounce settings, and clock/DSP controls. Volatile state includes raw/status/trigger/pin/DSP ready/full/active-channel bits.

## Dependencies and Integration Points

The immediate dependency is the rest of `include/linux/mfd/arizona/registers.h`, which supplies register address macros for the fields defined here and earlier field definitions for the same device family. Runtime dependencies are the Linux kernel drivers that include this header, typically through the Arizona MFD/regmap stack and ASoC codec components.

Important integration points include:

- Regmap update/read helpers that combine `_MASK` and `_SHIFT` values with 16-bit register accesses.
- IRQ-domain setup for the Arizona interrupt controller, including separate IRQ1/IRQ2 output masks and pin status.
- ASoC controls and DAPM/power-management code for EQ, DRC, filters, ASRC, ISRC, ANC, ADC reformatter, and clock-control fields.
- Jack-detect and low-power wake code using AOD status, trigger, mask, raw status, and debounce definitions.
- DSP firmware/control code using DSP1 enable/start/status and ADSP IRQ fields.
- Device-revision handling that selects normal versus `ARIZONA_V2_` alternate interrupt layouts.

## Risks and Edge Cases

- Revision-specific interrupt layouts are easy to misuse. Normal and `ARIZONA_V2_` macros can refer to the same logical event at different bit positions.
- Mask/status symmetry is mostly regular but not complete. Code generation or table construction should verify actual macro availability rather than assuming all EINT1 fields have identical EINT2/raw-status counterparts.
- Many fields are 16-bit full-width coefficient or status words. Call sites must preserve register width and endianness expectations.
- Set/clear-style clock-control bits (`*_SET` and `*_CLR`) should not be treated like ordinary read-modify-write state bits unless the hardware documentation confirms that behavior.
- Interrupt mask bits and raw/status bits have different semantics. Reading raw status for diagnostics is not equivalent to checking latched interrupt status after masking.
- The chunk starts mid-SLIMbus enable block; the preceding lines define SLIMTX5-SLIMTX8 enable fields and related context needed for a whole-file view.
- The file ends immediately after DSP1 status definitions. Other DSP instances or additional audio blocks may be defined earlier or in sibling headers, so a final per-file report should reconcile this chunk with the rest of the file.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Compile coverage from drivers that include `linux/mfd/arizona/registers.h`; undefined macro or duplicate-definition errors catch many table/refactor mistakes.
- Regmap trace or unit-level checks showing that IRQ mask updates write the expected bits for IRQ1, IRQ2, and AOD IRQ masks.
- Hardware or emulator interrupt tests for jack detect, mic detect, GP interrupts, clock faults, thermal/short-circuit paths, DSP IRQs, and boot/DCS/FLL completion events.
- Suspend/resume and runtime-PM tests verifying pad pulls, debounce settings, audio-processing coefficients, ASRC/ISRC enables, and DSP control state are restored correctly.
- Audio-path functional tests that exercise EQ1-EQ4, DRC1/DRC2, LHPF1-LHPF4, ASRC, ISRC, ANC source selection, and ADC reformatter modes.
- Revision-specific tests on later Arizona devices to confirm `ARIZONA_V2_` alternate interrupt layouts are selected where required.
