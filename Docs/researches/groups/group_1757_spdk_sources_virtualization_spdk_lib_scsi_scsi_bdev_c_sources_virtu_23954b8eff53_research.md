# Group Research: group_1757_spdk_sources_virtualization_spdk_lib_scsi_scsi_bdev_c_sources_virtu_23954b8eff53

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_bdev.c -->
# File Research: sources/virtualization/spdk/lib/scsi/scsi_bdev.c

This file translates SCSI block and primary commands into SPDK bdev operations for SCSI LUNs. It implements Inquiry/VPD data synthesis, Report LUNs, Mode Sense/Select handling, Request Sense, persistent reservation dispatch, SPC-2 reserve/release, capacity reporting, read/write/compare-and-write, synchronize cache, UNMAP, WRITE SAME, bdev reset, and DIF context derivation.

Inquiry handling is extensive. Standard Inquiry fabricates a disk peripheral with SPC-3/SBC-2/SAM-2 descriptors, default vendor/revision strings, product name from the bdev, and optional trailing descriptor/reserved bytes based on allocation length. EVPD pages include supported pages, unit serial, device identification, management network addresses, extended inquiry, mode page policy, SCSI ports, block limits, block device characteristics, and thin provisioning when the bdev supports UNMAP. Device identification builds NAA, T10 vendor ID, SCSI device/port name, relative target port, target port group, and logical unit group designators from bdev, SCSI device, and port metadata.

Mode Sense is generated with a two-pass size-then-fill pattern. It supports MODE SENSE(6)/(10), short or long block descriptors, DBD, page control validation, all-pages traversal, and a set of mostly zeroed standard pages. The caching page advertises write cache enablement from `spdk_bdev_has_write_cache()` and sets read cache disable. Saved mode pages are rejected with `SAVING PARAMETERS NOT SUPPORTED`.

Block command execution validates transfer direction, media bounds, block-size alignment of task offset/length, maximum transfer length from the advertised 4 MiB work block size, and write buffer length. Reads call `spdk_bdev_readv_blocks()` and retain the completed bdev I/O on the SCSI task until task release. Writes call `spdk_bdev_writev_blocks()`. COMPARE AND WRITE is limited to one block, rejects DPO/FUA/wrprotect, splits the single input iovec into compare and write halves, and calls `spdk_bdev_comparev_and_writev_blocks()`.

SYNCHRONIZE CACHE maps to `spdk_bdev_flush_blocks()` and treats a zero block count as the remainder of the device. UNMAP gathers or directly reads the task parameter list, validates descriptor data length and descriptor count, then submits one bdev unmap per descriptor. WRITE SAME validates one logical block of input data and submits one write per target block. UNMAP and WRITE SAME share `spdk_bdev_scsi_split_ctx`, which tracks current, remaining, and outstanding child I/Os, queues resubmission on `-ENOMEM`, and completes the SCSI task only after all child operations finish or a failure stops further splitting.

Primary command dispatch handles Inquiry, Report LUNs, Mode Select, Mode Sense, Request Sense, unsupported Log Select/Sense, Test Unit Ready, Start Stop Unit, PR IN/OUT, and SPC-2 reserve/release. Data-producing commands allocate temporary buffers, scatter only up to allocation length, set `data_transferred`, and mark GOOD on success. Unsupported opcodes return `SPDK_SCSI_TASK_UNKNOWN` so `bdev_scsi_execute()` can fall back or report invalid opcode.

Reset uses `spdk_bdev_reset()` and queues a retry on `-ENOMEM`; completion maps success to SCSI task management success and failure to complete. `bdev_scsi_get_dif_ctx()` builds a DIF context for read/write CDBs when the bdev has metadata, using the CDB LBA as reference tag and enabling guard/ref-tag checks according to bdev policy.

Important invariants are SCSI allocation length versus internal generated length, task lifetime while bdev I/O is outstanding, correct `data_transferred` semantics, no completion before split children drain, and consistent sense/status mapping. The file intentionally advertises capabilities derived from bdev support; changing VPD pages must stay aligned with command behavior such as UNMAP limits and maximum transfer length.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_internal.h -->
# File Research: sources/virtualization/spdk/lib/scsi/scsi_internal.h

