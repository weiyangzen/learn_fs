# subset-b-006356 Research

Grouped research for ALSA core and sequencer files under `sources/distributed-fs/ceph-client/sound/core`. Sections are source-tree aligned and wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_memory.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_memory.c

## Purpose
`seq_memory.c` implements the ALSA sequencer event-cell memory manager. It owns fixed-size pools of `struct snd_seq_event_cell` objects, duplicates sequencer events into those cells, stores variable-length event payloads as chained event cells, and exposes helpers to dump or expand variable payloads back into kernel or user buffers. This file is a critical backing allocator for sequencer FIFOs and priority queues.

## Important APIs, Types, and Functions
- `snd_seq_dump_var_event()` streams a variable-length event payload through a caller callback, handling kernel pointers, user pointers, and chained cells.
- `snd_seq_expand_var_event()` and `snd_seq_expand_var_event_at()` linearize variable payloads into a provided buffer, optionally padding to an alignment.
- `snd_seq_event_dup()` allocates a primary event cell and enough extra cells to hold sysex or other variable-length payloads.
- `snd_seq_cell_free()` returns a cell and any chained payload cells to the owning pool.
- `snd_seq_pool_new()`, `snd_seq_pool_init()`, `snd_seq_pool_mark_closing()`, `snd_seq_pool_done()`, and `snd_seq_pool_delete()` manage pool lifecycle.
- `snd_seq_pool_poll_wait()` exposes output-room readiness for poll users.
- `snd_seq_info_pool()` prints pool statistics for proc/info reporting.

## Control Flow
Variable payload handling starts with `get_var_len()`, which rejects non-variable events. `dump_var_event()` then selects one of three storage forms: user pointer payloads are copied in small stack chunks with `copy_from_user()`, non-chained kernel payloads are passed directly to the callback, and chained payloads iterate through `event.data.ext.ptr` as a linked list of `snd_seq_event_cell` nodes.

Allocation is centered on `snd_seq_cell_alloc()`. It takes `pool->lock`, waits on `pool->output_sleep` when the free list is empty and blocking allocation is allowed, temporarily drops a caller mutex around `schedule()`, aborts on signals, and refuses allocation once `pool->closing` is set. `snd_seq_event_dup()` uses that allocator for the main cell, copies the fixed event packet, then decomposes variable payloads into additional cells. Error unwind calls `snd_seq_cell_free()` on the primary cell, which also releases the chain.

## State and Persistence
The pool state is in-memory only: `ptr`, `free`, `counter`, `closing`, `room`, and allocation statistics. There is no disk persistence. Pool usage is guarded by a spinlock and an atomic counter. The free-list watermark `room` is half the pool size and controls wakeups for blocked writers.

## Dependencies and Integration Points
This file depends on ALSA sequencer event definitions from `<sound/seq_kernel.h>`, user-copy helpers, wait queues, and `seq_lock.h` guard macros. It is used by queueing code (`seq_prioq.c`, `seq_fifo.c`, `seq_queue.c`) to retain events until dispatch. MIDI and UMP conversion paths use the variable-event dump/expand helpers for sysex conversion.

## Risks
Variable payload correctness depends on consistent `SNDRV_SEQ_EXT_USRPTR` and `SNDRV_SEQ_EXT_CHAINED` flags. Pool teardown waits in a loop until all cells are returned; leaked cells can delay shutdown. The code is lock-sensitive because free-list mutation, waitqueue wakeups, and chained-cell release all happen under the same pool lock. Large variable events are rejected if they would consume at least the whole pool.

## Test Signals
Useful tests include sysex enqueue/dequeue with kernel, user, and chained payload forms; interrupted blocking allocation; pool closing while writers wait; poll readiness around the `room` watermark; and error unwind for partial variable-payload duplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_memory.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_memory.h

## Purpose
`seq_memory.h` declares the sequencer memory manager interfaces and the internal event-cell/pool structures used by the ALSA sequencer queues. It bridges legacy sequencer events and UMP-capable packets in one cell representation.

## Important APIs, Types, and Functions
- `union __snd_seq_event` aliases `struct snd_seq_event`, optional `struct snd_seq_ump_event`, and a packed raw layout with optional extra UMP data.
- `struct snd_seq_event_cell` stores an event packet, owning pool pointer, and next link.
- `struct snd_seq_pool` stores contiguous cell storage, a free list, counters, wait queue, and spinlock.
- Declared APIs include `snd_seq_cell_free()`, `snd_seq_event_dup()`, pool lifecycle helpers, poll helper, and proc-info dump helper.
- Inline helpers `snd_seq_unused_cells()` and `snd_seq_total_cells()` expose pool occupancy.

## Control Flow
The header defines the shared contract: users allocate pools, initialize them, duplicate incoming events into cells, enqueue cells in other sequencer structures, and eventually free cells back to the pool. Variable-length data is represented by setting the event's ext pointer to a chain of additional cells.

## State and Persistence
All fields are volatile kernel runtime state. `counter` tracks allocated cells despite the comment saying "cells free"; free count is derived as `total_elements - counter`. `closing` blocks further allocation during teardown.

## Dependencies and Integration Points
Includes `<sound/seq_kernel.h>` and `<linux/poll.h>`. The structures are consumed by `seq_memory.c`, priority queues, FIFOs, client manager code, and UMP conversion code where event packet size can differ from the legacy fixed event size.

## Risks
Because this header exposes internal structures, consumers can misuse `next`, `pool`, or counter assumptions. UMP layout compatibility depends on `CONFIG_SND_SEQ_UMP` and the raw aliasing staying aligned with `snd_seq_event_packet_size()`.

## Test Signals
Compile coverage with and without `CONFIG_SND_SEQ_UMP` is important. Runtime tests should confirm cell packet copying for legacy and UMP events and that free/total cell counts match queue pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_midi.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_midi.c

