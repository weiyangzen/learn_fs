# Research: subset-b-004263

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.c

Purpose: implements kernel-facing GRU services for SGI UV/SN platforms. It provides demand-loaded per-blade kernel GRU contexts, per-CPU control-block/data-segment resources, async resource reservations, GRU-backed message queues, GPA read/copy helpers, exception handling, and debug quicktests.

Important APIs and functions: exported entry points include `gru_create_message_queue()`, `gru_send_message_gpa()`, `gru_free_message()`, `gru_get_next_message()`, `gru_read_gpa()`, `gru_copy_gpa()`, `gru_reserve_async_resources()`, `gru_release_async_resources()`, `gru_wait_async_cbr()`, `gru_lock_async_resource()`, and `gru_unlock_async_resource()`. Internal resource helpers are `gru_load_kernel_context()`, `gru_lock_kernel_context()`, `gru_get_cpu_resources()`, and `gru_free_kernel_contexts()`. Exception helpers include `gru_wait_proc()`, `gru_check_status_proc()`, `gru_retry_exception()`, and `gru_get_cb_exception_detail()`.

Control flow: kernel callers obtain resources through `gru_get_cpu_resources()`, which locks and, if needed, loads the local blade kernel context. Message sends copy the caller payload into a reserved DSR, set GRU message header flags, issue `gru_mesq()`, and retry or repair based on CB substatus. Queue-full handling flips the message queue head between halves with GRU atomic operations. PUT-nack recovery rewrites possibly partial messages and may send a NOOP to force interrupt delivery. Receivers poll a memory queue directly and free entries in order with `gru_free_message()`.

State and persistence: state is mostly hardware-backed and in-memory: `bs_kgts`, `kernel_cb`, `kernel_dsr`, async reservation counters, message queue head/next/limit pointers, and per-message present bits. No disk persistence exists. The kernel context may be unloaded and reloaded, with hardware context state discarded for kernel use.

Dependencies and integration: depends on GRU instruction helpers, `grutables.h` state, UV blade/GPA translation helpers, kernel completions, wait queues, and cache flush/barrier primitives. XP UV code uses `gru_read_gpa()` and `gru_copy_gpa()` for cross-partition memory operations.

Risks: heavy use of `BUG_ON()` and `panic()` makes unexpected GRU failures fatal. Locking is subtle around `bs_kgts_sema` downgrade/reload and context stealing. Message recovery depends on GRU substatus semantics and correct two-cacheline present-bit handling. Async resources support only one reservation per blade and assume callers pair reserve/lock/unlock/release correctly.

Test signals: `gru_ktest()` exposes quicktests for GPA load/store, message queue capacity/order, async completion, and block copy. Runtime signals include `STAT()` counters for message send/receive failures, congestion, queue-full transitions, context loads, and GPA copy/read operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.h

Purpose: declares the kernel-service API exported by `grukservices.c` for GRU message queues, GPA access, and async GRU resource use. It is a contract for other kernel drivers that want GRU transport or copy services without managing GRU contexts directly.

Important APIs/types: `struct gru_message_queue_desc` stores the queue virtual address, global physical address, cacheline count, and optional interrupt routing fields. Message queue APIs are `gru_create_message_queue()`, `gru_send_message_gpa()`, `gru_get_next_message()`, and `gru_free_message()`. GPA helpers are `gru_read_gpa()` and `gru_copy_gpa()`. Async APIs are `gru_reserve_async_resources()`, `gru_release_async_resources()`, `gru_wait_async_cbr()`, `gru_lock_async_resource()`, and `gru_unlock_async_resource()`. Message send status codes include `MQE_OK`, `MQE_CONGESTION`, `MQE_QUEUE_FULL`, `MQE_UNEXPECTED_CB_ERR`, `MQE_PAGE_OVERFLOW`, and `MQE_BUG_NO_RESOURCES`.

