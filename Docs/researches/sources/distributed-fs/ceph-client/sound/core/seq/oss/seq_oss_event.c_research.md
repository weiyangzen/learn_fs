# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.c

Purpose: converts legacy OSS sequencer event records into ALSA sequencer events, handles echo events returning from the sequencer, and forwards incoming ALSA events to the OSS MIDI input path.

Important APIs and functions: exports `snd_seq_oss_process_event()` and `snd_seq_oss_event_input()`. Internal converters include `old_event()`, `extended_event()`, `chn_voice_event()`, `chn_common_event()`, `timing_event()`, `local_event()`, `note_on_event()`, `note_off_event()`, `set_note_event()`, `set_control_event()`, and `set_echo_event()`.

Control flow: write-side records are classified by OSS opcode. Timing records may update timer state, sysex goes to synth sysex conversion, `SEQ_MIDIPUTC` feeds the MIDI byte encoder, echo/private events are specially translated, and note/control events resolve a synth target before filling ALSA event data. Input-side `snd_seq_oss_event_input()` handles `SNDRV_SEQ_EVENT_ECHO` locally, waking write sync for `SEQ_SYNCTIMER` or enqueueing echo records to the read queue; non-echo events go to `snd_seq_oss_midi_input()`.

State and persistence: mutates per-open synth channel tracking (`seq_oss_chinfo`) for process-events mode, timer state through timer helpers, read queue content for echoes, and MIDI coder state indirectly through the MIDI path.

Dependencies and integration: depends on OSS legacy event definitions, `seq_oss_synth.c` for device addressing and raw/sysex callbacks, `seq_oss_midi.c` for byte output/input, timer/readq/writeq helpers, and ALSA sequencer event formats.

Risks: legacy encodings have mode-specific validity rules; accepting old 4-byte events in `/dev/music` mode would break ABI expectations. Channel and device indexes must be nospec-bounded. The note-on volume-control convention for note 255 depends on per-voice state. Some endian-sensitive echo construction is explicitly noted in code.

Test signals: exercise old, extended, channel voice/common, sysex, MIDI putc, echo, private, and timing records in synth and music modes; validate invalid opcode rejection; verify echo readback and write-sync wakeups; fuzz device/channel indexes.
