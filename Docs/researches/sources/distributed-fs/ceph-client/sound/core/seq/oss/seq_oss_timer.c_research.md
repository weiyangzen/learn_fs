# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_timer.c

Purpose: translates OSS sequencer timing semantics into ALSA sequencer queue tempo and timer events.

Important APIs and functions: exports `snd_seq_oss_timer_new()`, `snd_seq_oss_timer_delete()`, `snd_seq_oss_process_timer_event()`, `snd_seq_oss_timer_start()`, `snd_seq_oss_timer_stop()`, `snd_seq_oss_timer_continue()`, `snd_seq_oss_timer_tempo()`, and `snd_seq_oss_timer_ioctl()`. Internal helpers are `calc_alsa_tempo()` and `send_timer_event()`.

Control flow: new timers initialize OSS tempo/timebase and derived ALSA tempo/PPQ. Write-side timer records update `cur_tick`, realtime mode, or start the queue. Starting sets queue tempo with `snd_seq_set_queue_tempo()` and dispatches a system timer START event. Stop/continue/tempo dispatch system timer events. Ioctl handles control rate, start/stop/continue, tempo, timebase, and ignored metronome/source/select commands.

State and persistence: per-open timer state includes current tick, realtime flag, running flag, ALSA tempo/PPQ, OSS tempo/timebase, and owning `seq_oss_devinfo`. No state persists after close.

Dependencies and integration: depends on ALSA sequencer system timer port events, queue tempo API from `seq_clientmgr.c`, OSS event records, and write/read paths that consult `cur_tick`.

Risks: tempo/timebase clamping must match OSS expectations. Timer events are dispatched atomically with `atomic=1`, so callbacks must be safe. Realtime mode bypasses queueing in write path. `SNDCTL_SEQ_CTRLRATE` rejects nonzero requested rates.

Test signals: relative/absolute waits, zero wait enabling realtime, start/stop/continue idempotence, tempo/timebase clamp boundaries, control-rate query, and queued versus direct dispatch decisions in `seq_oss_rw.c`.