Control flow: callers allocate physically contiguous, cacheline-aligned queue memory, initialize a descriptor, send one- or two-cacheline messages, and poll/free received messages in order. Async users reserve per-blade CBR/DSR resources, lock them to obtain GRU addresses, issue their own GRU instructions, wait through a supplied completion, then unlock and release.

State and persistence: the header itself has no state, but its descriptor exposes the persistent in-memory identity of a message queue. Interrupt fields couple the queue to UV cross-partition notification routes.

Dependencies and integration: includes kernel `struct completion` via the declaration context and depends on GRU cacheline/GPA semantics implemented in the C file. It is used by SGI XP UV transport to create GRU-backed activation and notification queues and by any kernel subsystem using XP/GRU cross-partition services.

Risks: comments make clear the first 32 bits of a message are reserved by the transport, so payload users can corrupt queue semantics if they treat the full payload as application-owned. The receive API requires ordered freeing and single-receiver semantics. Queue memory alignment and physical contiguity are caller obligations.

Test signals: successful use is visible through message queue behavior and the `grukservices.c` quicktests. API misuse is likely to show as message send status codes, stalled receives, or GRU fatal diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grulib.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grulib.h

Purpose: defines the user/kernel ABI for `/dev/gru`, including ioctl numbers, request structures, GSEG address helpers, dump formats, and temporary test/config interfaces. It is the public UAPI-style header for GRU user context management.

Important APIs/types: ioctl IDs include `GRU_CREATE_CONTEXT`, `GRU_SET_CONTEXT_OPTION`, `GRU_USER_GET_EXCEPTION_DETAIL`, `GRU_USER_CALL_OS`, `GRU_USER_UNLOAD_CONTEXT`, `GRU_DUMP_CHIPLET_STATE`, `GRU_GET_GSEG_STATISTICS`, `GRU_USER_FLUSH_TLB`, `GRU_GET_CONFIG_INFO`, and `GRU_KTEST`. Request structures include `gru_create_context_req`, `gru_unload_context_req`, `gru_set_context_option_req`, `gru_flush_tlb_req`, `gru_dump_chiplet_state_req`, `gru_dump_context_header`, `gru_get_gseg_statistics_req`, and `gru_config_info`.

Control flow: users create a GRU context, mmap one or more GSEGs, set placement/options, handle TLB or exception events via ioctl calls, optionally unload or flush, and fetch statistics/dumps for diagnostics. Macros such as `CONTEXT_WINDOW_BYTES()`, `THREAD_POINTER()`, and `GSEG_START()` map between a multi-thread context window and per-thread GSEG addresses.

State and persistence: this header defines ABI data copied between user space and the driver. Persistent kernel state lives in `gru_thread_state`, `gru_vma_data`, and GRU hardware contexts; user-visible request structures identify the GSEG base, selected options, address ranges, dump targets, and output buffers.

Dependencies and integration: depends on GRU constants and `struct gru_gseg_statistics` from lower GRU headers. It is consumed by ioctl handling outside this item and by `grutables.h` declarations that share request structures across driver modules.

Risks: ioctl numbers and structure layouts are ABI, so changes can break user programs. Several comments mark interfaces as primarily for tests or temporary emulator/debug use. Pointer fields in dump requests require careful copy_from_user/copy_to_user validation in ioctl handlers.

Test signals: `GRU_KTEST`, `GRU_GET_CONFIG_INFO`, dumps, statistics, and flush ioctls are explicit validation hooks. Runtime failures should be correlated with exception-detail and gseg-statistics queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grulib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grumain.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grumain.c

Purpose: manages GRU driver tables, resource allocation, ASID assignment, context load/unload, stealing, placement, and fault-time mapping of user GSEGs. It is the central lifecycle manager for user and kernel GRU contexts.

Important APIs/functions: exports `gru_cpu_fault_map_id()`, `gru_alloc_gts()`, `gru_alloc_vma_data()`, `gru_find_thread_state()`, `gru_alloc_thread_state()`, `gru_assign_gru_context()`, `gru_load_context()`, `gru_unload_context()`, `gru_update_cch()`, `gru_check_context_placement()`, `gru_steal_context()`, `gts_drop()`, `gru_reserve_cb_resources()`, `gru_reserve_ds_resources()`, and `gru_fault()`.

