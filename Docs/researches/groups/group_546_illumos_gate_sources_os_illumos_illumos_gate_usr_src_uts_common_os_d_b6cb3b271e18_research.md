# Group Research: group_546_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_d_b6cb3b271e18

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. Read all four listed source files completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dumpsubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dumpsubr.c

## Purpose

Implements illumos kernel crash dump setup and dump execution. It owns dump device configuration, dump header construction, page selection, page-to-PFN mapping metadata, compressed page streaming, panic/live dump helper coordination, and uncompressed trailer regions for stack summary, FMA ereports, and console messages.

## Main Responsibilities

- Maintains global dump configuration: `dumpvp`, `dumpvp_size`, `dumppath`, `dumphdr`, `dump_conflags`, `dumpbuf`, and `dumpcfg`.
- Initializes and tears down dump devices with `dumpinit()` and `dumpfini()`.
- Writes buffered dump data through `dumpvp_write()` and `dumpvp_flush()`, using `VOP_DUMP()` during panic and `vn_rdwr()` during live dump.
- Builds dump maps with `dump_addpage()`, `dump_page()`, `dump_as()`, and `dump_process()`.
- Runs `dumpsys()` to emit symbol tables, VA-to-PFN maps, PFN tables, compressed memory data, platform data, metrics, and leading/trailing dump headers.
- Supports single-threaded lzjb, parallel lzjb, and panic-time parallel bzip2 compression.
- Saves uncompressed summary, ereport, and message sections via `dump_summary()`, `dump_ereports()`, and `dump_messages()`.

## Key Data Structures

- `dumpcfg_t`: persistent compression/helper configuration, including helpers, buffers, bitmaps, spare-memory reservations, helper CPU bitmap, and panic helper lock state.
- `dumpbuf_t`: single buffered writer state for dump device offsets and aligned I/O.
- `dumpsync_t`: per-dump runtime counters, queues, progress, timing, and live/panic mode.
- `helper_t`: per-compression-stream state, including input/output buffers, lzjb page buffers, bzip2 stream state, metrics, and helper identity.
- `cbuf_t` and `cqueue_t`: stateful buffer descriptors and queue primitives used between master, helper, free-buffer, and writer paths.
- `dumpmlw_t`: physical memory list walker optimized for sequential bitnum-to-PFN lookup.

## Important Control Flow

- `dumphdr_init()` lazily allocates the dump header, dump I/O buffer, PID list, helper CPU bitmap, stack scratch buffer, UUID, and PFN bitmaps sized from physical memory.
- `dump_update_clevel()` chooses compression level from CPU count, platform threshold, and dump device I/O size; allocates minimum helpers/buffers and reserves virtual address space for best-case panic-time expansion.
- `dumpsys_get_maxmem()` runs only at panic dump time. It searches pages not selected for dumping, first in `CBUF_MAPSIZE` ranges and then as individual pages, maps them into reserved VM, marks them as dump-owned, and uses them to enable more helpers/output buffers/bzip2 state.
- `dumpsys()` is the top-level dump sequence:
  - determines dump offset and content mode,
  - writes kernel symbols,
  - walks kernel and optionally process address spaces,
  - writes PFN table,
  - starts live taskq helpers or panic idle-CPU helpers,
  - runs `dumpsys_main_task()`,
  - writes compression metadata and dump headers,
  - writes panic-only summary/ereport/message trailers.
- `dumpsys_main_task()` maps selected PFN ranges, dispatches them to helpers or compresses serially, drains write/error queues, unmaps ranges, updates progress, and closes helper queues at EOF or I/O error.
- `dumpsys_helper()` is entered by panic-idle CPUs. It claims a `FREEHELPER`, records CPU participation in `helpermap`, runs lzjb or bzip2 compression, and marks completion.
- `dumpsys_live_helper()` performs the same compression path from taskq context for live dumps.

## Compression and Stream Format Notes