## Purpose
`seq_midi.c` implements the generic MIDI synth sequencer driver that exposes rawmidi devices as ALSA sequencer ports. It creates sequencer kernel clients for rawmidi cards, converts raw MIDI byte streams into sequencer events on input, and converts sequencer events back into MIDI bytes on output.

## Important APIs, Types, and Functions
- `struct seq_midisynth` stores one sequencer port's rawmidi device, input/output files, parser, client id, and port id.
- `struct seq_midisynth_client` groups per-card sequencer clients and their per-device ports.
- `snd_midi_input_event()` reads bytes from a rawmidi input substream and dispatches encoded sequencer events to subscribers.
- `event_process_midi()` receives sequencer events and writes decoded MIDI bytes to the rawmidi output stream, with direct sysex streaming through `snd_seq_dump_var_event()`.
- Subscription/use callbacks open and close rawmidi input/output streams.
- `snd_seq_midisynth_probe()` and `snd_seq_midisynth_remove()` implement the `snd_seq_driver` binding for `SNDRV_SEQ_DEV_ID_MIDISYNTH`.

## Control Flow
Probe inspects rawmidi input and output subdevice counts, creates or reuses a per-card kernel sequencer client, allocates one `seq_midisynth` per port, initializes a `snd_midi_event` parser, and creates sequencer ports with callback tables. Input subscriptions call `midisynth_subscribe()`, which opens rawmidi input, configures buffer parameters, installs `snd_midi_input_event()` as the rawmidi runtime callback, and primes the stream. Output use calls `midisynth_use()`, which opens output and sets buffer/no-active-sensing parameters.

Incoming rawmidi bytes are parsed one byte at a time. A complete MIDI event is dispatched to `SNDRV_SEQ_ADDRESS_SUBSCRIBERS`. Outgoing sequencer events are decoded to MIDI bytes or streamed as sysex, then written through `snd_rawmidi_kernel_write()`.

## State and Persistence
State is per card in the static `synths[]` table and protected by `register_mutex`. Per-port state persists while the sequencer device is bound. Runtime input/output file handles exist only while the port has active subscriptions or users. No persistent storage is used.

## Dependencies and Integration Points
Depends on rawmidi, sequencer kernel client control, `seq_device` bus registration, and MIDI event parser APIs from `seq_midi_event.c`. It integrates with port callbacks from `seq_ports.c` and with rawmidi device-specific `get_port_info()` overrides.

## Risks
Buffer sizing is module-param controlled and can trigger output overrun errors. Probe has several partial-allocation unwind paths, so leaks or stale sequencer clients are the main lifecycle risk. Input and output share one parser per `seq_midisynth`, so concurrent stream usage must respect rawmidi/port callback serialization assumptions.

## Test Signals
Test by registering rawmidi devices with input-only, output-only, duplex, and multiple subdevices; subscribing/unsubscribing sequencer clients; sending sysex and running-status MIDI; and verifying remove tears down ports and the kernel client when the last device is gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_emul.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_emul.c

## Purpose
`seq_midi_emul.c` provides driver-independent MIDI channel state emulation for ALSA sequencer clients. It tracks notes, controllers, RPN/NRPN state, GM/GS/XG sysex modes, drum-channel status, and common controller semantics so hardware or software drivers can consume normalized callbacks.

## Important APIs, Types, and Functions
- `snd_midi_process_event()` is the main event interpreter. It updates channel state and calls driver callbacks in `struct snd_midi_op`.
- `snd_midi_channel_set_clear()` resets all channels to GM-like defaults.
- `snd_midi_channel_alloc_set()` and `snd_midi_channel_free_set()` allocate/free channel sets.
- `do_control()` handles controller changes, sustain/sostenuto, data entry, RPN/NRPN selection, reset controllers, all-sounds-off, and all-notes-off.
- `sysex()` parses GM on, GS reset/drum/reverb/chorus/master-volume, and XG on messages.
- `rpn()` and `nrpn()` parse registered/nonregistered parameter changes.

## Control Flow
`snd_midi_process_event()` determines the target channel for channel events, normalizes note-on with velocity zero into note-off, filters invalid notes/channels, and switches on event type. Note events update `chan->note[]` and call `note_on`, `note_off`, or `key_press`. Controller events pass through `do_control()`, where switch-type controllers are normalized and special controllers alter note hold/release state or parameter tracking. Sysex events are expanded into a small stack buffer and parsed for known GM/GS/XG macros before optionally invoking the driver's `sysex` callback.

## State and Persistence
State lives in `struct snd_midi_channel_set` and its channel array: note flags, controller values, program, pressure, pitchbend, GM RPN values, GS settings, MIDI mode, and drum-channel flags. It is in-memory only and owned by the driver that allocated the set.

## Dependencies and Integration Points
Uses public ALSA sequencer MIDI emulation types from `<sound/seq_midi_emul.h>`, asoundef controller constants, and `snd_seq_expand_var_event()` for sysex payloads. Hardware synth drivers can route sequencer events through this layer to implement MIDI behavior without duplicating common controller logic.

## Risks
The sysex parser expands into a 64-byte stack buffer, so longer sysex messages are ignored by this emulation layer. Channel set allocation does not initialize every top-level field unless allocation succeeds, so callers should clear or set private data explicitly. Callback ordering around sustain/sostenuto affects stuck-note behavior.

## Test Signals
Good tests include note-on/off including velocity-zero note-on, sustain and sostenuto release sequences, all-notes/off and all-sounds/off, RPN pitch bend range/fine/coarse tuning, GS/XG sysex mode changes, and invalid channel/note filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_emul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_event.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_event.c

## Purpose
`seq_midi_event.c` converts between raw MIDI 1.0 byte streams and ALSA sequencer events. It implements byte-by-byte MIDI command parsing, running-status-aware decoding back to bytes, sysex buffering, and special handling for 14-bit controls and RPN/NRPN events.

