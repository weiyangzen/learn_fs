# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_init.c

Purpose: owns OSS sequencer kernel-client creation, per-application open/release/reset, discovery of MIDI ports from sequencer announcements, and per-open queue/timer allocation.

Important APIs and functions: exports `snd_seq_oss_create_client()`, `snd_seq_oss_delete_client()`, `snd_seq_oss_open()`, `snd_seq_oss_release()`, `snd_seq_oss_reset()`, and proc `snd_seq_oss_system_info_read()`. Internal helpers include `receive_announce()`, `translate_mode()`, `create_port()`, `delete_port()`, `alloc_seq_queue()`, `delete_seq_queue()`, `free_devinfo()`, and async MIDI lookup work.

Control flow: module init creates a fixed OSS kernel client, creates a receiver port, subscribes it to system announcements, and schedules a scan of existing MIDI ports. Each open allocates `seq_oss_devinfo`, reserves an application slot, discovers synth/MIDI devices, creates an ALSA port, creates a locked queue, initializes read/write queues by file mode, initializes a timer, sets file private data, and opens MIDI devices according to synth/music mode. Release removes the client table slot, resets devices/queues/timer, cleans synth/MIDI subscriptions, detaches the port, and deletes the queue; actual `dp` memory is freed by the port callback.

State and persistence: module state includes `system_client`, `system_port`, `num_clients`, `client_table`, async lookup work, and `maxqlen` module parameter. Per-open state persists until port detach triggers `free_devinfo()`.

Dependencies and integration: depends on sequencer kernel-client APIs, system announcement events, synth/MIDI/readq/writeq/timer/event components, and ALSA queue ioctls.

Risks: open error paths call cleanup/delete helpers before all fields may be initialized, so sentinel values are important. `client_table` is bounded to 16 applications. Async lookup must be cancelled before deleting the system client. The proc loop iterates `num_clients` rather than the full table, which can miss sparse high-index opens after lower-index closes.

Test signals: create/delete OSS client, open many applications up to limit, open with no devices, force queue/port/readq/writeq/timer allocation failure, process system port start/change/exit announcements, verify release frees queue/port and cancels async work.
