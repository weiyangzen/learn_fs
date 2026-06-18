# Research: subset-b-007643

Grouped research for `subset-b-007643`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c_research.md`.

Purpose: implements the `/proc` diagnostics and test controls for the Lustre GNI LND. It exposes aggregate device counters, memory descriptor debug views, SMSG/FMA mailbox inventory, connection and peer listings, per-peer connection tracing, and a write-only checksum benchmark.

Important APIs/types/functions: proc entry names are `stats`, `mdd`, `smsg`, `conn`, `peer_conns`, `peer`, and `cksum_test`. `_kgnilnd_proc_run_cksum_test()` allocates bio_vec pages and compares `kgnilnd_cksum_kiov()` over copied data. `kgnilnd_stats_seq_show()` and `kgnilnd_proc_stats_write()` sample and reset counters. Iterator structs `kgn_mdd_seq_iter_t`, `kgn_smsg_seq_iter_t`, `kgn_conn_seq_iter_t`, and `kgn_peer_seq_iter_t` back seq-file walkers. `kgnilnd_proc_init()` creates the tree and `kgnilnd_proc_fini()` removes it.

Control flow: init creates the proc directory named from `libcfs_lnd2modname(GNILND)`, then registers checksum, stats, MDD, SMSG, connection, per-peer connection, and peer files with unwind labels on failure. Reads enter seq-file start/seek/show/next/stop callbacks. MDD iteration locks the device map list for the read pass, SMSG iteration versions and locks FMA blocks around individual seeks/shows, and peer/connection walkers use `kgn_peer_conn_lock` with version checks plus temporary refcounts. Writes either parse small user buffers or reset sampled counters.

State and persistence behavior: no durable state is stored. The proc files expose live global `kgnilnd_data`, device atomics, peer/connection lists, FMA memory blocks, and transmit map state. `stats` write clears selected counters with a write barrier. `peer_conns` stores a global debug NID until changed. Iterators detect list mutation using version counters and may return `-ESTALE`.

Dependencies and integration: depends on `gnilnd.h`, Linux procfs/seq_file, Lustre libcfs allocation/logging helpers, LNet NID formatting, GNI memory handle fields, and internal peer/connection/FMA structures. The checksum test integrates with LNet iov copy helpers and GNI checksum code.

Risks: several readers intentionally sample racy state; MDD holds a spinlock over seq traversal, which can be intrusive on large maps. `smsg_seq_next()` frees the iterator on seek failure even though `stop()` may also run, so error-path ownership is delicate. User-triggered checksum tests can allocate many pages and run long loops. Proc teardown order must match creation order.

Test signals: mount procfs and read each file before and after traffic, reset `stats` and confirm selected counters clear, exercise checksum cases 0-3 with odd/even offsets, mutate peers/connections while reading for `-ESTALE` behavior, set `peer_conns` to valid and invalid NIDs, and verify init unwind leaves no partial proc entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c_research.md`.

Purpose: handles GNI LND hardware quiesce, timeout bumping, critical-error reset, and optional RCA node-state monitoring. It is the recovery path used when Gemini/GNI hardware pauses or reports unrecoverable errors.

Important APIs/types/functions: `kgnilnd_bump_timeouts()` refreshes peer, connection, TX, and datagram timers after a pause. `kgnilnd_quiesce_wait()` transitions all worker threads into or out of quiescence. `kgnilnd_reset_stack()` tears down and recreates device resources. `kgnilnd_ruhroh_thread()` serializes quiesce and reset work. `kgnilnd_pause_threads()`, `kgnilnd_hw_in_quiesce()`, `kgnilnd_check_hw_quiesce()`, `kgnilnd_quiesce_end_callback()`, and `kgnilnd_critical_error()` are the hardware event entry points. Under `GNILND_USE_RCA`, `kgnilnd_rca()` subscribes to RCA events and reports peer up/down state.

Control flow: a quiesce or callback sets global flags and wakes the ruhroh waitqueue. The ruhroh thread locks `kgn_quiesce_mutex`, sets `kgn_quiesce_trigger`, wakes LND worker queues, waits until `GNILND_IS_QUIESCED`, handles timeout-bump callbacks, then clears the trigger and waits for workers to resume. Reset flow first quiesces, cancels network datagrams and connections, drains ready/purgatory lists, asserts all hardware resources are gone, finalizes devices, reinitializes devices/datagrams/FMA blocks, bumps timers by reset duration, and resumes traffic.

State and persistence behavior: all state is in live globals: quiesce trigger, reset/pause flags, bump duration, reset count, connection lists, peer queues, device counters, datagrams, and optional RCA subscription tickets. Barriers (`set_mb`, `smp_rmb`) enforce visibility between interrupt callbacks and the ruhroh thread. No state persists across module unload.

Dependencies and integration: tightly coupled to GNI device lifecycle (`kgnilnd_dev_init/fini`, datagram cancellation, FMA mapping), peer/connection locks, LNet peer notification, wait queues, timers, and optional Cray RCA APIs (`krca_register`, `krca_subscribe`, `krca_wait_event`, `krca_get_sysnodes`).

Risks: reset is assert-heavy and can panic if resources remain. Quiesce waits scale with timeout tunables and can stall if a worker fails to check in. Nested loops reuse `i` in `kgnilnd_bump_timeouts()` while walking devices/datagram buckets, which is easy to break during edits. Callback overwrites of bump information are acknowledged as possible but assumed rare. RCA filtering must not report irrelevant service/GPU events as LNet peer changes.

