# sources/distributed-fs/ceph-client/include/linux/mfd/wm8994/registers.h lines 1-4378

## Purpose

This chunk is the public register-definition header for the Wolfson/Cirrus WM8994 family codec MFD. It contains preprocessor constants only: register addresses, register-count/cache bounds, and bitfield mask/shift/width definitions used by the WM8994 core, ASoC codec, interrupt, GPIO, regulator, jack-detect, clocking, DSP, and firmware-control code to address the hardware register map without magic numbers.

The covered range begins with the include guard and register-address map and continues through field definitions up to the first `WM8994_SPKMODE_PU` macro in `R1825 (0x721) - Pull Control (2)`. The requested slice stops at line 4378, so later field definitions for the rest of pull control, interrupts, GPIOs, DSP, and write-sequencer fields are outside this chunk even though their register addresses may already be listed in the address table.

## Important APIs, Types, And Constants

There are no C functions, structs, enums, or runtime APIs in this slice. Its API surface is macro names consumed by driver code.

Key address constants:

- Core analogue/power path: `WM8994_SOFTWARE_RESET`, `WM8994_POWER_MANAGEMENT_1` through `_6`, input/output mixer, volume, Class-D, charge-pump, Class-W, DC-servo, headphone, MICBIAS, and LDO registers.
- Chip/control and sequencing: `WM8994_CHIP_REVISION`, `WM8994_CONTROL_INTERFACE`, `WM8994_WRITE_SEQUENCER_CTRL_1`, `WM8994_WRITE_SEQUENCER_CTRL_2`, plus `WM8994_WRITE_SEQUENCER_0` through `_511`.
- Clocking and FLL: AIF1/AIF2 clocking, sample-rate, rate-status, FLL1/FLL2 control, and WM8958 EFS registers.
- Digital audio interfaces: AIF1/AIF2 control, master/slave, BCLK, LRCLK, data inversion, and WM8958 AIF3 registers.
- Digital audio processing: AIF volume/filter, noise gate, DRC, EQ coefficient windows, DAC/ADC mixer routing, DAC soft-mute, oversampling, and sidetone.
- GPIO/IRQ and pins: GPIO 1-11, WM1811 jack-detect alias at `0x705`, pull controls, interrupt status/mask/control, and debounce addresses.
- WM8958 DSP/firmware parameter windows: DSP2 program/config/status/config registers and firmware, MBC, crossover/filter, RMS limit, and write-sequencer memory ranges.

Important global limits:

- `WM8994_REGISTER_COUNT` is `736`, used by driver tables sized to the sparse register cache.
- `WM8994_MAX_REGISTER` is `0x31FF`, matching the final write-sequencer slot.
- `WM8994_MAX_CACHED_REGISTER` is `0x749`, excluding high DSP/firmware/write-sequencer windows from the normal cached range.

Field-definition pattern:

- Single-bit fields usually expose the bit value, `_MASK`, `_SHIFT`, and `_WIDTH`, for example `WM8994_BIAS_ENA`, `WM8994_CP_ENA`, `WM8994_AIF1_MSTR`, and `WM8994_DAC_OSR128`.
- Multi-bit fields expose `_MASK`, `_SHIFT`, and `_WIDTH`, for example `WM8994_VMID_SEL_MASK`, `WM8994_FLL1_N_MASK`, `WM8994_AIF1_WL_MASK`, and `WM8994_AIF2DRC_KNEE_IP_MASK`.
- Stereo-linked volume update bits are intentionally reused across left/right registers, such as `WM8994_AIF1DAC1_VU`, `WM8994_AIF2DAC_VU`, `WM8994_DAC1_VU`, and `WM8994_DAC2_VU`.
- Variant-specific fields use prefixes such as `WM8958_` and `WM1811_`, but they live in the same header because the related devices share a large register map.

## Control Flow

This header has no executable control flow. Runtime behavior is created by consumers that combine these constants with register-map helpers such as `regmap_update_bits()`, `regmap_write()`, IRQ status reads, ASoC DAPM routing, mixer control callbacks, and clock/FLL configuration routines.

The implied operational flows are hardware sequencing flows:

