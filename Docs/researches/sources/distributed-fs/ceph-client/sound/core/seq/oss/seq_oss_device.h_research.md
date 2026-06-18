# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_device.h

Purpose: central private header for OSS sequencer emulation state, limits, file-mode helpers, and integration wrappers into the ALSA sequencer core.

Important APIs and types: defines `SNDRV_SEQ_OSS_MAX_CLIENTS`, synth/MIDI device limits, version strings, `reltime_t`, `abstime_t`, `struct seq_oss_chinfo`, `struct seq_oss_synthinfo`, and `struct seq_oss_devinfo`. Declares open/release/read/write/ioctl/poll/reset functions and proc readers. Inline helpers include `is_read_mode()`, `is_write_mode()`, `is_nonblock_mode()`, `snd_seq_oss_dispatch()`, `snd_seq_oss_control()`, and `snd_seq_oss_fill_addr()`.

Control flow: other OSS source files pass a `seq_oss_devinfo` through these declarations. Event writers call `snd_seq_oss_fill_addr()` before dispatch/enqueue; ioctl/writeq paths use `snd_seq_oss_control()` to issue sequencer ioctls against the OSS kernel client.

State and persistence: `seq_oss_devinfo` is per open application and stores client/port/queue ids, mode flags, discovered MIDI and synth counts, per-open synth metadata, read/write queues, and timer state. It is allocated on open and freed by the sequencer port private-free callback.

Dependencies and integration: includes ALSA core, rawmidi, sequencer kernel, OSS legacy API, info/proc, and `seq_clientmgr.h` for kernel client dispatch/control.

Risks: this header defines ownership assumptions for per-open state. Incorrect mode helper use can allow read/write on the wrong queue. `snd_seq_oss_dispatch()` bypasses queueing by using direct kernel dispatch, so callers must set event timestamps and destinations correctly.

Test signals: compile coverage for all OSS files, static checks of mode-guarded entry points, and runtime open in synth/music/read/write/nonblocking combinations.