## Important APIs, Types, and Functions
- `snd_midi_event_new()` and `snd_midi_event_free()` allocate/free parser state.
- `snd_midi_event_reset_encode()` resets byte-to-event parser state; `snd_midi_event_reset_decode()` resets running-status output state.
- `snd_midi_event_no_status()` disables running status when callers need explicit status bytes.
- `snd_midi_event_encode_byte()` consumes one raw MIDI byte and reports when a complete sequencer event is ready.
- `snd_midi_event_decode()` converts one sequencer event into raw MIDI bytes.
- Static `status_event[]` maps MIDI status families to sequencer event types, payload lengths, and encode/decode helpers.
- Static `extra_event[]` handles `CONTROL14`, `NONREGPARAM`, and `REGPARAM` sequencer events.

## Control Flow
Encoding treats realtime bytes (`>= 0xf8`) as immediate fixed-length events. Other status bytes reset parser state and determine expected data length. Data bytes either complete the current command, extend sysex, or use running status. Sysex emits a variable-length event when an end marker is seen or the parser buffer fills.

Decoding searches standard and extra event tables, composes the appropriate status byte, and either expands sysex with `snd_seq_expand_var_event()` or emits fixed byte packets. Running status is preserved in `dev->lastcmd` unless system messages or `nostat` force status bytes.

## State and Persistence
Parser state is in `struct snd_midi_event`: buffer pointer/size, `lastcmd`, current parser type, queued length, read offset, `nostat`, and a spinlock. State persists per parser instance, usually per MIDI port or rawmidi file.

## Dependencies and Integration Points
The file is exported to many ALSA MIDI bridges: `seq_midi.c`, `seq_virmidi.c`, and drivers that need MIDI stream conversion. It relies on sequencer variable-event expansion for sysex and `<sound/asoundef.h>` constants for status/control values.

## Risks
Parser buffer size determines sysex chunking; size zero is acceptable for decoders but unsafe for byte encoding if used incorrectly. Running status state is shared per parser, so callers must not reuse one parser for independent streams without locking/resetting. Invalid or unsupported events return `-ENOENT` or are silently skipped depending on path.

## Test Signals
Exercise every status family, realtime interleaving, running status, forced no-status output, sysex chunk and end behavior, 14-bit control output, RPN/NRPN output, invalid format rejection, and concurrent encode/decode reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_midi_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ports.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ports.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.c

## Purpose
`seq_prioq.c` implements the sequencer priority queue used by timing queues. It orders event cells by tick or real-time timestamp, preserves FIFO order for equal timestamps unless priority is requested, and removes queued cells by client or flush criteria.

## Important APIs, Types, and Functions
- `snd_seq_prioq_new()` and `snd_seq_prioq_delete()` manage queue lifecycle.
- `snd_seq_prioq_cell_in()` inserts an event cell in timestamp order.
- `snd_seq_prioq_cell_out()` pops the head only when no current time is provided or the head timestamp is ready.
- `snd_seq_prioq_avail()` reports number of queued cells.
- `snd_seq_prioq_leave()` removes events related to a client, optionally including all timestamped events.
- `snd_seq_prioq_remove_events()` removes events matching `snd_seq_remove_events` filters.

## Control Flow
Insertion first tries a fast tail append when the new cell is non-priority and timestamp is >= current tail. Otherwise it walks the linked list until it finds an earlier timestamp position or an equal timestamp with priority. Dequeue compares the head event timestamp against the current tick/time pointer. Removal walks the queue under lock, unlinks matching nodes into a temporary free list, then frees cells outside the queue lock.

## State and Persistence
The queue stores `head`, `tail`, `cells`, and a spinlock. It is purely in-memory and owns references to cells until dequeue/removal/free.

## Dependencies and Integration Points
Uses `seq_timer.h` timestamp comparison helpers and `seq_memory.h` cell ownership/freeing. `seq_queue.c` maintains separate tick and real-time priority queues per sequencer queue.

## Risks
The queue is an O(n) linked list; large scheduled-event workloads can make insertion expensive. The insertion loop contains a fixed count guard against list corruption. Tail update in removal must be correct when deleting the last node. Timestamp comparison assumes event flag type matches the queue it is in.

## Test Signals
Test sorted insertion, equal timestamp FIFO, priority insertion before equal timestamp events, dequeue readiness for tick and real time, client-leave removal, all remove-mode filters, and corruption-resistant behavior under heavy queue sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.h

## Purpose
`seq_prioq.h` declares the ALSA sequencer priority queue structure and operations. It is the internal interface between timer queues and event-cell storage.

## Important APIs, Types, and Functions
- `struct snd_seq_prioq` contains linked-list head/tail pointers, cell count, and a spinlock.
- Declares constructor/destructor, enqueue/dequeue, availability, client-leave cleanup, and remove-events APIs.

## Control Flow
Consumers create a priority queue, enqueue `snd_seq_event_cell` objects, periodically dequeue ready cells based on the current timer value, and remove cells on client departure or explicit flush.

## State and Persistence
State is transient and cell-backed. The priority queue does not allocate events itself; it only owns cell links while queued.

## Dependencies and Integration Points
Includes `seq_memory.h`. Used directly by `seq_queue.c` for separate tick and real-time queues.

## Risks
The API gives direct cell pointers, so ownership transfer must be clear: enqueue transfers ownership to the prioq; dequeue transfers ownership to the caller; removal frees internally.

## Test Signals
Compile-time include coverage plus queue lifecycle tests that ensure all queued cells are freed by `snd_seq_prioq_delete()` and no cells leak across remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_queue.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_queue.c

## Purpose
`seq_queue.c` manages ALSA sequencer timing queues. A timing queue owns separate tick and real-time priority queues plus a sequencer timer, accepts scheduled events, dispatches ready events, and handles queue-control events such as start, stop, tempo, position, and skew.

