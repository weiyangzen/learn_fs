# sources/distributed-fs/ceph-client/sound/core/seq/seq_info.c

Purpose: creates and removes ALSA sequencer procfs entries for queues, clients, and timer state.

Important APIs and functions: `create_info_entry()`, `snd_seq_info_init()`, and `snd_seq_info_done()`.

Control flow: init creates module entries under `snd_seq_root`, assigns text read callbacks from client manager, queue, and timer modules, registers them, and unwinds all entries on any failure. Done frees all stored entries.

State and persistence: module-static `queues_entry`, `clients_entry`, and `timer_entry` hold proc entry handles while the sequencer is loaded. Proc contents are generated live; no data persists.

Dependencies and integration: depends on ALSA info/proc APIs and read callbacks `snd_seq_info_queues_read()`, `snd_seq_info_clients_read()`, and `snd_seq_info_timer_read()`.

Risks: only built with `CONFIG_SND_PROC_FS`; header stubs make callers no-op otherwise. Partial init must free earlier entries to avoid dangling proc nodes.

Test signals: procfs-enabled load/unload, failure injection for each entry registration, reading `/proc/asound/seq/{queues,clients,timer}`, and build with procfs disabled.
