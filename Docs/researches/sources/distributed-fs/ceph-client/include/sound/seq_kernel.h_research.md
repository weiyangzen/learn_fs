<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_kernel.h -->
# sources/distributed-fs/ceph-client/include/sound/seq_kernel.h

## Purpose
`seq_kernel.h` is the main in-kernel ALSA sequencer API. It defines sequencer limits, kernel port callbacks, kernel client management, variable event expansion, queue tempo control, and port attach/detach helpers.

## Important APIs, types, and functions
Limits include maximum queues, clients, ports, events, client events, hops, and event length. `struct snd_seq_port_callback` supplies subscribe/unsubscribe/use/unuse/event-input/private-free hooks. APIs include `snd_seq_create_kernel_client()`, `snd_seq_delete_kernel_client()`, `snd_seq_kernel_client_enqueue()`, `snd_seq_kernel_client_dispatch()`, `snd_seq_kernel_client_ctl()`, variable event expansion/dump helpers, `snd_seq_event_packet_size()`, `snd_seq_set_queue_tempo()`, `snd_seq_event_port_attach()`, `snd_seq_event_port_detach()`, and autoload init/exit.

## Control flow
Kernel users create a sequencer client, attach ports with callbacks and capabilities, enqueue or dispatch events, optionally expand variable-length events into buffers, and detach/delete during teardown. `snd_seq_event_packet_size()` selects normal or UMP event packet size.

## State and persistence behavior
The header defines interfaces to sequencer core runtime state: clients, queues, ports, event pools, subscriptions, and queue tempo. No state is persisted outside the running kernel.

## Dependencies and integration points
It depends on ALSA sequencer UAPI types and time definitions. It is used by MIDI, virtual MIDI, OSS emulation, UMP, and hardware synth drivers.

## Risks and test signals
Risks include event pool exhaustion, variable event user-pointer handling, overlong delivery paths, callback invocation in atomic contexts, module owner lifetime, and UMP versus legacy packet-size mismatches. Test signals include kernel client create/delete, subscription callbacks, direct and queued dispatch, UMP events, variable-length sysex expansion, autoload paths, and queue tempo changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/seq_kernel.h -->