## Important APIs, Types, and Functions
- `snd_seq_queue_alloc()`, `snd_seq_queue_delete()`, and `snd_seq_queues_delete()` manage queue lifecycle.
- `queueptr()` returns a referenced queue pointer; `queuefree()` releases it via use lock.
- `snd_seq_enqueue_event()` schedules an event cell onto the destination queue.
- `snd_seq_check_queue()` dispatches ready tick/time events in bounded batches.
- `snd_seq_queue_use()`, `snd_seq_queue_is_used()`, and `snd_seq_queue_client_leave()` track clients using queues and cleanup on client exit.
- `snd_seq_queue_timer_open()`, `snd_seq_queue_timer_close()`, `snd_seq_queue_timer_set_tempo()`, and `snd_seq_queue_set_owner()` expose queue control.
- `snd_seq_control_queue()` receives system timer-port events and applies queue operations.

## Control Flow
Queue allocation creates a `snd_seq_queue`, two priority queues, and a timer, marks the creating client as a user, takes one use lock reference for the caller, and inserts the queue into a global array. Enqueue converts relative timestamps to absolute using the queue timer state, inserts into tick or real-time prioq, and immediately checks for ready events.

`snd_seq_check_queue()` prevents reentrant queue scans with `check_lock`, dispatches ready tick events then real-time events, and stops after `MAX_CELL_PROCESSES_IN_QUEUE` to avoid monopolizing CPU. If another thread requested a check while blocked, it loops again before releasing the block.

Queue-control events are permission-checked by owner/lock state. Start clears timestamped events from the controlling client, starts the timer, and broadcasts; continue/stop/tempo/position/skew update the timer and broadcast successful changes from the system timer port.

## State and Persistence
Global runtime state is `queue_list[]` and `num_queues`. Per-queue state includes owner/lock bits, client-use bitmap/count, timer, priority queues, name, info flags, and use locks. State is in-memory only and destroyed when queues are deleted or the sequencer exits.

## Dependencies and Integration Points
Uses event cells from `seq_memory.c`, priority queues from `seq_prioq.c`, timer operations from `seq_timer.c`, client dispatch from `seq_clientmgr`, system broadcast semantics, and proc reporting. Queue ids are referenced by sequencer events and user ioctls.

## Risks
Concurrency risk is high: global list locking, queue owner locking, timer mutex, check reentrancy, and use-lock lifetime must agree. `snd_seq_queues_delete()` deletes queues still present in `queue_list[]` without clearing the array in this file, so it is intended for final teardown. Client-leave paths must remove both owned queues and remaining events in non-owned queues.

## Test Signals
Test queue allocation limits, owner permission checks, relative timestamp conversion, timer control event effects, bounded dispatch under large ready queues, client leave cleanup, remove-events filters across both prioqs, and proc queue reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_queue.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_queue.h

## Purpose
`seq_queue.h` defines the sequencer queue structure and declares queue management, scheduling, access-control, timer, and control-event APIs.

## Important APIs, Types, and Functions
- `struct snd_seq_queue` contains queue id/name, tick/time prioqs, timer, owner and lock flags, reentrancy flags, client bitmap/count, timer mutex, owner/check spinlocks, and use lock.
- Declares lifecycle (`snd_seq_queue_alloc/delete`, `snd_seq_queues_delete`), enqueue/check, remove, lookup, access, timer, use, and system control APIs.
- `DEFINE_FREE(snd_seq_queue, ...)` enables scoped automatic queue reference release.

## Control Flow
Callers obtain queues through `queueptr()`, operate while a use-lock reference is held, and release through `queuefree()` or cleanup attributes. Events flow from client manager into `snd_seq_enqueue_event()`, then into prioqs and eventually dispatch by `snd_seq_check_queue()`.

## State and Persistence
Queue state is runtime-only. Client usage is represented by a bitmap over `SNDRV_SEQ_MAX_CLIENTS` plus a count, with timer open/close driven by whether at least one client uses the queue.

## Dependencies and Integration Points
Includes memory, priority queue, timer, seq lock, interrupt, list, and bitops headers. Used by queue users throughout the sequencer core, notably `seq_timer.c` callback dispatch and `seq_system.c` timer-control port.

## Risks
The header exposes many internal fields, so accidental direct mutation can bypass locking. Queue lookup/refcount discipline is essential to avoid use-after-free during timer interrupts or client teardown.

## Test Signals
Build tests should validate cleanup attribute availability. Runtime tests should confirm use bitmap/count transitions, timer open/close transitions, and queue pointer reference release under concurrent deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_system.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_system.c

## Purpose
`seq_system.c` creates and manages the ALSA sequencer internal "System" client. It provides the timer-control port used to manipulate queues and the announce port used to broadcast client/port lifecycle and UMP notifications.

## Important APIs, Types, and Functions
- `snd_seq_system_client_init()` creates the kernel system client and its Timer and Announce ports.
- `snd_seq_system_client_done()` deletes the system client.
- `snd_seq_system_broadcast()` broadcasts fixed system events to announce subscribers.
- `snd_seq_system_notify()` sends a system event directly to a client/port.
- `event_input_timer()` forwards timer-port events to `snd_seq_control_queue()`.
- `sys_announce_subscribe()` and `sys_announce_unsubscribe()` track announce subscription count.

## Control Flow
Initialization creates a kernel client named `System`, then creates a fixed Timer port with write/read/subscription capabilities and an input callback to queue control. It creates a fixed Announce port with read/subscription capabilities and subscription callbacks. Broadcasts are skipped unless the announce port exists and at least one subscriber is present.

## State and Persistence
Static runtime state stores `sysclient`, `announce_port`, and `announce_subscribed`. There is no persistent state. On teardown `sysclient` and `announce_port` are reset before deleting the kernel client.

## Dependencies and Integration Points
Depends on sequencer kernel client APIs, queue control (`seq_queue.c`), and timer event semantics. Client and port lifecycle macros in `seq_system.h` are used by client/port management and UMP endpoint code.