This private SCSI header defines the internal data model shared by the SPDK SCSI library: ports, devices, LUN descriptors, LUN state, persistent reservation registrants/reservation state, and internal function prototypes.

`struct spdk_scsi_port` stores use state, numeric ID, relative target port index, transport ID bytes, and port name. `struct spdk_scsi_dev` owns allocation/removal state, device name, the LUN list, up to `SPDK_SCSI_DEV_MAX_PORTS` port entries, and protocol ID. `struct spdk_scsi_lun_desc` tracks open LUN descriptors and hot-remove callbacks.

`struct spdk_scsi_lun` is the central runtime object. It contains LUN identity and removal/resizing flags, owning device, associated bdev/descriptor/thread/channel, hot-remove and resize callbacks, open descriptors, submitted and pending task queues, submitted and pending management task queues, reset poller, refcount, persistent reservation generation, registrant list, current reservation, and an embedded SPC-2 reservation holder.

Persistent reservation structures distinguish registrants by I_T nexus using initiator and target ports plus copied names/transport IDs. `struct spdk_scsi_pr_reservation` stores flags, holder, reservation type, and current reservation key. `SCSI_SPC2_RESERVE` marks legacy SPC-2 reservations.

The declaration surface ties the library together: LUN construct/destruct, task and management task execution/completion, pending-task queries, I/O channel allocation/free, device list access, port construct/destruct, bdev-backed SCSI execution/reset/DIF context helpers, persistent reservation IN/OUT/check functions, and SPC-2 reserve/release/check functions.

The key invariant is that most SCSI internals operate on thread-affine LUN state and queue membership. Reservation code relies on stable `spdk_scsi_port` pointers for live nexus matching while also storing copied names/transport IDs for reporting.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_pr.c -->
# File Research: sources/virtualization/spdk/lib/scsi/scsi_pr.c

This file implements SCSI persistent reservations and compatible SPC-2 RESERVE/RELEASE behavior for SPDK SCSI LUNs. It manages registrant lists, reservation holders, PR OUT service actions, PR IN reporting, reservation conflict checks, and legacy reserve interop.

Registrants are keyed by the live initiator and target port pointers. Registration allocates a `spdk_scsi_pr_registrant`, copies initiator/target names and transport ID details for later reporting, stores the reservation key, inserts it on the LUN registrant list, and increments `pr_generation`. Unregistration removes the registrant, releases or transfers reservation ownership if needed, frees the object, and increments generation. Key replacement updates the holder's current reservation key when the holder is modified.

Reservation holder logic supports both single-holder and all-registrants reservation types. For all-registrants types, any registrant is considered a holder, and release can transfer the reservation holder pointer to another registrant before clearing state. `scsi_pr_has_reservation()` treats a non-null holder as the reservation-present marker.

PR OUT supports REGISTER, REGISTER AND IGNORE EXISTING KEY, RESERVE, RELEASE, CLEAR, and PREEMPT. SPEC_I_PT, ALL_TG_PT, and APTPL are rejected as unsupported. REGISTER enforces key matching for the normal action, handles zero service-action key as unregister/no-op, and creates or replaces registrants. RESERVE requires LU scope, an existing matching registrant key, compatible reservation type if already reserved, and holder eligibility. RELEASE validates registration, reservation type, and current key, then clears or transfers the reservation. CLEAR removes all registrants after key validation. PREEMPT handles no-reservation removal by service-action key, all-registrants special cases, preempt-self type changes, and preempting current holders.

PR IN supports READ KEYS, READ RESERVATION, REPORT CAPABILITIES, and READ FULL STATUS. READ KEYS returns generation plus all keys that fit. READ RESERVATION reports current reservation type and key, using zero key for all-registrants reservations. REPORT CAPABILITIES advertises compatible reservation handling and supported reservation types. READ FULL STATUS emits descriptors with rkey, holder flag/type, scope, relative target port ID, and transport ID, truncating to the caller buffer when necessary.