- Compression level meanings:
  - `0`: serial lzjb, no helper stream format.
  - `DUMP_CLEVEL_LZJB`: parallel lzjb streams.
  - `DUMP_CLEVEL_BZIP2`: parallel bzip2 streams.
- Parallel streams are tagged with helper-specific stream tags so multiple helper outputs can be interleaved.
- `dumpsys_lzjbrun()` writes stream blocks containing a tagged block-size word followed by stream headers or per-page compressed records.
- `dumpsys_bzrun()` feeds page data and stream headers into the bzip2 stream and writes tagged compressed blocks.
- Live dumps downgrade bzip2 to lzjb because the panic-only spare-memory path is not used.

## Concurrency and Panic Constraints

- Panic helpers cannot rely on normal blocking kernel services, so panic queues use custom spin locks and atomic state; live dumps use mutexes and condition variables.
- `cqueue_t` producer counts let consumers distinguish “temporarily empty” from “closed and done.”
- `dump_pagecopy()` uses `on_trap()` to tolerate data access/ECC faults while copying pages and substitutes sentinel words for bad memory.
- `dump_timeleft` is refreshed throughout long-running loops to avoid dump timeout expiration.
- `dump_check_used` is enabled when dumpsys borrows pages so allocator paths can avoid dump-owned memory.

## External Interfaces and Dependencies

- Exports dump control and support functions including `dumpinit()`, `dumpfini()`, `dumpsys()`, `dump_resize()`, `dumpvp_resize()`, `dump_set_uuid()`, `dump_get_uuid()`, `dump_page()`, `dump_addpage()`, `dumpvp_write()`, `dumpsys_helper()`, and `dumpsys_helper_nw()`.
- Depends on VM/HAT page mapping, vnode/block-device dump operations, ksyms, lzjb `compress()`, bzip2, FMA ereport dumping, error queues, logging queues, platform dump hooks, and panic state.

## Notable Edge Cases

- Avoids block-device dump use when the device is mounted or is a ZFS swap zvol.
- For zvol dump devices, invokes `DKIOCDUMPINIT`/`DKIOCDUMPFINI`.
- Reserves first device page and special trailer regions; swap dump starts one-fifth into the device.
- Clears `DF_COMPLETE` if I/O failed or fewer pages were written than expected.
- `dump_set_uuid()` accepts exactly canonical 36-character UUID strings and only permits setting once.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dumpsubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/errorq.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/errorq.c

## Purpose

Implements kernel error queues: preallocated, panic-aware queues for hardware/error events that may be produced from high interrupt context and later drained safely by soft interrupt, explicit drain, or panic handling.

## Main Responsibilities

- Creates fixed-size error queues with `errorq_create()` and nvlist-backed queues with `errorq_nvcreate()`.
- Dispatches copied error payloads with `errorq_dispatch()`.
- Supports reserve/fill/commit/cancel workflows through `errorq_reserve()`, `errorq_commit()`, and `errorq_cancel()`.
- Drains queues in chronological order with `errorq_drain()`.
- Drains vital and nvlist queues during panic with `errorq_panic()`.
- Writes queued nvlist ereports into the dump file via `errorq_dump()`.
- Publishes per-queue kstats for dispatched, dropped, logged, reserved, failed, committed, and cancelled counters.

## Key Data Structures

- `errorq_t`: queue descriptor with element array, payload buffer, free bitmap, pending list, processing list, panic dump list, soft interrupt id, lock, flags, kstat, and global-list linkage.
- `errorq_elem_t`: queue element containing list pointers and a pointer into the preallocated payload region.
- `errorq_nvelem_t`: nvlist queue element wrapper, with a fixed-buffer nvlist allocator and nvlist pointer.
- `errorq_kstat_template`: named kstat layout copied into each queue.

## Queue Model

