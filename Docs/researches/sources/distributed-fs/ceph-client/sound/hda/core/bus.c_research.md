# sources/distributed-fs/ceph-client/sound/hda/core/bus.c

## Purpose
`bus.c` implements generic HD-audio core bus setup, verb execution dispatch, unsolicited event queuing, codec list membership, optional aligned MMIO helpers, and codec-link power delegation.

## Important APIs, Types, and Functions
Exports include `snd_hdac_bus_init()`, `snd_hdac_bus_exit()`, `snd_hdac_bus_exec_verb()`, `snd_hdac_bus_exec_verb_unlocked()`, `snd_hdac_bus_queue_event()`, `snd_hdac_bus_add_device()`, `snd_hdac_bus_remove_device()`, optional `snd_hdac_aligned_read/write()`, and `snd_hdac_codec_link_up/down()`.

## Control Flow
Bus init zeroes the bus, assigns ops or defaults, initializes lists/work/locks/waitqueues, sets default DMA type, IRQ `-1`, and SDO striping limit. Verb execution serializes on `cmd_mutex`, sends commands, handles `-EAGAIN` by draining pending responses, and fetches responses when requested. Unsolicited events are queued from interrupt context and processed by `unsol_work`, which dispatches to the bound HDA driver’s `unsol_event`.

## State and Persistence Behavior
State includes codec/stream/hlink lists, address table, codec power bits, command locks, unsol ring pointers, and bus ops. Codec add/remove updates list membership, address table, power bits, and codec count; removal flushes pending unsolicited work.

## Dependencies and Integration Points
The file depends on `struct hdac_bus`, `hdac_device`, `hdac_driver`, default controller command ops, Linux workqueues/locks, and tracepoints. Controllers call bus init/exit; codecs join through device initialization.

## Risks
Unsolicited event queue is fixed-size and overwrites by ring pointer progression if producers outrun work processing. Driver callbacks run outside the spinlock but require the codec still be registered. Link-power ops may be overridden by extended bus implementations.

## Test Signals
Test bus initialization invariants, verb serialization and `-EAGAIN` recovery, unsolicited event dispatch to the correct codec/driver, codec address collision rejection, removal flushing, and aligned MMIO helpers on aligned-MMIO platforms.
