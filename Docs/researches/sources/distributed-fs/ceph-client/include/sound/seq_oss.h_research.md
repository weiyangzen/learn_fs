<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_oss.h -->
# sources/distributed-fs/ceph-client/include/sound/seq_oss.h

## Purpose
`seq_oss.h` defines the registration contract for OSS-compatible ALSA sequencer synth devices.

## Important APIs, types, and functions
`struct snd_seq_oss_arg` carries application index, file mode, sequencer mode, opened sequencer address, private data, and event-passing mode. `struct snd_seq_oss_callback` supplies owner, open, close, ioctl, load-patch, reset, and raw-event callbacks. `struct snd_seq_oss_reg` registers type, subtype, voice count, callbacks, and private data. Flags define file access mode, synth/music sequencer mode, event-passing behavior, control rate, queue length, and `SNDRV_SEQ_DEV_ID_OSS`.

## Control flow
An OSS emulation device opens a low-level synth through the callback table, passes raw or processed events depending on `event_passing`, supports ioctls and patch loading, and closes/resets through driver callbacks.

## State and persistence behavior
Per-open state is in `snd_seq_oss_arg` and driver-private data. Registration state is runtime-only and tied to the sequencer OSS emulation device.

## Dependencies and integration points
It includes ALSA sequencer UAPI and kernel sequencer APIs. It bridges old OSS sequencer applications to ALSA sequencer synth backends.

## Risks and test signals
Risks include ABI compatibility mistakes, unsafe user patch buffer handling in callbacks, mismatched event-passing modes, owner lifetime, and queue length/control-rate assumptions. Test signals include OSS synth and music modes, read/write/nonblock modes, patch loads, raw events, reset, ioctl coverage, and callback owner unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_oss.h -->
