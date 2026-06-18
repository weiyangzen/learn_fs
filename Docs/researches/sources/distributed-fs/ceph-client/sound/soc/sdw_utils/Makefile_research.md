# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/Makefile

## Purpose
Build recipe for the SoundWire ASoC utility library.

## APIs, Types, and Functions
Composes `snd-soc-sdw-utils-y` from the core utility file, DMIC helpers, Realtek helpers, Cirrus helpers, Maxim helpers, and TI amp helpers, then builds `snd-soc-sdw-utils.o` under `CONFIG_SND_SOC_SDW_UTILS`.

## Control Flow, State, and Persistence
No runtime state. Build-time composition means all listed codec helper exports are linked into one helper module/object.

## Dependencies and Integration
Integrates `soc_sdw_bridge_cs35l56.c`, `soc_sdw_cs42l42.c`, `soc_sdw_cs42l43.c`, and related helpers with generic SoundWire machine drivers through exported namespace functions.

## Risks and Test Signals
Risks include link failures when a helper references codec-specific symbols without matching build coverage, and broad helper inclusion increasing module footprint. Test signals are `SND_SOC_SDW_UTILS=m/y` builds and namespace import checks from machine drivers.
