# Research: subset-b-004052

Grouped research for DVB core files under `sources/distributed-fs/ceph-client/drivers/media/dvb-core`. Each section preserves the original source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_ca_en50221.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_ca_en50221.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_demux.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_demux.c

## Purpose

`dvb_demux.c` implements the in-kernel DVB demux core. It manages demux users, frontends, TS feeds, section feeds, software TS packet filtering, section reconstruction, section filter matching, CRC checking, PES PID tracking, and memory-fronted demux writes. Adapter demux drivers embed `struct dvb_demux`, supply optional `start_feed`, `stop_feed`, `write_to_decoder`, `check_crc32`, and `memcopy` callbacks, then call `dvb_dmx_init` to expose the generic `struct dmx_demux` API.

## Important APIs, Types, And Functions

The exported entry points are `dvb_dmx_init`, `dvb_dmx_release`, `dvb_dmx_swfilter_packets`, `dvb_dmx_swfilter`, `dvb_dmx_swfilter_204`, and `dvb_dmx_swfilter_raw`. The init function allocates filter/feed arrays, initializes frontend and feed lists, installs default CRC and memcpy callbacks, and populates the `dmx_demux` vtable.

Software filtering is implemented by `dvb_dmx_swfilter_packet`, `_dvb_dmx_swfilter`, `find_next_packet`, and helpers for payload, PID, continuity, and speed checks. Section reconstruction uses `dvb_dmx_swfilter_section_packet`, `dvb_dmx_swfilter_section_copy_dump`, `dvb_dmx_swfilter_section_new`, `dvb_dmx_swfilter_section_feed`, and `dvb_dmx_swfilter_sectionfilter`.

Feed APIs are split between TS and section feeds. TS feed setup/start/stop/release flows through `dmx_ts_feed_set`, `dmx_ts_feed_start_filtering`, `dmx_ts_feed_stop_filtering`, `dvbdmx_allocate_ts_feed`, and `dvbdmx_release_ts_feed`. Section equivalents are `dmx_section_feed_set`, `dmx_section_feed_allocate_filter`, `prepare_secfilters`, `dmx_section_feed_start_filtering`, `dmx_section_feed_stop_filtering`, `dmx_section_feed_release_filter`, `dvbdmx_allocate_section_feed`, and `dvbdmx_release_section_feed`.

## Control Flow

TS input enters through either fixed-packet `dvb_dmx_swfilter_packets` or byte-stream `_dvb_dmx_swfilter`. The byte-stream path resynchronizes on 188-byte sync `0x47` or 204-byte Reed-Solomon packet marker `0xB8`, carries incomplete packets in `demux->tsbuf`, normalizes 204-byte packets to a 188-byte TS packet, and dispatches each packet under `demux->lock`.

`dvb_dmx_swfilter_packet` computes PID, optionally logs speed, handles TEI and continuity checking, sets buffer flags for matching feeds, and iterates `demux->feed_list`. Matching TS feeds either receive full packets, payload-only bytes, decoder writes, or DVR wildcard PID `0x2000` data. Matching section feeds reconstruct complete sections from payload units before invoking section callbacks.

Section reconstruction tracks `tsfeedp`, `secbufp`, `seclen`, CRC state, continuity counter, and whether PUSI was seen. PUSI splits payload into bytes before the next section and bytes after the new pointer boundary. Complete sections are length-checked, optionally CRC-checked, matched against all chained section filters using precomputed mask/mode arrays, delivered to `cb.sec`, then reset for the next section.

Feed allocation obtains an unused feed slot and sometimes an unused filter slot from vmalloc-backed arrays. Starting a feed calls the adapter's `start_feed`, then marks the feed filtering under the spinlock. Stopping calls `stop_feed`, clears filtering state, and moves the feed back to allocated/ready state. Release removes feeds from `feed_list`, frees filter state, clears PES reservations, and resets PID to `0xffff`.

## State And Persistence Behavior

`struct dvb_demux` owns all persistent in-memory state: users count, feed/filter arrays, frontend list, active frontend, active feed list, PES filter table and PID cache, TS resynchronization buffer, optional continuity counter storage, and counters for speed logging. There is no disk persistence.

`demux->mutex` protects high-level feed/frontend allocation and state transitions. `demux->lock` protects packet delivery, active feed list inspection, and filtering flags. Feed state moves through `DMX_STATE_FREE`, `DMX_STATE_ALLOCATED`, `DMX_STATE_READY`, and `DMX_STATE_GO`; callbacks are only supposed to receive data once filtering is active.

Section filter state is linked per feed via `dvb_demux_filter::next`. Filter masks are transformed at start time into `maskandmode`, `maskandnotmode`, and `doneq`, so runtime filtering can perform fast equality/inequality checks across `DVB_DEMUX_MASK_MAX`.

