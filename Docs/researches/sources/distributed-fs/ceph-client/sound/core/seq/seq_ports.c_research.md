# sources/distributed-fs/ceph-client/sound/core/seq/seq_ports.c

## Purpose
`seq_ports.c` implements ALSA sequencer client port registration, lookup, information management, subscription lists, and driver attach/detach helpers. Ports are the public endpoints through which sequencer clients send and receive events.

## Important APIs, Types, and Functions
- `snd_seq_port_use_ptr()` and `snd_seq_port_query_nearest()` find ports and take their use lock.
- `snd_seq_create_port()`, `snd_seq_delete_port()`, and `snd_seq_delete_all_ports()` manage port lifecycle.
- `snd_seq_set_port_info()` and `snd_seq_get_port_info()` copy user/kernel port metadata.
- `snd_seq_port_connect()` and `snd_seq_port_disconnect()` create/remove bidirectional subscription records.
- `snd_seq_port_get_subscription()` queries a matching subscription.
- `snd_seq_event_port_attach()` and `snd_seq_event_port_detach()` are exported helpers for kernel drivers to create/delete event ports.

## Control Flow
Port creation allocates and initializes a port, then inserts it in the client's sorted port list under `ports_mutex` and `ports_lock`. Deletion first removes the port from the list, marks it closing, waits for active use locks to drain, clears source and destination subscriber lists, invokes private cleanup, and frees the object.

Subscription setup allocates one `snd_seq_subscribers` object and adds it to both source and destination subscription lists. Each side is protected by `list_mutex` and `list_lock`; exclusive subscriptions reject existing entries. The first subscription invokes the port's `open` callback and takes the owner module reference. Disconnect starts from the destination list to avoid concurrent deletion conflicts, then removes the source side and frees the shared subscription object.

## State and Persistence
Port state is stored in each `snd_seq_client_port`: address, name, capability/type, timestamping, UMP group/direction, MIDI channel counts, callback/private data, and source/destination subscription metadata. It is in-memory only and scoped to the owning sequencer client.

## Dependencies and Integration Points
This file depends on client manager functions (`snd_seq_client_use_ptr()`, `snd_seq_kernel_client_ctl()`, notification helpers), system notifications, module references, and UMP conversion state in port metadata. MIDI synth, UMP, virtual MIDI, and system clients all create ports through this layer.

## Risks
Subscription operations must keep both sides of a shared subscription synchronized; partial failure unwinds are important. `snd_seq_delete_all_ports()` moves lists while holding locks, so list-head manipulation correctness is critical. Port callbacks execute at subscription/use boundaries and can fail after module references are taken.

## Test Signals
Test automatic and fixed port numbering, inactive-port query filtering, exclusive subscription conflicts, duplicate subscription rejection, callback failure unwind, deleting a port while its peer is also deleting, module refcount behavior, and UMP port info round-tripping.
