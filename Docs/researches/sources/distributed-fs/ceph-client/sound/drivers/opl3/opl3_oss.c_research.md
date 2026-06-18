# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_oss.c

## Purpose
Provides OSS sequencer emulation glue for the OPL3 FM synth. It registers the FM synth with ALSA's OSS sequencer layer, creates an OSS-facing sequencer port, maps OSS patch loading into the shared OPL3 patch table, and manages open/close lifecycle.

## Important APIs, Types, And Functions
Exports `snd_opl3_init_seq_oss()` and `snd_opl3_free_seq_oss()`. Static callbacks include `snd_opl3_open_seq_oss()`, `snd_opl3_close_seq_oss()`, `snd_opl3_ioctl_seq_oss()`, `snd_opl3_load_patch_seq_oss()`, `snd_opl3_reset_seq_oss()`, and `snd_opl3_oss_event_input()`.

## Control Flow
Initialization allocates an `SNDRV_SEQ_DEV_ID_OSS` device, fills `snd_seq_oss_reg` with FM synth type/subtype/voice count, creates a write-only sequencer port, and registers callbacks. Open calls `snd_opl3_synth_setup()`, attaches the OSS channel set address to the OSS argument, increments the module reference, and selects synth mode. Events are processed through `snd_midi_process_event()` unless they are raw OSS event wrappers. Patch loading copies an OSS `sbi_instrument`, validates channel/program range, and calls `snd_opl3_load_patch()` in bank 127.

## State And Persistence
State is runtime-only: OSS sequencer device pointer, OSS MIDI channel set, synth mode, module reference, and the shared patch table. Closing releases synth setup and module ownership.

## Dependencies And Integration
Depends on `CONFIG_SND_SEQUENCER_OSS`, ALSA sequencer OSS callbacks, shared OPL3 MIDI ops, and patch APIs from `opl3_synth.c`.

## Risks And Test Signals
`snd_opl3_init_seq_oss()` appears to register the OSS synth only when `snd_opl3_oss_create_port()` returns nonzero, which is counterintuitive and should be verified against expected ALSA device registration behavior. Test signals include OSS synth enumeration, patch loading for FM and OPL3 formats, ioctl behavior, open exclusivity with hwdep/sequencer users, and module reference release.
