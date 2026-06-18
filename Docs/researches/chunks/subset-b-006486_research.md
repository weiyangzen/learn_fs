# sources/distributed-fs/ceph-client/sound/soc/codecs/wm5100.h lines 1-4680

## Scope

This chunk covers the first 4,680 lines of `sources/distributed-fs/ceph-client/sound/soc/codecs/wm5100.h`, the public/private register definition header for the Wolfson WM5100 ALSA SoC codec driver. The full file continues past this chunk with additional DSP memory field definitions and the `wm5100_reg_defaults` declaration, so this document is intentionally a chunk-level report rather than the final per-file synthesis.

## Purpose

The chunk is a generated-style register contract for `wm5100.c`. It gives the C driver stable symbolic names for:

- public driver clock identifiers and clock/FLL source selectors;
- every visible codec register address in the covered range, from software reset and clocking registers through analog input/output, AIF, mixer, GPIO, interrupt, EQ/DRC/filter, and DSP control blocks;
- bit masks, shifts, and widths for register fields used by ALSA controls, DAPM widgets, DAI clocking, jack detection, interrupt handling, and regmap access.

There is almost no executable logic in this chunk. Its main value is correctness of numeric constants: consumers combine these macros with `snd_soc_component_update_bits()`, `snd_soc_component_read()`, ALSA control macros, DAPM definitions, and regmap defaults.

## Important APIs, Types, and Defines

The only function prototype in this range is:

- `int wm5100_detect(struct snd_soc_component *component, struct snd_soc_jack *jack);` - jack/accessory detection entry point implemented in the codec driver and exposed via this header.

The chunk depends on ALSA SoC and regmap types through:

- `#include <sound/soc.h>` for `struct snd_soc_component`, `struct snd_soc_jack`, DAI/control/DAPM consumers, and component register helpers.
- `#include <linux/regmap.h>` for the register-default data declared later in the header and used by the codec regmap setup.

Key exported macro groups:

- Clock API selectors: `WM5100_CLK_AIF1`, `WM5100_CLK_AIF2`, `WM5100_CLK_AIF3`, `WM5100_CLK_SYSCLK`, `WM5100_CLK_ASYNCCLK`, `WM5100_CLK_32KHZ`, `WM5100_CLK_OPCLK`.
- Clock source IDs: `WM5100_CLKSRC_MCLK1`, `MCLK2`, `SYSCLK`, `FLL1`, `FLL2`, AIF BCLKs, and `WM5100_CLKSRC_ASYNCCLK`.
- FLL selectors and sources: `WM5100_FLL1`, `WM5100_FLL2`, plus `WM5100_FLL_SRC_*`.
- Register address map: `WM5100_SOFTWARE_RESET`, `DEVICE_REVISION`, `CLOCKING_*`, `ASRC_*`, `ISRC_*`, `FLL*_CONTROL_*`, supply/accessory-detect/input/output/AIF/mixer/GPIO/interrupt/FX/EQ/DRC/HPLPF/DSP register symbols.
- Register-space bounds: `WM5100_REGISTER_COUNT` is `1435`; `WM5100_MAX_REGISTER` is `0x97FF`.
- Bitfield triplets: most fields are expressed as `_MASK`, `_SHIFT`, and `_WIDTH`, with single-bit fields also commonly exposing the raw bit value, e.g. `WM5100_SYSCLK_ENA`, `WM5100_AIF1_BCLK_MSTR`, `WM5100_DRC_SIG_DET`, `WM5100_LHPF1_ENA`.

## Register and Field Coverage

The address section maps the codec register file by hardware block:

