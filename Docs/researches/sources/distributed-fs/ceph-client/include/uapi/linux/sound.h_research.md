# sources/distributed-fs/ceph-client/include/uapi/linux/sound.h

## Purpose
Defines legacy OSS sound device minor numbers used to identify mixer, sequencer, MIDI, DSP, audio, synth, and obsolete sound nodes.

## Important APIs, Types, and Constants
The header has no structs or functions. Constants include `SND_DEV_CTL`, `SND_DEV_SEQ`, `SND_DEV_MIDIN`, `SND_DEV_DSP`, `SND_DEV_AUDIO`, `SND_DEV_DSP16`, `SND_DEV_UNUSED`, `SND_DEV_AWFM`, `SND_DEV_SEQ2`, `SND_DEV_SYNTH`, `SND_DEV_DMFM`, `SND_DEV_UNKNOWN11`, `SND_DEV_ADSP`, `SND_DEV_AMIDI`, and `SND_DEV_ADMMIDI`.

## Control Flow, State, and Persistence
There is no runtime logic. The minor-number assignments are persistent ABI and must stay compatible with old `/dev/sound` and OSS node naming.

## Dependencies and Integration Points
Includes `<linux/fs.h>` for device-number context. Integrates with OSS compatibility device registration and old userspace device-node creation scripts.

## Risks and Test Signals
Risks are accidental reuse of obsolete numbers and mismatch with `soundcard.h` ioctl expectations. Test by compiling OSS compatibility code and checking that generated device minors match historical nodes.
