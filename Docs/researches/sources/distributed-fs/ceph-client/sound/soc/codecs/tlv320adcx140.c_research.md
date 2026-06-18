# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320adcx140.c

## Purpose

`tlv320adcx140.c` is an ASoC I2C capture driver for TI TLV320ADC3140/5140/6140 family ADCs. It manages regulators, reset, regcache-backed power transitions, capture DAI configuration, analog and PDM input routing, DRE/AGC/digital gain controls, phase calibration, GPI/GPO/GPIO setup, and mic-bias configuration.

## Important APIs, Types, and Functions

`struct adcx140_priv` holds regulators, optional reset GPIO, regmap, micbias/phase-calibration state, DAI format, and slot width. `adcx140_reset()`, `adcx140_pwr_ctrl()`, `adcx140_pwr_on()`, and `adcx140_pwr_off()` implement reset and power sequencing. `adcx140_hw_params()`, `adcx140_set_dai_fmt()`, and `adcx140_set_dai_tdm_slot()` program word length, format, polarity, master mode, and TDM constraints. `adcx140_codec_probe()` parses firmware properties and initializes device registers. `adcx140_phase_calib_*()` exposes cached phase-calibration state.

## Control Flow

I2C probe gets `avdd`/`iovdd`, optional reset, optional `areg`, initializes the regmap, marks it cache-only, and registers the component. Component probe runs when ASoC instantiates the codec: it parses mic-bias, VREF, PDM edge, GPI, GPIO, GPO, and ASI TX drive properties; resets and wakes the device; programs static configuration; then powers ADC/PLL/bias. Bias transitions from OFF to STANDBY call `adcx140_pwr_on()` to enable regulators, deassert reset, disable cache-only mode, and sync the cache. Transitions back to OFF mark the cache dirty, assert reset, and disable supplies.

## State and Persistence Behavior

The flat regcache is authoritative while the chip is powered off. Probe starts cache-only before hardware is accessible; power-on sync restores cached configuration. `phase_calib_on` is stored in private memory and written to `ADCX140_PHASE_CALIB` when enabling power. `micbias_vg`, `slot_width`, and `dai_fmt` also persist only in driver memory.

## Dependencies and Integration Points

Dependencies include I2C, regmap with a paged range, regulator bulk APIs, optional GPIO reset, generic device properties/OF/ACPI, and ASoC. The DAI exposes capture from two to eight channels at 44.1/48/96/192 kHz. Integration with board DT happens through TI-specific properties for mic bias, PDM edges, GPI/GPO/GPIO, and ASI TX behavior.

## Risks and Edge Cases

`set_tdm_slot()` only supports lower adjacent TX slots despite hardware supporting arbitrary masks. `slot_width` is validated but not otherwise used in current `hw_params()`. Several property arrays are accepted only within fixed sizes; malformed GPI arrays shorter than four values can be risky because indexed values are later accessed. Power sequencing relies on cache-only transitions being correct.

## Test Signals

Validate OFF/STANDBY/PREPARE/ON transitions with regulator tracing, reset GPIO timing, regcache sync after suspend/resume, DAI format and TDM error paths, capture on 2/4/8-channel PDM and analog routes, phase-calibration switch effects, and property validation for mic-bias/GPO/GPI/GPIO settings.
