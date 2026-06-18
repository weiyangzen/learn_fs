# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.c

Purpose: tracks ALSA sequencer MIDI ports exposed through OSS emulation, manages per-open subscriptions, encodes OSS MIDI bytes to ALSA events, and decodes ALSA events back to OSS read records.

Important APIs and functions: exports `snd_seq_oss_midi_lookup_ports()`, `snd_seq_oss_midi_check_new_port()`, `snd_seq_oss_midi_check_exit_port()`, `snd_seq_oss_midi_clear_all()`, setup/cleanup/open/close/reset helpers, `snd_seq_oss_midi_putc()`, `snd_seq_oss_midi_input()`, `snd_seq_oss_midi_filemode()`, `snd_seq_oss_midi_make_info()`, and `snd_seq_oss_midi_get_addr()`. Internal state is `struct seq_oss_midi` with client/port/capability/open/coder/devinfo/use-lock fields.

Control flow: lookup walks sequencer clients/ports and registers generic MIDI ports with read or write subscription capability. Open checks permissions and subscribes OSS app port to MIDI port for write, MIDI port to app port for read with timestamping, and records ownership by `seq_oss_devinfo`. Close unsubscribes. Output bytes are encoded by `snd_midi_event_encode_byte()` and addressed to the target port. Input events are matched by source client/port, converted either to synth-style OSS records in `/dev/music` mode or MIDI byte records in synth mode, and timestamped into the read queue.

State and persistence: global `midi_devs[]` and `max_midi_devs` are protected by `register_lock`; each MIDI device uses `use_lock` for removal synchronization and `open_mutex` for subscription state. Per-open `dp->max_mididev` snapshots available devices.

Dependencies and integration: depends on sequencer kernel ioctls for client/port queries and subscriptions, `snd_midi_event` encoder/decoder, readq/timer helpers, and system announcement handling from `seq_oss_init.c`.

Risks: one `seq_oss_midi` can be opened by only one OSS app at a time; `-EBUSY` is expected. Removal must clear the table, drop the lookup reference, synchronize `use_lock`, and free coder memory. Capability masks combine direct and subscription caps, so permission tests must remain exact. `send_midi_event()` starts the timer when receiving while stopped, but its local `len` may be set by the start helper before being overwritten by decode.

Test signals: register/remove MIDI ports, duplicate detection, max-device limit, read/write subscription open and close, busy opens by two apps, byte encoding with running status, sysex decode into readq, timestamp insertion, reset all-notes-off/controller events, and proc capability output.