## Dependencies And Integration Points

The file depends on `media/dvb_demux.h`, the kernel CRC32 API, vmalloc allocation, user-copy helpers, spinlocks, mutexes, and `struct dmx_demux` contracts. It is used by demux device layers, DVR capture, DVB network decapsulation, and adapter hardware drivers that need a generic software filter in their interrupt/DMA receive path.

`dvbdmx_write` integrates memory frontends by copying user TS data into kernel memory and feeding it through `dvb_dmx_swfilter`. `add_frontend`, `connect_frontend`, and related methods integrate tuner/demux routing. `get_pes_pids` exposes cached PES PID assignments to callers.

## Risks And Edge Cases

The demux is sensitive to packet loss, TEI bits, continuity mismatches, PUSI boundaries, oversized sections, and bad pointer fields. It records buffer flags for downstream consumers, but callbacks need to interpret those flags correctly. If `dvb_demux_feed_err_pkts` is enabled, TEI-marked packets are still forwarded with flags; disabling it drops them.

Resource exhaustion returns `-EBUSY` when feed or filter arrays are full. PES decoder feeds reserve one `pes_type`, so duplicate decoder assignment returns `-EINVAL`. Release while filtering stops section feeds indirectly in `dmx_section_feed_release_filter`, but callers must respect the locking contract.

This snapshot has visible source-integrity concerns worth build-testing: `find_next_packet` contains a duplicated `break` indentation pattern, and `dmx_section_feed_start_filtering` appears to call `mutex_unlock(&dvbdmx->mutex)` twice on the no-filter error path. These are high-signal compile/static-analysis or review targets.

## Test Signals

Tests should feed clean and corrupted 188/204-byte packet streams, garbage before sync, split packets across calls, TEI packets with both `dvb_demux_feed_err_pkts` settings, continuity jumps, adaptation-only packets, payload-only TS feeds, wildcard DVR feeds, and section filters with positive and negative masks. Section tests should cover first-data-before-PUSI discard, pointer field boundaries, multiple sections in one TS payload, section padding, CRC pass/fail, and oversized section rejection.

Lifecycle tests should allocate all feeds/filters to confirm `-EBUSY`, start/stop TS and section feeds around adapter callback failures, release active section filters, connect/disconnect frontends, memory frontend `write`, and verify `dvb_dmx_release` frees all vmalloc-backed arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_demux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_frontend.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_frontend.c

## Purpose

`dvb_frontend.c` implements the DVB frontend character device and tuning core. It registers frontend devices, manages open/release lifetime, runs the frontend tuning thread, translates DVBv3 and DVBv5 ioctl/property APIs into `struct dtv_frontend_properties`, handles event delivery, supports hardware/software/custom tuning algorithms, coordinates multi-frontend sharing, and integrates optional media-controller source pipelines.

The file is the user-visible control plane for demodulator/tuner drivers. Individual frontend drivers provide `struct dvb_frontend_ops`; this core supplies stable `/dev/dvb/adapterX/frontendY` behavior and compatibility semantics.

## Important APIs, Types, And Functions

`struct dvb_frontend_private` stores the registered `dvb_device`, output legacy parameters, event ring, tuning semaphore, wait queue, kthread pointer, release timeout, status, tune flags, remembered tone/voltage, software zigzag state, and media pipeline state.

Exported lifecycle APIs are `dvb_register_frontend`, `dvb_unregister_frontend`, `dvb_frontend_detach`, `dvb_frontend_suspend`, `dvb_frontend_resume`, `dvb_frontend_reinitialise`, and `dvb_frontend_sleep_until`. File operations are `dvb_frontend_open`, `dvb_frontend_release`, `dvb_frontend_ioctl`, compat ioctl support, and `dvb_frontend_poll`.

Tuning flow is organized around `dvb_frontend_start`, `dvb_frontend_thread`, `dvb_frontend_stop`, `dtv_set_frontend`, `prepare_tuning_algo_parameters`, `dvb_frontend_swzigzag`, and `dvb_frontend_swzigzag_autotune`. Property translation and validation use `dvb_frontend_check_parameters`, `dvb_frontend_get_frequency_limits`, `dvb_frontend_get_stepsize`, `dvb_frontend_clear_cache`, `dtv_property_cache_sync`, `dtv_property_legacy_params_sync`, `dvbv3_set_delivery_system`, `dvbv5_set_delivery_system`, and `emulate_delivery_system`.

## Control Flow

Registration allocates frontend-private state, initializes krefs and wait queues, registers a `DVB_DEVICE_FRONTEND`, sets the initial delivery system from `ops.delsys[0]`, and clears the property cache to delivery-system defaults. The open path handles adapter multi-frontend sharing, optional TS bus acquisition, generic DVB open accounting, optional media-controller source enablement, and starts the tuning thread for writable opens. Read-only opens can monitor most status ioctls without taking control of tuning.

