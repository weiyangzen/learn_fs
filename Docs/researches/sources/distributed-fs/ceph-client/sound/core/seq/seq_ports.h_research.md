# sources/distributed-fs/ceph-client/sound/core/seq/seq_ports.h

## Purpose
`seq_ports.h` declares sequencer port and subscription structures plus the internal APIs used by the client manager and kernel sequencer drivers. It defines the ownership, callback, and locking contract for ALSA sequencer ports.

## Important APIs, Types, and Functions
- `struct snd_seq_subscribers` stores a shared subscription object linked into both sender and destination lists.
- `struct snd_seq_port_subs_info` stores one direction's subscription list, count, exclusive flag, list rwsem/rwlock, and open/close callbacks.
- `struct snd_seq_client_port` stores address, module owner, name, use lock, subscription lists, event callback, private data/free hook, capability/type, MIDI metadata, UMP metadata, and MIDI2 conversion bank state.
- Declares lookup, query, create/delete, info set/get, connect/disconnect, subscription query, and attach/detach APIs.

## Control Flow
The header's contract is lock-based: lookup functions return a port with the use lock held; callers release via `snd_seq_port_unlock()` or the `__free(snd_seq_port)` cleanup helper. Subscription lists require both high-level rwsems and low-level rwlocks depending on traversal/update context.

## State and Persistence
All fields are runtime kernel state. UMP conversion banks are compiled only when `CONFIG_SND_SEQ_UMP` is enabled and maintain per-channel conversion carry state for bank select and RPN/NRPN aggregation.

## Dependencies and Integration Points
Includes `<sound/seq_kernel.h>`, `<sound/ump_convert.h>`, and `seq_lock.h`. It is consumed by `seq_ports.c`, client manager delivery paths, UMP conversion, MIDI synth, virtual MIDI, and system port code.

## Risks
Callers must release port references exactly once. The shared subscriber object has two list nodes and an atomic refcount; misuse can lead to double-free or leaked subscriptions. Port capability flags control user-visible access and callback invocation, so inconsistent metadata can break routing.

## Test Signals
Build with and without UMP support; assert lookup cleanup helpers release use locks; validate subscription list counts and exclusivity after connect/disconnect; and verify port info serialization includes direction, UMP group, and MIDI1 flags.