Control flow: mmap setup creates `gru_vma_data`; a page fault finds or allocates the caller's `gru_thread_state`, checks placement, assigns chiplet resources if unloaded, loads saved CB/DS/CBE data into hardware, starts the context, and remaps the GRU segment PFN into the VMA. If allocation fails, the thread sleeps briefly and may steal another context after a delay. Unload interrupts/deallocates the CCH, optionally saves context state, updates MMU tracking, frees bitmaps, and drops the GTS reference.

State and persistence: in-memory state includes per-GRU context/CBR/DSR bitmaps, ASID generation/limits, active context arrays, VMA lists of GTS entries, saved context data in `ts_gdata`, and mm notifier trackers. Context state is persistent only while held in `gru_thread_state`; hardware state can be unloaded and later restored.

Dependencies and integration: relies on GRU handle operations, UV topology helpers, MMU notifier state from `grutlbpurge.c`, ioctl/mmap code outside this item, and shared structures from `grutables.h`. It coordinates with kernel services because kernel contexts are represented as GTS objects without `ts_mm`.

Risks: ASID wrap and reuse are correctness-critical for stale TLB avoidance. Context stealing intentionally grabs locks out of normal order with trylocks and is sensitive to races. Fault handling returns `VM_FAULT_NOPAGE` after remapping and must avoid mapping stale contexts after migration. Many hardware failures use `BUG()`.

Test signals: `STAT()` counters track allocation, ASID reuse/wrap, context load/free/steal, placement unloads, and fault activity. Mapping tests should exercise migration, placement options, steal/reload, ASID wrap, and concurrent thread allocation on the same VMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grumain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruprocfs.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruprocfs.c

Purpose: creates `/proc/sgi_uv/gru` diagnostics for the GRU driver. It exposes statistics, microcode-operation timing, debug options, active CCH status, and per-GRU resource status.

Important APIs/functions: `gru_proc_init()` creates the proc subtree and files; `gru_proc_exit()` removes it. `statistics_show()` prints `gru_stats`, `statistics_write()` clears counters, `mcs_statistics_show()` prints MCS operation timing, `mcs_statistics_write()` clears timing, `options_show()` and `options_write()` expose `gru_options`, and seq operations drive `cch_status` and `gru_status`.

Control flow: init creates `statistics`, `mcs_statistics`, `debug_options`, `cch_status`, and `gru_status`. Reads use `seq_file` or `single_open()` callbacks. Writes to the statistics files reset in-memory counters. Writes to debug options parse a user value with `kstrtoul_from_user()`.

State and persistence: proc files are views over volatile in-memory state: `gru_stats`, `mcs_op_statistics`, `gru_options`, and `gru_base` chiplet/context structures. No state persists across module unload or reboot.

Dependencies and integration: depends on `grutables.h` structures and global counters maintained throughout the GRU driver. The proc path is an operational integration point for administrators and tests to inspect active contexts, ASIDs, PIDs, resource availability, and debug/statistics flags.

Risks: status output walks `gru->gs_gts[]` without taking the main context lock, so values are diagnostic snapshots rather than stable transactional views. The `cch_seq_show()` DSR display appears to use `ts_cbr_au_count * GRU_DSR_AU_BYTES` rather than `ts_dsr_au_count`, which is a reporting-risk signal. Reset writes are coarse and can erase concurrent diagnostic evidence.

Test signals: validate proc creation/removal, counter reset behavior, debug option parsing failures, and output shape while contexts are loaded/unloaded. Cross-check `gru_status` free/busy counts against allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruprocfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutables.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutables.h

Purpose: defines the shared internal data model for the GRU driver. It documents GRU hardware layout, state-table relationships, statistics, ASID macros, resource bitmaps, locking helpers, topology helpers, and cross-file function prototypes.

