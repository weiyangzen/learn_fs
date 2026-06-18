# sources/distributed-fs/ceph-client/sound/soc/codecs/da732x_reg.h

## Purpose

`da732x_reg.h` is the raw DA732x register-map header. It names codec register addresses, maximum register bounds, and bit masks for status, bias, mic/AUX inputs, headphone and line outputs, charge pump, PLL, clocks, AIF interfaces, routing, DSP/DMA, ADCs, DACs, HPF, EQ, and softmute controls.

## Important APIs, Types, and Constants

- Register address definitions span `0x00` through `DA732X_REG_UNLOCK` at `0xE0`, with `DA732X_MAX_REG` used by regmap configuration.
- Status and bias bits define PLL lock/MCLK detect, headphone detect, brownout, VMID/reference control, and bias boost/enable.
- Input bits cover mic-bias voltage/enable, mic detect, mic boost/gain/mute/enable, AUX gain/mute/enable, input pin bias, zero crossing, and ADC input mux selection.
- Output bits cover HP detect, HP DAC/output offset trim and comparator controls, HP output DAC/high-Z/mute/enable, lineout volume/DAC/high-Z/mute/enable, output zero crossing, and HP ground selection.
- Charge-pump and PLL/clock bits define CP operating modes, CP clocks, PLL input/SRM/enable, sample-rate nibbles, DSP frequency, and clock gates.
- AIF bits define frame width, source selection, master/slave clocking, word length, protocol mode, inversion, and enable bits for AIFA/AIFB.
- Routing and DSP bits define direct DSP bypass/all-to-DSP routes, digital/DSP core enable, mailbox/DMA selection, and DMA status.
- ADC/DAC bits define reset/power-down/enable/mute/volume, softmute, HPF, and 5-band EQ controls.

## Control Flow

This header has no control flow, but `da732x.c` uses it throughout probe, DAPM, controls, PLL, and calibration. The regmap maximum and volatile register callbacks depend on register definitions here. DAPM event handlers use ADC reset/power bits and output high-Z/enable bits. PLL and DAI ops use PLL divider, AIF, clock, and sample-rate fields. Bias startup and HP calibration use reference, charge pump, HP trim, DSP routing, and zero-crossing definitions.

## State and Persistence

All persistent hardware state encoded by DA732x regmap defaults and runtime writes is defined by this header. The most stateful areas are bias/reference power, clock gates, PLL enable/dividers, AIF format, DAPM endpoint enable/mute/high-Z state, ADC/DAC reset and power state, and HP calibration trim registers. Only `HPL_DAC_OFF_CNTL` and `HPR_DAC_OFF_CNTL` are marked volatile by the driver, even though other status registers also describe live hardware state.

## Dependencies and Integration Points

The header is consumed by `da732x.c` and indirectly by any future DA732x helper code. It has no includes, so it relies on plain integer macros. Its constants must align with the regmap default table, DAPM widget/register declarations, mixer control ranges in `da732x.h`, and the DA732x datasheet.

## Risks and Edge Cases

- Typos in macro names or comments can propagate into controls; for example the driver already has typo-prone ADC2 EQ control labels.
- `DA723X_CP_DIS` appears amid DA732x constants and may be intentional compatibility or a naming mistake; it should be checked before reuse.
- Some status registers are not marked volatile in the driver, so reading them through regmap cache may be misleading unless the driver bypasses cache or extends `da732x_volatile()`.
- Route and DSP bit definitions are broad; writing the wrong combination can silently redirect audio through DSP or bypass paths.
- Calibration masks and sign bits must be exact because the binary-search trim routines invert and combine them directly.

## Test Signals

Validation should include regmap default sync against this register map, bias and CP sequencing, AIF format programming for both AIFA/AIFB, ADC/DAC DAPM power transitions, HP offset calibration comparator behavior, DSP bypass routing, EQ/HPF control writes, DMA status reads if DSP DMA is ever used, and volatile-register behavior for live status fields.