The tuning thread initializes the frontend/tuner, then loops with a freezable wait. It exits on kthread stop, device removal, or a configurable shutdown timeout after last writer close. On wake, it handles requested reinitialization, restores tone/voltage, and dispatches to the frontend algorithm. Hardware algorithms call `ops.tune`; software algorithms run the core zigzag scan; custom algorithms call `ops.search` when `DVBFE_ALGO_SEARCH_AGAIN` is set and track lock status.

`dtv_set_frontend` validates frequency and symbol-rate ranges, syncs output DVBv3 parameters, derives bandwidth for systems that do not provide it directly, optionally forces auto inversion, normalizes low-priority FEC for non-hierarchical tuning, prepares algorithm parameters, sets `FESTATE_RETUNE`, clears old events, pushes an initial status-zero event, and wakes the thread. Software zigzag then cycles drift and inversion combinations until lock, switches from fast to slow search after wrapping, and records lock/lost-lock events.

The ioctl handler accepts batched DVBv5 `FE_SET_PROPERTY`/`FE_GET_PROPERTY`, legacy `FE_SET_FRONTEND`/`FE_GET_FRONTEND`, status/statistics reads, DiSEqC commands, tone/voltage controls, high-LNB voltage, tune mode, and event reads. `dvb_frontend_do_ioctl` serializes most operations with `fepriv->sem` and rejects write-affecting ioctls from read-only file descriptors.

## State And Persistence Behavior

Frontend state is volatile and held in `fe->dtv_property_cache`, `fepriv->state`, `fepriv->status`, event ring indices, the tuning thread pointer, and remembered tone/voltage. The property cache persists across ioctls and is reset by `DTV_CLEAR`, registration, or delivery-system changes. Tuning status is exposed asynchronously through the event ring and synchronously through status/statistics ioctls.

Lifetime is kref-based. Registration establishes references for unregister and detach; open obtains another reference; release drops it. `dvb_frontend_put` invokes detach before kref drop when relevant. Thread state is protected by `fepriv->sem`, wait queues, memory barriers around `fe->exit`, and the global `frontend_mutex` for registration/unregistration.

Multi-frontend sharing uses `adapter->mfe_lock`, `adapter->mfe_dvbdev`, `mfe_shared`, and a wait/retry loop controlled by `dvb_mfe_wait_time`. Media-controller integration stores a `media_pipeline` in private state and enables/disables sources around writable open/release.

## Dependencies And Integration Points

The core depends on frontend driver callbacks in `struct dvb_frontend_ops` and nested tuner/analog ops. Important callbacks include init/sleep/suspend/resume/release, set/get frontend, read status/statistics, tune/search/get_frontend_algo, DiSEqC/tone/voltage operations, LNA, TS bus control, and I2C gate control. It uses `dvbdev.c` for device registration and generic open/ioctl plumbing, media-controller APIs when enabled, Linux kthreads/freezer/wait queues, and compat user-copy structures for 32-bit userspace.

Userspace integration is via DVBv3 and DVBv5 frontend ioctls. Adapter integration is via `dvb_register_frontend` and `dvb_unregister_frontend`, typically called by PCI/USB/I2C bridge drivers when a demod/tuner stack is attached.

## Risks And Edge Cases

Compatibility behavior is complex. DVBv3 calls may emulate non-DVBv3 delivery systems, default to the first compatible delivery system, or fail if no compatible type exists. Early DVBv5 apps passing `SYS_UNDEFINED` are mapped to the first supported delivery system. These compatibility branches are necessary but can surprise multi-standard devices.

Thread state is sensitive to open mode and release timing. With `dvb_shutdown_timeout`, the thread may remain alive briefly after writer close; statistics ioctls return `-EAGAIN` when no thread exists. Read-only mode intentionally blocks event and DiSEqC reply ioctls because they interfere with tuning state.

Parameter derivation has several assumptions: satellite frequency units are converted to kHz for range checks, DVB-C/ATSC bandwidths are inferred, and software zigzag defaults rely on symbol rate or step size. Incorrect frontend ops metadata can cause false `-EINVAL`, warnings about undefined frequency limits, or ineffective scans.

Concurrency risks include MFE handoff races, source-enable failure cleanup, and thread stop/resume interactions. A build should also validate this snapshot against generated-tree anomalies elsewhere in the same folder.

## Test Signals

High-value tests include DVBv5 property batches with `DTV_CLEAR`, delivery-system switches, `DTV_TUNE`, and invalid message counts; DVBv3 `FE_SET_FRONTEND` compatibility across QPSK/QAM/OFDM/ATSC and unsupported systems; frequency and symbol-rate boundary checks; read-only ioctl permission checks; event overflow and blocking/nonblocking `FE_GET_EVENT`; software zigzag lock/lost-lock transitions; hardware/custom algorithm status event emission; suspend/resume restoring tone and voltage; MFE shared open contention; media-controller source busy cleanup; and unregister while users and the frontend thread are active.