- Free elements are tracked by `eq_bitmap`.
- Producers never allocate memory in dispatch/commit paths; they claim a bitmap slot atomically.
- Pending errors are a singly-linked LIFO list through `eqe_prev`.
- Drainers reverse pending order into a processing list so callbacks see oldest-to-newest order.
- Nvlist queues preserve panic-drained elements on `eq_dump` rather than freeing them, so crash dump code can serialize ereports later.

## Important Control Flow

- `errorq_create()` allocates all queue state, registers a fixed soft interrupt when possible, creates kstats, initializes element data pointers, and links the queue into `errorq_list`.
- Early boot queues may be created before soft interrupt registration is possible; `errorq_init()` later registers missing softints and drains early events.
- `errorq_dispatch()`:
  - drops if queue is inactive,
  - atomically claims a free element,
  - copies and zero-pads payload,
  - pushes the element onto `eq_pend` with CAS,
  - optionally triggers the queue soft interrupt.
- `errorq_drain()`:
  - serializes consumers with `eq_lock`,
  - CAS-moves `eq_pend` to processing state,
  - builds forward links for chronological traversal,
  - invokes `eq_func(private, data, elem)`,
  - frees elements or appends nvlist elements to the dump list during panic.
- `errorq_panic_drain()` repairs each intermediate state possible if panic interrupts a normal drain, then logs all visible elements and invokes `errorq_drain()` for newly pending errors.
- `errorq_panic()` drains vital non-nvlist queues first, optionally nonvital queues, then vital nvlist queues, then nonvital nvlist queues.

## Panic and Ordering Guarantees

- The file documents and implements at-least-once callback semantics.
- Memory barriers make processing-list state visible to panic code in a recoverable order.
- If panic occurs during callback execution, the same error may be logged again; callbacks are expected to be repeat-safe.
- `errorq_vitalmin` prevents nonvital queues from consuming panic-time attention when many vital errors were logged.

## Nvlist/Ereport Support

- `errorq_nvcreate()` embeds `errorq_nvelem_t` at the front of each element data area and creates fixed-buffer FMA nvlist allocators.
- `errorq_elem_nvl()` and `errorq_elem_nva()` expose the nvlist and allocator for a reserved element.
- `errorq_dump()` packs each nvlist on `eq_dump`, wraps it with `erpt_dump_t`, computes checksum, timestamps relative to panic time, and writes with `dumpvp_write()`.

## External Interfaces and Dependencies

- Public kernel interfaces: `errorq_create()`, `errorq_nvcreate()`, `errorq_destroy()`, `errorq_dispatch()`, `errorq_drain()`, `errorq_init()`, `errorq_panic()`, `errorq_reserve()`, `errorq_commit()`, `errorq_cancel()`, `errorq_dump()`, `errorq_elem_nvl()`, `errorq_elem_nva()`, `errorq_elem_dup()`.
- Depends on atomic bitmap operations, soft interrupts, kstats, panic state, FMA nvlist utilities, dump headers, checksum, and `dumpvp_write()`.

## Notable Edge Cases

- Global `errorq_lost` counts errors sent to inactive/uninitialized queues.
- `errorq_availbit()` uses a rotor to spread allocations across elements for post-mortem diagnosis.
- `errorq_destroy()` disables the queue before draining and requires callers to prevent concurrent producers at a higher layer.
- `errorq_elem_dup()` only supports non-nvlist queues.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/errorq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/evchannels.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/evchannels.c

## Purpose

Implements the general-purpose sysevent event channel framework. It provides event queues, channel binding, kernel and user subscriptions, event publication, delivery threads, per-zone channel state, event snapshots, and pseudo-driver-facing userland entry points.

## Main Responsibilities

- Maintains event channels per zone through `evch_zone_key`.
- Implements basic doubly-linked lists and single queues used by channel and event queue state.
- Delivers events from channel queues to subscriber queues and then to kernel callbacks or userland doors.
- Provides kernel API wrappers `sysevent_evc_*`.
- Provides sysevent pseudo-driver support functions `evch_usr*`.
- Supports persistent subscriptions, dump subscriptions, hold-pending channels, queue limits, and channel properties.

