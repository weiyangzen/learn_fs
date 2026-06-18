# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.h

## Purpose
Header for the RT1316 SoundWire SDCA amplifier driver. It defines SDCA function, entity, control, and channel identifiers plus the private runtime state used by `rt1316-sdw.c`.

## APIs, Types, and Functions
Constants identify function `FUNC_NUM_SMART_AMP`, entities for PDE23/PDE27/PDE22/PDE24/XU24/FU21/UDMPU21, controls for sample frequency, requested power state, bypass, mute, volume, and cluster selection, and channel ids `CH_L`/`CH_R`. `struct rt1316_sdw_priv` stores the ASoC component, regmap, SoundWire slave, current bus params, hardware init flags, and optional BQ parameter buffer/count.

## Control Flow
There is no executable code. `rt1316-sdw.c` combines these constants with `SDW_SDCA_CTL()` to address SDCA controls for DAPM power, mute switches, mixer controls, defaults, readable registers, and blind writes. The private state is allocated at SDW probe and then updated by attach, component probe, DAI setup, suspend, and resume paths.

## State and Persistence
The header defines runtime state layout but no persistent storage. Initialization flags coordinate SoundWire attach and regcache state, and `bq_params` is devm-managed property data.

## Dependencies and Integration
Includes Linux regmap, SoundWire core/type/register headers, and ALSA SoC headers because it exposes concrete kernel types. It is specific to the RT1316 SDCA SoundWire implementation and is not shared with an I2C variant in this subset.

## Risks and Test Signals
Risks are mostly contract drift: wrong SDCA entity or control ids would affect power, mute, bypass, or channel routing without compiler errors. Test signals include successful control reads/writes at generated SDCA addresses, DAPM transitions for PDE entities, mixer mute behavior, and capture/playback stream setup using the declared state.