- Reset/control/test signal basics: software reset, device revision, control-interface auto-increment, tone generator, and PWM drive registers.
- Clocking and sample-rate selection: `CLOCKING_1`, `CLOCKING_3` through `CLOCKING_8`; fields include 32 kHz source, SYSCLK/ASYNCCLK source and enable bits, and normal/async sample-rate codes.
- ASRC/ISRC/FLL blocks: ASRC enables/status/rate selection, two ISRC control blocks with interpolation/decimation enables, and FLL1/FLL2 enable, divider, ratio, theta, N, refclk, and lambda fields.
- Power/bias and accessory detection: mic/headphone charge pumps, LDO1/LDO2, three mic-bias controls, accessory/headphone/mic detect mode/status/level fields, and `HPCOM_SRC`.
- Analog and digital I/O: input enables/status, input mode/OSR/DMIC supply/PGA volume, ADC digital mute/volume/update fields, output enables/status, channel enables, output OSR/mono/ANC/PGA/limit fields, DAC digital mute/volume/update fields, AEC loopback, volume ramps, and PDM speaker mute/format controls.
- Three AIF blocks: AIF1 exposes eight TX/RX channels while AIF2/AIF3 expose two TX/RX channels. Each block has BCLK polarity/master/frequency, LRCLK polarity/master/force/source, data format, BCLK cycles per frame, word length, slot length, per-channel slot selectors, and channel-enable fields.
- Mixer source/volume address families: PWM, output, AIF TX, EQ, DRC, HPLP, DSP, ASRC, and ISRC mixer input source/volume registers are enumerated so the driver can construct many controls from a base register.
- GPIO/pad/interrupt blocks: six GPIO controls with direction, pull, polarity, output config, debounce, level, and function fields; pad pulls for MCLK/reset/address/DMIC/AIF pins; OPCLK selection; interrupt status/raw/mask registers; global interrupt mask; debounce controls.
- Audio processing: FX status/rate, four 20-register EQ coefficient/control banks, DRC controls, four high-pass/low-pass filter controls and coefficients.
- DSP control: address map entries for DSP1-DSP3 controls and memory windows appear near the top; this chunk reaches DSP2 Control 30 and starts DSP1 Control 30 bit definitions near the line boundary. Remaining DSP memory field macros are outside this chunk.

## Control Flow and Runtime Use

This header does not implement control flow. Runtime behavior is in `wm5100.c`, which includes this header and uses these constants as the hardware binding layer.

Observed integration patterns in `wm5100.c` include:

- ALSA mixer controls use address and shift macros for user-visible controls such as input/output volume, ADC/DAC mute, EQ band volumes, DRC coefficients, and filter coefficients.
- DAPM widgets use enable-bit shifts from this header for input PGAs, output paths, EQ/DRC/LHPF blocks, and AIF routes.
- `wm5100_set_fmt()` builds BCLK/LRCLK/data-format values from ALSA DAI format flags and writes `WM5100_AIF1_BCLK_MSTR`, `WM5100_AIF1_BCLK_INV`, `WM5100_AIF1TX_LRCLK_MSTR`, `WM5100_AIF1TX_LRCLK_INV`, and `WM5100_AIF1_FMT_MASK` against a DAI base register. The AIF1 macro names are reused with base offsets for AIF2/AIF3 because the register layout is parallel.
- `wm5100_hw_params()` uses AIF BCLK, frame length, word length, slot length, and sample-rate field macros to program the selected DAI after deriving BCLK/LRCLK from PCM params and SYSCLK/ASYNCCLK state.
- `wm5100_set_sysclk()` uses `WM5100_CLK_*`, `WM5100_CLKSRC_*`, clocking register addresses, and clock source masks to configure or record SYSCLK/ASYNCCLK/32 kHz/AIF-domain relationships.
- Interrupt handling reads raw interrupt status registers and tests error/lock/underrun bits defined here.

## State and Persistence Behavior

The header itself stores no runtime state. It defines the persistent hardware state layout that `regmap` and ALSA manipulate:

