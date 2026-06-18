# sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.c

Purpose: implements a simple use-counter synchronization helper for sequencer objects that need to wait until active users leave before freeing memory.

Important APIs and functions: exports `snd_use_lock_sync_helper()`, backing the `snd_use_lock_sync()` macro.

Control flow: if the atomic counter is negative, it warns and returns. Otherwise it sleeps one tick at a time until the counter reaches zero, warning once after roughly five seconds of waiting.

State and persistence: no module state; operates on caller-owned `snd_use_lock_t` atomics.

Dependencies and integration: used by FIFO cleanup, client teardown, OSS MIDI/synth removal, and other sequencer structures to coordinate with lockless referenced users.

Risks: this is not a full refcount with lifetime ownership; callers must remove objects from lookup tables before waiting. Sleeping makes it unsuitable for atomic contexts. A stuck positive counter can block teardown indefinitely with periodic warning only once per call.

Test signals: teardown while concurrent users hold/release locks, negative-counter warning path, and ensuring all callers invoke it only from sleepable context.
