# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_ca_en50221.c

## Purpose

`dvb_ca_en50221.c` implements the DVB Common Interface EN50221 core used by adapter drivers that expose Conditional Access Module slots. It owns slot probing, CAM attribute parsing, host/CAM link negotiation, control-interface packet transfer, the CA character-device file operations, and exported interrupt entry points that low-level CI drivers call when CAM insertion/removal/readiness/data events occur.

The file bridges a hardware-specific `struct dvb_ca_en50221` callback table to the DVB userspace CA API. It translates PC Card/CI slot status into `CA_GET_CAP`, `CA_GET_SLOT_INFO`, `CA_RESET`, `read`, `write`, and `poll` behavior on the registered `DVB_DEVICE_CA` node.

## Important APIs, Types, And Functions

`struct dvb_ca_slot` is per-slot runtime state. It tracks `slot_state`, `slot_lock`, CAM change counters, attribute-memory config values, negotiated link buffer size, DA IRQ support, the per-slot `dvb_ringbuffer` receive queue, and state-machine timeout.

`struct dvb_ca_private` is per-interface state behind `pubca->private`. It holds the DVB device, flags, slot array, userspace wait queue, monitor thread, open/wakeup bits, next slot for round-robin reads, ioctl/remove mutexes, and an `exit` flag protected by `remove_mutex`.

Exported driver-facing APIs are `dvb_ca_en50221_init`, `dvb_ca_en50221_release`, `dvb_ca_en50221_camchange_irq`, `dvb_ca_en50221_camready_irq`, and `dvb_ca_en50221_frda_irq`. The init path registers a CA device and starts `kdvb-ca-%i:%i`; release blocks opens, waits for active users to drain, stops the thread, shuts slots down, removes the DVB device, and drops the private kref.

Core protocol helpers include `dvb_ca_en50221_read_tuple`, `dvb_ca_en50221_parse_attributes`, `dvb_ca_en50221_set_configoption`, `dvb_ca_en50221_link_init`, `dvb_ca_en50221_read_data`, and `dvb_ca_en50221_write_data`. The ioctl/read/write paths are `dvb_ca_en50221_io_do_ioctl`, `dvb_ca_en50221_io_read`, `dvb_ca_en50221_io_write`, `dvb_ca_en50221_io_open`, `dvb_ca_en50221_io_release`, and `dvb_ca_en50221_io_poll`.

## Control Flow

Initialization allocates `dvb_ca_private`, allocates the slot table, registers a `DVB_DEVICE_CA`, initializes slot locks and slot state to `DVB_CA_SLOTSTATE_NONE`, then launches a monitor kthread. The kthread recalculates its minimum delay across all slots, sleeps unless explicitly woken, and runs `dvb_ca_en50221_thread_state_machine` on every slot.

The slot state machine handles CAM changes first. In IRQ mode, `camchange_count` drives work; in polling mode, `poll_slot_status` detects present/changed/ready transitions. Removal shuts down the slot and wakes userspace. Insertion moves the slot through `UNINITIALISED -> WAITREADY -> VALIDATE -> WAITFR -> LINKINIT -> RUNNING`.

`VALIDATE` reads PC Card CIS tuples from attribute memory, verifies expected tuple order, extracts manufacturer/device/config metadata, requires the `DVB_CI_V1.00` marker and a `DVB_HOST`/`DVB_CI_MODULE` CFTABLE entry, writes the selected config option, and resets the CAM control interface. `WAITFR` waits for module-free status. `LINKINIT` reads the CAM link buffer size, chooses the smaller of CAM size and `HOST_LINK_BUF_SIZE`, writes it back to the CAM, allocates the receive ringbuffer if needed, enables TS output, and marks the slot running.