Test signals: inject hardware quiesce callbacks and critical errors, verify all worker threads pause/resume, run traffic through reset and confirm peer notifications and reconnects, validate no live FMA blocks/EPs/connections remain before reinit, test shutdown races, and exercise RCA up/down/unavailable events when built with RCA support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c_research.md`.

Purpose: registers `/proc/sys/kgnilnd` controls for administrative GNI LND diagnostics and fault handling, including manual thread pause, hardware quiesce completion, stack reset, RDMAQ throttling override, and peer up/down injection.

Important APIs/types/functions: `kgn_sysctl_data_t` stores writable values. Handlers include `proc_toggle_thread_pause()`, `proc_hw_quiesce()`, `proc_trigger_stack_reset()`, `proc_toggle_rdmaq_override()`, and `proc_peer_state()`. `kgnilnd_insert_sysctl()` registers the ctl table and `kgnilnd_remove_sysctl()` unregisters it. Stub versions are compiled when `CONFIG_SYSCTL` is absent.

Control flow: sysctl writes first pass through `proc_dointvec` or `proc_dostring`, then validate `kgnilnd_data.kgn_init == GNILND_INIT_ALL` before mutating driver state. Thread pause changes copy into `kgn_quiesce_trigger` under `kgn_quiesce_mutex` and call `kgnilnd_quiesce_wait()`. Hardware quiesce writes call `kgnilnd_quiesce_end_callback()` on device 0. Stack reset calls `kgnilnd_critical_error()` and spins until `kgn_needs_reset` clears. Peer-state writes parse `up|down nid` and call `kgnilnd_report_node_state()`.

State and persistence behavior: sysctl values live in static `kgnilnd_sysctl`; effects are live kernel state only. `rdmaq_override` converts MiB/s to bytes/s and stores `kgn_rdmaq_override` with a write barrier. The registration header pointer prevents duplicate table registration and is nulled on removal.

Dependencies and integration: depends on Linux sysctl tables, Lustre version string, GNI quiesce/reset helpers, GNI device 0 handles, LNet node-state reporting, and global LND initialization flags.

Risks: `stack_reset` is a privileged destructive test hook and can block until reset completes. `sscanf("%s %d")` into a 10-byte command buffer depends on the sysctl string length cap. Device 0 assumptions mirror other GNI stack code and must hold for multi-device changes. Admin writes during partial init return errors.

Test signals: register/unregister with and without `CONFIG_SYSCTL`, read version, toggle thread pause and confirm all threads quiesce/resume, trigger stack reset and observe flag clearing, set RDMAQ override and inspect bytes value, inject peer up/down commands including malformed strings, and verify writes before full init fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile_research.md`.

Purpose: builds the in-kernel OFED variant of Lustre's o2iblnd module by deriving sources from the sibling `o2iblnd` directory and rewriting OFED feature macros for the in-kernel namespace.

Important APIs/types/functions: kbuild target `obj-m += ko2iblnd.o`; object list `ko2iblnd-objs := o2iblnd.o o2iblnd_cb.o o2iblnd_modparams.o`; generated-source target `sources`; `o2ib_sed_flags` rewrites `HAVE_OFED_` to `IN_KERNEL_HAVE_OFED_`.

Control flow: the `sources` target depends on generated headers and C files. Each generated file has a rule that runs `sed $(o2ib_sed_flags)` over the corresponding `../o2iblnd/` source. Optional `CONFIG_GCOV_PROFILE_LNET` sets `GCOV_PROFILE := y`.

State and persistence behavior: generated files persist in the build tree until cleaned. The Makefile itself carries no runtime state.

Dependencies and integration: depends on kbuild module semantics, sibling external o2iblnd sources, sed, and Lustre's in-kernel OFED compatibility macros.

Risks: regex rewriting is broad by token prefix and can miss nonstandard feature names or rewrite unintended text. Generated files can become stale if source generation is skipped. Object lists must stay synchronized with the external o2iblnd module.

Test signals: run `make sources`, diff generated files for only expected macro rewrites, build with in-kernel OFED headers, build with GCOV enabled, and verify changes in `../o2iblnd` trigger regenerated files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/in-kernel-o2iblnd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile_research.md`.

Purpose: declares the kfabric LND kernel module and its compilation units.

Important APIs/types/functions: kbuild emits `kkfilnd.o` from `kfilnd.o`, `kfilnd_modparams.o`, `kfilnd_tn.o`, `kfilnd_ep.o`, `kfilnd_dev.o`, `kfilnd_dom.o`, `kfilnd_peer.o`, `kfilnd_cq.o`, and `kfilnd_debugfs.o`. It adds `$(KFICPPFLAGS)` to `ccflags-y` and enables `GCOV_PROFILE` when requested.

Control flow: kbuild compiles each listed source and links them into the module. The object order places the LNet entry point and module parameters before transaction, endpoint, device, domain, peer, completion, and debugfs helpers.

State and persistence behavior: build-only file; no runtime state.

Dependencies and integration: integrates with Lustre/LNet kbuild and kfabric provider headers supplied through `KFICPPFLAGS`.

Risks: any new source file must be added here or it will be omitted. Missing `KFICPPFLAGS` causes kfabric include failures. GCOV flag affects instrumentation across the whole module.

Test signals: build `kkfilnd.o` with and without kfabric provider flags, check module symbols resolve, enable `CONFIG_GCOV_PROFILE_LNET`, and verify each object appears in the final module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c_research.md`.

Purpose: provides the main kfabric LND integration with LNet: module init/exit, NI startup/shutdown, send/receive entry points, tunable netlink export, and device-priority lookup.