- Power-up and bias flows set `BIAS_ENA`, `VMID_SEL`, MICBIAS, input/output enable, charge-pump, anti-pop, and DC-servo fields in a defined order to avoid pops and unsafe analogue states.
- Audio routing flows enable mixer path bits such as `INx_TO_MIXINx`, `DACx_TO_MIXOUTx`, `MIXOUTx_TO_LINEOUTx`, `DACx_TO_SPKMIXx`, and AIF-to-DAC or ADC-to-AIF routing bits.
- Clock setup flows select AIF clock sources, BCLK/LRCLK dividers, FLL fractional/integer parameters, and sample-rate fields before enabling digital paths.
- DSP/EQ/DRC flows write coefficient and control registers using the address constants and set enable bits after coefficients are in place.
- Pin and accessory flows configure pull-up/pull-down bits, MICBIAS thresholds, WM8958 mic-detect status fields, and WM1811 jack-detect fields.

## State And Persistence Behavior

The state represented here lives in hardware registers and, for cached registers, in the Linux regmap/cache layer. The header itself stores no state.

The distinction between `WM8994_MAX_REGISTER` and `WM8994_MAX_CACHED_REGISTER` is important. The hardware address space extends to `0x31FF`, but the normal cached register range ends at `0x749`; high firmware/DSP and write-sequencer windows are likely volatile, sparse, or special-purpose and should not be blindly cached by generic register-cache code.

Many fields persist only while the codec is powered and may reset on software reset or hardware power loss. Fields like soft-mute, mixer routing, volume, FLL configuration, MICBIAS, pull-control, and DRC/EQ settings need reprogramming during probe, resume, or bias-level transitions according to the owning driver logic. Write-sequencer memory and DSP/firmware windows are especially sensitive because they can encode hardware-side state machines or firmware parameters.

## Dependencies And Integration Points

Primary integration points are Linux kernel driver layers, not this repository's distributed filesystem logic:

- MFD core code includes this header to identify and cache registers, expose child devices, and service IRQs.
- ASoC codec code uses the address and bitfield macros in DAPM widgets, DAI operations, kcontrols, clock/FLL code, EQ/DRC controls, and bias/power sequencing.
- Regulator code can use LDO and MICBIAS definitions for enable, discharge, and voltage-selection behavior.
- GPIO/irq/jack-detect code consumes GPIO, pull-control, interrupt, MICBIAS, mic-detect, and WM1811 jack-detect definitions.
- Firmware/DSP loaders consume WM8958 DSP2, firmware ID/version, MBC, filter, RMS, and write-sequencer address constants.

The header depends only on the C preprocessor and include guards. It intentionally avoids pulling other headers, so it is safe to include from multiple kernel subsystems.

## Risks And Edge Cases

- Macro values are hardware ABI. Any incorrect address, mask, shift, or width can silently program the wrong register bit and cause audio failure, unsafe analogue output, broken clocking, failed jack detection, or firmware/DSP corruption.
- Some macro names are duplicated intentionally for shared update bits or repeated field semantics across paired registers. Consumers must rely on register address plus field macro context, not just macro name uniqueness.
- Device-family prefixes matter. `WM8958_` and `WM1811_` definitions may not apply to base WM8994 silicon even when the address is shared or adjacent.
- Register aliases exist, notably `WM1811_JACKDET_CTRL` sharing address `0x705` with `WM8994_GPIO_6`. Variant-aware code must avoid treating that address as both a normal GPIO and a jack-detect control register at the same time.
- The sparse register map has large gaps and high windows. Iterating from zero to `WM8994_MAX_REGISTER` without valid-register checks can touch reserved or volatile areas.
- The chunk boundary is mid-register-definition at `R1825 (0x721) - Pull Control (2)`. A final merged report must combine the continuation before describing pull control, interrupt, GPIO, or later field definitions as complete.
- Generated-style macro headers are easy to regress through formatting or regeneration churn. Manual edits should be checked against the datasheet and existing driver tables.

## Test Signals

Useful validation signals for changes involving this header:

- Kernel build coverage for all WM8994-family drivers that include this header, with warnings treated seriously because macro renames or duplicate definitions can break consumers at compile time.
- Static checks that register defaults/cache tables reference addresses within `WM8994_MAX_CACHED_REGISTER` unless deliberately accessing volatile/high windows.
- Driver probe on WM8994, WM8958, and WM1811 hardware or emulation sufficient to verify regmap initialization, readable/writable/volatile callbacks, and child-device registration.
- ASoC runtime tests for playback/capture on AIF1 and AIF2, FLL lock and sample-rate changes, mixer routing, volume update bits, soft mute, EQ/DRC enable paths, and suspend/resume restore.
- Accessory tests for MICBIAS/mic-detect thresholds and WM1811 jack-detect behavior, especially at the shared `0x705` address.
- Regmap trace or debugfs inspection showing writes use the intended register addresses and masks when enabling power rails, clocks, audio paths, and pull controls.
