# sources/distributed-fs/ceph-client/sound/core/seq/seq_info.h

Purpose: declares sequencer procfs initialization and read callbacks, with no-op stubs when procfs is disabled.

Important APIs: `snd_seq_info_clients_read()`, `snd_seq_info_timer_read()`, `snd_seq_info_queues_read()`, `snd_seq_info_init()`, and `snd_seq_info_done()`.

Control flow: `seq.c` calls init/done unconditionally; this header resolves to real functions or stubs based on `CONFIG_SND_PROC_FS`.

State and persistence: no state in the header.

Dependencies and integration: includes ALSA info and sequencer kernel headers; links client manager, timer, and queue proc readers.

Risks: callbacks are declared regardless of procfs, so implementations must be conditionally compiled consistently to avoid link errors.

Test signals: build with `CONFIG_SND_PROC_FS=y` and `n`, and read all proc entries when enabled.