Important APIs/types/functions: global `kfilnd_wq` and `kfilnd_debug_dir`; LNet callbacks `kfilnd_startup()`, `kfilnd_shutdown()`, `kfilnd_send()`, `kfilnd_recv()`, `kfilnd_tun_defaults()`, `kfilnd_nl_get()`, `kfilnd_nl_set()`, and `kfilnd_get_dev_prio()`; hello helper `kfilnd_send_hello_request()`; `the_kfilnd` registration; `kfilnd_init()` and `kfilnd_exit()`.

Control flow: init creates debugfs, validates tunables, initializes libcfs and transaction mempools, creates the workqueue, then registers the LND. Startup validates LND type, applies tunables, requires one interface string, allocates a kfabric device, records device CPT, and posts immediate receive buffers. Sends classify LNet ACK/GET/PUT/REPLY as immediate or bulk based on size, routing, and GPU buffers, allocate a transaction/key, trigger hello if needed, copy immediate payloads or map bulk buffers, then enter the transaction state machine. Receives complete immediate payload copies or set up target-side bulk RMA and feed transaction events.

State and persistence behavior: runtime state lives under `struct kfilnd_dev` in `ni->ni_data`, per-peer hello state, per-transaction buffers/status, debugfs entries, and the module workqueue. Module parameters and NI tunables determine provider version, auth key, traffic class, credits, and timeout. No durable state is stored.

Dependencies and integration: depends on LNet `struct lnet_lnd`, LNet message/finalization APIs, kfilnd transaction/device/tunable helpers, debugfs, workqueues, kfabric provider headers, GPU detection via `lnet_md_is_gpu()`, and netlink attribute helpers.

Risks: the immediate send path returns `-EFAULT` on failed copy without freeing the allocated transaction, which deserves review. The receive default case notes a TODO leak. Hello throttling can delay or cancel sends to new/stale peers. GET reply creation and bulk buffer mapping must be unwound correctly on errors. Module init has an error path after `libcfs_setup()` that may not mirror all setup steps.

Test signals: register/unregister LND, startup with missing/wrong interface, immediate ACK/PUT/GET/REPLY traffic, bulk PUT/GET including GPU buffers, hello negotiation with new/stale peers, netlink get/set of kfilnd tunables, shutdown with live receives, and fail-location tests for allocation/copy/map errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h_research.md`.

Purpose: central private header for the kfabric LND. It defines constants, fail-location IDs, tunable attributes, core objects, wire protocol, transaction states/events, stats buckets, and shared externs/prototypes.

Important APIs/types/functions: defines `KFILND_VERSION`, `KFILND_IMMEDIATE_MSG_SIZE`, `KFILND_EP_KEY_BITS/MAX`, `KFILND_BASE_ADDR()`, CFS fail codes, object states, netlink tunable attributes, `struct kfilnd_immediate_buffer`, `struct kfilnd_cq`, `struct kfilnd_ep`, `struct kfilnd_peer`, `struct kfilnd_fab`, `struct kfilnd_dom`, `struct kfilnd_dev`, wire messages (`kfilnd_hello_msg`, `kfilnd_immed_msg`, `kfilnd_bulk_req_msg`, `_v2`, `kfilnd_msg`), `enum kfilnd_msg_type`, `enum tn_states`, `enum tn_events`, and `struct kfilnd_transaction`.

Control flow: not executable, but it encodes the legal transaction states and events consumed by `kfilnd_tn.c`, message layouts packed/unpacked by transaction code, endpoint/peer/device relationships, and debug/stat structures printed by debugfs.

State and persistence behavior: declares all major in-memory state. Endpoints own KFI contexts, CQs, replay queues, immediate buffers, and IDA key allocation. Peers cache KFI addresses, session keys, hello state, health state, and RCU/refcount metadata. Devices own domain/AV/scalable endpoint, CPT endpoint maps, peer cache, stats, and debugfs dentries. Transactions own LNet messages, peer refs, KFI operation context, message buffers, timeout work/timer, bulk buffer mappings, keys, status, and replay metadata.

Dependencies and integration: includes Linux kernel, libcfs, LNet, LNet RDMA, and kfabric headers (`kfi_endpoint`, `kfi_rma`, `kfi_tagged`, `kfi_cxi_ext`). Externs connect module params, debugfs operations, workqueue, tunable setup, and transaction mempool stats.

Risks: this header is a high-blast-radius ABI/contract point. Wire structs are packed and versioned; incompatible edits break interop. `KFILND_EP_KEY_BITS` limits credits and RKEY space. State/event enum ordering is baked into debug output and dispatch tables. Feature conditionals around `HAVE_KFI_SGL` split DMA mapping behavior.

Test signals: compile all kfilnd files under both SGL and non-SGL configurations, run protocol version 1/2 bulk tests, validate debugfs state names match enum tables, test max credits/key exhaustion, and use fail codes to exercise each event/state edge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c_research.md`.

Purpose: drains kfabric completion queues and translates provider completion/error records into kfilnd transaction events or immediate-buffer reposts.

Important APIs/types/functions: `kfilnd_cq_process_error()` maps `kfi_cq_err_entry` flags to `TN_EVENT_*` and statuses. `kfilnd_cq_process_event()` maps successful `kfi_cq_data_entry` completions. `kfilnd_cq_process_completion()` drains events and error queues. `kfilnd_cq_completion()` is the KFI CQ callback that queues per-CPT work. `kfilnd_cq_alloc()` and `kfilnd_cq_free()` manage CQ objects.