## Risks
`announce_subscribed` is a plain integer and relies on sequencer subscription serialization. Broadcast events are dropped when no subscribers exist, which is intended but relevant for consumers expecting history. Timer-control input must validate queue permissions downstream.

## Test Signals
Test system client initialization failure unwind, timer port queue-control routing, announce subscribe/unsubscribe counts, lifecycle broadcasts to subscribers, direct system notification, and UMP change notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_system.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_system.h

## Purpose
`seq_system.h` declares the system client interfaces and provides convenience macros for broadcasting ALSA sequencer client, port, and UMP lifecycle events.

## Important APIs, Types, and Functions
- `snd_seq_system_broadcast()` and `snd_seq_system_notify()` are the exported event paths.
- `notify_event()` wraps normal broadcast calls.
- `snd_seq_system_ump_notify()` reuses the broadcast layout for UMP endpoint/function-block notifications.
- Macros such as `snd_seq_system_client_ev_client_start()` and `snd_seq_system_client_ev_port_exit()` encode standard lifecycle event types.
- Declares system client init/done functions.

## Control Flow
Callers use macros when clients or ports start, exit, or change. UMP code calls the inline notification helper with a client id and block id. The implementation in `seq_system.c` fills the event header and dispatches via the system client.

## State and Persistence
The header holds no state; it exposes the notification contract.

## Dependencies and Integration Points
Includes `<sound/seq_kernel.h>`. Used by client manager, port management, UMP client code, and any sequencer component emitting lifecycle notifications.

## Risks
The UMP helper relies on binary compatibility between `struct snd_seq_ev_ump_notify` and `struct snd_seq_addr` fields used by the broadcast path. Macro use hides the atomic flag, always using non-atomic broadcasts for normal lifecycle events.

## Test Signals
Compile-time layout assumptions for UMP notifications and runtime tests that lifecycle macros reach announce-port subscribers with the expected event type/address fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_timer.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_timer.c

## Purpose
`seq_timer.c` implements the timer backing each ALSA sequencer queue. It tracks musical tick position, real time, tempo, PPQ, skew, and the underlying ALSA timer instance, and invokes queue checks from timer interrupts.

## Important APIs, Types, and Functions
- `snd_seq_timer_new()` and `snd_seq_timer_delete()` manage timer object lifetime.
- `snd_seq_timer_defaults()` sets tempo/PPQ/timer id defaults.
- `snd_seq_timer_reset()`, `snd_seq_timer_start()`, `snd_seq_timer_continue()`, and `snd_seq_timer_stop()` control position and running state.
- `snd_seq_timer_set_tempo()`, `snd_seq_timer_set_tempo_ppq()`, `snd_seq_timer_set_position_tick()`, `snd_seq_timer_set_position_time()`, and `snd_seq_timer_set_skew()` update timing parameters.
- `snd_seq_timer_open()` and `snd_seq_timer_close()` bind/unbind an ALSA timer instance.
- `snd_seq_timer_get_cur_time()` and `snd_seq_timer_get_cur_tick()` read current positions.

## Control Flow
Defaults set 96 PPQ, 500000 microseconds per quarter at base 1000, ALSA timer id from global defaults, and neutral skew. Opening creates a named timer instance, installs `snd_seq_timer_interrupt()` as callback, tries the configured ALSA timer, and falls back to the global system timer for non-slave failures.

On interrupt, the callback checks `running`, scales elapsed resolution by ticks and skew, increments real time, updates tick fraction/current tick based on tempo resolution, records `last_update`, then calls `snd_seq_check_queue()` in atomic context. Start resets position, initializes timer ticks from desired frequency and hardware resolution, starts the ALSA timer, and marks running.

## State and Persistence
State is in `struct snd_seq_timer`: running/initialized bits, tempo, PPQ, current time, tick state, ALSA timer id/instance, tick period, preferred resolution, skew, tempo base, last update time, and spinlock. It is not persistent.

## Dependencies and Integration Points
Depends on ALSA timer core and `seq_queue.c` for dispatch. Queue control events in `seq_queue.c` call these APIs. Proc reporting reads timer details for active queues.

## Risks
Changing PPQ is refused while running to avoid song-position discontinuity. Timer instance open/close and running state require lock discipline; misuse can race callback execution. Frequency is clamped to 10..6250 Hz. Skew only accepts the 0x10000 base.

## Test Signals
Test default values, fallback timer open, start/continue/stop behavior, tick increment at known resolution/tempo, skew scaling, PPQ change rejection while running, current-time interpolation, and queue dispatch from interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_timer.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_timer.h

## Purpose
`seq_timer.h` defines sequencer timer state, inline timestamp math helpers, timer API declarations, and default timer configuration externs.

## Important APIs, Types, and Functions
- `struct snd_seq_timer_tick` tracks current tick, nanoseconds per tick, and fractional nanoseconds.
- `struct snd_seq_timer` stores running state, tempo, PPQ, current time, ALSA timer id/instance, tick count, skew, tempo base, and lock.
- `snd_seq_timer_update_tick()` advances tick state from elapsed nanoseconds.
- `snd_seq_compare_tick_time()` and `snd_seq_compare_real_time()` compare event timestamps.
- `snd_seq_sanity_real_time()`, `snd_seq_inc_real_time()`, and `snd_seq_inc_time_nsec()` normalize/increment sequencer real time.
- Declares timer lifecycle/control/read APIs and default timer globals.

## Control Flow
Queues and priority queues use the inline compare helpers to decide event readiness and ordering. Timer implementation uses update helpers to convert real elapsed time into musical ticks.

## State and Persistence
The header defines runtime-only timer state. Default timer parameters are external globals configured elsewhere in the sequencer module.

## Dependencies and Integration Points
Includes `<sound/timer.h>` and `<sound/seq_kernel.h>`. Used by `seq_timer.c`, `seq_queue.c`, and `seq_prioq.c`.