Important APIs/types: core structures are `gru_stats_s`, `mcs_op_statistic`, `gru_mm_tracker`, `gru_mm_struct`, `gru_vma_data`, `gru_thread_state`, `gru_state`, and `gru_blade_state`. Key macros include `STAT()`, `GRUASID()`, `TSID()`, `UGRUADDR()`, `GID_TO_GRU()`, `for_each_gru_on_blade()`, `for_each_cbr_in_allocation_map()`, and CCH/TGH lock helpers.

Control flow: this header does not execute control flow, but it encodes the relationships used by the C files: VMA data owns a list of GTS objects; GTS references an mm tracker and possibly a loaded GRU/context number; GRU state owns resource maps and active GTS pointers; blade state owns chiplets and kernel context state. The function prototypes connect mmap/fault, MMU notifier, interrupt, proc, kernel-service, and ioctl paths.

State and persistence: all defined state is volatile kernel memory or GRU hardware mapping state. `gru_thread_state::ts_gdata` is the software save area used to persist a context across hardware unloads. `gru_mm_struct` tracks ASIDs and active context bitmaps per address space for TLB shootdown.

Dependencies and integration: includes Linux mm, notifier, wait, mutex, and interrupt headers plus GRU handle and ABI headers. It is the integration backbone between `grumain.c`, `grutlbpurge.c`, `gruprocfs.c`, interrupts, ioctl handlers, and kernel services.

Risks: structure fields are protected by different locks (`gs_lock`, `gs_asid_lock`, `vd_lock`, `ts_ctxlock`, `bs_lock`, `bs_kgts_sema`), so callers must honor the intended lock ownership. Topology macros for Nehalem-EX CPU IDs are hardware-specific. Packed ASID trackers and bitmaps have capacity assumptions tied to `GRU_MAX_GRUS`.

Test signals: compile-time coverage is important because this header drives many modules. Runtime validation should inspect stats, ASID maps, context bitmaps, resource maps, and lock-sensitive paths under migration, fault, unload, and TLB invalidation workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutlbpurge.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutlbpurge.c

Purpose: integrates GRU TLB invalidation with Linux MMU notifier callbacks and provides low-level TGH-based flush helpers. It keeps GRU translations coherent with process address-space changes.

Important APIs/functions: exported helpers are `gru_flush_tlb_range()`, `gru_flush_all_tlb()`, `gru_register_mmu_notifier()`, `gru_drop_mmu_notifier()`, and `gru_tgh_flush_init()`. Internal helpers select and lock local or remote TGH handles, allocate/free notifier state, and implement `invalidate_range_start`/`invalidate_range_end`.

Control flow: when a range invalidation begins, the notifier increments `ms_range_active`, flushes GRU TLB entries for every GRU recorded in the address-space ASID map, and then completion of the invalidation decrements the range count and wakes waiters. For each GRU, active contexts receive a TGH invalidate command using the context bitmap; inactive contexts have their ASID cleared so a future load receives a fresh ASID. Full-chiplet flushes use a TGH invalidate over all ASIDs/contexts.

State and persistence: per-mm `gru_mm_struct` tracks `ms_asidmap` and `ms_asids[]` under `ms_asid_lock`, plus active invalidation count and wait queue. `gru_state` stores TGH selection parameters initialized by `gru_tgh_flush_init()`.

Dependencies and integration: depends on Linux MMU notifier APIs, UV topology, GRU TGH handle operations, and ASID state loaded in `grumain.c`. TLB preload/dropin paths outside this item observe `ms_range_active` and wait queues.

Risks: stale translations are the primary correctness risk. The code currently notes huge pages as TODO and uses `PAGE_SHIFT`. TGH selection uses private handles for local CPUs and locked shared handles for off-blade flushes; contention or bad topology setup can harm latency. Clearing ASIDs for inactive contexts trades correctness for future TLB-miss cost.

Test signals: exercise mmap/unmap/mprotect/fork/exit while GRU contexts are active, verify `flush_tlb*` stats, check ASID clearing on inactive contexts, and stress remote/off-blade invalidations and range-active waiters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutlbpurge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/Makefile