Control flow: provider callback queues one work item per CPU in the endpoint CPT, optionally skipping the provider's signaling-vector CPU when `prov_cpu_exclusive` is set. Work repeatedly calls `kfi_cq_read()`, handles `-KFI_EAVAIL` by draining `kfi_cq_readerr()`, processes successful events, exits on `-EAGAIN`, and flushes endpoint replay queues if pending. Immediate receive completions call `kfilnd_tn_process_rx_event()` and repost/release multi-receive buffers; tagged/RMA/send completions call `kfilnd_tn_event_handler()`.

State and persistence behavior: each `struct kfilnd_cq` persists for an endpoint lifetime and owns flexible-array work items bound to CPT CPUs. It does not persist completion history; transaction and endpoint state are updated synchronously by event handlers.

Dependencies and integration: depends on KFI CQ APIs, endpoint replay helpers, transaction event handler, immediate-buffer handling, workqueues, CPT CPU masks, and byte-order conversion for remote CQ data status.

Risks: exact flag combinations drive event classification; provider changes can trip `LBUG()`. `kfilnd_cq_free()` flushes the global workqueue before closing the CQ, which can affect unrelated endpoint work. Error status is negated from provider errno and must match transaction health semantics. Remote CQ data is interpreted as big-endian absolute errno.

Test signals: generate send, receive, tagged receive, RMA read/write, cancel, and error completions; inject fake errors from fail locations; test `prov_cpu_exclusive`; verify replay flush after `-EAGAIN`; and run teardown while CQ work is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h_research.md`.

Purpose: declares the completion-queue interface used by endpoints and fail-location error injection.

Important APIs/types/functions: exports `kfilnd_cq_process_error()`, `kfilnd_cq_alloc()`, and `kfilnd_cq_free()` over `struct kfilnd_ep`, `struct kfi_cq_err_entry`, `struct kfi_cq_attr`, and `struct kfilnd_cq`.

Control flow: endpoint allocation calls `kfilnd_cq_alloc()` for RX and TX CQs; endpoint teardown calls `kfilnd_cq_free()`; fake endpoint errors can call `kfilnd_cq_process_error()` asynchronously.

State and persistence behavior: no state is defined here beyond function contracts; concrete CQ state is in `kfilnd.h` and `kfilnd_cq.c`.

Dependencies and integration: includes `kfilnd.h`, so it inherits kfabric and LNet private structures.

Risks: this header exposes error processing, so callers must only pass provider-shaped error records and live endpoints.

Test signals: compile inclusion from endpoint and CQ modules, inject fake errors through `kfilnd_ep_gen_fake_err()`, and verify RX/TX CQ allocation/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c_research.md`.

Purpose: implements kfilnd debugfs files for transaction latency/state statistics, stats reset, and mempool reserve visibility.

Important APIs/types/functions: helpers `get_ave_duration()`, `get_min_duration()`, `seq_print_tn_state_stats()`, and `seq_print_tn_stats()` format per-size-bucket metrics. File operations exported are `kfilnd_initiator_state_stats_file_ops`, `kfilnd_target_state_stats_file_ops`, `kfilnd_initiator_stats_file_ops`, `kfilnd_target_stats_file_ops`, `kfilnd_reset_stats_file_ops`, and `kfilnd_mempool_stats_file_ops`.

Control flow: debugfs open uses `single_open()` with device pointer private data. State stats print one row per data-size bucket with average time spent in each transaction state. Aggregate stats print min/max/average/count for initiator or target transactions. Writing `reset_stats` calls `kfilnd_dev_reset_stats()`. `mempool_stats` calls `kfilnd_tn_get_mempool_stats()` and prints reserve and current availability or not-initialized messages.

State and persistence behavior: reads sample atomic duration/count fields stored in `struct kfilnd_dev`; write resets those atomics. Mempool stats reflect global transaction/message mempools. No persistent files are created beyond debugfs dentries.

Dependencies and integration: created by `kfilnd_dev_alloc()` under the device debugfs directory and by `kfilnd_tn_init()` for mempool stats. Depends on seq_file, debugfs, transaction state enums, and device reset helper.

Risks: averages can race with concurrent updates and are observational only. `TIME_MAX` clamps averages but max values are printed raw. Reset can race with active transaction finalization. Several debugfs dentry assignments in device allocation reuse the same struct member, so only cleanup-by-directory matters.