`scsi_pr_check()` enforces reservation conflicts for ordinary commands. Inquiry, Report LUNs, Request Sense, Log Sense, Test Unit Ready, Start Stop Unit, capacity, PR IN, service action in, and SPC-2 reserve/release are generally allowed. Mode Select/Sense and Log Select require the initiator to be registered when another nexus holds a reservation. PR OUT actions have action-specific permissions. For reads/writes/unmap/sync it applies the SCSI reservation type matrix: write-exclusive blocks writes by non-holders, exclusive-access blocks all, registrants-only variants allow registered initiators as specified, and unsupported commands conflict.

SPC-2 RESERVE/RELEASE compatibility is handled through the embedded `scsi2_holder`. If persistent reservations are active, specific registered/holder cases complete GOOD without changing PR state per SPC-4 compatible reservation handling. Otherwise RESERVE records the I_T nexus in `scsi2_holder` and marks `SCSI_SPC2_RESERVE`; RELEASE clears the legacy reservation. `scsi2_reserve_check()` allows Inquiry and Release, otherwise rejects commands from non-holders when an SPC-2 reservation is present.

Important invariants are reservation generation updates, holder pointer validity when registrants are removed, all-registrants semantics, and the distinction between CHECK CONDITION and RESERVATION CONFLICT status. The implementation is in-memory only; APTPL and target-port-wide registration options are explicitly unsupported.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_pr.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_rpc.c -->
# File Research: sources/virtualization/spdk/lib/scsi/scsi_rpc.c

This small file registers the `scsi_get_devices` JSON-RPC method.

The RPC rejects any parameters, begins a JSON array result, iterates the fixed `SPDK_SCSI_MAX_DEVS` device table returned by `scsi_dev_get_list()`, skips unallocated entries, and emits objects containing `id` and `device_name`. The method is registered for runtime use with `SPDK_RPC_REGISTER`.

The RPC intentionally exposes only basic SCSI device inventory, not LUNs, ports, bdev names, reservation state, or task state. Its correctness depends on `scsi_dev_get_list()` returning the global fixed-size device array expected by the loop.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/task.c -->
# File Research: sources/virtualization/spdk/lib/scsi/task.c

This file implements common SCSI task lifetime, task data movement, sense/status construction, and fallback handling for null LUN or aborted tasks.

Task construction installs completion and free callbacks, increments the task reference count, and initializes the scatter-gather view to point at the embedded single iovec. `spdk_scsi_task_put()` decrements the refcount, frees any attached bdev I/O, releases DMA-allocated task data, and calls the task-specific free callback when the count reaches zero.

Data helpers support both internal allocation and caller-provided iovecs. `spdk_scsi_task_scatter_data()` allocates a DMA buffer for simple one-iovec tasks with no buffer, verifies total iovec capacity, copies source bytes across iovecs, and sets illegal-request sense on short capacity. `spdk_scsi_task_gather_data()` copies all iovec data into a newly allocated contiguous buffer for command parsers such as MODE SELECT or PR OUT. `spdk_scsi_task_set_data()` attaches an external single buffer when no task allocation exists.

Sense data is fixed-format current sense. `spdk_scsi_task_build_sense_data()` fills response code, sense key, ASC, ASCQ, and an 18-byte sense length. `spdk_scsi_task_set_status()` builds sense data automatically for CHECK CONDITION, and `spdk_scsi_task_copy_status()` copies sense/status from one task to another.

`spdk_scsi_task_process_null_lun()` handles commands addressed to unsupported LUNs. INQUIRY returns a peripheral qualifier of unsupported/logical unit not connected with device type unknown, bounded by allocation length; other commands return CHECK CONDITION with logical unit not supported. `spdk_scsi_task_process_abort()` sets aborted-command sense.

The main invariants are task refcount ownership, avoiding double-free of `bdev_io` and DMA task buffers, and ensuring generated sense data matches the status returned to upper-layer protocols.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/task.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/sock/Makefile -->
# File Research: sources/virtualization/spdk/lib/sock/Makefile

This Makefile builds the SPDK `sock` shared library.

