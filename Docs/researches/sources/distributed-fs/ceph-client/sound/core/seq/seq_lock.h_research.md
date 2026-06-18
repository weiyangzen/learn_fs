# sources/distributed-fs/ceph-client/sound/core/seq/seq_lock.h

Purpose: defines the sequencer use-lock primitive as an atomic use counter plus helper macros.

Important APIs and types: `typedef atomic_t snd_use_lock_t`, `snd_use_lock_init()`, `snd_use_lock_use()`, `snd_use_lock_free()`, and `snd_use_lock_sync()` which records source file/line for diagnostics.

Control flow: users increment before using a shared object, decrement after use, and teardown removes object visibility then calls sync to wait for the counter to drain.

State and persistence: no global state; the counter lives inside protected structures such as clients, FIFOs, MIDI devices, and synth records.

Dependencies and integration: includes scheduler support for the sync implementation and is used throughout the sequencer core and OSS compatibility code.

Risks: macros do not prevent underflow or enforce object lifetime by themselves. Missing `free()` calls can hang teardown; extra `free()` calls drive the counter negative and trigger warnings.

Test signals: static audit of every use/free pair, concurrent lookup/removal stress, and lockdep-style validation that sync is only used in sleepable paths.