Test signals: run immediate and bulk traffic, read initiator/target aggregate and per-state files, reset stats while traffic runs, verify min reset displays as 0, inspect mempool stats before/after transaction init, and remove the NI while files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c_research.md`.

Purpose: manages one kfilnd device bound to an LNet NI: kfabric address vector/scalable endpoint setup, per-CPT endpoint allocation, peer cache initialization, debugfs files, stats reset, and teardown.

Important APIs/types/functions: `kfilnd_dev_alloc()`, `kfilnd_dev_free()`, `kfilnd_dev_post_imm_buffers()`, `kfilnd_dev_reset_stats()`, and `kfilnd_dev_get_session_key()`. The device owns `kfd_av`, `kfd_sep`, `dom`, `kfd_endpoints`, `cpt_to_endpoint`, peer cache, session-key counter, and debugfs dentries.

Control flow: allocation gets/reuses a KFI domain via `kfilnd_dom_get()`, extracts CXI NIC address, optionally obtains a Linux `struct device`, opens an AV with RX-context bits, creates and enables a scalable endpoint, allocates endpoint arrays, builds one RX/TX endpoint per NI CPT, initializes peers, marks the device initialized, stores `ni->ni_data`, rewrites the LNet NID address from NIC address, creates debugfs files, resets stats, and takes a module ref. Teardown removes debugfs, marks shutting down, cancels receive buffers, frees endpoints, destroys peers, frees arrays, closes KFI objects, puts the domain, frees the device, and drops the module ref.

State and persistence behavior: all state is per-NI runtime state. Session keys monotonically increment in an atomic for peer handshakes. Stats atomics are resettable. Endpoint and peer state are destroyed on NI shutdown.

Dependencies and integration: depends on kfabric AV/scalable endpoint APIs, CXI address and optional CXI domain ops, LNet CPT topology, endpoint/domain/peer modules, debugfs operations, and module refcounting.

Risks: resource unwinding must mirror partial allocation exactly. Device address assumptions are CXI-specific (`struct kcxi_addr`). The optional `get_device` debug message appears inverted (`if (!rc) CDEBUG("get_device failed")`). Debugfs file handles are all assigned to one member. Shutdown waits in endpoint free paths if transactions or receive buffers do not drain.

Test signals: startup/shutdown with one and multiple CPTs, allocation failure at AV/SEP/endpoint stages, provider with/without CXI ops, immediate buffer posting after startup, debugfs directory creation/removal, stats reset correctness, and module unload while NI references exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h_research.md`.

Purpose: declares the kfilnd device-management API and local hash sizing constants.

Important APIs/types/functions: `KFILND_CURRENT_HASH_BITS`, `KFILND_MAX_HASH_BITS`, `kfilnd_dev_post_imm_buffers()`, `kfilnd_dev_free()`, `kfilnd_dev_alloc()`, `kfilnd_dev_reset_stats()`, and `kfilnd_dev_get_session_key()`.

Control flow: the main LND uses allocation/post/free during NI startup/shutdown; debugfs and transaction code use stats and session-key helpers.

State and persistence behavior: no state is stored in the header. Hash constants constrain internal peer-cache sizing expectations.

Dependencies and integration: includes `kfilnd.h` for `struct kfilnd_dev`, `struct lnet_ni`, and shared definitions.

Risks: constants are marked TODO for module parameters; changing them must align with rhashtable use and memory expectations.

Test signals: compile all users, startup/shutdown NI, read debugfs stats after reset, and verify session keys advance across peer allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c_research.md`.

Purpose: shares and reference-counts kfabric fabrics and domains across kfilnd devices so multiple LNet NIs can reuse provider resources when compatible.

Important APIs/types/functions: global `fab_list` with `fab_list_lock`; `struct kfilnd_fab` and `struct kfilnd_dom` krefs; helpers `kfilnd_fab_alloc/free/reuse()`, `kfilnd_dom_alloc/free/reuse()`, public `kfilnd_dom_get()` and `kfilnd_dom_put()`.

Control flow: `kfilnd_dom_get()` builds KFI hints from NI tunables, probes dynamic resource allocation support, tries to reuse an existing fabric/domain by constraining hints and calling `kfi_getinfo()`, gets final provider info, allocates missing fabric/domain, enables CXI dynamic resource allocation when possible, and returns both domain and provider info. `kfilnd_dom_put()` drops the domain and its fabric ref; free callbacks unlink lists and close KFI FIDs.

State and persistence behavior: fabrics persist on the global list while referenced; each fabric has a domain list. Domains persist while devices reference them. Returned `kfi_info` is caller-owned and freed by device allocation.

Dependencies and integration: depends on kfabric `kfi_getinfo`, fabric/domain creation, CXI fabric ops, NI tunables for provider version/auth/traffic class, LNet CPT counts, and kref/list locking.

Risks: `kfilnd_dom_reuse()` is called with `fab` even when `kfilnd_fab_reuse()` returns NULL; the helper checks NULL, but hints restoration is fragile. Auth-key pointers are deliberately nulled before freeing hints to avoid freeing NI-owned memory. Dynamic resource probing opens a temporary fabric and must release refs correctly. Reuse logic depends on provider `kfi_getinfo()` behavior.

Test signals: create multiple NIs on same and different fabrics, verify fabric/domain refcounts and reuse, test provider versions/traffic classes/auth keys, simulate `kfi_getinfo` and domain allocation failures, and unload after repeated startup/shutdown cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h_research.md`.

Purpose: exposes the small public domain lifecycle API to device allocation code.

Important APIs/types/functions: `kfilnd_dom_get()` returns a referenced `struct kfilnd_dom` plus caller-owned `struct kfi_info`; `kfilnd_dom_put()` releases domain and fabric references.

Control flow: device startup calls get before AV/SEP creation; device teardown calls put after closing device KFI objects.

State and persistence behavior: the header defines no state, but its API owns fabric/domain reference transitions.

Dependencies and integration: includes `kfilnd.h` for LNet NI, domain, and kfabric info types.

Risks: callers must free the returned `kfi_info` and must pair every successful get with put. Passing invalid NI or output pointer returns error pointers.