## Key Data Structures

- `struct evch_globals`: per-zone channel list and list lock.
- `evch_chan_t`: channel descriptor with name, event queue, subscriber list, binding count, queue limits, ownership, hold-pending state, properties nvlist, publication counters, and locks.
- `evch_eventq_t`: event queue with queued events, subscriber list, delivery thread state, hold/abort flags, condition variables, current event, and traversal cursor.
- `evch_gevent_t`: refcounted event allocation wrapper with optional destructor and variable-length payload.
- `evch_subd_t`: subscription descriptor with subscriber queue, main/subscriber queue subscriptions, identity, class filter, delivery type, door/callback, persistence, dump flag, active state, and PID.
- `evch_bind_t`: per-opener binding to a channel plus list of subscriptions created through that binding.

## Event Queue Layer

- `evch_evq_create()` allocates queue state and creates the delivery thread if thread initialization has completed.
- `evch_delivery_thr()` repeatedly dequeues events, applies each subscription filter, calls delivery callbacks, handles retry/sleep results, then releases event references.
- `evch_evq_pub()` allocates a queue element, increments event refcount, queues it, and wakes the delivery thread.
- `evch_evq_stop()` and `evch_evq_continue()` hold and resume delivery, used for persistent subscribers, snapshots, and hold-pending channels.
- `evch_evq_evnext()` iterates current and queued events without allocation or locking, which is intentional for panic traversal.
- `evch_gevent_free()` decrements refcount, runs the event destructor if present, and frees the original allocation.

## Channel Layer

- `evch_chbind()` creates or finds a channel, enforces channel and binding limits, initializes hold-pending state, and returns a binding.
- `evch_chunbind()` frees a binding and destroys the channel when there are no bindings, subscribers, or retained pending events requiring indefinite hold.
- `evch_chsubscribe()` creates a per-subscriber queue, subscribes it to the channel queue with class filtering, and subscribes final delivery to either a kernel callback or userland door.
- `evch_chunsubscribe()` removes matching subscriptions, or parks persistent subscriptions by stopping their queue and dropping active door state.
- `evch_chpublish()` enforces per-channel event limits, optionally waits for space, timestamps/sequences the event, installs the destructor that decrements `ch_nevents`, and publishes to the channel queue.
- `evch_chgetnames()` and `evch_chgetchdata()` expose channel inventory and subscriber state.
- `evch_chsetpropnvl()` and `evch_chgetpropnvl()` manage a per-channel property nvlist plus generation counter.

## Delivery Paths

- Kernel delivery uses `evch_kern_deliver()` to invoke the registered callback.
- Userland delivery uses `evch_door_deliver()` with `door_ki_upcall_limited()`, exponential backoff for `EAGAIN`, sleep behavior when the process dies, and retry semantics for returned `EAGAIN`.
- Class filtering uses `evch_class_filter()` and `evch_clsmatch()`, a simple wildcard matcher with recursion bounded by `EVCH_WILDCARD_MAX`.

## Initialization and Zones

- `sysevent_evc_init()` calls `evch_chinit()`, which computes max channel/event limits from available kernel memory and creates zone-specific storage.
- `sysevent_evc_thrinit()` calls `evch_chinitthr()`, creating delivery threads for channels/subscriber queues created before thread availability.
- `evch_zonefree()` tears down all remaining channels for a zone, expecting ordinary bindings to be gone and forcibly removing persistent subscribers.

## Snapshot and Panic Traversal

- `sysevent_evc_walk_init()` snapshots subscriber and main queues into a temporary event queue during normal operation.
- During panic, it stores static traversal state and avoids allocation/locking; `sysevent_evc_walk_step()` then walks subscriber queue first, then main queue.
- `EVCH_SUB_DUMP` identifies the subscriber queue used for dump-oriented event walking; only one dump subscriber is allowed per channel.

## Kernel API Surface

