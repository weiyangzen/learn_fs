<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2yaudio.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2yaudio.c

## Purpose
Normal ALSA PCM implementation for older US-X2Y devices. It manages full-duplex synchronized isochronous capture/playback, sample-rate programming, format altsettings, PCM device creation, and period accounting.

## APIs, Types, and Functions
Exports `usx2y_audio_create()` and provides reusable helpers later included by `usx2yhwdeppcm.c`. Key functions are `usx2y_urb_capt_retire()`, `usx2y_urb_play_prepare()`, `usx2y_urb_play_retire()`, `usx2y_urb_submit()`, `usx2y_usbframe_complete()`, `i_usx2y_urb_complete()`, `usx2y_urbs_allocate()`, `usx2y_urbs_start()`, `snd_usx2y_pcm_prepare()`, `snd_usx2y_pcm_trigger()`, `usx2y_rate_set()`, and `usx2y_format_set()`.

## Control Flow, State, and Persistence
Open rejects normal PCM while mmap hwdep mode is active, installs 2-channel S16/S24 hardware constraints, and records runtime private data. `hw_params` enforces one rate/format across all substreams. Prepare resets substream pointers, changes USB altsetting for format, sends pipe-4 sample-rate command sequences, starts capture first for sync, then playback. URB completions pair capture and playback by USB frame; capture actual packet lengths drive playback packet lengths. Retire paths copy capture data into ALSA buffers and advance period counters; playback copies from ALSA or temp buffer around wrap.

## Dependencies and Integration
Depends on ALSA PCM, USB isochronous APIs, pipe-4 control from `usbusx2y.c`, snd-usbmidi input stop/start during altsetting changes, and shared `usx2ydev` state.

## Risks and Test Signals
Risks include strict packet-size range 43-50, synchronization state complexity, inclusion by hwdep PCM source, rate magic tables only for 44.1/48 kHz, MIDI interruption during altsetting, and error paths stopping all clients. Test signals are duplex playback/capture, US-428 second capture PCM, S16/S24 formats, rate switching, xrun behavior, and hot-unplug during active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbusx2yaudio.c -->