Runtime signals include frontend registration logs, creation of `/dev/dvb/adapterX/frontendY`, event poll readiness after tuning state changes, clean kthread exit on close/unregister, and no leaked media source pipeline after failed writable open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_frontend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_net.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_net.c

## Purpose

`dvb_net.c` exposes DVB data services as Linux Ethernet-like network interfaces. It supports MPE section decapsulation and ULE TS-packet decapsulation, manages DVB network interface creation/removal through net ioctls, programs demux feeds and section filters, applies unicast/multicast/promiscuous receive modes, builds `sk_buff` frames, and injects packets into the kernel network stack with `netif_rx`.

## Important APIs, Types, And Functions

`struct dvb_net_priv` is per-net-device state. It stores the PID, host `struct dvb_net`, demux pointer, active section/TS feeds, section filters, multicast filter list, receive mode, work items, feed type, ULE synchronization/continuity state, current ULE skb, ULE header fields, remaining SNDU bytes, TS cell count, and a mutex.

Public module integration is `dvb_net_init` and `dvb_net_release`, exported to adapter code. Userspace-facing net-device management is handled by `dvb_net_do_ioctl` through `NET_ADD_IF`, `NET_GET_IF`, `NET_REMOVE_IF`, and old binary-compatible ioctl variants.

MPE flow uses `dvb_net_feed_start`, `dvb_net_filter_sec_set`, `dvb_net_sec_callback`, and `dvb_net_sec`. ULE flow uses `dvb_net_ts_callback`, `dvb_net_ule`, `dvb_net_ule_new_ts_cell`, `dvb_net_ule_ts_pusi`, `dvb_net_ule_new_ts`, `dvb_net_ule_new_payload`, `dvb_net_ule_check_crc`, `handle_ule_extensions`, and `dvb_net_ule_should_drop`.

Network-device operations are `dvb_net_open`, `dvb_net_stop`, `dvb_net_tx`, `dvb_net_set_multicast_list`, and `dvb_net_set_mac`, installed through `dvb_netdev_ops`. Interface allocation uses `alloc_netdev`, `dvb_net_setup`, `register_netdev`, and `free_netdev`.

## Control Flow

`dvb_net_init` initializes mutexes, clears interface slots, stores the demux pointer, and registers a `DVB_DEVICE_NET`. Userspace opens that DVB net control device and uses privileged ioctls to add/remove interfaces. `NET_ADD_IF` checks `CAP_SYS_ADMIN`, pins the adapter module, allocates a free interface slot, creates a netdev named like `dvbA_B` or `dvbAIDB`, copies the adapter proposed MAC, initializes private state, and registers the netdev.

Opening a netdev increments `in_use` and starts the demux feed. For MPE, the driver allocates a section feed, sets it to the configured PID with CRC checking, programs one or more MAC section filters depending on receive mode, and starts filtering. For ULE, it allocates a TS feed, sets a TS packet feed for the PID, stores the netdev pointer in `tsfeed->priv`, and starts filtering. Stop reverses that state by stopping feed callbacks, releasing section filters or TS feed, and clearing pointers.

MPE callbacks receive complete sections. `dvb_net_sec` validates minimum length and scrambling bits, optionally handles LLC/SNAP, rejects multi-section datagrams, allocates an skb, builds an Ethernet header from the MPE MAC fields and inferred protocol, updates rx stats, and submits the skb.

ULE callbacks receive TS packets. `dvb_net_ule` iterates TS cells, validates sync/TEI/scrambling, synchronizes on PUSI when needed, checks continuity counters, parses ULE SNDU length/D-bit/type, allocates an skb sized for worst-case bridged headers, copies payload across TS cells, verifies CRC32 over length/type/payload, filters destination MAC when present, handles optional and mandatory extension headers, creates or preserves an Ethernet header, updates stats, and calls `netif_rx`.

## State And Persistence Behavior

State is per DVB net control object plus per netdev. `dvbnet->state[]` marks allocated interface slots; `dvbnet->device[]` holds netdev pointers. Per-netdev demux feed state is allocated on open and released on stop. ULE decoder state persists across TS callbacks so fragmented SNDUs can span packets; `reset_ule` clears this state after completion or error.

Receive mode changes and MAC address changes are deferred through work items. The multicast work item stops the feed, computes `RX_MODE_UNI`, `RX_MODE_MULTI`, `RX_MODE_ALL_MULTI`, or `RX_MODE_PROMISC` from netdev flags and multicast list under `netif_addr_lock_bh`, then restarts the feed. MAC changes schedule feed restart if the interface is running.

