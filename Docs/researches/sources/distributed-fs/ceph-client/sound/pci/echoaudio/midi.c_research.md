# sources/distributed-fs/ceph-client/sound/pci/echoaudio/midi.c

## Purpose

`midi.c` implements raw MIDI support for Echoaudio cards that define `ECHOCARD_HAS_MIDI`. It manages DSP MIDI input flags, MIDI output polling, MIDI time-code timestamp filtering, and ALSA rawmidi registration.

## Important APIs, Types, and Functions

`enable_midi_input()` toggles `DSP_FLAG_MIDI_INPUT` and sends `DSP_VC_UPDATE_FLAGS`. `write_midi()` writes a bounded MIDI packet into `comm_page->midi_output` and sends `DSP_VC_MIDI_WRITE` when host flag HF4 says the DSP can accept data. `mtc_process_data()` skips timestamp words inserted after MTC `0xF1`. `midi_service_irq()` copies DSP input bytes into `chip->midi_buffer`. ALSA callbacks are `snd_echo_midi_input_open()`, `snd_echo_midi_input_trigger()`, `snd_echo_midi_input_close()`, `snd_echo_midi_output_open()`, `snd_echo_midi_output_write()`, `snd_echo_midi_output_trigger()`, `snd_echo_midi_output_close()`, and `snd_echo_midi_create()`.

## Control Flow

Input open stores the substream and trigger toggles the DSP MIDI input flag under `chip->lock`. IRQ service reads the comm-page count and filters timestamp words. Output trigger starts a timer; the timer peeks rawmidi bytes, attempts a DSP write, acknowledges sent bytes, and rearms itself based on MIDI wire time if data remains or the DSP FIFO is full.

## State and Persistence Behavior

Persistent state includes `midi_in`, `midi_out`, `rmidi`, `midi_input_enabled`, `midi_full`, `tinuse`, `mtc_state`, a timer, and `midi_buffer`. DSP-visible state lives in comm-page MIDI input/output arrays and `midi_out_free_count`.

## Dependencies and Integration Points

It depends on shared DSP handshake/vector helpers, `struct comm_page`, ALSA rawmidi APIs, timers, and card IRQ service in `echoaudio_dsp.c`.

## Risks and Test Signals

Risks include timer deletion races, writing too many bytes to the DSP MIDI buffer, mishandling MTC timestamp words, and rawmidi callbacks after close. Test signals are duplex rawmidi creation, input byte delivery from IRQ, output progress under FIFO-full conditions, clean trigger start/stop, and no timer use-after-close.
