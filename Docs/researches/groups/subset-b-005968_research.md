# subset-b-005968 Research

This grouped report covers the source-tree-aligned files assigned to research work item `subset-b-005968`. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tcp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/tcp.h

Purpose: Defines the `tcp` trace system for TCP packet loss, resets, socket lifetime, receive-window growth, retransmission, congestion state, TCP probe telemetry, MD5/AO authentication failures, and sequence-number-extension updates.

Important APIs/types/functions: Exports tracepoints including `tcp_retransmit_skb`, `tcp_send_reset`, `tcp_receive_reset`, `tcp_destroy_sock`, `tcp_rcv_space_adjust`, `tcp_rcvbuf_grow`, `tcp_retransmit_synack`, `tcp_sendmsg_locked`, `tcp_probe`, `tcp_bad_csum`, `tcp_cong_state_set`, `tcp_hash_*`, and `tcp_ao_*`. It declares reusable event classes `tcp_event_sk`, `tcp_event_skb`, `tcp_hash_event`, `tcp_ao_event`, `tcp_ao_event_sk`, and `tcp_ao_event_sne`, plus `DECLARE_TRACE(tcp_cwnd_reduction)`. It uses `DEFINE_RST_REASON` to register reset-reason enum names.

Control flow: Callers in TCP fast paths invoke generated `trace_tcp_*` helpers; TP assignment snapshots `sock`, `sk_buff`, TCP/IPv4/IPv6 tuple, ports, sequence numbers, window metrics, congestion state, reset reason, and AO key/MAC context into ring-buffer records. Conditional AO events are only compiled with `CONFIG_TCP_AO`.

State/persistence: The file owns no TCP state; it serializes volatile socket and packet fields into ftrace/perf buffers. Trace output depends on lifetime-safe dereferences of live `sock`, request-sock, and skb objects.

Dependencies/integration: Includes TCP, IPv6, socket-diagnostic, reset-reason, and net probe common helpers; consumed by kernel TCP implementation and user tooling under tracefs/perf/BPF.

Risks: Tracepoint ABI field names and enum string mappings are user-visible. Misreading IPv4/IPv6 address families, AO optional data, or reset reasons would break diagnostics or cause unsafe dereferences on hot paths.

Test signals: Build with tracing, IPv6, and TCP_AO variants; enable `tcp:*` events while running retransmit/reset/AO failure scenarios and confirm stable formatted tuples and no lockdep/KASAN issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tegra_apb_dma.h -->
# sources/distributed-fs/ceph-client/include/trace/events/tegra_apb_dma.h

Purpose: Provides the `tegra_apb_dma` trace system for NVIDIA Tegra APB DMA transfer status, completion callbacks, and interrupt-service activity.

Important APIs/types/functions: Defines `tegra_dma_tx_status`, `tegra_dma_complete_cb`, and `tegra_dma_isr`. The tracepoints expose DMA cookie/status, residue, callback channel identity, and interrupt channel/status data.

Control flow: Tegra DMA driver paths call generated trace helpers around status polling, descriptor completion, and ISR handling. Each event copies scalar channel/status fields into a trace entry and formats them for tracefs.

State/persistence: No persistent state is created. The observable state is a sampled DMA channel status at trace time.

Dependencies/integration: Includes `linux/tracepoint.h` and `linux/dmaengine.h`; integrated with the Tegra APB DMA driver and generic ftrace event generation through `trace/define_trace.h`.

Risks: DMA completion paths are latency-sensitive, so field collection must remain cheap and must not dereference invalid descriptors. Cookie/status formatting must stay aligned with dmaengine semantics.

Test signals: Build Tegra DMA support with tracing; run DMA transfer tests with trace events enabled and verify status/residue transitions and ISR records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tegra_apb_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/thp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/thp.h

Purpose: Defines transparent huge page tracepoints for PMD state changes, updates, and migration-entry transitions.

Important APIs/types/functions: Declares event classes `hugepage_set`, `hugepage_update`, and `migration_pmd`, with concrete THP events built from those templates. They capture mm address, PMD/PTE values, and old/new state where relevant.

Control flow: Memory-management code invokes generated helpers while installing, modifying, or replacing huge PMD entries. The event classes centralize field layout so related operations share the same trace ABI.

State/persistence: No memory state is owned here. Events persist snapshots of page-table state into trace buffers for later debugging.

Dependencies/integration: Uses tracepoint infrastructure and MM/page-table types. It integrates with THP fault, collapse, split, and migration paths.

Risks: Page-table values are architecture-sensitive and timing-sensitive. Incorrect field types or formatting can hide THP races or produce misleading traces.

Test signals: Compile with THP enabled; run hugepage fault/collapse/migration tests while enabling `thp:*` events and confirm PMD transitions are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/thp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/timer.h -->
# sources/distributed-fs/ceph-client/include/trace/events/timer.h

Purpose: Defines the `timer` trace system for low-resolution timers, high-resolution timers, interval timers, and tick-stop decisions.

Important APIs/types/functions: Uses `timer_class`, `hrtimer_class`, `itimer_state`, and related templates to define `timer_start`, `timer_expire_entry`, timer cancel/expire events, `hrtimer_setup`, `hrtimer_start`, `hrtimer_expire_entry`, hrtimer cancel/expire/forward/rearm events, `itimer_*`, and `tick_stop`.

Control flow: Timer core code calls generated helpers when timers are initialized, started, cancelled, expired, or when the periodic tick is stopped. TP assignment records timer addresses, callbacks, expiry times, clock base, modes, and process/signal context for interval timers.

State/persistence: No timer ownership is introduced. The trace stream persists point-in-time timer configuration and expiry observations.

Dependencies/integration: Includes timer/hrtimer, signal, and tracepoint-related kernel types; integrated with ftrace, perf, and timer debugging tools.

Risks: Timer callbacks are often on hot paths or interrupt context. Trace fields must avoid sleeping, must tolerate partially initialized timers, and must preserve event ABI names used by diagnostics.

Test signals: Kernel timer selftests, hrtimer stress, NO_HZ/tick-stop workloads, and tracefs checks for start/expire/cancel event pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/timer_migration.h -->
# sources/distributed-fs/ceph-client/include/trace/events/timer_migration.h

Purpose: Instruments timer migration hierarchy behavior, including group setup, CPU/group connection, idle transitions, event updates, and remote timer handling.

Important APIs/types/functions: Defines templates `tmigr_group_set`, `tmigr_connect_child_parent`, `tmigr_connect_cpu_parent`, `tmigr_group_and_cpu`, `tmigr_cpugroup`, `tmigr_idle`, plus events such as `tmigr_cpu_new_timer`, `tmigr_cpu_active`, `tmigr_cpu_online`, `tmigr_cpu_offline`, `tmigr_cpu_idle`, `tmigr_cpu_new_timer_idle`, `tmigr_update_events`, and `tmigr_handle_remote`.

Control flow: Timer migration code emits records as CPUs enter/exit idle, join or leave groups, enqueue migratable timers, and process remote expiry decisions. Event templates capture group pointer/topology, CPU id, wake-up state, nextevt, expiry, and active/idle masks.

State/persistence: This header does not maintain migration state; it samples hierarchy state into trace buffers.

Dependencies/integration: Depends on timer migration internal structs and the trace event generator; used by NO_HZ and power-management diagnostics.

Risks: Tracepoint fields mirror internal hierarchy structures, so refactors can silently desynchronize field meaning. CPU hotplug and idle paths require low-overhead, race-tolerant reads.

Test signals: Build with timer migration enabled; exercise CPU hotplug, idle, and timer migration workloads and verify coherent parent/child and remote-event traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/timer_migration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/timestamp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/timestamp.h

Purpose: Defines timestamp tracepoints for ctime/mtime change tracking and multigrain timestamp fill/exchange behavior.

Important APIs/types/functions: Provides `ctime`, `ctime_ns_xchg`, and `fill_mg_cmtime` event definitions/classes that capture inode pointers, device/inode identifiers, current and updated timestamp seconds/nanoseconds, and exchange results.

Control flow: VFS timestamp update paths emit events when inode change times are set, exchanged, or filled with multigrain cmtime data. Assignment copies inode and time fields into the raw event entry.

State/persistence: No inode state is changed by this header; trace buffers persist timestamp observations.