It sets `SPDK_ROOT_DIR`, includes the common SPDK make rules, declares shared object version `14.0`, compiles `sock.c` and `sock_rpc.c`, names the library `sock`, enables `-Wpointer-arith`, points `SPDK_MAP_FILE` at `spdk_sock.map`, and includes `spdk.lib.mk`.

The build unit therefore contains the transport-independent socket facade plus its JSON-RPC configuration interface. ABI/export control is delegated to the map file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/sock/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/sock/sock.c -->
# File Research: sources/virtualization/spdk/lib/sock/sock.c

This file is SPDK's transport-independent socket facade. It manages registered socket implementations, default implementation selection, ABI-safe option handling, POSIX address/fd helpers, connect/listen/accept/close wrappers, grouped polling, placement-ID mapping, socket implementation options, configuration JSON output, initialization, interrupt-fd integration, and tracepoint registration.

Socket implementations are stored in `g_net_impls`; `g_default_impl` is selected explicitly through `spdk_sock_set_default_impl()`. `spdk_net_impl_register()` inserts implementations before initialization, and `spdk_sock_initialize()` applies ABI-safe initialize options, prevents reinitialization with different options, calls each implementation's `init()` hook, and removes implementations whose initialization fails.

Options are versioned by `opts_size`. `spdk_sock_get_default_initialize_opts()` and `spdk_sock_get_default_opts()` set only fields present in the caller's structure. `sock_init_opts()` combines library defaults with caller-provided fields before connect/listen. Implementation-specific options are passed through for construction but cleared from the stored `sock->opts` to avoid retaining a dangling caller pointer.

The POSIX helper layer parses numeric IPv4/IPv6 addresses, strips bracketed IPv6 literals, creates stream sockets, sets receive/send buffers, `SO_REUSEADDR`, `TCP_NODELAY`, optional `SO_PRIORITY`, `IPV6_V6ONLY`, and Linux `TCP_USER_TIMEOUT`, then supports blocking or asynchronous connect via nonblocking `connect()`, `poll(POLLOUT)`, and `SO_ERROR` checks. Source address/port binding is supported through socket options.

Connect and listen choose the requested implementation or the default, validate support for async connect, create the transport socket through implementation callbacks, copy final options, set `sock->net_impl`, and initialize request queues for connected sockets. Accept inherits options and implementation from the listener. Close rejects sockets still in a group, marks the pointer closed for the caller, defers destruction if callbacks are active, aborts queued requests, and calls the implementation close hook.

The read/write surface mostly dispatches to implementation hooks after closed/null checks. It includes synchronous recv/readv/writev, async writev, flush, buffer size/low-water setters, IPv4/IPv6/connected queries, interface name, NUMA ID, implementation name, and deprecated zero-copy receive buffer helpers.

Socket groups contain one `spdk_sock_group_impl` per registered net implementation plus an optional fd group for interrupt mode. Group creation calls each implementation's group factory and registers implementation interrupt fds when available. Adding a socket validates callback and matching implementation group, calls the implementation add hook, links the socket, and records callback state. Polling bounds events to `MAX_EVENTS_PER_POLL`, polls each implementation group, and calls each returned socket's callback. Removal clears group/callback state after implementation removal succeeds. Group close requires all implementation socket lists to be empty, unregisters interrupt fds, closes implementation groups, destroys the fd group, and frees the group.

Placement-ID mapping provides a small refcounted map from placement IDs to group implementations. Insert, lookup, release, find-free, and cleanup are protected by a mutex. Lookup can assign an unbound placement ID to a hint group, enabling consistent steering of related sockets.

RPC/config support uses `spdk_sock_impl_get_opts()` and `spdk_sock_impl_set_opts()` to delegate option access to named implementations. `spdk_sock_write_config_json()` emits JSON-RPC reconstruction calls for default implementation and each implementation's configurable options.

Important invariants are implementation callback contracts, option-size compatibility, socket group membership before close, callback count deferral during close, placement-ID refcounts, and interrupt fd registration symmetry. The facade does not own transport-specific socket internals; it standardizes lifecycle, grouping, and configuration around implementation hooks.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/sock/sock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/sock/sock_rpc.c -->
# File Research: sources/virtualization/spdk/lib/sock/sock_rpc.c

