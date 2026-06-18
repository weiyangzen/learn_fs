<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_virmidi.h -->
# sources/distributed-fs/ceph-client/include/sound/seq_virmidi.h

## Purpose
`seq_virmidi.h` defines the virtual raw MIDI device that routes rawmidi file I/O through ALSA sequencer clients and ports.

## Important APIs, types, and functions
`struct snd_virmidi` is a per-open file instance with list node, mode, client/port, trigger state, MIDI parser, current sequencer event, parent device, rawmidi substream, and output work. `struct snd_virmidi_dev` is the shared device with card/rawmidi pointers, mode, device/client/port IDs, flags, file list locks/semaphore, and open-file list. Modes are `SNDRV_VIRMIDI_SEQ_NONE`, `SNDRV_VIRMIDI_SEQ_ATTACH`, and `SNDRV_VIRMIDI_SEQ_DISPATCH`. The creation API is `snd_virmidi_new()`.

## Control flow
Creating a virmidi rawmidi device allocates shared state. Each open file creates a `snd_virmidi`, receives or emits MIDI bytes through a `snd_midi_event` parser, and routes events either to an attached port or to subscribers of a virmidi-created sequencer port.

## State and persistence behavior
Shared state persists while the rawmidi device exists; per-open parser and trigger state persists until close. File lists are protected by rwlock and rwsem. No durable state exists.

## Dependencies and integration points
It depends on ALSA rawmidi and MIDI event conversion. It integrates sequencer event routing with rawmidi character device users.

## Risks and test signals
Risks include file-list locking races, delayed output work after close, parser lifetime issues, attach versus dispatch mode confusion, and subscriber use flag handling. Test signals include multiple concurrent opens, subscribe/use flags, attach and dispatch routing, trigger start/stop, close during output work, and parser reset on reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_virmidi.h -->