Dependencies/integration: Integrates with VFS inode timestamp code, tracepoint infrastructure, and user-space trace consumers debugging ctime granularity.

Risks: Timestamp semantics are subtle across filesystems. Incorrect field naming or seconds/nanoseconds pairing can mislead filesystem ordering and cache-coherency investigations.

Test signals: Run timestamp/VFS tests with tracing enabled; validate ctime and multigrain events during file update, stat, and concurrent timestamp exchange workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/timestamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tlb.h -->
# sources/distributed-fs/ceph-client/include/trace/events/tlb.h

Purpose: Defines a single `tlb_flush` tracepoint with symbolic reasons for TLB invalidation activity.

Important APIs/types/functions: `TLB_FLUSH_REASON` registers enum values via `TRACE_DEFINE_ENUM` and provides symbolic output through `__print_symbolic`; `tlb_flush` records page count and reason.

Control flow: Architecture/MM TLB-flush paths call `trace_tlb_flush(reason, pages)`, which snapshots the reason code and page count into the trace buffer.

State/persistence: No TLB state is owned. It records flush events for profiling and debugging.

Dependencies/integration: Includes MM types and tracepoint infrastructure; consumed by MM/architecture code and performance tools.

Risks: Reason enums must stay synchronized with producers. Page-count interpretation may vary for full-ASID/full-mm flushes, so formatting must remain clear.

Test signals: Enable `tlb:tlb_flush` under mmap/munmap/page-fault workloads and compare emitted reasons with expected MM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tsm_mr.h -->
# sources/distributed-fs/ceph-client/include/trace/events/tsm_mr.h

Purpose: Provides tracepoints for trusted security module measurement register read, refresh, and write operations.

Important APIs/types/functions: Defines `tsm_mr_read`, `tsm_mr_refresh`, and `tsm_mr_write`, using `linux/tsm-mr.h` types to expose MR index, provider/device context, and operation result data.

Control flow: TSM MR code emits these events around measurement register accesses. The event assignments snapshot object identity and return/status fields without owning the operation.

State/persistence: Measurement registers remain owned by TSM/provider code. This header only persists operation observations in trace buffers.

Dependencies/integration: Depends on the TSM MR kernel API and tracepoint generator; useful for confidential-computing attestation diagnostics.

Risks: Measurement data may be security-sensitive. Tracepoint payloads should avoid leaking raw secrets and must keep provider/index semantics stable.

Test signals: Build TSM MR support with tracing; perform read/write/refresh operations and verify event emission and result codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/tsm_mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/udp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/udp.h

Purpose: Defines UDP receive-queue failure tracing for packets that cannot be queued to a socket.

Important APIs/types/functions: `udp_fail_queue_rcv_skb` captures socket identity, network tuple data through `net_probe_common`, skb length, and failure return code.

Control flow: UDP receive paths call the generated helper when `skb` queueing fails. The trace assignment records socket/packet metadata and the error reason.

State/persistence: No socket or skb state is mutated here; only a trace record is persisted.

Dependencies/integration: Includes UDP, tracepoint, and network probe common helpers; consumed by networking diagnostics and perf/ftrace.

Risks: Receive error paths may run under pressure; tracepoint dereferences must be safe for partially processed skbs and sockets.

Test signals: Generate UDP receive buffer pressure while `udp:*` is enabled and confirm failure codes match drop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/udp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/v4l2.h -->
# sources/distributed-fs/ceph-client/include/trace/events/v4l2.h

Purpose: Instruments V4L2 buffer queue/dequeue and videobuf2 V4L2 buffer lifecycle events with human-readable buffer type, field, flags, and timecode data.

Important APIs/types/functions: Defines `v4l2_event_class` with `v4l2_dqbuf` and `v4l2_qbuf`, plus `vb2_v4l2_event_class` with `vb2_v4l2_buf_done`, `vb2_v4l2_buf_queue`, `vb2_v4l2_dqbuf`, and `vb2_v4l2_qbuf`. Helper macros map V4L2 buffer types, fields, flags, timecode types, and timecode flags.

Control flow: V4L2 ioctl and vb2 paths emit events around buffer queueing and completion. Assignments copy buffer index/type/bytesused/flags/field/timestamp/timecode/sequence data into trace entries.

State/persistence: Buffer ownership remains in V4L2/vb2 queues; traces persist snapshots useful for driver timing analysis.

Dependencies/integration: Includes `media/videobuf2-v4l2.h` and tracepoint infrastructure; integrated with media drivers and tracefs.

Risks: V4L2 trace ABI must track public V4L2 enums. Stale enum maps or flag decoders can make media pipeline failures hard to diagnose.

Test signals: Run media/v4l2-compliance or streaming workloads with `v4l2:*` enabled and inspect qbuf/dqbuf ordering, sequence numbers, and timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/v4l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vb2.h -->
# sources/distributed-fs/ceph-client/include/trace/events/vb2.h

Purpose: Defines core videobuf2 tracepoints for buffer done, queue, dequeue, and queue-buffer operations.

Important APIs/types/functions: `vb2_event_class` backs `vb2_buf_done`, `vb2_buf_queue`, `vb2_dqbuf`, and `vb2_qbuf`, capturing queue pointer, buffer pointer, buffer index, type, memory model, and state.

Control flow: vb2 core emits events at buffer lifecycle transitions. The shared event class keeps a consistent field layout across operations.

State/persistence: No queue state is changed. Trace records persist selected buffer state for postmortem ordering analysis.

Dependencies/integration: Depends on `media/videobuf2-core.h`; integrated with media subsystem drivers and tracefs.

Risks: Buffer state values are internal and may change with vb2 refactors. Events must avoid dereferencing freed buffers around completion paths.

Test signals: Stream with vb2-backed drivers and verify qbuf/dqbuf/done sequences under tracefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vmalloc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/vmalloc.h

Purpose: Instruments vmap area allocation, lazy purge, and no-flush free activity in the vmalloc allocator.

Important APIs/types/functions: Defines `alloc_vmap_area`, `purge_vmap_area_lazy`, and `free_vmap_area_noflush`, exposing virtual address range, size/alignment, requested address window, caller return address, and purge/free counters.

Control flow: vmalloc/vmap code emits allocation/free/purge events as vmap areas move through allocator paths. TP assignments snapshot scalar range metadata.

State/persistence: Vmap areas remain managed by vmalloc internals. The trace stream provides persistent allocator observations.

Dependencies/integration: Includes tracepoint infrastructure and vmalloc internal callers; consumed by MM fragmentation and leak diagnostics.

Risks: Address and caller fields may be sensitive in production traces. Field changes can break scripts that monitor vmalloc pressure.

Test signals: Exercise vmalloc/vfree/module-load paths with `vmalloc:*` enabled and verify allocation/free pairing and purge counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vmscan.h -->
# sources/distributed-fs/ceph-client/include/trace/events/vmscan.h

Purpose: Defines memory reclaim tracepoints for kswapd, direct reclaim, memcg reclaim, slab shrinking, LRU isolation/shrink, writeback during reclaim, throttling, and hopeless-zone handling.

Important APIs/types/functions: Provides reclaim flag helpers (`RECLAIM_WB_*`, `show_reclaim_flags`, `show_throttle_flags`) and events including `mm_vmscan_kswapd_sleep`, `mm_vmscan_kswapd_wake`, `mm_vmscan_wakeup_kswapd`, direct/memcg reclaim begin/end templates, `mm_shrink_slab_start/end`, `mm_vmscan_lru_isolate`, `mm_vmscan_write_folio`, `mm_vmscan_reclaim_pages`, `mm_vmscan_lru_shrink_inactive/active`, `mm_vmscan_node_reclaim_begin/end`, `mm_vmscan_throttled`, `mm_vmscan_kswapd_reclaim_fail`, and `mm_vmscan_kswapd_clear_hopeless`.

Control flow: Reclaim code emits begin/end events around reclaim phases and point events for page isolation, writeback, throttling, and kswapd state changes. Assignments copy node/zone/order/gfp/memcg/reclaim counts and reason flags.

State/persistence: No reclaim state is owned; trace buffers persist samples from reclaim loops.

Dependencies/integration: Includes MM, memcontrol, and mmflags trace helpers; conditional memcg events depend on `CONFIG_MEMCG`.