## Risks
Inline compare helpers return boolean-like "a >= b" values, not three-way comparisons. Nanosecond normalization loops only handles overflow, not negative values. Callers must hold appropriate locks when directly accessing mutable timer fields.

## Test Signals
Unit-level tests for tick fraction rollover, real-time normalization, timestamp comparisons, and conversion from tempo/PPQ to tick resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_client.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.c

## Purpose
`seq_ump_convert.c` converts events between UMP sequencer clients and legacy ALSA sequencer clients, and between MIDI 1.0 and MIDI 2.0 UMP channel voice formats. It handles value scaling, group filtering/rewriting, sysex7 packetization, bank-select carry state, and RPN/NRPN aggregation.

## Important APIs, Types, and Functions
- `snd_seq_deliver_from_ump()` receives a UMP event and delivers it to a UMP or legacy destination, converting protocol/format as needed.
- `snd_seq_deliver_to_ump()` converts a legacy sequencer event to UMP MIDI 1.0, UMP MIDI 2.0, or sysex7 UMP packets for a UMP destination.
- `snd_seq_ump_group_port()` returns the 1-based UMP group port for a UMP event or `-1`.
- Scaling helpers convert 7/14/16/32-bit MIDI value ranges.
- `cvt_ump_midi1_to_event()`, `cvt_ump_midi2_to_event()`, and `cvt_ump_system_to_event()` produce legacy events from UMP packets.
- `cvt_ump_midi1_to_midi2()` and `cvt_ump_midi2_to_midi1()` adapt raw UMP channel voice packets between MIDI versions.
- `cvt_sysex_to_ump()` and `cvt_ump_sysex7_to_event()` convert sysex byte streams and UMP data packets.

## Control Flow
For UMP-source delivery, variable events are skipped, destination group filters are applied, and the UMP message type determines the conversion. UMP destinations receive packet copies, protocol-adapted MIDI1/MIDI2 packets, or group-rewritten packets when a destination port is tied to a specific group. Legacy destinations receive converted sequencer events; MIDI 2 program-with-bank can emit two legacy events.

For legacy-to-UMP delivery, destination group filters are applied first. Sysex events are expanded chunk by chunk into UMP sysex7 packets, stripping start/end markers and setting single/start/continue/end status. Non-sysex events are looked up in `seq_ev_ump_encoders[]` and converted to MIDI 1.0 or MIDI 2.0 UMP depending on destination client protocol and port MIDI1 flag.

MIDI 2 conversion keeps per-port/per-channel state in `dest_port->midi2_bank[]` to combine bank select and RPN/NRPN controller sequences into richer MIDI 2 messages.

## State and Persistence
The file's own state is static tables only. Persistent conversion carry state is stored in destination port `midi2_bank[]` fields for bank select, RPN/NRPN selection, and data entry until flushed or consumed.

## Dependencies and Integration Points
Depends on UMP message helpers from `<sound/ump.h>` and `<sound/ump_msg.h>`, sequencer client/port internals, and `__snd_seq_deliver_single_event()`. It is used by the client manager delivery path when UMP and non-UMP clients interoperate.

## Risks
Protocol conversion is lossy when downscaling MIDI 2.0 high-resolution values to legacy/MIDI1 ranges. Sysex7 conversion currently handles 7-bit sysex packets, not arbitrary UMP data formats. Bank/RPN carry state can be affected by interleaved controller streams on the same destination port/channel. Group filter bit semantics are 1-based for groups plus a groupless bit, so off-by-one errors are easy.

## Test Signals
Test every event mapping in `seq_ev_ump_encoders[]`, value scaling boundaries, MIDI2 note-on velocity zero correction, MIDI2 program bank-valid splitting, MIDI1 bank-select-to-MIDI2 program carry, RPN/NRPN aggregation and reset, sysex start/continue/end/single packetization, group rewriting, group filtering, and UMP-to-legacy multi-event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.h -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.h

## Purpose
`seq_ump_convert.h` declares the internal UMP conversion entry points used by the sequencer client delivery code.

## Important APIs, Types, and Functions
- `snd_seq_deliver_from_ump()` converts/delivers UMP-source events to a destination client/port.
- `snd_seq_deliver_to_ump()` converts/delivers legacy sequencer events to UMP destination clients.
- `snd_seq_ump_group_port()` extracts a 1-based group port from UMP events.

## Control Flow
The client manager can choose the appropriate delivery helper based on source/destination client capabilities. Both helpers receive source client, destination client, destination port, event pointer, atomic context flag, and hop count.

## State and Persistence
The header defines no state. Conversion state lives in destination ports and implementation-local stack variables.

## Dependencies and Integration Points
Includes `seq_clientmgr.h` and `seq_ports.h` to access client/port internals. Used only when sequencer UMP support is compiled.

## Risks
These helpers depend on internal client/port layouts and on the caller passing correctly referenced destination objects. Incorrect source/destination classification can skip conversion or deliver incompatible packets.

## Test Signals
Compile delivery paths with UMP enabled and verify both UMP-to-legacy and legacy-to-UMP clients route through the declared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_virmidi.c -->
# sources/distributed-fs/ceph-client/sound/core/seq/seq_virmidi.c

## Purpose
`seq_virmidi.c` implements virtual rawmidi devices backed by ALSA sequencer ports. A normal rawmidi device file can be connected to arbitrary sequencer clients, allowing raw MIDI applications and sequencer applications to interoperate.

## Important APIs, Types, and Functions
- `snd_virmidi_new()` creates a rawmidi device with virtual MIDI global and stream ops.
- `snd_virmidi_dev_attach_seq()` creates the backing sequencer kernel client and port in dispatch mode.
- `snd_virmidi_event_input()` receives sequencer events for the virmidi port.
- `snd_virmidi_dev_receive_event()` decodes sequencer events to raw MIDI bytes for each open input file.
- `snd_vmidi_output_work()` parses rawmidi output bytes into sequencer events and dispatches them.
- Rawmidi stream ops open/close/trigger/drain allocate per-file parser state and manage work.
- Subscription/use callbacks gate output-to-rawmidi and rawmidi-to-sequencer directions with module references.

