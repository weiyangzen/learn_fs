# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_rw.c

Purpose: implements OSS sequencer file read, write, and poll operations on top of readq/writeq, event conversion, and sequencer enqueue/dispatch.

Important APIs and functions: exports `snd_seq_oss_read()`, `snd_seq_oss_write()`, and `snd_seq_oss_poll()`. Internal `insert_queue()` processes a single OSS event record.

Control flow: read loops while the user buffer can hold at least a short record, peeks a queued record under lock, optionally waits, copies the event length to userspace, and advances the queue. Write copies 4-byte records first, handles `SEQ_FULLSIZE` patch loading as a whole-buffer operation, copies 8-byte long records when needed, rejects mode-incompatible record types, and passes each record to `insert_queue()`. `insert_queue()` consumes timer events, converts records to ALSA events, sets current tick, then dispatches immediately for realtime/stopped timers or enqueues on the ALSA queue otherwise.

State and persistence: mutates readq head/tail, write queue through ALSA pool enqueueing, timer current tick/realtime/running state, and downstream synth/MIDI state from conversion.

Dependencies and integration: depends on readq, writeq, synth patch loading, event conversion, timer state, and sequencer kernel enqueue/dispatch/poll helpers.

Risks: the read size check uses `if (ev_len < count)` where the expected condition appears to be insufficient user buffer when `ev_len > count`; as written it can break when the buffer is larger than the event. This is a high-value behavior to verify against upstream or tests. Patch loading only allowed as the first write item. Blocking behavior is split between readq wait and sequencer pool enqueue.

Test signals: read short/long records with exact, smaller, and larger buffers; blocking and nonblocking read/write; fullsize patch write; invalid mode writes for `/dev/music`; timer wait scheduling; poll readiness for read and write.
