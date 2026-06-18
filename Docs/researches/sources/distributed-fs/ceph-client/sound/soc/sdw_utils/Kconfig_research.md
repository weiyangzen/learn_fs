# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/Kconfig

## Purpose
Kconfig symbol for common SoundWire ASoC machine-driver helper utilities.

## APIs, Types, and Functions
Defines `SND_SOC_SDW_UTILS` as a tristate helper library. It has no user prompt dependencies in this file beyond the help text.

## Control Flow, State, and Persistence
No runtime state. It gates compilation of the `snd-soc-sdw-utils` helper object bundle.

## Dependencies and Integration
Intended for generic SoundWire machine drivers that need common codec helper functions. Actual dependency selection is expected from parent Kconfig users.

## Risks and Test Signals
Risks include missing explicit dependencies if parent symbols do not select required ASoC/SoundWire codec support, and helper library bloat because many codec helpers build together. Test signals are builds with machine drivers selecting this symbol and link coverage for exported `SND_SOC_SDW_UTILS` namespace helpers.