- Binding/subscription/publication: `sysevent_evc_bind()`, `sysevent_evc_unbind()`, `sysevent_evc_subscribe()`, `sysevent_evc_unsubscribe()`, `sysevent_evc_publish()`.
- Control/properties: `sysevent_evc_control()`, `sysevent_evc_setpropnvl()`, `sysevent_evc_getpropnvl()`.
- Event walking: `sysevent_evc_walk_init()`, `sysevent_evc_walk_step()`, `sysevent_evc_walk_fini()`, `sysevent_evc_event_attr()`.
- Event accessors: `sysevent_get_class_name()`, `sysevent_get_subclass_name()`, `sysevent_get_seq()`, `sysevent_get_time()`, `sysevent_get_size()`, `sysevent_get_pub()`, `sysevent_get_attr_list()`.

## User/Pseudo-Driver API Surface

- `evch_usrchanopen()`, `evch_usrchanclose()`, `evch_usrallocev()`, `evch_usrfreeev()`, `evch_usrpostevent()`, `evch_usrsubscribe()`, `evch_usrunsubscribe()`, `evch_usrcontrol_set()`, `evch_usrcontrol_get()`, `evch_usrgetchnames()`, `evch_usrgetchdata()`, `evch_usrsetpropnvl()`, `evch_usrgetpropnvl()`.

## Notable Edge Cases

- Hold-pending channels can retain queued events until a subscriber appears; indefinite hold changes channel destruction behavior.
- `EVCH_QWAIT` lets publishers wait for queue capacity and return `EINTR` on signal.
- Userland channel length changes require root or channel owner.
- Door handles are released on unsubscribe or subscription failure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/evchannels.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exacct.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exacct.c

## Purpose

Implements kernel extended accounting record assembly and commit paths for tasks, processes, network link/flow records, and user-supplied accounting tags. It collects usage data, builds libexacct object trees, packs them, and writes them safely to accounting files.

## Main Responsibilities

- Allocates and attaches exacct object items/groups with `ea_alloc_item()`, `ea_alloc_group()`, and `ea_attach_item()`.
- Creates exacct file headers with `exacct_create_header()` and writes them with `exacct_write_header()`.
- Safely appends packed records to accounting vnodes with rollback-on-error behavior.
- Computes task usage for final, partial, and interval records.
- Computes process usage for final and partial records.
- Assembles and commits network link, network flow, and legacy flow records.
- Implements `putacct(2)` tagging support for tasks and processes.
- Initializes exacct cache/taskq state with `exacct_init()`.
- Accounts for process movement between tasks with `exacct_move_mstate()`.

## Key Data and Globals

- `exacct_queue`: uses `system_taskq` for deferred accounting work.
- `exacct_object_cache`: kmem cache for `ea_object_t`.
- `exacct_zone_key`: zone-specific accounting globals key, initialized by acctctl outside this file.
- `exacct_version`, `exacct_header`, `exacct_creator`: static file header fields.

## File Write Safety

- `exacct_vn_write_impl()` requires `ac_lock`, reads current vnode size, appends via `vn_rdwr(FAPPEND)`, and restores the previous size on write error or short write.
- `exacct_vn_write()` skips inactive/null accounting files and serializes each accounting file through `ac_lock`.
- `exacct_commit_callback()` is the standard callback used by record assemblers to write packed buffers.

## Task Accounting Flow

- `exacct_update_task_mstate()` adds exiting process microstate/resource counters into its task aggregate.
- `exacct_snapshot_task_usage()` walks current task members under `pidlock`, adds approximate live-process usage, subtracts inherited usage, and stamps finish time.
- `exacct_get_interval_task_usage()` subtracts previous interval usage and updates either zone-local or global previous-usage storage.
- `exacct_calculate_task_usage()` chooses final, partial, or interval calculation rules.
- `exacct_attach_task_item()` maps selected `AC_TASK_*` resources into exacct catalog items.
- `exacct_assemble_task_usage()` copies the active resource mask, builds a task group (`TASK`, `TASK_PARTIAL`, or `TASK_INTERVAL`), packs it, and invokes the supplied callback.
- `exacct_commit_task()` writes final task records for the task’s zone and, for non-global zones, also for the global zone, then calls `task_end()`.

