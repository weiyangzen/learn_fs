# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_ioctl.c

Purpose: implements OSS sequencer ioctl compatibility for timer control, reset/sync, device enumeration/info, MIDI open tests, queue counts, and synth-driver passthrough.

Important APIs and functions: exports `snd_seq_oss_ioctl()`. Helpers copy synth and MIDI info to userspace (`snd_seq_oss_synth_info_user()`, `snd_seq_oss_midi_info_user()`) and dispatch out-of-band events (`snd_seq_oss_oob_user()`).

Control flow: timer ioctls are routed to `snd_seq_oss_timer_ioctl()`. Reset/panic reset per-open state. `SNDCTL_SEQ_SYNC` loops on `snd_seq_oss_writeq_sync()` until the queued echo confirms completion or a signal interrupts. Device info commands copy legacy `synth_info`/`midi_info`. Unknown write-mode commands fall through to synth ioctl handling for device 0.

State and persistence: mutates timer tempo/timebase/running state, readq pre-event timeout, writeq output-room threshold, MIDI open subscriptions, and synth/device reset state.

Dependencies and integration: depends on readq/writeq/timer/synth/MIDI/event conversion modules and OSS legacy ioctl constants.

Risks: some legacy commands intentionally return success without doing work; tests must distinguish compatibility stubs from missing handling. `SNDCTL_SEQ_PANIC` resets but returns `-EINVAL`, matching historical behavior but surprising to callers. Default passthrough can issue arbitrary synth ioctls when opened for write.

Test signals: ioctl matrix covering timer commands in synth/music mode, sync with echo delivery and signal interruption, get input/output counts, MIDI/synth info copy faults, threshold clamping, pretime conversion, out-of-band event dispatch, and unsupported command behavior.