Risks: These are high-frequency pressure paths. Field reads must be cheap and race-tolerant, and flag decoders must stay aligned with reclaim internals.

Test signals: Run memory pressure, memcg, and slab pressure tests with `vmscan:*`; verify begin/end pairing, count consistency, and no tracing-induced reclaim regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vmscan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vsock_virtio_transport_common.h -->
# sources/distributed-fs/ceph-client/include/trace/events/vsock_virtio_transport_common.h

Purpose: Instruments virtio-vsock packet allocation and receive paths.

Important APIs/types/functions: Defines `virtio_transport_alloc_pkt` and `virtio_transport_recv_pkt`, capturing virtio-vsock header fields such as source/destination CID/port, length, type, operation, flags, buffer allocation size, and return status.

Control flow: Virtio-vsock transport code emits allocation traces when constructing packets and receive traces when packets arrive. TP assignment snapshots packet header state before later queueing or freeing changes it.

State/persistence: Packet state remains owned by virtio-vsock transport; trace buffers persist copies of header metadata.

Dependencies/integration: Depends on virtio-vsock transport structs and tracepoint infrastructure; integrated with host/guest vsock diagnostics.

Risks: Header field semantics are protocol ABI. Incorrect formatting or reading freed packets would break debugging and stability.

Test signals: Run vsock connect/send/receive tests with trace events enabled and verify packet op/type/length sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/vsock_virtio_transport_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/watchdog.h -->
# sources/distributed-fs/ceph-client/include/trace/events/watchdog.h

Purpose: Defines watchdog device tracepoints for start, ping, stop, and timeout changes.

Important APIs/types/functions: `watchdog_template` backs `watchdog_start`, `watchdog_ping`, and `watchdog_stop`; `watchdog_set_timeout` records old/new timeout state for a `watchdog_device`.

Control flow: Watchdog core or drivers emit events during lifecycle operations. Assignments copy watchdog id, status, timeout, and operation-specific values.

State/persistence: Watchdog device state is not changed here; trace buffers retain operation snapshots.

Dependencies/integration: Includes `linux/watchdog.h` and tracepoints; useful for watchdog core and driver debugging.

Risks: Watchdog paths may be time-critical. Trace overhead must not delay pings, and timeout units must remain clear.

Test signals: Enable `watchdog:*` and run watchdog start/ping/stop/timeout tests, checking trace order against driver callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/wbt.h -->
# sources/distributed-fs/ceph-client/include/trace/events/wbt.h

Purpose: Instruments block writeback throttling latency, statistics, step changes, and timer activity.

Important APIs/types/functions: Defines `wbt_stat`, `wbt_lat`, `wbt_step`, and `wbt_timer`, exposing throttling window/depth, inflight counters, latency targets, step direction, and timer expiry/queue state.

Control flow: Writeback throttling code emits events when sampling latency, adjusting throttle depth, reporting stats, or arming timers. Events snapshot request-queue and throttling state.

State/persistence: WBT state remains in block-layer structures. Trace records provide persistent throttle-control observations.

Dependencies/integration: Depends on block queue/wbt internals and tracepoint infrastructure; consumed by block I/O latency diagnostics.

Risks: WBT is performance-sensitive. Tracepoint fields must not take locks or perturb throttling decisions, and queue lifetime must be respected.

Test signals: Run write-heavy block workloads with `wbt:*` enabled and verify latency/depth changes correlate with observed throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/wbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/workqueue.h -->
# sources/distributed-fs/ceph-client/include/trace/events/workqueue.h

Purpose: Defines workqueue tracepoints for queueing, activation, execution start, and execution end.

Important APIs/types/functions: Provides `workqueue_queue_work`, `workqueue_activate_work`, `workqueue_execute_start`, and `workqueue_execute_end`, capturing work struct pointer, function pointer, target CPU, workqueue pointer/name, and execution context.

Control flow: Workqueue core emits queue/activation events before execution and start/end events around worker callback invocation. Trace entries snapshot callback identity for latency and ordering analysis.

State/persistence: Workqueue state remains in core structures; traces persist lifecycle observations.

Dependencies/integration: Integrated with kernel workqueue core, ftrace, perf, and latency tools.

Risks: Workqueue paths are hot and highly concurrent. The work item may be reused quickly, so trace consumers must interpret pointer identity with timestamps.

Test signals: Enable `workqueue:*` during workqueue selftests or driver activity and verify queue/execute event correlation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/workqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/writeback.h -->
# sources/distributed-fs/ceph-client/include/trace/events/writeback.h

Purpose: Defines extensive writeback tracing for dirty folios/inodes, writeback work scheduling/execution, cgroup writeback ownership, writeback-control state, dirty throttling, superblock requeueing, and single-inode writeback.

Important APIs/types/functions: Provides helper decoders for inode state and writeback reasons, templates such as `writeback_folio_template`, `writeback_dirty_inode_template`, `writeback_write_inode_template`, `writeback_work_class`, `wbc_class`, `writeback_single_inode_template`, and `writeback_inode_template`, and events including `writeback_dirty_folio`, `writeback_mark_inode_dirty`, `inode_switch_wbs*`, `track_foreign_dirty`, `flush_foreign`, `writeback_queue/exec/start/written/wait`, `writeback_pages_written`, `writeback_bdi_register`, `writeback_queue_io`, `global_dirty_state`, `bdi_dirty_ratelimit`, `balance_dirty_pages`, `writeback_sb_inodes_requeue`, and inode writeback/lazytime events.

Control flow: VFS/MM writeback paths emit events as dirty state is created, queued, throttled, written, and cleared. Assignments snapshot inode identifiers, bdi/wb names, cgroup ids, page counts, bandwidth limits, dirty thresholds, and reason flags.

State/persistence: It owns no writeback state; trace buffers persist sampled dirty/writeback state for analysis.

Dependencies/integration: Includes backing-device and writeback headers; cgroup-specific events depend on `CONFIG_CGROUP_WRITEBACK`.

Risks: This trace ABI is heavily used by performance tools. Field changes can break scripts, and high-frequency dirtying paths require minimal overhead.

Test signals: Run filesystem writeback, dirty throttling, and cgroup writeback tests with `writeback:*`; verify work lifecycle and dirty accounting fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/writeback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/xdp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/xdp.h

Purpose: Defines XDP tracepoints for exceptions, bulk TX, redirects, cpumap/devmap paths, memory provider connect/disconnect, and failed BPF XDP link attachment.

Important APIs/types/functions: Provides action/memory-type symbol maps, `xdp_exception`, `xdp_bulk_tx`, redirect template events (`xdp_redirect`, `xdp_redirect_err`, map variants), helper macros `_trace_xdp_redirect*`, `xdp_cpumap_kthread`, `xdp_cpumap_enqueue`, `xdp_devmap_xmit`, `mem_disconnect`, `mem_connect`, and `bpf_xdp_link_attach_failed`.

Control flow: XDP and BPF map code emits events when programs return exceptional actions, redirect frames, enqueue/dequeue batches, transmit via devmap/cpumap, attach links, or manage page-pool memory providers. Events snapshot netdevice identity, program/map ids, action/error codes, batch counts, and memory ids.

State/persistence: XDP data path state is not owned. Trace buffers persist packet-path decisions and resource lifecycle observations.

Dependencies/integration: Includes netdevice, filter/BPF, `net/xdp.h`, and private XDP memory helpers; some events require `CONFIG_BPF_SYSCALL`.

Risks: XDP is a very hot path. Tracepoints must remain disabled-fast, avoid costly formatting unless enabled, and keep action/memory enum maps synchronized.

Test signals: Run XDP redirect, devmap/cpumap, and attach-failure selftests with `xdp:*` enabled; verify action/error/map metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/xen.h -->
# sources/distributed-fs/ceph-client/include/trace/events/xen.h

Purpose: Defines Xen tracepoints for multicall batching, MMU page-table operations, TLB flushes, CR3 writes, and descriptor-table CPU operations.

