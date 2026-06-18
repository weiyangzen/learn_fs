# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_peq.h

## Purpose
Defines PEQ register offsets, bitfields, RAM control bits, channel/stage limits, per-channel RAM payload sizes, and exported PEQ helper prototypes.

## Important APIs, Types, And Functions
Important constants include `TEGRA210_PEQ_MAX_BIQUAD_STAGES`, `TEGRA210_PEQ_MAX_CHANNELS`, `TEGRA210_PEQ_GAIN_PARAM_SIZE_PER_CH`, and `TEGRA210_PEQ_SHIFT_PARAM_SIZE_PER_CH`. Prototypes expose regmap/component initialization and save/restore hooks to the OPE parent.

## Control Flow
No executable flow exists. RAM size constants are consumed by control generation, default initialization, and suspend/resume save/restore loops.

## State And Persistence
The header defines the expected size of coefficient and shift RAM payloads. Persistence is implemented by the PEQ C file and OPE runtime PM using buffers sized from these macros.

## Dependencies And Integration Points
Included by `tegra210_peq.c` and `tegra210_ope.h`. It includes platform-device, regmap, and ASoC declarations because its APIs cross those subsystems.

## Risks
Payload size macros are central to RAM addressing; if the hardware layout changes, stale size arithmetic would corrupt adjacent channel RAM. `TEGRA210_PEQ_BIQUAD_INIT_STAGE` must remain within max stages.

## Test Signals
Compile-time tests catch prototype drift. Runtime tests should verify each channel's RAM offset equals `channel * size_per_channel` for both gain and shift memories.