Test signals: compile device code, startup/shutdown under repeated NI creation, and inject failures after get to confirm put/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c_research.md`.

Purpose: implements per-CPT kfabric endpoints, immediate receive buffer lifecycle, send/tagged/RMA post operations, replay queues for `-EAGAIN`, endpoint allocation/free, and memory-region key allocation.

Important APIs/types/functions: immediate receive helpers `kfilnd_ep_post_recv()`, `kfilnd_ep_imm_buffer_put()`, `kfilnd_ep_post_imm_buffers()`, `kfilnd_ep_cancel_imm_buffers()`; operation posters `kfilnd_ep_post_send()`, `kfilnd_ep_post_tagged_send()`, `kfilnd_ep_post_tagged_recv()`, `kfilnd_ep_post_read()`, `kfilnd_ep_post_write()`, `kfilnd_ep_cancel_tagged_recv()`; replay helpers `kfilnd_ep_queue_tn_replay()` and `kfilnd_ep_flush_replay_queue()`; lifecycle `kfilnd_ep_alloc/free()`; key helpers `kfilnd_ep_get_key()` and `kfilnd_ep_put_key()`.

Control flow: allocation creates RX/TX CQs, RX/TX contexts, binds them, enables them, allocates physically contiguous multi-receive buffers, initializes replay queues/timer/work, and IDA keys. Immediate buffer put decrements refs and reposts; `-EAGAIN` queues the buffer for timer-driven replay. KFI post helpers validate device state, optionally inject fake errors, submit provider operations, and return `-EAGAIN` for transaction replay. Replay work drains queued transactions and buffers into their original handlers. Free waits for replay count, cancels receives, waits for buffer refs and transaction list to drain, frees buffers, closes contexts/CQs, destroys keys, and frees memory.

State and persistence behavior: endpoint state persists for the NI lifetime: KFI contexts/CQs, receive buffers, transaction list, replay lists, replay timer/work, and IDA key allocator. Immediate buffers carry refcounts and repost suppression. Transaction keys are unique per endpoint up to `KFILND_EP_KEY_MAX`.

Dependencies and integration: depends on kfabric endpoint/tagged/RMA APIs, completion queues, transaction state machine, peer addressing/session key bits, LNet CPT CPU masks, fail-location framework, timers, workqueues, and Linux IDA.

Risks: teardown can wait indefinitely if transactions or RX refs leak. RKEY composition combines session key and endpoint key; ordering with peer deletion is security-sensitive. Physically contiguous receive buffer allocation can fail for large sizes. Operation flag combinations must match CQ processing. Replay list manipulation relies on `replay_count` balancing.

Test signals: endpoint allocation per CPT, receive repost and cancel, `-EAGAIN` replay for send/read/write/tagged recv/buffer repost, fail-location fake errors, key exhaustion/reuse, shutdown with active operations, and provider event flag coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h_research.md`.

Purpose: declares endpoint posting, replay, key, and fake-error APIs plus a small work item used for asynchronous error injection.

Important APIs/types/functions: `struct kfilnd_ep_err_fail_loc_work`, inline `kfilnd_ep_replays_pending()`, operation posters/cancelers, immediate-buffer APIs, lifecycle `kfilnd_ep_alloc/free()`, replay queue APIs, key APIs, and `kfilnd_ep_gen_fake_err()`.

Control flow: transaction code posts sends/RMA/tagged receives through this API; CQ code checks/flushes replay queues; device code allocates/frees endpoints and posts immediate buffers.

State and persistence behavior: the inline replay predicate observes endpoint `replay_count`; all other state is owned by `struct kfilnd_ep`.

Dependencies and integration: includes `kfilnd.h` and exposes kfabric error-entry types to endpoint users.

Risks: declarations include `kfilnd_ep_reg_mr()`/`dereg_mr()` but the current source set does not define/use them, so stale prototypes should be watched. Callers must respect endpoint initialization state and transaction ownership.

Test signals: compile all users, run replay/fake-error paths, and use symbol checks to detect stale undeclared or undefined APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c_research.md`.

Purpose: defines kfilnd module parameters, validates defaults, translates traffic-class strings, and applies module/NI tunables to LNet common and kfilnd-specific configuration.

Important APIs/types/functions: module params `cksum`, `kfi_timeout`, `tx_scale_factor`, `rx_cq_scale_factor`, `tx_cq_scale_factor`, `eq_size`, `immediate_rx_buf_count`, `prov_cpu_exclusive`, workqueue flags, `credits`, `peer_credits`, reserve mins, `peer_buffer_credits`, `peer_timeout`, provider version, `auth_key`, and `traffic_class`. Public APIs are `kfilnd_tunables_setup()`, `kfilnd_tunables_init()`, `kfilnd_get_tn_reserve_min()`, `kfilnd_get_msg_reserve_min()`, and `kfilnd_get_peer_credits()`.

Control flow: init validates module params, clamps `wq_max_active`, converts traffic class, and fills `kfi_default_tunables`. NI setup fills unset common LNet tunables from module params, clamps peer credits to max credits, initializes unset provider/auth/traffic values, validates credit/key limits, provider major version, and traffic class, then stores timeout.

State and persistence behavior: module params are global runtime configuration; most are read-only after load, while timeout, provider CPU exclusivity, and reserve mins can be writable according to mode. `kfi_default_tunables` snapshots defaults for netlink export.

Dependencies and integration: depends on Linux module_param, LNet common/kfilnd tunable structs, KFI traffic-class constants, endpoint key limit, and transaction mempool sizing.

Risks: the zero-initialized provider check repeats `lnd_prov_major_version` instead of checking minor, likely a typo. Invalid traffic strings or excessive credits prevent startup. Reserve defaults derive from peer credits times CPT count, so high CPT counts can increase memory pressure. `auth_key` zero is rejected/replaced.

Test signals: load with invalid scale factors, too few receive buffers, bad/empty traffic class, excessive credits, provider major version mismatch, custom NI tunables, reserve-min overrides, and netlink export of default tunables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_modparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c_research.md`.