Removal sets the DVB net control `exit` flag, waits for users, unregisters the DVB control device, then removes all allocated netdevs. `NET_REMOVE_IF` refuses in-use netdevs and drops the adapter module reference only after successful removal.

## Dependencies And Integration Points

The file depends on the DVB demux API for section and TS feeds, Linux netdevice APIs, Ethernet helpers, CRC32, `dvbdev.c` registration/usercopy helpers, and `linux/dvb/net.h` ioctl definitions. It integrates directly with `dvb_demux.c`: MPE uses section feeds and filters, while ULE uses TS feeds.

The net stack sees these as Ethernet-style devices with `IFF_NOARP`, 4096-byte MTU/max MTU, standard Ethernet header ops, receive stats, and an always-drop transmit path (`dvb_net_tx`) because DVB data services are receive-only in this implementation.

## Risks And Edge Cases

ULE decapsulation is stateful and error-prone by design. Invalid sync, TEI, scrambling, continuity jumps, malformed pointer fields, invalid SNDU lengths, CRC failures, unknown mandatory extension headers, and destination MAC mismatches all trigger drops and stats updates. PUSI resynchronization is crucial after partial payload errors.

MPE only handles one-section datagrams; nonzero section number is rejected with frame errors. Some MPE validation is deliberately relaxed for real-world ISP streams, so malformed-but-unscrambled sections may proceed further than strict spec checks.

Feed restart work can race with netdev stop/removal if not flushed. This file flushes both work items during removal, and feed operations use `priv->mutex`, but tests should still exercise concurrent multicast changes, MAC changes, interface close, and removal. Another behavioral edge is `dvb_net_remove_if`: it checks `in_use`, then calls `dvb_net_stop(net)` even when not in use, which decrements `in_use`; tests should verify whether this matches expected lifecycle in this tree.

## Test Signals

Useful tests include adding/removing MPE and ULE interfaces with valid and invalid feed types, permission failures for unprivileged ioctls, get-if bounds checks, netdev open/stop feed allocation failure cleanup, multicast mode transitions with filter programming, MAC change feed restart, MPE sections with IPv4/IPv6/SNAP and bad lengths, ULE TS streams with fragmented SNDUs, D-bit set/unset, bridged extension headers, unknown mandatory extensions, CRC pass/fail, continuity loss, invalid pointer fields, and PUSI resynchronization.

Runtime signals include created/removed network interface logs, rx packet/byte counters increasing on valid data, rx error counters increasing on malformed TS/SNDU/section input, no active demux feeds after netdev stop, and module references balancing after interface removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_ringbuffer.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_ringbuffer.c

## Purpose

`dvb_ringbuffer.c` provides the generic circular buffer and packet-record helpers used by DVB core components. It supports byte-stream reads/writes, user-copy variants, flush/reset operations, waitqueue wakeups, and packetized records with a small header containing length and ready/disposed state. In this subset, CA EN50221 uses the packet helpers to queue CAM link fragments.

## Important APIs, Types, And Functions

The exported API includes `dvb_ringbuffer_init`, `dvb_ringbuffer_empty`, `dvb_ringbuffer_free`, `dvb_ringbuffer_avail`, `dvb_ringbuffer_flush`, `dvb_ringbuffer_reset`, `dvb_ringbuffer_flush_spinlock_wakeup`, `dvb_ringbuffer_read_user`, `dvb_ringbuffer_read`, `dvb_ringbuffer_write`, and `dvb_ringbuffer_write_user`. Packet helpers in this file include `dvb_ringbuffer_pkt_write`, `dvb_ringbuffer_pkt_read_user`, `dvb_ringbuffer_pkt_read`, `dvb_ringbuffer_pkt_dispose`, and `dvb_ringbuffer_pkt_next`.

The packet format is `len_hi`, `len_lo`, `status`, followed by payload. Status is `PKT_READY` or `PKT_DISPOSED`. Disposed packets are lazily reclaimed only from the read pointer forward, preserving later packets until all earlier packets are disposable.

## Control Flow

Initialization sets read/write positions to zero, stores caller-provided backing storage and size, clears error state, and initializes the wait queue and spinlock. Free/available calculations use circular pointer arithmetic with one byte reserved to distinguish full from empty.

Read and write operations handle wraparound in two phases. If the requested transfer crosses the end of the backing array, they copy the split tail first, publish the pointer as zero, then copy the remaining head bytes and publish the final modulo position. User variants use `copy_to_user`/`copy_from_user`.

Packet write emits the three-byte header using ring macros, writes the payload, and rolls back `pwrite` if the payload write fails. Packet reads inspect packet length at an arbitrary packet index, clamp reads to the packet length, skip the packet header plus caller offset, and copy across wraparound if needed. Packet dispose marks an arbitrary packet disposed, then advances the read pointer over consecutive disposed packets at the front. Packet next walks from either `pread` or a supplied packet index until it finds a ready packet or runs out of available bytes.