Important APIs/types/functions: Declares classes and events such as `xen_mc_batch`, `xen_mc_issue`, `xen_mc_entry`, `xen_mc_entry_alloc`, `xen_mc_callback`, `xen_mc_flush_reason`, `xen_mc_flush`, `xen_mc_extend_args`, `xen_mmu_set_pte/pmd/pud/p4d`, PAE-only PTE atomic/clear events, `xen_mmu_ptep_modify_prot_*`, `xen_mmu_alloc/release_ptpage`, `xen_mmu_pgd_pin/unpin`, `xen_mmu_flush_tlb_*`, `xen_mmu_write_cr3`, and GDT/IDT/LDT events.

Control flow: Xen paravirtualization code emits events around multicall queue management, page-table updates, TLB invalidation, and CPU descriptor operations. Assignments copy pointers, page-table values, hypercall op/args, CPU masks, and descriptor metadata.

State/persistence: Xen/MMU state remains in architecture code and hypervisor interfaces; trace buffers persist operation snapshots.

Dependencies/integration: Includes Xen hypervisor and trace type headers; conditional branches reflect x86 PAE and page-table-level configuration.

Risks: Architecture-specific type sizes and page-table levels must be exact. Tracepoint mistakes can break Xen builds or misrepresent low-level MMU behavior.

Test signals: Build Xen PV/PVH configurations with tracing; run boot, multicall, MMU update, and CPU descriptor workloads while checking `xen:*` events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/fs.h -->
# sources/distributed-fs/ceph-client/include/trace/misc/fs.h

Purpose: Provides reusable filesystem trace formatting helpers for dirent types, open flags, file modes, fcntl commands, lock types, lookup flags, inode attribute-valid flags, and statx masks.

Important APIs/types/functions: Defines `show_fs_dirent_type`, `show_fs_fcntl_open_flags`, `show_fs_fmode_flags`, `show_fs_fcntl_cmd`, `show_fs_fcntl_lock_type`, `show_fs_lookup_flags`, `show_ia_valid_flags`, and `show_statx_mask`. It uses `TRACE_DEFINE_ENUM` and `__print_flags`/`__print_symbolic` style mappings.

Control flow: Trace event headers include this misc helper and use the macros in `TP_printk` expressions. There is no runtime control flow beyond macro expansion into trace formatters.

State/persistence: No state is stored; it defines symbolic presentation for values captured by other events.

Dependencies/integration: Depends on VFS constants from fs/fcntl/stat headers and trace formatting macros. Used across filesystem trace systems to avoid duplicated flag maps.

Risks: These helpers form user-visible string decoding. Missing new flags or stale command values produce misleading traces even when raw values are correct.

Test signals: Build all filesystem trace users and inspect trace format files for complete flag mappings; exercise open/fcntl/lookup/statx traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/nfs.h -->
# sources/distributed-fs/ceph-client/include/trace/misc/nfs.h

Purpose: Provides NFS/NFSv4 trace formatting helpers for protocol status codes, stability modes, verifiers, pNFS layout I/O modes, recallable-object masks, sequence status flags, and callback operations.

Important APIs/types/functions: Registers many `NFSERR_*`, `NFS4ERR_*`, `NFS_*`, `IOMODE_*`, and callback op enums with `TRACE_DEFINE_ENUM`; exports macros `show_nfs_status`, `show_nfs_stable_how`, `show_nfs4_status`, `show_nfs4_verifier`, `show_pnfs_layout_iomode`, `show_rca_mask`, `show_nfs4_seq4_status`, and `show_nfs4_cb_op`.

Control flow: NFS tracepoint headers include this file and call the helpers from `TP_printk`. The file has macro-generation flow only.

State/persistence: No client/server state is stored. It controls symbolic rendering of values already captured by NFS trace events.

Dependencies/integration: Includes Linux and UAPI NFS headers; integrated with NFS client/server and SUNRPC trace events.

Risks: NFS protocol status coverage must track protocol headers. Missing enum registration degrades trace readability and BPF/perf enum decoding.

Test signals: Build NFS trace events and run NFSv3/v4 client/server tests with trace enabled, checking status and callback strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/rdma.h -->
# sources/distributed-fs/ceph-client/include/trace/misc/rdma.h

Purpose: Provides RDMA trace formatting helpers for InfiniBand async events, work-completion statuses, IB CM events, and RDMA CM events.

Important APIs/types/functions: Defines list macros `IB_EVENT_LIST`, `IB_WC_STATUS_LIST`, `IB_CM_EVENT_LIST`, and `RDMA_CM_EVENT_LIST`; registers enum values through `TRACE_DEFINE_ENUM`; exports `rdma_show_ib_event`, `rdma_show_wc_status`, `rdma_show_ib_cm_event`, and `rdma_show_cm_event`.

Control flow: RDMA tracepoint headers expand the list macros twice: once to register enums and once to build symbolic tables for `TP_printk`.

State/persistence: No RDMA state is owned. It only maps captured numeric states to stable text.

Dependencies/integration: Depends on RDMA/IB enum definitions and tracepoint formatting. Used by RDMA core, CM, and driver trace events.

Risks: Enum drift is the primary risk; stale maps make transport failures opaque. Macro hygiene matters because list macros redefine helper names.

Test signals: Compile RDMA trace users; exercise connection manager and completion failure paths and confirm symbolic status/event names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/sunrpc.h -->
# sources/distributed-fs/ceph-client/include/trace/misc/sunrpc.h

Purpose: Defines shared SUNRPC trace printf specifiers for stable task/client identifiers.

Important APIs/types/functions: Exports `SUNRPC_TRACE_PID_SPECIFIER`, `SUNRPC_TRACE_CLID_SPECIFIER`, and `SUNRPC_TRACE_TASK_SPECIFIER`.

Control flow: SUNRPC tracepoint headers include this helper and embed the specifier macros in `TP_printk` strings. There is no runtime logic.

State/persistence: No state is stored; the file standardizes formatting.

Dependencies/integration: Depends only on tracepoint headers. Integrated with SUNRPC/NFS trace events that need consistent task and client id formatting.

Risks: Format-string changes affect trace ABI readability and tooling assumptions.

Test signals: Build SUNRPC trace events and inspect formatted task/client ids in trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/misc/sunrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/perf.h -->
# sources/distributed-fs/ceph-client/include/trace/perf.h

Purpose: Adds perf-event probe generation for trace events when `CONFIG_PERF_EVENTS` is enabled.

Important APIs/types/functions: Redefines `__DECLARE_EVENT_CLASS`, `DECLARE_EVENT_CLASS`, `DECLARE_EVENT_SYSCALL_CLASS`, `DEFINE_EVENT`, and `DEFINE_EVENT_PRINT` to emit perf callback wrappers. Supports `__perf_count` and `__perf_task` assignment helpers and includes `stage6_event_callback.h` to populate raw event data.

Control flow: The trace generator includes the target trace header under these macro definitions. For each event class, generated perf functions reserve/populate trace event buffers and submit data to perf consumers.

State/persistence: No persistent state is owned by this header; it creates callback code that writes records into perf ring buffers.

Dependencies/integration: Conditional on `CONFIG_PERF_EVENTS`; relies on trace event call structures, event offsets, raw event structs, and perf tracing internals.

Risks: Macro redefinition order is fragile. Generated function signatures must match event prototypes exactly or trace/perf builds fail.

Test signals: Build with perf events enabled and run `perf trace`/tracepoint recording for representative generated events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/init.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/init.h

Purpose: Initializes trace event code generation with trace-system string creation and enum/sizeof mapping support.

Important APIs/types/functions: Defines token-pasting helpers `__app__`, `__app`, `TRACE_SYSTEM_STRING`, `TRACE_MAKE_SYSTEM_STR`, `TRACE_DEFINE_ENUM`, and `TRACE_DEFINE_SIZEOF`. It emits `trace_eval_map` records for symbolic enum and sizeof decoding.

Control flow: Early trace generator stages include this file before expanding event headers. `TRACE_DEFINE_ENUM` and `TRACE_DEFINE_SIZEOF` expand into linker-visible map entries used by trace tooling.

State/persistence: It creates static/linker-section metadata, not runtime mutable state.

Dependencies/integration: Included by `trace_events.h` and `trace_custom_events.h`; depends on trace event map definitions.

Risks: Linker-section naming and token pasting are sensitive to `TRACE_SYSTEM_VAR`; mistakes break enum decoding across all trace systems.

Test signals: Build trace headers that call `TRACE_DEFINE_ENUM`/`TRACE_DEFINE_SIZEOF` and inspect generated format/printk maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage1_struct_define.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/stage1_struct_define.h