Once running and opened by userspace, the thread drains up to `MAX_RX_PACKETS_PER_ITERATION` packets from the CAM into the ringbuffer. Reads assemble link fragments with the same connection id until a last-fragment marker is found, prepend `{slot, connection_id}` to userspace, and dispose consumed packet records. Writes accept `{slot, connection_id, payload...}`, fragment payload into CAM link frames, retry `-EAGAIN` for up to half a second, and use `slot_lock` while writing to the physical interface.

## State And Persistence Behavior

All state is in memory. Slot state survives open/close while the interface exists; the monitor thread continues probing slots even when no CA fd is open, but running slots only drain CAM data while `ca->open` is true. Receive data is kept in per-slot `dvb_ringbuffer` storage allocated on first successful link init and freed when the private object is released.

Reference lifetime uses a private `kref` plus `dvb_device_get/put`. `open` obtains the low-level module owner and increments the CA private ref after successful `dvb_generic_open`; `release` clears `open`, releases the generic DVB device reference, drops the module owner, drops the private ref, and wakes removal if this was the last active user.

Synchronization is split by concern: `slot_lock` serializes hardware access for one CI slot, `ioctl_mutex` serializes CA ioctls, `remove_mutex` gates disconnect/open/release, ringbuffer internals provide pointer barriers, and wait queues drive userspace read/poll wakeups. `wakeup` is a plain flag with memory barriers around thread wake operations, not a locked field.

## Dependencies And Integration Points

The file depends on adapter callbacks in `struct dvb_ca_en50221`: slot polling/reset/shutdown/TS enable, attribute-memory reads/writes, CAM control register reads/writes, and optional direct `read_data`/`write_data`. It uses `dvb_register_device`, `dvb_remove_device`, `dvb_generic_open/release`, and `dvb_usercopy` from `dvbdev.c`, and packet ring helpers from `dvb_ringbuffer.c`.

Hardware drivers integrate by registering this core through `dvb_ca_en50221_init`, wiring their IRQ handlers to the exported `*_irq` functions, and providing stable callback behavior for slow CI accesses. Userspace sees `/dev/dvb/adapterX/caY` semantics through standard CA ioctls plus read/write message transfer.

## Risks And Edge Cases

Timeout and retry behavior is central. Slow CAMs can cycle through invalid, uninitialized, and link-init states; low-level callbacks that block for long periods directly affect the monitor thread delay. Single-buffer CAM interfaces are handled by refusing writes while DA/RE is set and waking the thread, but this creates retry-sensitive write behavior.

Input validation includes `array_index_nospec` for slot numbers, but read/write still depend on consistent slot state outside and inside locks; removal during writes returns `-EIO`. Ringbuffer pressure returns `-EAGAIN` to the monitor-thread read path, so userspace that stops draining can throttle CAM reads.

Attribute parsing is strict about tuple order, tuple lengths, the DVB CI version string, and CFTABLE contents. That is good for safety but can reject unusual CAMs. There is also visible source-integrity risk in this snapshot: the file contains an apparent extra closing brace after `dvb_ca_en50221_set_configoption` and an apparent duplicated comment terminator before `dvb_ca_en50221_io_write`; a build or parser pass should confirm whether this tree is expected to compile as-is.

## Test Signals

Useful coverage includes simulated callback drivers for poll-mode and IRQ-mode CAM insertion/removal; attribute-memory tuple fixtures for valid CAMs, unsupported CI versions, missing CFTABLE entries, malformed tuple lengths, and CAM removal during validation; link-init tests for negotiated buffer sizes and CAM size overflow; read tests for fragmented messages, round-robin slots, partial user buffers, and ringbuffer disposal; write tests for fragmentation, `-EAGAIN` retry, non-running slot rejection, oversized link frames, and removal mid-write.

Runtime signals include successful `DVB CAM detected and initialised successfully` logs, `CA_GET_SLOT_INFO` ready flags, wakeable `poll()` on completed last fragments, no lingering users during `dvb_ca_en50221_release`, and no ringbuffer corruption under concurrent CAM IRQs and userspace read/write.
