# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_asrc.c

## Purpose
This ASoC component driver controls the Tegra186/Tegra264 asynchronous sample-rate converter. It exposes CIF DAIs for ASRC RX/TX paths, DAPM routes through the Tegra audio crossbar, user controls for sample-rate ratio source/value and thresholds, and runtime PM state restoration for conversion lanes.

## Important APIs, types, and functions
`tegra186_asrc_reg_defaults` seeds per-stream and global registers. `tegra186_asrc_set_audio_cif()` translates PCM params into Tegra CIF configuration. `tegra186_asrc_in_hw_params()` programs RX thresholds and RX CIF, while `tegra186_asrc_out_hw_params()` programs TX thresholds/CIF, HW ratio compensation, ratio source, software ratio registers, and lock status. Getter/setter controls manipulate `asrc->lane[]` fields and sometimes hardware registers. `tegra186_asrc_widget_event()` soft-resets a stream after DAPM power-down. Regmap callbacks define readable/writeable/volatile ranges across per-stream stride and global registers. Probe initializes regmap, SoC ARAM address data, defaults, DAIs, controls, routes, and PM.

## Control flow
Probe maps registers, creates cached MMIO regmap, selects Tegra186 or Tegra264 ARAM start address from DT match data, writes global 32-bit fractional precision while cache-only, initializes six lane state records, registers the component and DAIs, then enables runtime PM. Runtime resume leaves cache-only mode, writes scratch ARAM address and global enable before regcache sync, then replays software ratio registers and lock writes for lanes using SW ratio. Runtime suspend only marks the regcache dirty. During playback/capture setup, CIF formatting supports S16 and S24/S32, 1-12 channels, and fixed 24-bit client width. DAPM routes bind RXn CIF inputs to TXn CIF outputs for six streams and route RX7 to a depacketizer for ratio estimator input.

## State and persistence
Per-lane control state (`int_part`, `frac_part`, `ratio_source`, `hwcomp_disable`, `input_thresh`, `output_thresh`) is stored in `struct tegra186_asrc` and used to reprogram hardware on `hw_params()` and runtime resume. Regmap uses `REGCACHE_FLAT` with explicit volatile registers. Ratio integer/fraction registers are marked volatile, so software ratio state is replayed manually after PM.

## Dependencies and integration points
The driver depends on `tegra186_asrc.h`, Tegra CIF helper `tegra_set_cif()`, ASoC DAPM/control/DAI infrastructure, regmap MMIO, runtime PM, and DT compatibles `nvidia,tegra186-asrc` and `nvidia,tegra264-asrc`. DAI and route names are designed for Tegra AHUB/XBAR graph integration.

## Risks and edge cases
Software ratio writes are rejected while the lane source is ARAD, so userspace mixer ordering matters. Ratio lock sequencing is critical after any SW ratio change or PM resume. `Stream6 Input Threshold` is defined with `ASRC_STREAM_REG(..., 4)`, which appears to target stream 5's register rather than stream 6's index 5. DAI ID arithmetic assumes output DAIs start at ID 7. Missing error checks on `regcache_sync()` in runtime resume can hide restore failures. Volatile ratio registers require careful testing across suspend.

## Test signals
Test probe on both compatibles, route all six stream pairs through XBAR, run S16/S24/S32 at channel counts 1 and 12, change ratio source and SW integer/fraction controls before and during streams, verify lock writes, suspend/resume with SW ratios, and specifically validate all six input/output threshold controls program distinct stream registers.