Purpose: Stage 1 of trace generation: converts `TP_STRUCT__entry` field macros into members of the raw trace event structure.

Important APIs/types/functions: Defines `__field`, `__field_ext`, `__field_struct`, `__array`, `__dynamic_array`, `__string`, `__vstring`, `__bitmask`, `__cpumask`, `__sockaddr`, and relative dynamic variants. Dynamic fields become `u32 __data_loc_*` or `__rel_loc_*` descriptors.

Control flow: `trace_events.h` includes this stage while redefining `DECLARE_EVENT_CLASS`; event headers are then expanded to build `struct trace_event_raw_<call>`.

State/persistence: Defines compile-time struct layout; no runtime state is mutated here.

Dependencies/integration: Relies on trace event macro protocol and the raw event structure generated in surrounding headers.

Risks: Field layout is ABI-critical for tracefs/perf/BPF consumers. Incorrect dynamic-data descriptors corrupt event decoding.

Test signals: Compile trace events with scalar, array, string, bitmask, cpumask, sockaddr, and relative fields; inspect generated `format` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage1_struct_define.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage2_data_offsets.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/stage2_data_offsets.h

Purpose: Stage 2 of trace generation: builds offset metadata for dynamic fields in each event.

Important APIs/types/functions: Redefines field macros so only dynamic arrays, strings, bitmasks, cpumasks, sockaddrs, and relative variants generate `u32` offset members in `struct trace_event_data_offsets_<call>`.

Control flow: The generator expands each trace event under these definitions to compute which variable-length data offsets are needed. Static fields expand away.

State/persistence: Produces compile-time offset structs used by generated callbacks; no runtime storage is owned here.

Dependencies/integration: Consumed by stage 5 offset calculation and stage 6 event callback population.

Risks: Offset struct mismatches cause callback code to write variable data to wrong positions, corrupting trace records.

Test signals: Build events with multiple dynamic and relative fields and validate trace output lengths and payload strings/arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage2_data_offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage3_trace_output.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/stage3_trace_output.h

Purpose: Stage 3 defines macros used while generating human-readable trace output functions.

Important APIs/types/functions: Defines `__entry`, `TP_printk`, dynamic-data accessors (`__get_str`, `__get_dynamic_array`, relative variants, bitmask/cpumask/sockaddr accessors), symbolic printers (`__print_flags`, `__print_symbolic`, u64 variants), hex/array dump helpers, namespace time printers, and IRQ-context helpers.

Control flow: `trace_events.h` expands event `TP_printk` blocks under these definitions so each event class gets a generated print function.

State/persistence: No state is owned. It defines how raw event payloads are interpreted for text output.

Dependencies/integration: Relies on trace sequence APIs, trace print flag structs, raw event layout, and helper functions for arrays/time/buffers.

Risks: Accessor arithmetic must match dynamic data layout. Formatting helper changes are user-visible in tracefs output.

Test signals: Inspect trace text for events using dynamic strings, flags, arrays, cpumasks, sockaddrs, and namespace time values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage3_trace_output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage4_event_fields.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/stage4_event_fields.h

Purpose: Stage 4 emits trace event field metadata used by tracefs `format` files and event parsers.

Important APIs/types/functions: Defines `ALIGN_STRUCTFIELD` and field macros that call `trace_event_define_field()` for scalar, struct, array, dynamic, string, bitmask, cpumask, sockaddr, and relative fields.

Control flow: The trace generator expands `TP_STRUCT__entry` under these macros inside event-class field registration functions. Each macro registers field type, name, offset, size, signedness, and filtering behavior.

State/persistence: Registers metadata with trace event infrastructure; no event payload is stored here.

Dependencies/integration: Depends on `trace_event_define_field`, raw event structs, and trace filtering/format consumers.

Risks: Field names, offsets, and signedness are trace ABI. Mistakes break filters, perf/BPF decoders, and trace parsers.

Test signals: Compare generated `/sys/kernel/tracing/events/.../format` fields against expected struct layout and filtering behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage4_event_fields.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage5_get_offsets.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/stage5_get_offsets.h

Purpose: Stage 5 computes runtime offsets and total payload size for variable-length trace event data.

Important APIs/types/functions: Defines `__data_offsets`, validates static field macros with dummy structs, and implements dynamic sizing for `__dynamic_array`, `__string`, `__string_len`, `__vstring`, relative dynamic arrays/strings, bitmasks, cpumasks, and sockaddrs. It also defines bitmask sizing helpers.

Control flow: Generated `trace_event_get_offsets_<call>()` functions expand event field macros to increment `__data_size` and fill `__data_offsets` members before event reservation.

State/persistence: It computes per-event-call transient offsets; no persistent state beyond generated code.

Dependencies/integration: Used by stage 6 callbacks before writing dynamic payloads into `trace_event_buffer`.

Risks: Off-by-one string lengths, alignment mistakes, or relative-location calculations corrupt trace records and readers.

Test signals: Trace events with multiple variable fields and verify payload lengths, string termination, and relative offsets under ftrace/perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage5_get_offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage6_event_callback.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/stage6_event_callback.h

Purpose: Stage 6 defines macros used by generated event callbacks to assign captured values into raw trace records.

Important APIs/types/functions: Provides `__entry`, static/dynamic field declarations, assignment helpers `__assign_str`, `__assign_vstr`, `__assign_bitmask`, `__assign_cpumask`, `__assign_sockaddr`, relative assignment variants, and `TP_fast_assign`. It also sets defaults for `__perf_count` and `__perf_task`.

Control flow: Generated trace/perf callbacks reserve an event buffer, expand `TP_fast_assign` under this stage, copy scalar/dynamic values into the raw record, and then commit the event.

State/persistence: Writes one raw event payload per callback invocation; no long-lived state is owned by the macros.

Dependencies/integration: Depends on stage 5 offsets, raw event structs, trace event buffers, and dynamic data accessors.

Risks: Assignment helpers must match field declarations exactly. String and relative-buffer copying bugs can corrupt trace buffers or leak data.

Test signals: Enable events with strings, varargs strings, bitmasks, cpumasks, and sockaddrs; verify correct raw and formatted output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage6_event_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage7_class_define.h -->
# sources/distributed-fs/ceph-client/include/trace/stages/stage7_class_define.h

Purpose: Stage 7 supplies minimal macro definitions while defining final `trace_event_class` objects.

Important APIs/types/functions: Defines neutral `__entry`, IRQ-context helpers, namespace time printers, and `TP_printk` as a string wrapper so class definitions can reference print formats without generating print code again.

Control flow: `trace_events.h` expands event declarations under these macros to build event class metadata and associate print format strings/functions produced by earlier stages.

State/persistence: Produces static event class metadata; no mutable state is owned.

Dependencies/integration: Final stage in the trace event macro pipeline, feeding `trace_event_class` and `trace_event_call` definitions.

Risks: Macro defaults must be compatible with all event `TP_printk` bodies. Missing helper definitions can break otherwise valid trace headers.

Test signals: Full kernel build across diverse trace event headers; class registration succeeds and format strings are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/stages/stage7_class_define.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/syscall.h -->
# sources/distributed-fs/ceph-client/include/trace/syscall.h

Purpose: Declares syscall tracing metadata and registration interfaces used by the trace event subsystem.

Important APIs/types/functions: Defines/forwards `struct syscall_metadata`, `struct trace_event_call`, `struct task_struct`, and syscall trace registration hooks for enter/exit tracepoints and metadata lookup.

Control flow: Architecture syscall table and tracing code use this header to connect syscall numbers to trace event calls. Runtime syscall enter/exit paths consult metadata and emit generated syscall trace events when enabled.

State/persistence: Metadata is statically registered by syscall tracing code; per-task syscall events are transient trace records.

Dependencies/integration: Integrates syscall entry code, trace event registration, perf/ftrace, and task context.

Risks: Syscall metadata must match architecture ABI and argument layout. Incorrect prototypes or registration hooks break syscall tracing globally.

Test signals: Build syscall tracing and run `trace-cmd`/perf syscall events, checking syscall names, numbers, and argument decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/trace_custom_events.h -->
# sources/distributed-fs/ceph-client/include/trace/trace_custom_events.h