Purpose: manages the per-device peer cache that maps LNet NIDs to kfabric addresses, negotiates hello/session metadata, tracks peer health, and removes stale/down peers.

Important APIs/types/functions: rhashtable params keyed by `kp_nid`; lifecycle `kfilnd_peer_init()`, `kfilnd_peer_destroy()`, `kfilnd_peer_get()`, `kfilnd_peer_put()`; address helpers `kfilnd_peer_get_kfi_addr()` and `kfilnd_peer_target_rx_base()`; health helpers `kfilnd_peer_alive()`, `kfilnd_peer_tn_failed()`, and internal stale/down/delete/purge routines; protocol `kfilnd_peer_process_hello()`.

Control flow: lookup takes an RCU ref if a non-removing peer exists; otherwise it allocates a peer, formats node/service from NID address/net number, inserts a KFI address with `kfi_av_insertsvc()`, initializes state/session key/refcounts, inserts into rhashtable, and marks alive. Transaction failures mark peers stale or down based on errno and optionally delete them to protect RKEY reuse. Hello processing records remote RX base/session key and negotiates version, moving NEW to WAIT_RSP for requests and UPTODATE for responses, then notifies LNet that the peer is up.

State and persistence behavior: peer entries persist in the device rhashtable under RCU/refcounting. Each peer stores KFI address, local/remote session keys, hello state, peer state, last-alive time, remove flag, and RX base. Deletion removes from hash, drops allocation ref, notifies LNet down, removes KFI AV address, and frees via RCU.

Dependencies and integration: depends on Linux rhashtable/RCU/refcount, KFI AV insertion/removal, LNet NID conversion and notification, device session-key generation, endpoint CPT mapping, and transaction failure logic.

Risks: RKEY safety depends on deleting peers before releasing transaction keys in certain failure paths. New-peer hello throttling can replay or drop traffic. `KP_PURGE_LIMIT` ties cache lifetime to timeout. Service/node formatting assumes NID4 address/net layout. RX count support is TODO and currently uses one RX context base.

Test signals: concurrent peer lookup/insert/delete races, hello request/response negotiation, transaction failures with `-EHOSTUNREACH`, `-ENOTCONN`, timeout, and delete true/false, stale peer purge after timeout, KFI AV insertion failures, and LNet up/down notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h_research.md`.

Purpose: declares peer-cache and peer-health APIs used by transaction and device code.

Important APIs/types/functions: `KP_PURGE_LIMIT`, `kfilnd_peer_get/put()`, `kfilnd_peer_alive()`, `kfilnd_peer_destroy/init()`, `kfilnd_peer_get_kfi_addr()`, `kfilnd_peer_target_rx_base()`, `kfilnd_peer_process_hello()`, and `kfilnd_peer_tn_failed()`.

Control flow: transactions acquire peers during allocation, update liveness on completions, process hellos, and report failures; device teardown destroys the cache.

State and persistence behavior: no state is defined here, but `KP_PURGE_LIMIT` establishes how long stale/down peers can remain before cache removal.

Dependencies and integration: includes `kfilnd.h`, so callers share private peer/device/message structures.

Risks: timeout-derived purge duration changes with `kfi_timeout`. Callers must hold/release peer references correctly.

Test signals: compile all users, run peer lifecycle under traffic, and verify purge timing changes when timeout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_peer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c_research.md`.

Purpose: implements the kfilnd transaction allocator, wire-message packing/unpacking, transaction state machine, timeout/replay handling, LNet finalization, mempool setup, and bulk buffer mapping.

Important APIs/types/functions: global kmem caches and mempools for transactions and immediate message buffers; packing helpers for hello, immediate, and bulk v1/v2 messages; `kfilnd_tn_unpack_msg()` validation; `kfilnd_tn_process_rx_event()`; state handlers for `TN_STATE_IDLE`, `IMM_SEND`, `IMM_RECV`, `WAIT_COMP`, `WAIT_TAG_COMP`, timeout/fail states, and dispatch table; public `kfilnd_tn_event_handler()`, `kfilnd_tn_alloc()`, `kfilnd_tn_alloc_for_hello()`, `kfilnd_tn_free()`, `kfilnd_tn_init()`, `kfilnd_tn_cleanup()`, `kfilnd_tn_get_mempool_stats()`, and `kfilnd_tn_set_buf()`.

Control flow: outbound LNet sends allocate a transaction, optional key, peer ref, and message buffer, then feed an init event. Inbound immediate receive completions validate headers/checksum/NIDs, allocate a target transaction, attach the posted buffer, and feed RX/hello events. The state machine serializes on `tn_lock`, posts KFI operations via endpoint APIs, returns `-EAGAIN` to queue replay, starts/cancels timeout timers for bulk initiators, finalizes LNet messages/replies, releases peers and buffers, records duration stats, and frees the transaction. Bulk initiator flow posts a tagged receive, sends a bulk request, waits for send and tagged completion, and times out/cancels if needed. Target flow parses into LNet, receives `kfilnd_recv()`, posts read/write RMA or a zero-length tagged send, then finalizes.

State and persistence behavior: transactions are live objects on an endpoint list. They carry status/health, state timestamps, deadlines, replay event/status, LNet messages, peer refs, local/remote keys, KFI context, posted immediate buffer refs, mapped SGL/BVEC data, and timeout work/timer. Mempools persist module-wide and reserve elements based on tunables.

Dependencies and integration: depends on endpoint posting/replay/key APIs, peer cache and hello state helpers, device stats, LNet parse/finalize/reply helpers, checksum routines, DMA or LNet RDMA mapping for GPU buffers, Linux mempool/slab/timer/workqueue, and CFS fail locations.