## Process Accounting Flow

- `exacct_calculate_proc_usage()` runs under `p_lock`, computes CPU and time fields, identifiers, terminal device, wait status, credentials, command, zone name, nodename, memory RSS average/max, and microstate counters.
- Partial records aggregate live LWP counters with `exacct_calculate_proc_mstate()`.
- Final records copy already accumulated process resource counters with `exacct_copy_proc_mstate()`.
- `exacct_attach_proc_item()` maps `AC_PROC_*` resources into exacct catalog items.
- `exacct_assemble_proc_usage()` builds `PROC` or `PROC_PARTIAL` groups based on the active process mask.
- `exacct_commit_proc()` commits final process records for the process zone and, for non-global zones, also for the global zone.

## Network and Flow Accounting

- `exacct_attach_netstat_item()` records link/flow statistics such as bytes, packets, and error packets.
- `exacct_attach_netdesc_item()` records descriptors such as link/device names, Ethernet addresses, VLAN fields, SAP, priority, bandwidth limit, IP addresses, ports, protocol, and DS field.
- `exacct_assemble_net_usage()` builds one of `NET_LINK_DESC`, `NET_LINK_STATS`, `NET_FLOW_DESC`, or `NET_FLOW_STATS`.
- `exacct_commit_netinfo()` uses global-zone network accounting settings.
- `exacct_attach_flow_item()` records legacy flow attributes: addresses, ports, protocol, DS field, creation/last-seen time, bytes, packets, project id, uid, and action name.
- `exacct_assemble_flow_usage()` builds an `EXD_GROUP_FLOW` record.
- `exacct_commit_flow()` commits legacy flow usage through global-zone flow accounting settings.

## Tagging Support

- `exacct_tag_task()` builds a task tag group with task id, hostname, and caller-supplied raw or exacct-object payload.
- `exacct_tag_proc()` builds a process tag group with pid, task id, hostname, and caller-supplied payload.
- Both return `ENOTACTIVE` if the accounting file is off or missing.

## Task Movement Accounting

- `exacct_snapshot_proc_mstate()` snapshots a process’s current user/system time and resource counters into `task_usage_t`.
- `exacct_move_mstate()` is called during task changes with `pidlock` and `p_lock` already held; it adds the process snapshot to the old task’s aggregate and to the new task’s inherited usage so accounting excludes pre-move consumption from the new task.

## External Interfaces and Dependencies

- Exported/accounting-facing functions include `exacct_create_header()`, `exacct_write_header()`, `exacct_update_task_mstate()`, `exacct_assemble_task_usage()`, `exacct_commit_task()`, `exacct_calculate_proc_usage()`, `exacct_assemble_proc_usage()`, `exacct_commit_callback()`, `exacct_commit_proc()`, `exacct_assemble_net_usage()`, `exacct_commit_netinfo()`, `exacct_assemble_flow_usage()`, `exacct_commit_flow()`, `exacct_tag_task()`, `exacct_tag_proc()`, `exacct_init()`, and `exacct_move_mstate()`.
- Depends on tasks/projects/zones, process and LWP resource accounting, vnode writes, acctctl state, bitmap masks, libexacct packing, microstate accounting, and network/flow accounting structures.

## Notable Edge Cases

- If a selected resource mask produces an empty record, assembly returns success without writing.
- If acctctl is not loaded (`exacct_zone_key == ZONE_KEY_UNINITIALIZED`) or zone-specific globals are unavailable during zone teardown, commit paths skip work.
- Network and flow accounting currently use global-zone settings even though comments note nominal per-zone flow settings.
- Header creation zeroes the final backskip so reverse readers do not treat the file header as a normal trailing record.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/exacct.c -->