Purpose: wires SGI XP-related modules into the kernel build for `CONFIG_SGI_XP`. It defines object composition for the XP base module, XPC communication module, and xpnet module.

Important build entries: `xp.o` is built from `xp_main.o xp_uv.o`; `xpc.o` is built from `xpc_main.o xpc_channel.o xpc_partition.o xpc_uv.o`; `xpnet.o` is also selected by `CONFIG_SGI_XP`.

Control flow: there is no runtime control flow, but build-time composition determines which implementation files are linked into each module. The UV-specific files are included directly in the object lists, so the C code performs runtime/platform gating through `is_uv_system()` and compile-time guards.

State and persistence: no persistent state. The Makefile controls module boundaries and symbol ownership.

Dependencies and integration: `xp.o` exports the public XP interface and UV address/copy hooks. `xpc.o` consumes those XP hooks and provides channel/partition messaging. `xpnet.o` likely uses XP/XPC channels for network transport outside this work item.

Risks: because both `xp.o` and `xpc.o` are gated by the same config, callers may still see XP loaded without XPC initialized until `xpc_set_interface()` runs. Build failures in `xpc_uv.o` or `xpnet.o` can surface even when this subset looks self-contained.

Test signals: kernel build with `CONFIG_SGI_XP=y/m`, module link symbol checks, and load/unload sequencing for `xp`, `xpc`, and `xpnet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp.h

Purpose: defines the public XP/XPC interface used by kernel-level cross-partition clients. It provides partition/channel limits, message size constraints, status codes, callback signatures, registration records, exported interface wrappers, and architecture hooks.

Important APIs/types: `enum xp_retval` is the central status/reason code set. Callback types are `xpc_channel_func` and `xpc_notify_func`. `struct xpc_registration` stores per-channel client registration. `struct xpc_interface` is the runtime dispatch table populated by XPC. Public functions are `xpc_connect()`, `xpc_disconnect()`, `xpc_send()`, `xpc_send_notify()`, `xpc_received()`, and `xpc_partid_to_nasids()`.

Control flow: clients register a channel with message size, queue depth, kthread limits, and a channel callback. XP stores the registration and, if XPC is loaded, asks XPC to connect. Sends go through inline wrappers that return `xpNotLoaded` when XPC has not installed its interface. Received payloads must be acknowledged with `xpc_received()`.

State and persistence: global exported state includes local partition identity, maximum partitions, region size, architecture function pointers, `xpc_registrations[]`, and `xpc_interface`. All are volatile module state.

Dependencies and integration: includes UV headers when configured and is shared by XP base, XPC, and clients such as xpnet. The message sizing macro aligns differently on UV versus non-UV systems and enforces the 128-byte maximum.

Risks: callback functions have strict context requirements; notify callbacks must not block. Registration limits (`assigned_limit`, `idle_limit`) directly affect kthread fan-out. The enum is append-sensitive because values are externally meaningful as callout reasons. Inline wrappers rely on interface pointer consistency during module unload.

Test signals: validate payload size rejection, duplicate registration, disconnect wait semantics, send behavior before XPC load, callback reason propagation, and correct `xp_retval` mapping under partition/channel failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_main.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_main.c

Purpose: implements the XP base module, exports cross-partition service hooks and channel registration state, and decouples XP clients from the XPC module's load state.

Important APIs/functions: exports `xp`, `xp_max_npartitions`, `xp_partition_id`, `xp_region_size`, architecture function pointers, `xpc_registrations`, and `xpc_interface`. `xpc_set_interface()` and `xpc_clear_interface()` are called by XPC load/unload. `xpc_connect()` registers a channel; `xpc_disconnect()` unregisters a channel and asks XPC to tear down active connections.

Control flow: module init initializes registration mutexes and calls `xp_init_uv()` on UV systems. Client registration validates payload sizing and channel parameters, records registration fields under the channel mutex, and triggers `xpc_interface.connect()` if available. Disconnect clears the registration under the mutex and then invokes `xpc_interface.disconnect()`.

State and persistence: all state is module-global and volatile. The XP interface table is zero when XPC is not loaded. Registrations persist while XP remains loaded, allowing XPC to connect newly active partitions after registration.

Dependencies and integration: depends on `xp.h` and UV backend initialization. XPC depends on XP by calling `xpc_set_interface()` and reading `xpc_registrations[]`. XP clients depend only on this base layer and receive `xpNotLoaded` when XPC dispatch is absent.

Risks: disconnect invokes the XPC disconnect hook while holding the registration mutex, so XPC paths must avoid deadlocks with registration operations. Interface pointer updates are simple assignments/zeroing and depend on module lifecycle ordering. `DBUG_ON()` compiles to no-op unless debug mode is enabled, so production validation relies on explicit returns.

Test signals: module init on UV/non-UV, registration success/failure cases, duplicate registration, oversized payload rejection, XPC absent send behavior, and unload sequencing with registered channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_uv.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_uv.c

Purpose: supplies UV-specific implementations for XP address translation, remote memory copy, CPU-to-NASID conversion, and BIOS memory protection operations. It connects XP/XPC transport to GRU kernel services.

Important APIs/functions: `xp_init_uv()` installs UV hooks into XP globals; `xp_exit_uv()` validates platform exit. Internal hook implementations include `xp_pa_uv()`, `xp_socket_pa_uv()`, `xp_remote_memcpy_uv()`, `xp_remote_mmr_read()`, `xp_cpu_to_nasid_uv()`, `xp_expand_memprotect_uv()`, and `xp_restrict_memprotect_uv()`.

Control flow: initialization checks `is_uv_system()`, sets partition count and partition/region identity, then assigns function pointers. Remote copies route MMR-space reads through `gru_read_gpa()` with an 8-byte constraint; other memory copies use `gru_copy_gpa()`. BIOS memory protection hooks call `uv_bios_change_memprotect()` to allow or restrict access.

State and persistence: no private persistent state. It mutates XP global function pointers and exported partition metadata during init.

Dependencies and integration: depends on UV hub/BIOS APIs and `../sgi-gru/grukservices.h`. XPC partition discovery and reserved-page reads use `xp_remote_memcpy`, so GRU service availability is a runtime prerequisite for cross-partition operation.

Risks: failures in GRU copy/read map to `xpGruCopyError` after logging. `xp_remote_mmr_read()` asserts source is MMR space and length is exactly 8 bytes. BIOS memory-protection changes are platform-specific and return `xpBiosError` on firmware failure. Non-x86_64 paths are explicitly unsupported.

Test signals: UV boot/module init, remote reserved-page copy, MMR read path, GRU copy failure injection, BIOS memprotect allow/restrict calls, and non-UV init returning unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_uv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc.h -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc.h

Purpose: defines XPC's internal partition, channel, reserved-page, heartbeat, message, state-machine, and architecture-operation contracts. It is the shared private header for `xpc_main.c`, `xpc_channel.c`, `xpc_partition.c`, and UV-specific XPC code.

Important APIs/types: key structures include `xpc_rsvd_page`, `xpc_heartbeat_uv`, `xpc_gru_mq_uv`, activation message variants, `xpc_openclose_args`, UV FIFO/message-slot types, `xpc_channel_uv`, `xpc_channel`, `xpc_partition_uv`, `xpc_partition`, and `xpc_arch_operations`. It defines channel flags, chctl flags, partition activation/setup states, default heartbeat/disengage tunables, and refcount helpers.

Control flow: the header encodes the major state machines: reserved page setup advertises heartbeat and activation queue addresses; partition activation transitions from inactive to activation requested, activating, active, and deactivating; channels move through open request/reply/complete and close request/reply flags; kthreads deliver payloads and manage disconnect callouts. `xpc_arch_operations` abstracts UV/SN transport details such as heartbeat, chctl sends, message queues, and engagement.

State and persistence: XPC state is volatile in `xpc_partitions[]`, per-channel message queues, cached remote descriptors, heartbeat values, chctl bitfields, timers, wait queues, atomics, and references. The reserved page is a shared firmware/platform memory area whose timestamp advertises initialization.

Dependencies and integration: includes `xp.h` for public return codes and registration/callback contracts. UV architecture code fills `xpc_arch_ops`. XP base installs XPC entry points after XPC init.

Risks: many flags can coexist transiently; invalid combinations are guarded mostly by `DBUG_ON()`. Refcount helpers are central to avoiding use-after-free of partition infrastructure and message queues. Message sizes must stay within one or two GRU cachelines. Reserved page version major mismatch rejects peers.

Test signals: state-machine coverage for activation, reactivation, heartbeat loss, open/close races, disconnect wait, message delivery/ack, notifier completion, and architecture-operation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_channel.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_channel.c

Purpose: implements XPC channel connection/disconnection protocol and send/receive entry points. It manages per-channel state, message queue references, user callouts, and kthread activation for message delivery.

Important APIs/functions: external functions include `xpc_process_sent_chctl_flags()`, `xpc_partition_going_down()`, `xpc_initiate_connect()`, `xpc_connected_callout()`, `xpc_initiate_disconnect()`, `xpc_disconnect_channel()`, `xpc_disconnect_callout()`, `xpc_allocate_msg_wait()`, `xpc_initiate_send()`, `xpc_initiate_send_notify()`, `xpc_deliver_payload()`, and `xpc_initiate_received()`. Core internal state-machine helpers are `xpc_process_connect()`, `xpc_process_disconnect()`, `xpc_process_openclose_chctl_flags()`, and `xpc_connect_channel()`.

Control flow: channel connection requires local and remote open requests, message structure setup, open replies, open complete messages, and final connected flags. Disconnect sends close request, waits for local kthreads/references and remote close protocol or partition disengagement, notifies blocked senders, tears down message structures, clears registration-derived fields, and completes unregister waiters. Send APIs reference the partition, delegate payload placement to `xpc_arch_ops.send_payload()`, and dereference. Receive delivery obtains an architecture-provided payload, takes a message-queue reference, calls the registered channel callback, and requires user acknowledgment through `xpc_initiate_received()`.

State and persistence: channel fields track flags, reason/line, queue sizes, callback/key, kthread counts, message allocation waiters, notify counts, and delayed chctl flags. State is per active remote partition and not persistent across teardown.

Dependencies and integration: depends on XP registrations, XPC partition references, architecture operations for all transport-specific queue/chctl work, and kthread management in `xpc_main.c`.

Risks: open/close races are complex, especially delayed flags while `XPC_C_WDISCONNECT` is set. Callouts may run with locks held in some notify paths and must obey non-blocking requirements where documented. Failure to pair payload delivery with `xpc_received()` holds message-queue references and can block teardown. Message-size mismatches disconnect the channel.

Test signals: exercise simultaneous open/close, registration/unregistration while partitions are active, queue exhaustion with wait/nowait, notify callbacks on disconnect, missing receive acknowledgments, partition going down, and architecture send/setup failure returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_channel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_main.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_main.c

Purpose: implements the XPC module core: heartbeat thread, discovery thread, partition activation manager, channel-manager/kthread lifecycle, sysctl tunables, reboot/die notifiers, module init, and orderly exit.

Important APIs/functions: exports devices `xpc_part` and `xpc_chan`, global `xpc_arch_ops`, wake/IRQ state, and helpers such as `xpc_kzalloc_cacheline_aligned()`, `xpc_activate_partition()`, `xpc_activate_kthreads()`, `xpc_create_kthreads()`, and `xpc_disconnect_wait()`. Internal key functions include `xpc_hb_checker()`, `xpc_channel_mgr()`, `xpc_setup_ch_structures()`, `xpc_activating()`, `xpc_kthread_start()`, `xpc_setup_partitions()`, `xpc_do_exit()`, and notifier callbacks.

Control flow: init selects UV operations, allocates partition structures, registers sysctls, sets up the local reserved page, registers reboot/die notifiers, starts heartbeat and discovery kthreads, then installs XP-facing XPC entry points. The heartbeat checker increments local heartbeat, checks remote heartbeats, and processes activation IRQs. Partition activation spawns a per-partition kthread that sets up channels, makes first contact, marks active, and runs the channel manager until deactivation. Channel worker kthreads issue connected/disconnecting callouts and deliver payloads until the channel disconnects.

State and persistence: module-global volatile state includes tunables, timers, completions, IRQ counters, partition array, architecture ops, and `xpc_exiting`. Sysctl changes persist only while loaded. Reserved-page timestamp advertises local XPC readiness to peers.

Dependencies and integration: depends on XP base, `xpc_partition.c`, `xpc_channel.c`, UV-specific `xpc_uv.c`, Linux kthreads/timers/sysctl/reboot/die notifiers, and architecture callbacks.

Risks: shutdown must coordinate discovery, heartbeat, active partitions, engagement timeouts, callouts, and XP interface clearing. Die notifier paths use polling/udelay and intentionally bypass normal sleep-heavy teardown. Kthread creation failures can disconnect channels or abort init. CPU pinning to CPU 0 for heartbeat checking is topology-sensitive.

Test signals: module load/unload, sysctl bounds, heartbeat timeout behavior, discovery completion, partition activation/deactivation, kthread limit behavior, reboot/die notifier deactivation, and disengage timeout logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_partition.c -->
# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_partition.c

Purpose: implements XPC partition discovery and partition activation/deactivation support. It handles reserved-page setup/teardown, remote reserved-page reads, NASID discovery, disengage timeout handling, partition active/inactive transitions, and partid-to-NASID lookups.

Important APIs/functions: exports `xpc_kmalloc_cacheline_aligned()`, `xpc_setup_rsvd_page()`, `xpc_teardown_rsvd_page()`, `xpc_get_remote_rp()`, `xpc_partition_disengaged()`, `xpc_partition_disengaged_from_timer()`, `xpc_mark_partition_active()`, `xpc_deactivate_partition()`, `xpc_mark_partition_inactive()`, `xpc_discovery()`, and `xpc_initiate_partid_to_nasids()`. It owns globals `xpc_exiting`, `xpc_rsvd_page`, `xpc_mach_nasids`, `xpc_nasid_mask_nlongs`, and `xpc_partitions`.

Control flow: local setup locates the firmware reserved page, validates partition identity, fills XPC version and NASID mask metadata, lets architecture code append transport fields, then sets `ts_jiffies` to advertise readiness. Discovery scans hardware regions/NASIDs from SAL masks, skips local or already discovered partitions, copies remote reserved pages with `xp_remote_memcpy()`, validates version and partition IDs, and requests activation. Deactivation moves the partition to deactivating, sends architecture deactivation request, starts a disengage timer, and asks channels to go down.

State and persistence: local reserved page fields are shared platform memory but initialized at runtime; `ts_jiffies` is the readiness marker and is reset to zero on teardown. Remote partition state is cached in `xpc_partition` entries, including `remote_rp_pa`, heartbeat metadata, act_state, reason, and timer state.

Dependencies and integration: depends on XP architecture hooks for reserved-page lookup/copy, heartbeat engagement, activation requests, and memory address conversion. XPC main uses these functions during init, discovery, activation, and exit.

Risks: reserved-page version or partid mismatch prevents activation. Discovery depends on correct NASID masks and region-size interpretation. `xpc_initiate_partid_to_nasids()` computes a remote mask address from `remote_rp_pa`, so stale remote reserved-page addresses after partition down would be unsafe; it guards on zero. Disengage timeout can force-assume a peer is dead.

Test signals: reserved-page setup with SAL version variants, remote copy failures, major-version mismatch, local-partition detection, discovery over region masks, activation request issuance, deactivation timeout, reactivation reason handling, and partid-to-NASID behavior when remote partition is down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_partition.c -->
