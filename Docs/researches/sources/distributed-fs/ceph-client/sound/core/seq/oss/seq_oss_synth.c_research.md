# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.c

Purpose: manages OSS synth-device registration, per-open synth setup/cleanup, MIDI-as-synth mapping for `/dev/music`, synth addressing, reset, patch loading, sysex/raw event conversion, and legacy synth info/proc output.

Important APIs and functions: exports `snd_seq_oss_synth_init()`, `snd_seq_oss_synth_probe()`, `snd_seq_oss_synth_remove()`, setup/setup_midi/cleanup helpers, `snd_seq_oss_synth_reset()`, `snd_seq_oss_synth_load_patch()`, `snd_seq_oss_synth_info()`, `snd_seq_oss_synth_sysex()`, `snd_seq_oss_synth_addr()`, `snd_seq_oss_synth_ioctl()`, `snd_seq_oss_synth_raw_event()`, `snd_seq_oss_synth_make_info()`, and proc `snd_seq_oss_synth_info_read()`.

Control flow: sequencer-device probe allocates a `seq_oss_synth`, copies registration callbacks, and inserts it in the global table. Per-open setup walks registered synths, pins callback owner modules, calls low-level open, allocates voice tracking, and records opened synths. `/dev/music` setup can append MIDI devices as pseudo synths. Cleanup closes opened synth callbacks, drops module refs, closes MIDI mappings, and frees channel state. Event conversion uses `snd_seq_oss_synth_addr()` before setting note/control/sysex/raw event payloads.

State and persistence: global `synth_devs[]`, `max_synth_devs`, and `midi_synth_dev` are protected by `register_lock` and `snd_use_lock_t`. Per-open `seq_oss_synthinfo` stores callback args, channel state, voice count, MIDI mapping, and opened flags.

Dependencies and integration: registered by `seq_oss.c` as a `snd_seq_driver`; uses callbacks from low-level OSS synth providers, module owner refs, MIDI device helpers, sequencer dispatch, and procfs.

Risks: cleanup sets `rec->opened = 0` rather than decrementing, so multiple opens of the same synth require careful review of historical semantics. MIDI synth reset calls `snd_seq_oss_midi_close(dp, dev)` with the synth index rather than `midi_mapped`, which should be tested. Use-lock synchronization protects removal from active users. Channel arrays depend on driver voice counts.

Test signals: synth probe/remove under use, open/cleanup with failing callbacks or allocation, multiple OSS opens, MIDI pseudo-synth mapping, reset with and without low-level callback, patch/ioctl passthrough, sysex termination at `0xff`, raw event conversion, and proc listing.
