# sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.h

## Purpose
Shared private header for the ADAU17x1 codec family.

## APIs, Types, and Functions
Defines `enum adau17x1_type`, PLL/source/clock enums, the shared `struct adau`, exported helper prototypes, `extern const struct snd_soc_dai_ops adau17x1_dai_ops`, and common register/bit definitions. `struct adau` persists sysclk, PLL frequency and six-byte PLL register image, optional MCLK, selected clock source, type, SPI mode-switch callback, DAI format, master flag, stream-to-TDM-slot mapping, DSP bypass flags, regmap, and SigmaDSP pointer.

## Control Flow, State, and Persistence
The header itself has no logic, but it defines the state that `adau17x1.c`, `adau1761.c`, and `adau1781.c` share across probe, stream setup, DAPM transitions, firmware loading, suspend/resume, and remove.

## Dependencies and Integration
Includes regmap, platform data for ADAU17x1 board options, and `sigmadsp.h`. It is the integration boundary between device-specific drivers, bus glue, and the common core.

## Risks and Test Signals
Risks include shared state fields being updated by multiple code paths without clear locking outside normal ASoC serialization, register constants being reused by devices with slightly different maps, and enum/type mismatches in bus match data. Build coverage and stream tests across ADAU1361, ADAU1761, ADAU1381, and ADAU1781 are the meaningful signals.
