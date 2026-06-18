# sources/distributed-fs/ceph-client/sound/core/seq/seq_dummy.c

Purpose: implements the autoloadable ALSA sequencer MIDI-through client at `SNDRV_SEQ_CLIENT_DUMMY`, forwarding received events to subscribers.

Important APIs and types: module parameters `ports`, `duplex`, and optional `ump`; `struct snd_seq_dummy_port`; callbacks `dummy_input()` and `dummy_free()`; setup helpers `create_port()`, `register_client()`, `delete_client()`, and module init/exit.

Control flow: init creates a kernel sequencer client named "Midi Through", optionally sets its UMP/MIDI conversion mode, and creates one or two ports per requested index. Each port has read/write/subscription capabilities and a kernel input callback. On input, non-system/non-error events are copied, source port is rewritten to the same port or paired duplex port, destination becomes subscribers, and the event is dispatched through the kernel client.

State and persistence: module state is `my_client`, module parameters, and per-port private `snd_seq_dummy_port` records freed by port private-free callback. No persistent storage.

Dependencies and integration: depends on sequencer kernel client create/delete/control/dispatch APIs and optional UMP client fields from `seq_clientmgr.h`.

Risks: invalid `ports < 1` is rejected, but very large `ports` relies on sequencer port limits. Duplex setup must clean up the whole client on second-port failure. UMP filter choices affect whether events are converted or passed through.

Test signals: load with default, multiple ports, duplex, and UMP modes; connect ports with `aconnect`; verify event forwarding, subscriber delivery, module autoload alias, and cleanup on partial port creation failure.