This file registers socket JSON-RPC methods for implementation option inspection, option mutation, default implementation selection, and default implementation query.

`sock_impl_get_options` decodes required `impl_name`, calls `spdk_sock_impl_get_opts()`, and returns the implementation option fields: receive/send buffer sizes, receive pipe, quickack, placement ID, server/client zerocopy send enablement, zerocopy threshold, TLS version, and KTLS enablement. It is available at startup and runtime.

`sock_impl_set_options` decodes `impl_name` plus optional option fields. It first fetches current/default implementation options, pre-fills the request context with those values using an X-macro field list, decodes again so provided JSON fields override defaults, copies the same field list back into `spdk_sock_impl_opts`, and calls `spdk_sock_impl_set_opts()`. A static assert on `sizeof(struct spdk_sock_impl_opts) == 80` forces maintainers to audit the X-macro when the option structure grows. The setter is startup-only.

`sock_set_default_impl` decodes `impl_name`, calls `spdk_sock_set_default_impl()`, and returns a boolean success response. `sock_get_default_impl` rejects parameters, returns the current default implementation name, or reports an internal error if no socket implementation is registered as default. It is available at startup and runtime.

The main invariants are keeping the RPC field list synchronized with `spdk_sock_impl_opts`, freeing autogenerated decode contexts on every return path, and respecting startup-only semantics for mutating socket implementation configuration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/sock/sock_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/thread/Makefile -->
# File Research: sources/virtualization/spdk/lib/thread/Makefile

This Makefile builds the SPDK `thread` shared library.

It sets `SPDK_ROOT_DIR`, includes common SPDK rules, declares shared object version `13.0`, compiles `thread.c` and `iobuf.c`, names the library `thread`, points `SPDK_MAP_FILE` at `spdk_thread.map`, and includes `spdk.lib.mk`.

The build unit therefore packages the SPDK cooperative thread/message/poller subsystem together with the shared iobuf pool facility. ABI/export control is delegated to the map file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/thread/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/thread/iobuf.c -->
# File Research: sources/virtualization/spdk/lib/thread/iobuf.c

This file implements SPDK's shared I/O buffer pool service. It provides globally configured small and large DMA buffer pools, optional per-NUMA allocation, per-thread/per-module channel caches, wait queues for buffer starvation, module registration, asynchronous finish, and stats aggregation across channels.

Global state lives in `g_iobuf`: options, registered module list, finish callback, and one `iobuf_node` per NUMA ID. Each node owns a small and large `spdk_ring` plus contiguous DMA backing memory. Defaults are 8192 small 8 KiB buffers and 1024 large 132 KiB buffers, aligned to 4096 bytes; minimum pool and buffer sizes are enforced by `spdk_iobuf_set_opts()`.

Initialization rounds buffer sizes up to alignment, initializes each configured NUMA node, fills central rings with buffer pointers, registers `g_iobuf` as an SPDK I/O device, and enables the initialized flag. Finish unregisters the I/O device; the unregister callback frees module names/records, validates and frees node pools, and invokes the user finish callback. If finish is called before initialization, the callback runs immediately.

Each SPDK thread gets an internal `iobuf_channel` via the I/O device system. Public `spdk_iobuf_channel_init()` validates that the named module was registered, obtains the parent iobuf I/O channel, stores the caller channel in one of 64 per-thread slots for stats, initializes small/large cache structures for each NUMA node, and pre-populates configured cache sizes from central rings. Failure unwinds through `spdk_iobuf_channel_fini()`. Finalization asserts no pending wait entries from the module remain, returns cached buffers to central rings in batches, removes the channel from the per-thread slot array, and releases the parent I/O channel.

Module registration is a simple name list with duplicate checks. Unregistration removes and frees a module by name. Pending iobuf entries store a module pointer when queued, and `spdk_iobuf_for_each_entry()` iterates only entries owned by the channel's module across small and large queues. `spdk_iobuf_entry_abort()` removes a queued request entry from any NUMA-node queue that matches its size class.

