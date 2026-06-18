# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.c

Purpose: implements the per-open OSS MIDI input/read queue as a fixed-size circular buffer of `union evrec` records.

Important APIs and functions: exports `snd_seq_oss_readq_new()`, `snd_seq_oss_readq_delete()`, `snd_seq_oss_readq_clear()`, `snd_seq_oss_readq_puts()`, `snd_seq_oss_readq_sysex()`, `snd_seq_oss_readq_put_event()`, `snd_seq_oss_readq_pick()`, `snd_seq_oss_readq_wait()`, `snd_seq_oss_readq_free()`, `snd_seq_oss_readq_poll()`, `snd_seq_oss_readq_put_timestamp()`, and proc `snd_seq_oss_readq_info_read()`.

Control flow: producers enqueue MIDI byte records, expanded sysex bytes, echo records, and timestamp records. Consumers lock the queue, peek with `pick()`, copy to userspace, then advance with `free()`. Blocking reads wait on `midi_sleep` with `pre_event_timeout`; poll registers the same wait queue.

State and persistence: per queue state includes record array, max length, current length, head/tail indexes, timeout, last input timestamp, wait queue, and spinlock. It persists only for an open OSS file.

Dependencies and integration: used by read/write file paths, event input, MIDI input conversion, ioctl pretime/count commands, and proc diagnostics. Uses `snd_seq_dump_var_event()` to expand ALSA variable sysex events.

Risks: queue-full threshold is `maxlen - 1`, so one slot is reserved to distinguish full/empty. `snd_seq_oss_readq_poll()` reads `qlen` without taking the spinlock, which is lightweight but racy for exact counts. Timestamp insertion updates `input_time` after enqueue attempts and does not propagate queue-full failure to callers.

Test signals: enqueue/dequeue wraparound, full queue behavior, blocking read timeout and signal interruption via caller, poll readiness, sysex expansion, timestamp de-duplication in synth and music modes, and clear wakeup.
