# sources/distributed-fs/ceph-client/include/sound/emux_legacy.h

## Purpose
This header defines legacy OSS/emux control command numbers and effect identifiers for the ALSA emux synthesizer compatibility layer.

## Important APIs, Types, and Constants
It defines `_EMUX_OSS_*` command IDs for debug, reverb/chorus, chip initialization, effects, channel termination/reset, volume/attenuation, drum/channel modes, release/note-off, pressure, and equalizer controls. Enums define modulation/control targets and raw effect IDs, with `EMUX_NUM_EFFECTS` and effect flag values.

## Control Flow
OSS sequencer compatibility code interprets legacy command IDs and maps them into emux control/effect updates. Effect flags describe whether a raw effect is off, set, or added.

## State and Persistence
The header stores no state. State lives in emux ports, voices, and effect tables maintained by `emux_synth.h` consumers.

## Dependencies and Integration Points
It includes `sound/seq_oss_legacy.h` and is included by `emux_synth.h`. Integration is with ALSA sequencer OSS compatibility and wavetable synth drivers such as EMU8000 and EMU10K1 synth.

## Risks and Edge Cases
Legacy numeric command IDs are ABI-sensitive. Changing values can break OSS applications. Some cooked/raw effect modes are explicitly unsupported or constrained by hardware-specific effect tables.

## Test Signals
OSS sequencer compatibility tests, legacy reverb/chorus/effect ioctl/event handling, channel reset/terminate commands, and ABI value preservation checks are useful.
