# sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp.h

Purpose: public interface for the SigmaDSP firmware helper subsystem. It declares the shared `struct sigmadsp`, optional operation hooks, transport-specific initializers, and runtime setup/reset/constraint APIs used by SigmaDSP codec drivers.

Important APIs and data: `struct sigmadsp_ops` currently provides optional `safeload()` for atomic parameter updates. `struct sigmadsp` owns firmware control/data lists, ALSA rate constraints, current samplerate, attached ASoC component, device pointer, mutex, opaque transport data, and transport read/write callbacks. Exported prototypes cover core initialization, I2C/regmap initialization, component attachment, samplerate setup, reset notification, and PCM rate restriction.

Control flow: there is no executable code here, but the lifecycle is defined by the prototypes: initialize from firmware, attach to an ASoC component during codec probe, restrict startup PCM params when firmware declares rates, call setup during stream configuration, and call reset when hardware DSP memory is lost.

State and persistence: the struct layout documents what persists across firmware setup: lists, cached current samplerate, component pointer, mutex, and transport callbacks. The actual allocation and cleanup are in `sigmadsp.c` and transport files.

Dependencies and integration points: depends on Linux device/regmap/list definitions, ALSA PCM types, forward-declared I2C client, and ASoC component declarations. Risks include exposing mutable internals to codec drivers, lifetime coupling between attached controls and firmware memory, and fixed transport callback signatures for 16-bit-address-style DSP memories. Test signals are successful compilation of I2C and regmap adapters, codec integration using safeload ops, setup/reset API use, and PCM constraint application.