## State And Persistence Behavior

The buffer state is in caller-owned `struct dvb_ringbuffer` and caller-provided data storage. There is no allocation or persistence in this file. The `queue` waitqueue is initialized here but only signaled by `dvb_ringbuffer_flush_spinlock_wakeup`; most users perform their own wakeups.

Memory ordering is explicitly documented. Writer pointer publication uses `smp_store_release`; reader-side availability/empty checks use `smp_load_acquire`; writer-side free checks use `READ_ONCE` on `pread`. This makes single-reader/single-writer style usage safer across CPUs, but callers still need external locking for multi-writer or multi-reader cases and for packet-level compound operations.

## Dependencies And Integration Points

The file depends on kernel wait queues, spinlocks, string copy helpers, and user access helpers. It exposes symbols to the rest of DVB core and adapter drivers. Packet macros and `DVB_RINGBUFFER_PKTHDRSIZE` come from `media/dvb_ringbuffer.h`.

The main integration point in this work item is `dvb_ca_en50221.c`, where CAM link fragments are packet-written by the monitor thread and packet-read/disposed by userspace read paths.

## Risks And Edge Cases

Callers must check available/free space before writing; `dvb_ringbuffer_write` itself does not enforce capacity. Packet helpers assume the header and packet fit and can leave partial header state if misused. `dvb_ringbuffer_pkt_write` only rolls back on negative payload write status, while normal `dvb_ringbuffer_write` currently returns the requested length.

User-copy write returns `len - todo` on copy failure, but during the second copy `todo` has not been reduced yet, so partial-copy semantics need careful testing. Packet indices are `size_t`, but `dvb_ringbuffer_pkt_next` uses `idx == -1` as the sentinel; this relies on unsigned wrap to `SIZE_MAX` and matching caller convention.

External synchronization is still required around compound operations such as scanning packets and disposing selected records. Packet disposal marks status without a barrier or lock in this file; correctness depends on caller locking or single-consumer assumptions.

## Test Signals

Tests should cover empty/free/avail across initial, wrapped, full-minus-one, flush, and reset states; byte reads/writes that split at the end; user-copy fault behavior; packet write/read/read_user for wrapped headers and wrapped payloads; disposing out-of-order packets and verifying only front-disposed packets are reclaimed; `pkt_next` iteration across ready and disposed records; and concurrent producer/consumer stress under the locking model used by each caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_ringbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_vb2.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_vb2.c

## Purpose

`dvb_vb2.c` adapts the videobuf2 core to DVB demux capture buffers. It provides a small DVB-facing context that supports mmap buffer allocation, queue/dequeue/query/export operations, stream on/off, poll/mmap wrappers, and a demux callback helper that copies incoming TS or section data into queued vb2 buffers.

Only `VB2_MMAP` is supported in this implementation, using `vb2_vmalloc_memops`. The code is intended for DVB demux devices that expose the newer buffer API through `dmx_buffer` request/query/qbuf/dqbuf style operations.

## Important APIs, Types, And Functions

The queue ops are `_queue_setup`, `_buffer_prepare`, `_buffer_queue`, `_start_streaming`, and `_stop_streaming`. Buffer conversion ops are `_fill_dmx_buffer` and `_fill_vb2_buffer`.

The exported DVB-facing functions are `dvb_vb2_init`, `dvb_vb2_release`, `dvb_vb2_stream_on`, `dvb_vb2_stream_off`, `dvb_vb2_is_streaming`, `dvb_vb2_fill_buffer`, `dvb_vb2_reqbufs`, `dvb_vb2_querybuf`, `dvb_vb2_expbuf`, `dvb_vb2_qbuf`, `dvb_vb2_dqbuf`, `dvb_vb2_mmap`, and `dvb_vb2_poll`.

`struct dvb_vb2_ctx` fields used here include `vb_q`, `slock`, `dvb_q`, `buf`, `buf_siz`, `buf_cnt`, `remain`, `offset`, `flags`, `count`, `nonblocking`, `state`, and `name`. `struct dvb_buffer` wraps a `vb2_buffer` plus list node.

## Control Flow

Initialization clears the context, configures a capture queue, sets mmap-only I/O, installs queue and buffer ops, points queue locking at the caller-provided mutex, initializes the DVB queued-buffer list, stores the context name and nonblocking behavior, marks the state initialized, and calls `vb2_core_queue_init`.

`REQBUFS` clamps requested buffer size to `DVB_V2_MAX_SIZE`, stores size/count in the context, and calls `vb2_core_reqbufs` with `VB2_MEMORY_MMAP`. Queue setup then exposes one plane per buffer sized to `ctx->buf_siz`. Buffer prepare verifies the plane is large enough and sets initial payload to the full configured size. Buffer queue appends the DVB buffer to `ctx->dvb_q` under `slock`.