Purpose: Implements the multi-stage generator for custom trace events built with `TRACE_CUSTOM_EVENT`, `DECLARE_CUSTOM_EVENT_CLASS`, and `DEFINE_CUSTOM_EVENT`.

Important APIs/types/functions: Redefines custom-event macros across stages 1-7 to generate raw structs, offset structs, print functions, field metadata, callbacks, event classes, and event calls under a `custom` trace system.

Control flow: The file repeatedly includes `TRACE_INCLUDE(TRACE_INCLUDE_FILE)` under different macro definitions, mirroring `trace_events.h` but for custom events. Each pass produces a different piece of generated code.

State/persistence: Produces static metadata and generated callbacks; runtime state is limited to emitted trace records.

Dependencies/integration: Depends on `linux/trace_events.h`, all trace generation stages, and trace include-file conventions.

Risks: Macro ordering is fragile. Custom event class/call names must not collide, and generated callbacks must stay ABI-compatible with normal trace events.

Test signals: Build a custom trace event provider and verify format files, enable/disable behavior, and trace/perf record emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/trace_custom_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/trace_events.h -->
# sources/distributed-fs/ceph-client/include/trace/trace_events.h

Purpose: Core trace event macro engine that expands `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, syscall events, flags, perf permissions, callbacks, classes, and calls through seven generation stages.

Important APIs/types/functions: Redefines `TRACE_EVENT`, `TRACE_EVENT_SYSCALL`, `DECLARE_EVENT_CLASS`, `DECLARE_EVENT_SYSCALL_CLASS`, `DEFINE_EVENT`, `DEFINE_EVENT_FN`, `DEFINE_EVENT_PRINT`, `TRACE_EVENT_FN`, `TRACE_EVENT_FN_COND`, `TRACE_EVENT_FLAGS`, and `TRACE_EVENT_PERF_PERM`. It includes stage headers for raw structs, data offsets, print output, field registration, offset calculation, callbacks, and class definitions.

Control flow: The target trace header is included repeatedly via `TRACE_INCLUDE(TRACE_INCLUDE_FILE)`. Each inclusion uses a different macro environment to generate one part of the tracepoint implementation, then perf-specific hooks are added when enabled.

State/persistence: Generates static `trace_event_class`/`trace_event_call` metadata and runtime callbacks that write raw event records into trace/perf buffers.

Dependencies/integration: Central to all `include/trace/events/*.h` providers; depends on tracepoint definitions, trace event internals, perf optional support, and syscall tracing.

Risks: This file is macro-order critical. A small change can break all trace event compilation, field ABI, enable/disable behavior, or perf integration.

Test signals: Full kernel build with broad trace configs, trace event selftests, format-file inspection, ftrace enable/disable, filters, and perf tracepoint recording.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/trace_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/Kbuild -->
# sources/distributed-fs/ceph-client/include/uapi/Kbuild

Purpose: Controls top-level UAPI header export exclusions for architecture-dependent Linux headers.

Important APIs/types/functions: Uses `no-export-headers += linux/a.out.h`, `linux/kvm.h`, and `linux/kvm_para.h` when the corresponding architecture UAPI or generated UAPI asm headers are absent.

Control flow: During headers install, Kbuild evaluates `wildcard` checks against `$(srctree)` and `$(objtree)` for `$(SRCARCH)` and appends headers that must not be exported.

State/persistence: No runtime state; it influences generated/install header trees.

Dependencies/integration: Integrated with kernel headers-install machinery and architecture include directories.

Risks: Wrong wildcard logic can export unusable UAPI headers or hide valid ones for an architecture.

Test signals: Run `make headers_install` for architectures with and without KVM/a.out support and verify exported header set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/Kbuild -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/Kbuild

Purpose: Lists mandatory generic UAPI asm headers that architectures should provide or inherit for user-space header installation.

Important APIs/types/functions: `mandatory-y` entries include `auxvec.h`, `bitsperlong.h`, `bpf_perf_event.h`, `errno.h`, `fcntl.h`, `ioctl.h`, `ioctls.h`, IPC/memory/resource/signal/socket/stat/term/types/unistd headers, and more.

Control flow: The headers-install Kbuild pass reads this file to decide which `usr/include/asm/` headers are required for non-UML architectures.

State/persistence: No runtime state; affects installed UAPI header completeness.

Dependencies/integration: Used by Kbuild UAPI export logic and architecture-specific asm-generic fallback mechanisms.

Risks: Missing mandatory headers break user-space builds; adding headers without compatible generic definitions can expose unstable ABI.

Test signals: Run `make headers_install` and compile representative userspace programs against the installed asm headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/auxvec.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/auxvec.h

Purpose: Provides an empty generic architecture auxiliary-vector header for architectures that need no extra auxvec constants beyond `linux/auxvec.h`.

Important APIs/types/functions: Only defines the include guard `__ASM_GENERIC_AUXVEC_H`; no constants or types are exported.

Control flow: Included by exported asm header sets as a placeholder/fallback.

State/persistence: No state.

Dependencies/integration: Complements `linux/auxvec.h` and architecture-specific overrides.

Risks: Adding generic constants here would affect all inheriting architectures and user-space ABI.

Test signals: Headers-install and userspace compile checks that include `<asm/auxvec.h>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/bitsperlong.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/bitsperlong.h

Purpose: Defines generic user-space bit width macros for C `long` and `long long`.

Important APIs/types/functions: Provides `__BITS_PER_LONG`, derived from compiler `__CHAR_BIT__ * __SIZEOF_LONG__` when available or defaulting to 32, and `__BITS_PER_LONG_LONG` defaulting to 64.

Control flow: Preprocessor-only fallback logic lets architectures override `__BITS_PER_LONG` before inclusion.

State/persistence: No runtime state; establishes compile-time ABI assumptions.

Dependencies/integration: Included by many asm-generic UAPI headers that need layout decisions for 32-bit vs 64-bit user space.

Risks: Incorrect `__BITS_PER_LONG` breaks UAPI struct layout and ABI compatibility, especially for compat user space on 64-bit kernels.

Test signals: Build headers for 32-bit, 64-bit, and compat targets; validate IPC/time struct layout expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/bpf_perf_event.h

Purpose: Exposes the architecture pt_regs type used by BPF perf-event programs.

Important APIs/types/functions: Includes `linux/ptrace.h` and typedefs `struct pt_regs` to `bpf_user_pt_regs_t`.

Control flow: Header inclusion gives user BPF programs a stable alias for perf-event register context.

State/persistence: No runtime state.

Dependencies/integration: Used by libbpf/BPF programs and architecture UAPI ptrace definitions.

Risks: The alias must match actual perf-event register context; incompatible pt_regs exposure breaks BPF program compilation or register reads.

Test signals: Compile BPF perf-event samples against installed headers for architectures using asm-generic fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno-base.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno-base.h

Purpose: Defines the base POSIX/Linux errno values 1-34 for generic UAPI.

Important APIs/types/functions: Exports macros such as `EPERM`, `ENOENT`, `EINTR`, `EIO`, `EAGAIN`, `ENOMEM`, `EACCES`, `EINVAL`, `EMFILE`, `ENOSPC`, `EPIPE`, `EDOM`, and `ERANGE`.

Control flow: Preprocessor constants only; included by `asm-generic/errno.h` and user-space headers.

State/persistence: No state; constants are ABI.

Dependencies/integration: Baseline errno namespace for architectures using generic error numbering.

Risks: Numeric changes are ABI-breaking. Comments are less critical than values but influence user understanding.

Test signals: User-space compile checks and ABI comparison against expected errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno.h

Purpose: Extends base errno definitions with generic Linux error numbers 35-133 and aliases.

Important APIs/types/functions: Includes `errno-base.h`; defines `EDEADLK`, `ENOSYS`, networking errors (`ENOTSOCK`, `ECONNRESET`, `ETIMEDOUT`, etc.), filesystem/media/key errors (`ESTALE`, `EUCLEAN`, `ENOKEY`, etc.), robust mutex errors, `ERFKILL`, and `EHWPOISON`. Also aliases `EWOULDBLOCK` to `EAGAIN`, `EDEADLOCK` to `EDEADLK`, and `EFSCORRUPTED` to `EUCLEAN`.

Control flow: Preprocessor-only ABI definitions.

State/persistence: No runtime state; values are user-kernel ABI.

Dependencies/integration: Used by libc/kernel headers for generic architectures and syscall error reporting.

Risks: Returning `ENOSYS` from real syscalls is explicitly discouraged because arch syscall entry uses it for nonexistent syscalls. Numeric changes are ABI-breaking.

Test signals: Header ABI checks and userspace compile/runtime errno value comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/fcntl.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/fcntl.h

Purpose: Defines generic UAPI open flags, fcntl command numbers, owner/lock constants, and file lock structures.

Important APIs/types/functions: Exports `O_*` flags, `F_*` fcntl commands including OFD locks, `F_OWNER_*`, `struct f_owner_ex`, `FD_CLOEXEC`, lock constants, `F_LINUX_SPECIFIC_BASE`, and generic `struct flock`/`struct flock64` unless an architecture overrides them.

Control flow: Preprocessor guards allow architectures to predefine flag or struct variants. `__BITS_PER_LONG` gates 64-bit lock commands for 32-bit userspace/kernel contexts.

State/persistence: No runtime state; constants and structures define syscall ABI for `open`, `fcntl`, `flock`, and lockf-like operations.

Dependencies/integration: Includes `linux/types.h`; consumed by libc and filesystem/syscall code.

Risks: Flag uniqueness is critical, as noted by the file. Struct layout and flag values are ABI-stable and architecture-sensitive.

Test signals: Headers ABI checks; compile and run open/fcntl/flock tests across 32-bit/64-bit user-space ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/hugetlb_encode.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/hugetlb_encode.h

Purpose: Defines the generic encoding for selecting hugetlb page sizes in syscall flag arguments.

Important APIs/types/functions: Exports `HUGETLB_FLAG_ENCODE_SHIFT`, `HUGETLB_FLAG_ENCODE_MASK`, and size encodings from 16KB through 16GB.

Control flow: Preprocessor constants encode log2(page size) into bits 26-31 of flags such as `MAP_HUGETLB`.

State/persistence: No runtime state; constants define ABI flag encoding.

Dependencies/integration: Included by syscall-specific headers that expose hugepage-size flags, such as mmap-related UAPI.

Risks: Encoding collisions or wrong shifts break user requests for non-default hugepage sizes.

Test signals: Compile programs using `MAP_HUGE_*`-style definitions and run mmap hugetlb size-selection tests where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/hugetlb_encode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-l64.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-l64.h

Purpose: Defines fixed-width signed/unsigned integer typedefs for architectures where C `long` is the 64-bit type.

Important APIs/types/functions: Under non-assembly builds, typedefs `__s8/__u8`, `__s16/__u16`, `__s32/__u32`, and `__s64/__u64` with `__s64` as signed long and `__u64` as unsigned long.

Control flow: Preprocessor guard excludes typedefs for assembly and lets include guards prevent duplication.

State/persistence: No runtime state; typedefs influence UAPI struct layout.

Dependencies/integration: Includes `asm/bitsperlong.h`; used by architectures following the LP64 long-based UAPI model.

Risks: Selecting this header for an architecture whose ABI uses long long for 64-bit UAPI types would alter type compatibility and layout.

Test signals: Compile installed headers and verify `sizeof(__u64)` and struct layouts on LP64 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-l64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-ll64.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-ll64.h

Purpose: Defines fixed-width integer typedefs for architectures where 64-bit UAPI integer types use C `long long`.

Important APIs/types/functions: Typedefs `__s8/__u8`, `__s16/__u16`, `__s32/__u32`, and `__s64/__u64`; with GCC it uses `__extension__` for long long typedefs to avoid strict C90 warnings.

Control flow: Assembly inclusion skips typedefs. Non-GCC compilers receive plain long long typedefs through the alternate branch.

State/persistence: No runtime state; typedefs define exported ABI type spelling and layout.

Dependencies/integration: Includes `asm/bitsperlong.h`; used by many architectures and generic UAPI headers.

Risks: Mismatching int-l64 vs int-ll64 can break user-space ABI compatibility even when sizes are equal because type models differ.

Test signals: Headers compile tests under GCC and non-GCC-compatible modes; ABI layout checks for structs using `__u64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-ll64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctl.h

Purpose: Defines the generic ioctl command-number bit layout and helper macros.

Important APIs/types/functions: Exports `_IOC_*BITS`, masks, shifts, direction constants `_IOC_NONE/_IOC_WRITE/_IOC_READ`, `_IOC()`, `_IO`, `_IOR`, `_IOW`, `_IOWR`, bad-size variants, extractors `_IOC_DIR/_IOC_TYPE/_IOC_NR/_IOC_SIZE`, and legacy `IOC_*` aliases.

Control flow: Preprocessor guards allow architectures to override size/direction bits or direction constants. In userspace, `_IOC_TYPECHECK(t)` uses `sizeof(t)`.

State/persistence: No runtime state; establishes ABI encoding for ioctl numbers.

Dependencies/integration: Used by almost every UAPI ioctl definition through `<linux/ioctl.h>` or asm headers.

Risks: Bit allocation and size checking are ABI-critical. Incorrect `_IOC_SIZEBITS` can truncate command sizes or conflict with architecture numbering.

Test signals: Compile representative ioctl headers and compare generated command numbers against known ABI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctls.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctls.h

Purpose: Defines generic terminal, pty, serial, and file ioctl command numbers.

Important APIs/types/functions: Exports `TCGETS/TCSETS*`, `TCGETS2/TCSETS2*`, `TIOC*` pty/session/window/serial controls, `FIONREAD/FIONBIO/FIOCLEX/FIONCLEX/FIOASYNC/FIOQSIZE`, packet-mode flags `TIOCPKT_*`, and `TIOCSER_TEMT`.

Control flow: Includes `linux/ioctl.h` and uses `_IOR/_IOW/_IOWR` for typed commands. Guards allow architectures to predefine conflicting values like `TIOCSRS485` or `FIOQSIZE`.

State/persistence: No runtime state; constants are ioctl ABI.

Dependencies/integration: Used by tty, pty, serial, and libc terminal APIs.

Risks: Numeric conflicts are permanent ABI issues. Type arguments in typed ioctl macros must match UAPI structs.

Test signals: Headers compile checks and tty/pty/serial ioctl ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ipcbuf.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/ipcbuf.h

Purpose: Defines the generic SysV IPC permission structure shared by message queues, semaphores, and shared memory UAPI.

Important APIs/types/functions: Exports `struct ipc64_perm` with key, uid/gid/cuid/cgid, mode, padding, sequence, and unused extension fields.

Control flow: Header-only struct definition; padding handles mode_t width and future expansion.

State/persistence: No runtime state; struct layout is copied across user/kernel syscall boundaries.

Dependencies/integration: Includes `linux/posix_types.h`; embedded by `msgbuf.h`, `sembuf.h`, and `shmbuf.h`.

Risks: Padding and field widths are ABI-sensitive across 32/64-bit userspace and endian variants.

Test signals: SysV IPC userspace tests and ABI layout comparisons for `ipc64_perm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/ipcbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/kvm_para.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/kvm_para.h

Purpose: Placeholder generic KVM paravirtualization UAPI header for architectures without generic definitions.

Important APIs/types/functions: No API is exported; a comment keeps the file non-empty so patch tooling does not delete it.

Control flow: Included only as a fallback header.

State/persistence: No state.

Dependencies/integration: Participates in UAPI header installation when architecture-specific/generated `kvm_para.h` is absent.

Risks: Adding symbols here would expose them broadly to architectures that may not implement matching KVM features.

Test signals: Headers-install and compile checks for `<asm/kvm_para.h>` on architectures using the placeholder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman-common.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman-common.h

Purpose: Defines generic memory-protection, mmap, mlock, msync, madvise, guard, and protection-key constants common to architectures.

Important APIs/types/functions: Exports `PROT_*`, common `MAP_*` flags including `MAP_FIXED_NOREPLACE`, `MAP_SYNC`, `MAP_HUGETLB`, `MAP_UNINITIALIZED`, `MLOCK_ONFAULT`, `MS_*`, many `MADV_*` values including hugepage/KSM/pageout/populate/collapse/guard controls, `MAP_FILE`, and `PKEY_*`.

Control flow: Preprocessor constants only; architecture-specific `mman.h` layers add or override other bits.

State/persistence: No runtime state; constants define syscall ABI.

Dependencies/integration: Included by `asm-generic/mman.h` and architecture mmap headers.

Risks: Values must remain non-overlapping with architecture-specific bits and hugetlb encoding. ABI changes break mmap/madvise users.

Test signals: mmap/mlock/madvise headers compile checks and runtime mmap flag tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman.h

Purpose: Adds generic architecture mmap and mlock constants on top of `mman-common.h`.

Important APIs/types/functions: Defines `MAP_GROWSDOWN`, `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_LOCKED`, `MAP_NORESERVE`, `MCL_CURRENT`, `MCL_FUTURE`, `MCL_ONFAULT`, and shadow-stack setup flags.

Control flow: Header includes common definitions, then adds generic flags while reserving bits 26-31 for hugetlb encoding.

State/persistence: No runtime state; constants are memory-management syscall ABI.

Dependencies/integration: Used by libc and kernel UAPI for `mmap`, `mlockall`, and shadow-stack setup interfaces.

Risks: Flag collisions with architecture-specific flags or hugetlb bits are ABI-breaking.

Test signals: Headers compile checks and mmap/mlock/shadow-stack flag validation where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/msgbuf.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/msgbuf.h

Purpose: Defines generic SysV message queue status structure layout.

Important APIs/types/functions: Exports `struct msqid64_ds` containing `ipc64_perm`, send/receive/change timestamps with 32-bit high halves on 32-bit user space, queue byte/message counts, byte limit, last sender/receiver pids, and unused fields.

Control flow: `__BITS_PER_LONG` selects direct long timestamp fields for 64-bit or split low/high fields for 32-bit.

State/persistence: No runtime state; struct is the user-kernel ABI for message queue status.

Dependencies/integration: Includes `asm/bitsperlong.h` and `asm/ipcbuf.h`; used by SysV IPC syscalls and libc.

Risks: Timestamp split layout and endian notes are ABI-sensitive. Padding changes break old user space.

Test signals: SysV message queue tests and struct layout checks on 32-bit and 64-bit ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/param.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/param.h

Purpose: Defines generic user-visible system parameter constants.

Important APIs/types/functions: Provides `__USER_HZ` default 100, `HZ` as `__USER_HZ` unless overridden, `EXEC_PAGESIZE` 4096, `NOGROUP` -1, and `MAXHOSTNAMELEN` 64.

Control flow: Preprocessor guards allow architecture or build headers to override selected values.

State/persistence: No runtime state; constants inform user-space assumptions.

Dependencies/integration: Used by exported asm headers and libc compatibility code.

Risks: `HZ` and page-size assumptions are ABI-visible; careless overrides affect time conversion and executable loading assumptions.

Test signals: Headers compile checks and user-space validation of exported constants for architectures using generic params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/poll.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/poll.h

Purpose: Defines generic poll/select event masks and `struct pollfd`.

Important APIs/types/functions: Exports standard masks `POLLIN`, `POLLPRI`, `POLLOUT`, `POLLERR`, `POLLHUP`, `POLLNVAL`, normalization/band masks, optional `POLLMSG/POLLREMOVE/POLLRDHUP`, internal `POLLFREE`, `POLL_BUSY_LOOP`, and `struct pollfd { int fd; short events; short revents; }`.

Control flow: Preprocessor guards allow architectures to define some nonstandard values before inclusion.

State/persistence: No runtime state; constants and struct layout define poll syscall ABI.

Dependencies/integration: Used by libc, event loops, and kernel poll implementations.

Risks: Mask value changes break every poll/select consumer. `__force __poll_t` casts rely on Linux type annotations.

Test signals: Headers compile checks and poll/epoll/select runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/posix_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/posix_types.h

Purpose: Defines generic kernel POSIX-compatible typedefs exported to user space.

Important APIs/types/functions: Provides `__kernel_long_t`, `__kernel_ino_t`, `__kernel_mode_t`, pid/uid/gid types, `__kernel_size_t`/`ssize_t`/`ptrdiff_t` selected by `__BITS_PER_LONG`, `__kernel_fsid_t`, offsets, time types, clock/timer ids, caddr, and 16-bit uid/gid aliases.

Control flow: Many typedefs are guarded so architectures can override before inclusion. `__BITS_PER_LONG` controls size-related typedefs.

State/persistence: No runtime state; typedefs determine UAPI struct layout.

Dependencies/integration: Includes `asm/bitsperlong.h`; foundational for many UAPI headers.

Risks: Namespace pollution and ABI layout are key risks. Changing typedef widths breaks user-kernel structures.

Test signals: Headers compile tests and ABI layout checks for structs using these typedefs on 32-bit/64-bit targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/resource.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/resource.h

Purpose: Defines generic resource limit identifiers and infinity value.

Important APIs/types/functions: Exports `RLIMIT_CPU`, `RLIMIT_FSIZE`, `RLIMIT_DATA`, `RLIMIT_STACK`, `RLIMIT_CORE`, guarded `RLIMIT_RSS/NPROC/NOFILE/MEMLOCK/AS`, `RLIMIT_LOCKS`, `RLIMIT_SIGPENDING`, `RLIMIT_MSGQUEUE`, `RLIMIT_NICE`, `RLIMIT_RTPRIO`, `RLIMIT_RTTIME`, `RLIM_NLIMITS`, and guarded `RLIM_INFINITY`.

Control flow: Guards preserve architecture-specific historical order for limits 5-9 and infinity representation.

State/persistence: No runtime state; constants define `getrlimit`/`setrlimit` ABI.

Dependencies/integration: Used by libc resource APIs and kernel resource limit handling.

Risks: Limit numbering is ABI-sensitive, especially for architectures with historical ordering differences.

Test signals: Headers ABI checks and getrlimit/setrlimit tests across generic and overriding architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/sembuf.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/sembuf.h

Purpose: Defines generic SysV semaphore status structure layout.

Important APIs/types/functions: Exports `struct semid64_ds` containing `ipc64_perm`, operation/change timestamps using either long or split low/high halves, semaphore count, and unused extension fields.

Control flow: `__BITS_PER_LONG` selects 64-bit or split 32-bit timestamp representation.

State/persistence: No runtime state; struct is copied across user/kernel semaphore IPC APIs.

Dependencies/integration: Includes `asm/bitsperlong.h` and `asm/ipcbuf.h`; used by SysV semaphore syscalls.

Risks: Big-endian 32-bit padding is historically odd and documented; changing it breaks compatibility.

Test signals: SysV semaphore IPC tests and struct layout checks on 32-bit/64-bit and endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/sembuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/setup.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/setup.h

Purpose: Provides the generic command-line size constant for architecture setup UAPI.

Important APIs/types/functions: Defines `COMMAND_LINE_SIZE` as 512.

Control flow: Header-only constant with include guard.

State/persistence: No runtime state.

Dependencies/integration: Used by architecture setup headers and userspace tools that inspect boot command-line limits.

Risks: The constant is ABI-visible for architectures inheriting it; changing it may affect tools or boot protocols.

Test signals: Headers compile checks for `<asm/setup.h>` and architecture boot metadata consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/shmbuf.h -->
# sources/distributed-fs/ceph-client/include/uapi/asm-generic/shmbuf.h

Purpose: Defines generic SysV shared-memory status and system-info structures.

Important APIs/types/functions: Exports `struct shmid64_ds` with `ipc64_perm`, segment size, attach/detach/change timestamps with 32-bit split fields when needed, creator/last-op pids, attach count, and unused fields; exports `struct shminfo64` with shmmax, shmmin, shmmni, shmseg, shmall, and unused fields.

Control flow: `__BITS_PER_LONG` selects timestamp layout. The header includes generic IPC and POSIX type definitions.

State/persistence: No runtime state; structures define shared-memory syscall ABI.

Dependencies/integration: Includes `asm/bitsperlong.h`, `asm/ipcbuf.h`, and `asm/posix_types.h`; used by SysV shared-memory syscalls and libc.

Risks: Timestamp and padding layout are ABI-sensitive, especially for 32-bit and big-endian user space.

Test signals: SysV shared-memory tests and ABI layout validation for `shmid64_ds` and `shminfo64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/asm-generic/shmbuf.h -->