- Register fields correspond to state latched in the WM5100 hardware or in the regmap cache.
- Volume, mute, mixer-route, EQ, DRC, and filter coefficient macros are used by ALSA controls, so user-space mixer state eventually becomes writes to these addresses/fields.
- Clocking/FLL/AIF fields define timing state that must remain consistent with PCM stream setup and machine-driver clock configuration.
- Interrupt mask/status and GPIO/pad fields define event and pin behavior that persists until changed or reset.
- Repeated generic field names such as `WM5100_IN_VU` and `WM5100_OUT_VU` are intentionally shared across channel registers; consumers rely on identical bit positions across the channel banks.

## Dependencies and Integration Points

Primary dependencies:

- ALSA SoC core (`sound/soc.h`): component register I/O, DAI ops, DAPM widgets, controls, jack reporting.
- Linux regmap (`linux/regmap.h`): register default table and cache/register access constraints in the rest of the driver.
- WM5100 hardware register ABI: all numeric values in this header must match the silicon datasheet.

Important integration points:

- `sources/distributed-fs/ceph-client/sound/soc/codecs/wm5100.c` is the main consumer and implementation partner.
- Machine drivers call component/DAI operations using `WM5100_CLK_*`, `WM5100_CLKSRC_*`, and `WM5100_FLL*` selectors rather than raw register values.
- User-space ALSA controls depend on the correctness of `_SHIFT`, `_MASK`, and byte/coefficient ranges.
- DAPM route construction depends on the enumerated mixer source register layout and on enable-bit polarity.

## Risks and Edge Cases

- Numeric drift risk is high: a one-bit error in a mask, shift, or address can silently program the wrong hardware field. This is especially risky for clock/FLL/AIF timing, interrupt masks, supply controls, and DSP memory windows.
- The chunk uses repeated macro names for fields shared across multiple channel registers (`WM5100_IN_VU`, `WM5100_OUT_VU`). These are identical redefinitions in this snapshot, but any non-identical duplicate would create preprocessor warnings or wrong control behavior.
- AIF2/AIF3 runtime code appears to rely on AIF1 field masks plus DAI base offsets for common layouts. That works only while the bit layout is truly identical across AIF blocks.
- Several long register families are patterned but sparse. Missing or incorrectly ordered mixer/AIF slot/EQ coefficient macros would break table-driven control generation in `wm5100.c`.
- This chunk ends mid-DSP-control area; downstream research must reconcile the remaining DSP1/DSP3 memory field definitions and the `wm5100_reg_defaults` declaration before producing a full-file conclusion.
- Interrupt fields cover raw, status, mask, and debounce registers. Tests should distinguish sticky status bits from mask bits and avoid treating `_EINT` and `IM_*_EINT` macros interchangeably.

## Test Signals

Useful validation signals for this chunk:

- Build the codec driver with `W=1` or equivalent warning settings to catch duplicate macro mismatches, missing declarations, and invalid consumers after macro edits.
- Boot/probe test should confirm regmap initialization accepts `WM5100_MAX_REGISTER` and the default table count from the full header.
- ALSA control enumeration should expose expected controls for inputs, outputs, EQ, DRC, LHPF, mixers, and AIF paths without read/write failures.
- PCM playback/capture on AIF1, AIF2, and AIF3 should validate BCLK/LRCLK/word-length programming paths that rely on the AIF masks in this chunk.
- Clock tests should cover SYSCLK, ASYNCCLK, 32 kHz source selection, FLL1/FLL2 source/divider programming, and invalid-source rejection.
- Jack/accessory tests should exercise headphone and mic-detect status/interrupt fields.
- IRQ tests should trigger and mask GPIO, FLL lock, AIF error, underclock, accessory/headphone, and speaker shutdown events.
- Audio processing tests should write/read EQ, DRC, and LHPF coefficient controls and verify enable bits do not corrupt coefficient payloads.

## Open Cross-Chunk References

- Lines after 4,680 continue DSP field definitions and eventually declare `wm5100_reg_defaults[WM5100_REGISTER_COUNT]`.
- The final per-file report should merge this register/API overview with the remaining DSP memory/register-default section to describe the complete header contract.