Risks: this is the highest-risk file. RKEY reuse protection depends on key-before-peer lookup and peer deletion ordering. State/event combinations use `LBUG()` on unexpected input. Some comments mark possible leaks around invalid receive paths and cancel failures. Timeout races are handled with WAIT_TIMEOUT states but require exact event ordering. SGL mapping mutates `orig_nents` and must restore it before free. Mixed-endian byte swapping is TODO.

Test signals: exhaustive state-machine tests for immediate, hello, bulk PUT, bulk GET, zero-length target skips, timeouts, cancels, send/tagged/RMA failures, replay `-EAGAIN`, early RX before hello completion, protocol v1/v2 messages, checksum enabled/disabled, GPU and non-GPU DMA mapping, mempool reserve exhaustion, and teardown with active timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h_research.md`.

Purpose: declares the transaction subsystem interface consumed by LNet entry points, CQ processing, endpoints, and debugfs.

Important APIs/types/functions: `kfilnd_tn_process_rx_event()`, `kfilnd_tn_free()`, `kfilnd_tn_alloc()`, `kfilnd_tn_alloc_for_hello()`, `kfilnd_tn_event_handler()`, `kfilnd_tn_cleanup()`, `kfilnd_tn_init()`, and `kfilnd_tn_set_buf()`.

Control flow: send/receive paths allocate and initialize transactions, CQs deliver events through the event handler, endpoint replay replays saved events, and module init/exit initializes/cleans mempools.

State and persistence behavior: no state is declared here, but API ownership is important: after the first event handler call, the transaction subsystem owns lifetime until finalization.

Dependencies and integration: includes `kfilnd.h` for transaction, device, peer, and bio_vec/LNet types.

Risks: callers must not use a transaction after handing it to the event handler unless a specific LNet callback contract says it remains valid. `key` argument naming means memory-region key allocation, not auth key.

Test signals: compile all users, verify transaction ownership in send/receive paths, and run event replay plus cleanup with outstanding transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile_research.md`.

Purpose: builds the external OFED o2iblnd Lustre LND module and sets compiler include/feature flags so external OFED headers override in-kernel ones.

Important APIs/types/functions: conditional `obj-m += ko2iblnd.o` under `BUILD_EXT_O2IB`; object list `o2iblnd.o o2iblnd_cb.o o2iblnd_modparams.o`; `ccflags-y += $(EXTRA_KCFLAGS)`; `NOSTDINC_FLAGS` adds `EXTRA_OFED_CONFIG`, `EXTRA_OFED_INCLUDE`, `-DEXTERNAL_OFED_BUILD`, and `-DEXTERNAL_OFED_VERSION`.

Control flow: when external build is enabled, kbuild links the three objects into `ko2iblnd`. Include flags are arranged to prefer external OFED. Optional `CONFIG_GCOV_PROFILE_LNET` enables coverage.

State and persistence behavior: build-only file; runtime module state is in the C sources.

Dependencies and integration: depends on external OFED config/include variables, Lustre kbuild, and version variable `EXT_O2IB_VER`.

Risks: missing or misordered OFED include flags can silently build against in-kernel headers. `BUILD_EXT_O2IB` controls module emission but object variables are still declared. Version define quoting must survive make/shell expansion.

Test signals: build with and without `BUILD_EXT_O2IB`, verify include precedence, inspect compiler command for external defines, build with GCOV enabled, and load module against the expected OFED stack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h_research.md`.

Purpose: defines the o2iblnd InfiniBand wire protocol message layouts, magic/version constants, message type IDs, connection parameters, RDMA descriptors, completions, and rejection reasons.

Important APIs/types/functions: packed structs `kib_connparams`, `kib_immediate_msg`, `kib_rdma_frag`, `kib_rdma_desc`, `kib_putreq_msg`, `kib_putack_msg`, `kib_get_msg`, `kib_completion_msg`, `kib_msg`, and `kib_rej`. Constants include `IBLND_MSG_MAGIC`, protocol versions 1/2, message types `CONNREQ`, `CONNACK`, `NOOP`, `IMMEDIATE`, `PUT_REQ/NAK/ACK/DONE`, `GET_REQ/DONE`, and reject reasons for races, resources, fatal errors, incompatibility, stale peers, RDMA-frag mismatch, queue-size mismatch, invalid service ID, and early NI state.

Control flow: not executable; send/receive code packs these structures into sender byte order and receivers must flip as needed. `kib_msg` has a fixed leading magic/version pair, common routing/checksum/NID/stamp header, and a union payload selected by `ibm_type`.

State and persistence behavior: wire structs carry transient protocol state: connection queue depth/frags/message size, LNet headers, RDMA keys/fragments, completion cookies/status, source/destination incarnations, and rejection metadata. No kernel memory state is stored here.

Dependencies and integration: includes UAPI LNet IDL for `lnet_hdr_nid4` and `LNET_PROTO_IB_MAGIC`. Used by both external and generated in-kernel o2iblnd builds.

Risks: all structures are `__packed`, and comments note misaligned `u64` RDMA fragment addresses; direct dereference/alignment assumptions are unsafe. Wire compatibility requires preserving first fields and version/type values. Extending variable-length payloads/descriptors must keep `ibm_nob` and checksum logic synchronized.

Test signals: interop between protocol version 1 and 2 peers, endian-swap tests, packed layout/sizeof assertions, immediate payload bounds, RDMA fragment count/key handling, completion status propagation, and each rejection reason during connection setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd-idl.h -->
