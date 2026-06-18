# sources/distributed-fs/ceph-client/sound/core/seq/seq_clientmgr.h

Purpose: declares internal sequencer client-manager structures and APIs shared across sequencer core files and kernel clients.

Important APIs and types: defines `SND_SEQ_GROUP_FILTER_MASK`, `struct snd_seq_user_client`, `struct snd_seq_kernel_client`, `struct snd_seq_client`, and `struct snd_seq_usage`. Declares initialization/device APIs, client reference helpers, `DEFINE_FREE(snd_seq_client)`, event dispatch, kernel write-poll, subscription notification, low-level single-event delivery, OSS-only kernel ioctl wrapper, kernel client get/put, and UMP mode predicates.

Control flow: other modules acquire client references via `snd_seq_client_use_ptr()` or kernel get/put, dispatch event cells through `snd_seq_dispatch_event()`, and call kernel client control paths. Reference helpers wrap `snd_use_lock_t`.

State and persistence: describes in-memory client state including ports, locks, pools, filters, UMP info, and user/kernel owner data. No storage beyond module memory.

Dependencies and integration: includes sequencer kernel API, FIFO, ports, and use-lock headers. Used by `seq_clientmgr.c`, OSS emulation, dummy client, and other sequencer internals.

Risks: structure fields are internal but widely shared, so changes can affect UMP conversion, proc dumps, and kernel clients. Reference helper misuse leads to use-after-free during client teardown.

Test signals: build all sequencer modules after structure changes, run client creation/removal under concurrent dispatch, and verify UMP predicate behavior for legacy/MIDI1/MIDI2 clients.