Streaming on/off delegates to vb2 core and updates state bits. Stop streaming drains all queued DVB buffers and completes them with `VB2_BUF_STATE_ERROR`.

`dvb_vb2_fill_buffer` is the data path. It ignores null/zero source calls, captures demux buffer flags into `ctx->flags`, obtains the next queued vb2 buffer if none is active, drops data if no buffer exists, aborts the current buffer if streaming has stopped, copies as much input as fits into the current plane, completes full buffers with `VB2_BUF_STATE_DONE`, and optionally flushes a partially filled buffer as done.

## State And Persistence Behavior

State is entirely per `dvb_vb2_ctx` and volatile. Buffer ownership moves from userspace/vb2 to the driver list via `_buffer_queue`, to active `ctx->buf` during fill, and back to vb2 with DONE or ERROR completion. `ctx->flags` accumulates demux buffer flags until `dvb_vb2_dqbuf`, where they are copied to userspace and cleared; `ctx->count` increments per dequeue.

`ctx->state` tracks initialized, requested-buffers, and stream-on states. Error paths often set state to `DVB_VB2_STATE_NONE`, so callers should treat failed core vb2 operations as requiring reinitialization or careful recovery.

Synchronization uses the vb2 queue mutex supplied by the caller for core operations and `ctx->slock` for the internal DVB queue, active buffer pointer, offsets, flags, and counter.

## Dependencies And Integration Points

The file depends on `media/dvb_vb2.h`, `media/dvbdev.h`, videobuf2 core, and the vmalloc memory allocator. It is used by DVB demux/DVR implementations that need mmap-backed capture rather than older ringbuffer read paths. The demux callback passes `enum dmx_buffer_flags` to `dvb_vb2_fill_buffer`, and userspace observes those flags on dequeue.

## Risks And Edge Cases

The data path silently drops bytes when no queued buffer is available, logging only by debug level. Partial flush uses `vb2_set_plane_payload(&ctx->buf->vb, 0, ll)`, where `ll` is the last copy chunk length rather than the accumulated `ctx->offset`; this is a high-value review/test target because a flushed partial buffer may report too few bytes used after multiple copy iterations.

`_buffer_prepare` sets payload to full buffer size before data is captured, which is common for fixed-size capture buffers but can be misleading if users expect payload to reflect actual bytes until DONE. Request size has a maximum but is not rounded to 188/204-byte TS packet multiples despite a FIXME. Error paths in stream on/off and reqbufs clear the whole state, which may make recovery coarse.

The function ignores `flush` calls with null source because it returns early on `!src || !len`; if callers use a second null callback to signal end-of-frame, that signal is not enough to flush unless they pass data and `flush=true`.

## Test Signals

Tests should cover queue setup size/count propagation, prepare rejecting undersized planes, qbuf list insertion, streamoff completing all queued buffers as ERROR, fill with no queued buffers, fill across multiple queued buffers, flush of partial buffers, demux flag propagation and clearing on dqbuf, nonblocking dqbuf behavior, query/export/mmap/poll wrappers, max-size clamping, and stop-streaming while a buffer is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_vb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvbdev.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvbdev.c

## Purpose

`dvbdev.c` is the DVB core device registry and common character-device plumbing. It owns adapter registration, per-adapter DVB device registration/removal, minor allocation, `/dev/dvb/adapterN/typeM` device creation, generic open/release/ioctl helpers, usercopy dispatch, optional media-controller entity/interface graph creation, I2C module probe/release helpers, uevents, devnode naming, and module init/exit for the DVB major.

This file is the base layer used by frontend, demux, DVR, CA, net, and other DVB device classes in this source tree.

## Important APIs, Types, And Functions

Exported core APIs include `dvb_register_adapter`, `dvb_unregister_adapter`, `dvb_register_device`, `dvb_remove_device`, `dvb_unregister_device`, `dvb_device_get`, `dvb_device_put`, `dvb_generic_open`, `dvb_generic_release`, `dvb_generic_ioctl`, and `dvb_usercopy`. I2C helper exports are `dvb_module_probe` and `dvb_module_release` when I2C is enabled. Media-controller export is `dvb_create_media_graph` when `CONFIG_MEDIA_CONTROLLER_DVB` is enabled.

Key global state includes `dvb_adapter_list`, `dvbdev_register_lock`, `dvbdev_mutex`, `dvbdevfops_list`, `dvb_minors[]`, `minor_rwsem`, `dvb_class`, and `dvb_device_cdev`. Static device-name mapping `dnames[]` translates DVB device type enum values into devnode names.

## Control Flow

