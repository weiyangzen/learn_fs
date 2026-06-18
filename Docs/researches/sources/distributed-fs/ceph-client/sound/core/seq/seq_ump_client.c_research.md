# sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_client.c

## Purpose
`seq_ump_client.c` binds ALSA UMP rawmidi endpoints to sequencer kernel clients. It creates endpoint and group ports, forwards incoming UMP packets to sequencer subscribers, writes sequencer UMP events to rawmidi output, and propagates endpoint/function-block/protocol changes to sequencer clients.

## Important APIs, Types, and Functions
- `struct seq_ump_client` stores endpoint, sequencer client id, per-direction open counts, output rawmidi file, UMP info shadow pointers, input parser context, and group-notify work.
- `seq_ump_input_receive()` dispatches raw UMP packets from an endpoint to sequencer subscribers.
- `seq_ump_process_event()` writes UMP sequencer events to the rawmidi output stream.
- `seq_ump_client_open()` and `seq_ump_client_close()` manage rawmidi open counts and output file lifetime.
- `fill_port_info()`, `seq_ump_group_init()`, and `create_ump_endpoint_port()` build sequencer ports for groups and endpoint port 0.
- `setup_client_midi_version()` and `setup_client_group_filter()` synchronize sequencer client protocol/filter metadata.
- `snd_seq_ump_probe()` and `snd_seq_ump_remove()` implement the `SNDRV_SEQ_DEV_ID_UMP` sequencer driver.

## Control Flow
Probe allocates a client context, creates a kernel sequencer client named after the UMP endpoint, stores endpoint and block info pointers, sets MIDI version from endpoint protocol, creates group ports for valid groups, computes group filters, creates the endpoint UMP port, attaches UMP info to the sequencer client, and installs endpoint seq ops.

Incoming endpoint packets are delivered only when the input side has been opened by subscription. Groupless messages use port 0; grouped messages map group N to port N+1. Outgoing events must already be marked as UMP; their packet word count is derived from type and written to rawmidi output.

Endpoint and function-block notifications schedule port-info updates, adjust client names/group filters, and broadcast system UMP change events.

## State and Persistence
Runtime state is attached to `snd_ump_endpoint->seq_client` and `seq_ops`. Open counts track subscription/use per direction. `ump_info[]` shadows endpoint and block info addresses for seq client exposure. No persistent storage exists.

## Dependencies and Integration Points
Depends on rawmidi UMP endpoint structures, sequencer kernel client APIs, port callbacks, and system notifications from `seq_system.h`. It works with UMP conversion paths in delivery code via port `ump_group`, `is_midi1`, client `midi_version`, and `group_filter`.

## Risks
Open count underflow would be serious if close callbacks are unbalanced. Group port updates compare only capability and name, so other metadata changes may not trigger set-port-info. Endpoint removal must cancel work before clearing seq ops/client pointers. Packet word count table must match UMP message type definitions.

## Test Signals
Test endpoints with static/dynamic groups, inactive groups, input-only/output-only/duplex flags, MIDI 1 and MIDI 2 protocol switching, endpoint name changes, function-block updates, group filter behavior, and raw UMP packet forwarding both directions.
