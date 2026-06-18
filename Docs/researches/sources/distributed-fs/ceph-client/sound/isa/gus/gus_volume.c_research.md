<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_volume.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_volume.c

Purpose: GF1 volume and frequency conversion helpers plus attenuation table allocation/export.

Important APIs/types/functions: exported `snd_gf1_lvol_to_gvol_raw()` converts linear volume to GF1 exponential/mantissa format, and `snd_gf1_translate_freq()` converts fixed-point frequency to GF1 frequency register units using current playback frequency. `snd_gf1_atten_table` is allocated here and exported for the synth module.

Control flow: volume conversion clamps input to 65535, finds exponent and mantissa, and packs them into a 16-bit GF1 volume. Frequency conversion shifts input, clamps a low minimum, detects overflow, and scales by `gus->gf1.playback_freq`.

State and persistence: functions are pure except overflow logging; the attenuation table is read-only static data. `snd_gf1_translate_freq()` depends on current active-voice-derived playback frequency.

Dependencies and integration: PCM volume controls call `snd_gf1_lvol_to_gvol_raw()`, PCM trigger uses `snd_gf1_translate_freq()`, and external synth code uses `snd_gf1_atten_table`.

Risks: conversion accuracy affects playback gain and pitch. Overflow handling assigns a bitwise-negated mask-like value before scaling, which is legacy behavior and should be regression-tested before modification. Test signals are boundary values for volume, frequency conversion at supported rates/voice counts, exported symbol resolution, and audible PCM pitch/volume sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_volume.c -->