Module init reserves `DVB_MAJOR` minors, adds a single cdev whose open function is `dvb_device_open`, creates the `dvb` class, and installs uevent/devnode callbacks. The generic cdev open looks up `dvb_minors[minor]` under `minor_rwsem`, obtains the device fops, stores a krefed `dvb_device` in `file->private_data`, replaces file operations with the device-specific fops, and calls the real open method.

Adapter registration selects a requested or first-free adapter number, initializes the adapter structure and device list, records module/device/name, initializes MFE and optional media locks, and appends it to the global adapter list. Adapter unregistration removes it from the list.

Device registration finds a free id for the type on the adapter, reuses or clones the template file-operations table for the adapter module/type/template tuple, allocates and initializes `struct dvb_device`, assigns a static or dynamic minor, stores a krefed pointer in `dvb_minors`, optionally registers media-controller entities/interfaces, creates the class device, and appends the device to the adapter device list. Removal clears the minor slot, drops the minor-held kref, frees media-controller state, destroys the class device, and unlinks from the adapter list. Unregister does remove plus an additional `dvb_device_put` for the caller-held reference.

Generic open/release enforce `users`, `readers`, and `writers` counters. Read-only opens decrement `readers`; other opens decrement `writers`; both decrement `users`. Release reverses the counters and drops the file-held `dvb_device` reference.

`dvb_usercopy` implements the common ioctl copy pattern: allocate stack or heap temp storage based on `_IOC_SIZE`, copy input for write/read-write commands, call the device-specific handler, map `-ENOIOCTLCMD` to `-ENOTTY`, and copy output for read/read-write commands.

## State And Persistence Behavior

All registry state is in memory. Adapter numbers and device ids persist only while registered. Minor slots hold krefs so an open racing with removal can safely pin the `dvb_device`. File operations are cloned once and cached in `dvbdevfops_list` to avoid leaking fops allocations across repeated probes of the same device type/template.

Locking layers are explicit: `dvbdev_register_lock` serializes adapter/device registration and removal, `minor_rwsem` protects `dvb_minors`, `dvbdev_mutex` serializes generic open fops replacement, and krefs handle object lifetime after lookup. Per-device users/readers/writers counters are manipulated by generic open/release and are expected to be reached with higher-level serialization from the open path.

Media-controller state is attached to `struct dvb_device` and the adapter. `dvb_media_device_free` unregisters entities, TS output entities, interface devnodes, and RF connector state. `dvb_create_media_graph` links tuner, demod, demux, CA, DVR/demux TS outputs, and interfaces after entities exist.

## Dependencies And Integration Points

The file integrates with Linux char-device, class/device, kref, I2C, module, and media-controller APIs. Every DVB core component in this subset calls into it: CA and net register `DVB_DEVICE_CA`/`DVB_DEVICE_NET`; frontend registers `DVB_DEVICE_FRONTEND`; demux/DVR layers elsewhere depend on the same registration/usercopy helpers.

Userspace integration is through device nodes named by `dvb_devnode`, uevents carrying `DVB_ADAPTER_NUM`, `DVB_DEVICE_TYPE`, and `DVB_DEVICE_NUM`, and stable minor allocation semantics depending on `CONFIG_DVB_DYNAMIC_MINORS`.

## Risks And Edge Cases

Registration failure cleanup is complex because it may need to unwind fops cache insertion, media entities, adapter list insertion, minor krefs, and class devices. Tests should cover failures at each allocation/registration step. Static minor mode must avoid collisions via adapter/type/id encoding; dynamic minor mode must scan all minors.

Generic users/readers/writers counters are simple integer fields; device-specific open paths need to provide serialization and removal coordination. `dvb_device_open` replaces fops before invoking the real open; if that open fails it drops the kref, but any partially initialized device-specific state must be cleaned by that open implementation.

Media-controller graph creation assumes at most one tuner/demod for simple auto-linking; when multiple exist, it deliberately leaves some links for caller drivers. RF connector and pad allocation failures can leave partially allocated adapter media state unless cleanup paths are exercised.

This snapshot shows an apparent extra opening brace at the start of `dvb_device_get`, which is a source-integrity/build concern to verify. More broadly, because many files in this subset appear generated or transformed, compile and sparse checks are essential before trusting behavior.

## Test Signals

Tests should cover adapter number selection with requested and fallback lists, duplicate/full adapter handling, device id allocation per type, static and dynamic minor allocation, cdev open dispatch to device fops, generic reader/writer/user accounting, open failure kref cleanup, ioctl copy directions and heap-vs-stack argument sizes, device registration failure injection at fops allocation, minor assignment, media registration, and class device creation, as well as unregister while file descriptors are open.

Media-controller tests should verify entity/pad/interface creation for frontend, demux, DVR, CA, and net types; graph creation with tuner/demod/demux/CA/DVR entities; cleanup of TS output entities and RF connector; and correct uevent/devnode strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvbdev.c -->
