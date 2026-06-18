<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.h

## Purpose
Private US-X2Y driver header defining URB counts, runtime state structures, module packet-count policy, and cross-file declarations for card/audio/control code.

## APIs, Types, and Functions
Defines `NRURBS`, default and maximum packet counts, optional `nrpacks`, async sequence constants, `struct snd_usx2y_async_seq`, `struct snd_usx2y_urb_seq`, `struct usx2ydev`, and `struct snd_usx2y_substream`. Declares `usx2y_audio_create()`, `usx2y_async_seq04_init()`, `usx2y_in04_init()`, and macro `usx2y(card)`.

## Control Flow, State, and Persistence
No executable logic, but it defines persistent card state used across firmware loading, audio PCM, hwdep PCM, pipe-4 control, and MIDI. `usx2ydev` keeps USB device, card index, stride, control URBs, async sequences, rate/format, chip status, PCM mutex, shared memories, substreams, prepare synchronization, and MIDI list. Substreams track endpoint, state machine, ring pointers, URBs, and playback temp buffer.

## Dependencies and Integration
Includes USB-audio and MIDI headers, US-428 control definitions, and hwdep PCM definitions. Used by all older US-X2Y implementation files.

## Risks and Test Signals
Risks include heavy shared mutable state, volatile/atomic state-machine expectations, compile-time inclusion of hwdep PCM interfaces, and `nrpacks` behavior changing available modes. Test signals include build coverage with `USX2Y_NRPACKS_VARIABLE`, normal PCM and hwdep PCM operation, rate/format consistency checks, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2y.h -->