`spdk_iobuf_get()` is thread-affine to the channel's parent SPDK thread. It currently uses cache index 0 for allocation, chooses small or large class by requested length, returns from the per-channel cache when possible, otherwise dequeues a batch from the central ring and caches all but the returned buffer. If no buffer is available, an optional entry is appended to the pool wait queue with module/callback metadata and NULL is returned.

`spdk_iobuf_put()` determines the buffer's NUMA node when NUMA is enabled, selects size class by length, and either returns to the local cache/central ring or directly satisfies the first waiter by invoking its callback with the returned buffer. Local caches can exceed configured size by one batch; when high enough, a batch is pushed back to the central pool. The callback path includes queue manipulation intended to preserve fairness when callbacks requeue entries.

Stats collection allocates a module stats array, seeds module names, then uses `spdk_for_each_channel()` on the iobuf I/O device to visit every thread's internal iobuf channel. It aggregates per-module small/large cache hits, main-pool hits, retries, and configured cache sizes, then calls the user callback and frees temporary storage.

Important invariants are NUMA index bounds, channel/thread affinity, matching `spdk_iobuf_get()` and `spdk_iobuf_put()` size classes, no outstanding module wait entries during channel finalization, central ring counts returning to configured pool counts at shutdown, and keeping option ABI handling updated when `struct spdk_iobuf_opts` grows.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/thread/iobuf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/thread/thread.c -->
# File Research: sources/virtualization/spdk/lib/thread/thread.c

This file implements SPDK's cooperative threading substrate: SPDK thread objects, message passing, pollers, timed pollers, thread iteration, I/O device/channel lifecycle, interrupt-mode integration, fd-group interrupt wrappers, and SPDK spinlock safety checks.

Thread library initialization creates the global message mempool and records either legacy new-thread callback hooks or extended thread operation hooks. Thread creation allocates a cache-line-aligned `spdk_thread` plus optional user context, initializes poller queues, timed-poller RB tree, paused poller list, message ring/cache, I/O channel tree, cpuset, trace owner, monotonic thread ID, and optional interrupt fd group. It inserts the thread in the global thread list under `g_devlist_mutex`, calls the framework new-thread hook when present, marks the thread running, and records the first created thread as the app thread.

Message passing uses per-thread MP/SC rings plus a per-thread cache of `spdk_msg` objects backed by the global mempool. `spdk_thread_send_msg()` obtains a message from the current thread cache or mempool, fills function/context, enqueues it to the target thread, and writes the target eventfd if interrupt mode is active and the target is in interrupt mode. Critical messages use an atomic single-slot callback and abort on overwrite. `msg_queue_run_batch()` drains up to eight messages, executes callbacks, enforces no SPDK spinlocks held across callback return, and recycles message objects.

Pollers are per-thread callback objects with states WAITING, RUNNING, UNREGISTERED, PAUSING, and PAUSED. Busy pollers live in an active TAILQ and run round-robin in reverse-safe traversal. Timed pollers live in an RB tree keyed by next run tick, with a cached earliest pointer. Registration assigns a per-thread poller ID, converts microsecond periods to ticks, optionally creates interrupt resources, and inserts into the active or timed structure. Execution updates run/busy stats and handles unregister/pause transitions after callback return. Unregister, pause, and resume must be called from the owning SPDK thread; wrong-thread use logs and aborts/asserts.

`spdk_thread_poll()` temporarily installs the target as TLS current thread, polls messages and pollers in poll mode, handles transition into interrupt mode, runs exit checks when exiting, or waits on the thread fd group in interrupt mode. Thread exit is cooperative: `spdk_thread_exit()` marks EXITING and sets a timeout, while `thread_exit()` waits for messages, for-each operations, pollers, I/O channels, and pending unregister callbacks to drain before marking EXITED, or forces exit after timeout. Destruction frees pollers, cached messages, interrupt resources, message ring, and non-app thread memory; app thread memory is kept until library finalization.

Post-poller handlers provide a small per-thread list of callbacks run after poller execution. Registration is limited to four handlers and intentionally blocks reentrant registration while handlers are running.