## Control Flow
Device creation allocates a duplex rawmidi with 16 input and 16 output substreams, initializes a `snd_virmidi_dev`, and installs global/stream ops. On registration in dispatch mode, a kernel sequencer client and duplex software port are created. Rawmidi input opens allocate a `snd_virmidi`, create a decode parser, and add it to the device file list. Rawmidi output opens allocate a parser and work item.

Sequencer-to-rawmidi delivery iterates open input files under either spin/read lock or rwsem depending on atomic context, decodes events to MIDI bytes, and feeds each triggered substream. Rawmidi-to-sequencer delivery runs in a high-priority workqueue, reads bytes while triggered, encodes complete sequencer events, and dispatches them.

## State and Persistence
State is runtime-only in `snd_virmidi_dev` and per-open `snd_virmidi` objects. The device tracks file list, client/port, flags for subscription/use, mode, and locks. Each open file owns its parser, trigger flag, and pending event/work.

## Dependencies and Integration Points
Depends on rawmidi core, sequencer kernel clients, MIDI event parser, variable-event dump helpers, and ALSA card module refcounts. It can operate in dispatch mode with its own port or attach mode against an existing client/port.

## Risks
File-list locking switches between atomic and sleepable modes; mistakes could deadlock or race close. Dispatch mode drops rawmidi output unless the port is subscribed. Workqueue processing must be canceled on close to avoid use-after-free. Subscription/use flags are coarse per device, not per open file.

## Test Signals
Test multiple rawmidi opens with independent input buffers, trigger on/off behavior, dispatch mode with and without subscriptions, sysex delivery, workqueue drain/close ordering, attach mode validation, module refcount on subscribe/use, and duplex routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq/seq_virmidi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq_device.c -->
# sources/distributed-fs/ceph-client/sound/core/seq_device.c

## Purpose
`seq_device.c` implements the ALSA sequencer device bus. It lets low-level card drivers register sequencer device entries, and lets sequencer drivers bind to those entries by id/argsize, with optional module autoloading and proc reporting.

## Important APIs, Types, and Functions
- `snd_seq_bus_type` defines the `snd_seq` bus with match/probe/remove callbacks.
- `snd_seq_device_new()` creates a `struct snd_seq_device`, initializes its `struct device`, and registers it as an ALSA card device.
- `__snd_seq_driver_register()` and `snd_seq_driver_unregister()` register/unregister sequencer drivers.
- `snd_seq_autoload_init()`, `snd_seq_autoload_exit()`, and `snd_seq_device_load_drivers()` control driver autoloading.
- Device ops `snd_seq_device_dev_register()`, `snd_seq_device_dev_disconnect()`, and `snd_seq_device_dev_free()` bridge ALSA card device lifecycle to Linux device core.
- Proc helper prints `snd-id,loaded/empty,flag` rows.

## Control Flow
At subsystem init the `snd_seq` bus is registered and the optional proc entry is created. Card drivers call `snd_seq_device_new()` to create bus devices with id and argsize. `snd_seq_bus_match()` binds only drivers with matching id and argsize. Registration adds the Linux device and queues autoload if no driver is bound. Autoload work scans bus devices and requests modules named `snd-<id>` while guarded against reentrance by `snd_seq_in_init`.

## State and Persistence
State is in Linux device core, the bus registry, optional proc entry, and autoload work/atomic. Sequencer devices are card-owned runtime objects; no persistent storage is involved.

## Dependencies and Integration Points
Depends on Linux driver core, ALSA card device management, proc info, module loading, and `sound/seq_device.h`. MIDI synth and UMP clients register as `snd_seq_driver` instances consumed by this bus.

## Risks
Autoloading is asynchronous and gated by `snd_seq_in_init`; incorrect transitions can miss or duplicate requests. `private_free` runs before `put_device()` on free. Match requires exact argsize, so driver/device metadata mismatches prevent binding.

## Test Signals
Test bus registration/unregistration, device creation per card, driver match by id/argsize, probe/remove callbacks, autoload work with modules enabled, proc driver listing, and cleanup when card devices disconnect before drivers bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/seq_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/sound.c -->
# sources/distributed-fs/ceph-client/sound/core/sound.c

## Purpose
`sound.c` is the ALSA native core character-device registry. It registers the ALSA major, handles `/dev/snd/*` opens by minor lookup and fops replacement, supports module autoload for card/control/global devices, and provides device registration/unregistration for ALSA subsystems.

## Important APIs, Types, and Functions
- `snd_request_card()` requests `snd-card-N` modules for autoloadable cards.
- `snd_lookup_minor_data()` looks up registered minor private data and takes a card device reference.
- `snd_register_device()` assigns a native ALSA minor, sets device `devt`, calls `device_add()`, and stores a `snd_minor` registry entry.
- `snd_unregister_device()` removes a registered device and frees its minor entry.
- `snd_open()` is the major-device open trampoline that autoloads missing devices and replaces file ops with the real device operations.
- `snd_minor_info_init()` creates optional `/proc/asound/devices` style native-device reporting.
- `alsa_sound_init()` and `alsa_sound_exit()` register/unregister the major, info core, and debugfs root.

## Control Flow
Subsystem init stores module parameters in exported globals, registers the char major with `snd_fops`, initializes ALSA info, and creates debugfs if enabled. On open, `snd_open()` indexes `snd_minors[]` under `sound_mutex`; if absent and modules are enabled it temporarily drops the mutex and requests either a card module or global sequencer/timer module, then retries lookup. The open path grabs the real file operations, replaces fops, and invokes the real open.