Thread iteration uses `spdk_for_each_thread()`. It allocates a context on the originating thread, increments `for_each_count`, walks the global thread list under the mutex, skips non-running threads, sends a message to each target thread in order, and returns to the origin for optional completion. `for_each_count` prevents thread exit from completing while iteration is active.

The I/O device/channel subsystem maps arbitrary device pointers to registered `io_device` records in a global RB tree, and maps per-thread channels in each thread's RB tree. `spdk_io_device_register()` must run on an SPDK thread and records create/destroy callbacks, context size, name, refcount, and per-device thread links. `spdk_get_io_channel()` finds the device, returns an existing channel with incremented refcount or allocates a new channel plus thread-link, increments device refcount, drops the global mutex for `create_cb`, and unwinds carefully if create fails or the device was unregistered concurrently.

`spdk_put_io_channel()` is thread-affine and decrements the channel refcount. The actual destruction is deferred by sending a message to the owning thread, allowing new references to arrive before destruction runs. `put_io_channel()` removes the channel and thread-link, calls the device destroy callback outside the global mutex, decrements device refcount, and frees the device if it had been unregistered and no references remain.

Device unregistration removes the device immediately when no for-each iteration is active, otherwise marks pending unregister. A user unregister callback runs back on the unregistering thread after all channels are gone. `spdk_for_each_channel()` iterates all threads currently holding channels for a device by walking the device's thread-link RB tree and sending a message to each thread; continuation decrements `for_each_count`, returns to the origin for completion, and triggers pending unregister when the last iteration drains.

Interrupt mode is Linux-only and must be enabled before thread library initialization. Each interrupt-capable thread owns an fd group and eventfd for messages. Periodic pollers use timerfd; busy pollers use eventfd that can remain level-triggered. `spdk_thread_set_interrupt_mode()` toggles every poller's interrupt callback and flips the thread mode. Generic interrupt registration wraps callbacks so TLS current thread is set correctly and spinlock invariants are checked. Nested fd groups can also be registered as thread interrupts.

SPDK spinlocks wrap `pthread_spinlock_t` with SPDK-thread ownership tracking. In debug builds they capture init/lock/unlock stacks. The wrapper aborts on use outside an SPDK thread, recursive lock, unlock from the wrong thread, destroy while held, use before init/after destroy, pthread errors, and returning from messages/pollers/interrupts while locks remain held.

Important invariants are thread-affinity for pollers, channels, interrupts, and spinlocks; never holding `g_devlist_mutex` across user create/destroy callbacks except where explicitly avoided; balancing thread/device/channel refcounts; draining messages/pollers/channels before destruction; and keeping interrupt-mode state synchronized with eventfd/timerfd registration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/thread/thread.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/thread/thread_internal.h -->
# File Research: sources/virtualization/spdk/lib/thread/thread_internal.h

This private header defines the internal layout of `struct spdk_io_channel`.

An I/O channel records its owning `spdk_thread`, associated internal `io_device`, reference count, deferred-destroy reference count, RB-tree linkage, and the device-specific destroy callback. It includes fixed padding and documents that modules allocate additional context immediately after the structure for hardware- or module-specific channel data.

The `SPDK_STATIC_ASSERT` requires the structure size to match the public ABI constant `SPDK_IO_CHANNEL_STRUCT_SIZE`. That keeps the private layout compatible with public macros and the common pattern where `spdk_io_channel_get_ctx()` returns memory immediately after the header.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/thread/thread_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/trace/Makefile -->
# File Research: sources/virtualization/spdk/lib/trace/Makefile

This Makefile builds the SPDK `trace` shared library.

It sets `SPDK_ROOT_DIR`, includes common SPDK rules, declares shared object version `13.0`, compiles `trace.c`, `trace_flags.c`, and `trace_rpc.c`, names the library `trace`, links `-lrt`, enables `-Wpointer-arith`, points `SPDK_MAP_FILE` at `spdk_trace.map`, and includes `spdk.lib.mk`.

The build unit packages trace data handling, trace flag support, and trace RPC control. ABI/export control is delegated to the map file, and the realtime library dependency supports trace timing/shared-memory functionality used by the trace implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/trace/Makefile -->