Device registration allocates a `snd_minor`, finds a free static or dynamic minor, sets `device->devt`, calls `device_add()`, then publishes the registry entry. Unregistration finds the matching `struct device`, clears the registry entry, calls `device_del()`, and frees metadata.

## State and Persistence
Global runtime state includes `snd_major`, `snd_ecards_limit`, optional `sound_debugfs_root`, and `snd_minors[]` protected by `sound_mutex`. There is no persistent storage.

## Dependencies and Integration Points
Depends on Linux char device and device core, module loading, ALSA card refcount helpers, minor-number macros, ALSA info, controls, and debugfs. All native ALSA device classes register through this file.

## Risks
Open-time autoload deliberately drops `sound_mutex`; the subsequent minor entry can appear/disappear and must be rechecked. `snd_lookup_minor_data()` transfers a card reference expectation to callers. Static minor mapping must match ABI. `device_add()` occurs before publishing in `snd_minors[]`, so failure cleanup must free only unpublished state.

## Test Signals
Test static and dynamic minor allocation, duplicate minor failure, open fops replacement, autoload for card/control and global seq/timer minors, lookup reference behavior, unregister by device pointer, proc devices output, and module init/exit failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/sound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/sound_kunit.c -->
# sources/distributed-fs/ceph-client/sound/core/sound_kunit.c

## Purpose
`sound_kunit.c` is a KUnit suite for selected ALSA sound-core utility functions. It verifies PCM format metadata/silence behavior, playback/capture availability arithmetic, card id sanitization, PCM format names, and component-string assembly.

## Important APIs, Types, and Functions
- `struct snd_format_test_data` stores expected PCM format properties and silence bytes.
- `struct avail_test_data` stores PCM ring-buffer pointer scenarios.
- `valid_fmt[]` enumerates many signed/unsigned/endian/packed/compressed/DSD formats.
- Tests cover `snd_pcm_format_physical_width()`, `snd_pcm_format_width()`, `snd_pcm_format_signed()`, `snd_pcm_format_unsigned()`, endian helpers, `snd_pcm_format_set_silence()`, `snd_pcm_playback_avail()`, `snd_pcm_capture_avail()`, `snd_card_set_id()`, `snd_pcm_format_name()`, and `snd_component_add()`.
- `sound_utils_suite` registers the KUnit suite as `sound-core-test`.

## Control Flow
Format tests iterate `valid_fmt[]` and compare helper returns to expected metadata, including invalid format cases. Silence tests allocate a buffer and verify repeated silence patterns across several sample counts. Availability tests allocate a minimal `snd_pcm_runtime` with status/control substructures and verify boundary wrap behavior. Card/component tests use KUnit-allocated `snd_card` objects.

## State and Persistence
No persistent state. KUnit allocates per-test objects with test lifetime. Static test vectors define expectations.

## Dependencies and Integration Points
Depends on KUnit, `<sound/core.h>`, and `<sound/pcm.h>`. It exercises utility functions implemented elsewhere in ALSA core/PCM code, not the sequencer code in this subset.

## Risks
Expected format tables can become stale when new PCM formats or helper semantics change. Some invalid-format tests in signedness call width helpers for invalid cases, so they may not fully assert the signedness invalid path. Availability tests use hand-built runtime structures and cover only selected pointer cases.

## Test Signals
Run with KUnit enabled and confirm `sound-core-test` passes. Add cases for new PCM formats, larger silence counts, more boundary wrap scenarios, duplicate component handling, and additional card id sanitization edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/sound_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/sound_oss.c -->
# sources/distributed-fs/ceph-client/sound/core/sound_oss.c

## Purpose
`sound_oss.c` implements the ALSA OSS-compatibility minor registry. It maps OSS device types to legacy OSS minor numbers, registers/unregisters sound special devices, exposes lookup with card references, and provides optional proc reporting.

## Important APIs, Types, and Functions
- `snd_lookup_oss_minor_data()` returns registered OSS private data for a minor/type and takes a card device reference.
- `snd_oss_kernel_minor()` maps OSS device type/card/device to the legacy minor number.
- `snd_register_oss_device()` allocates a `snd_minor`, stores it in `snd_oss_minors[]`, registers the primary sound special device, and for PCM/MIDI registers alternate OSS aliases.
- `snd_unregister_oss_device()` clears primary/alias registry entries, unregisters sound special devices, and frees the metadata.
- `snd_minor_info_oss_init()` creates optional proc reporting of OSS devices.

## Control Flow
Registration first computes the kernel minor, silently ignores cards outside the OSS device-card range, allocates metadata, stores the primary minor under `sound_oss_mutex`, determines any alias minor (`audio`, `dmmidi`, or `dmmidi1`), and calls `register_sound_special_device()` for primary and alias. On registration failure it unregisters any successful special devices, clears the registry, and frees metadata.

Unregistration computes the same primary and alias minors, clears registry entries while holding the mutex, then calls `unregister_sound_special()` outside the mutex because unregister can trigger card release paths.

## State and Persistence
Global runtime state is `snd_oss_minors[256]` protected by `sound_oss_mutex`. Entries may be shared by a primary minor and alias minor. No persistent storage exists.

## Dependencies and Integration Points
Depends on ALSA core/card structures, OSS minor macros, Linux sound special device registration, and proc info. OSS PCM, mixer, MIDI, sequencer, and sndstat compatibility layers register through this file.

## Risks
Primary and alias minors share one `snd_minor`, so cleanup must avoid double-free. The registry entry is assigned before special-device registration completes, so failure paths must clear it. Lookup returns private data with an implied card reference contract. Minor mapping is ABI-sensitive.

## Test Signals
Test every OSS device type mapping, invalid card/device rejection, alias registration for PCM/MIDI, partial registration failure unwind, unregister outside-lock behavior, lookup type filtering/refcounting, high card number silent ignore, and proc devices output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/core/sound_oss.c -->
