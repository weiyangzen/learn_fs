# Research: subset-b-005966

Grouped research for Linux trace event headers under `sources/distributed-fs/ceph-client/include/trace/events`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mptcp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mptcp.h

Purpose: Defines tracepoints for Multipath TCP subflow selection, mapping-extension inspection, ACK advancement, data-availability checks, and receive-buffer growth. It turns MPTCP socket/subflow state into stable ftrace/perf records without adding runtime state outside the tracing subsystem.

Important APIs/types/functions: `TRACE_SYSTEM mptcp`; `mptcp_subflow_get_send`; `DECLARE_EVENT_CLASS(mptcp_dump_mpext)` reused by `mptcp_sendmsg_frag` and `get_mapping_status`; `ack_update_msk`; `subflow_check_data_avail`; `mptcp_rcvbuf_grow`. The events read `struct sock`, `struct mptcp_subflow_context`, `struct mptcp_ext`, `struct mptcp_sock`, TCP `write_seq`, subflow token, data sequence numbers, mapping lengths, checksum flags, and reset reasons.

Control flow: MPTCP transmit paths emit send-subflow and mapping events while choosing where data is sent. Receive paths emit ACK-update, data-available, and receive-buffer growth events as DSS mappings are validated and the meta socket advances. Trace fast-assign blocks snapshot mutable socket fields into ring-buffer entries before printing.

State and persistence: No durable state is owned. Event records are transient tracing output; sampled state belongs to MPTCP sockets, TCP subflows, and skb extension metadata.

Dependencies and integration points: Depends on TCP/IPv6/MPTCP socket structures, `sock_diag`, reset-reason helpers, and `trace/events/net_probe_common.h` address/port assignment macros. It integrates with `net/mptcp` diagnostic workflows and generic kernel trace infrastructure.

Risks and test signals: Risks include reading subflow fields after lifecycle changes, confusing host/network byte order in address fields, format drift when MPTCP structs change, and tracepoint overhead on hot data paths. Test with MPTCP selftests for multi-subflow send/receive, DSS checksum, fallback/reset, IPv4/IPv6, and tracepoint enable/disable while exercising packet loss and re-injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/mptcp.h` completely for this pass (264 lines, 7145 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/mptcp.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mptcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/napi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/napi.h

Purpose: Provides tracepoints for NAPI poll execution and dynamic queue limit stall detection in networking drivers. It helps correlate driver poll budget use, work completion, and transmit queue stalls.

Important APIs/types/functions: `napi_poll` records a `struct napi_struct *`, associated `struct net_device *`, poll work, and budget. `dql_stall_detected` records stall counters from `struct dql`, the running DQL numbers, a device name, queue index, and the source line that emitted the trace.

Control flow: Network drivers and core NAPI scheduling code call `trace_napi_poll()` after poll callbacks return. DQL code calls the stall event when queue accounting suggests transmit completion progress has stopped. Trace assignment snapshots device naming and queue counters while the caller still owns the relevant objects.

State and persistence: The header stores no state. Runtime state lives in NAPI instances, netdev queues, and DQL accounting; emitted records are transient tracing data.

Dependencies and integration points: Includes netdevice, tracepoint, and ftrace headers. It integrates with driver poll loops, byte queue limits, perf/ftrace, and troubleshooting of interrupt moderation and softirq receive processing.

Risks and test signals: Risks include stale device pointers during unregister, inaccurate budget/work interpretation for drivers with unusual poll semantics, and high-volume tracing on busy queues. Test signals include NAPI selftests or driver RX stress, DQL stall injection, netdev teardown with tracing enabled, and build coverage for drivers using byte queue limits.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/napi.h` completely for this pass (77 lines, 1945 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/napi.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/napi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/nbd.h -->
# sources/distributed-fs/ceph-client/include/trace/events/nbd.h

Purpose: Defines trace event classes for Network Block Device transport I/O and request send attempts. It exposes byte counts, handles, request types, and index/name information for diagnosing userspace-backed block device traffic.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(nbd_transport_event)` underlies `nbd_header_sent`, `nbd_payload_sent`, `nbd_header_received`, and `nbd_payload_received`. `DECLARE_EVENT_CLASS(nbd_send_request)` underlies request-send events and captures `struct nbd_request`, command cookie, type string, index, and size.

Control flow: NBD send and receive paths emit transport events as headers or payload fragments cross a socket. Request submission emits send-request traces as block requests are prepared for the NBD protocol. Shared event classes keep the output schema identical across send and receive phases.

State and persistence: No state is stored by the header. It snapshots transient socket/request state from the NBD device, including cookies and lengths; persistence remains in the block layer request queue and userspace NBD server.

Dependencies and integration points: Depends on Linux tracepoints and NBD internal structs from the including C files. It integrates with block layer request diagnostics, NBD socket transport, and ftrace/perf.

Risks and test signals: Risks include mismatched format specifiers for cookies or sizes, tracing partial payloads as complete transfers, and assuming request pointers remain valid outside fast assignment. Test NBD connect/disconnect, read/write/flush/discard, short sends, reconnects, timeout paths, and tracing under high queue depth.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/nbd.h` completely for this pass (107 lines, 2188 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/nbd.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/nbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/neigh.h -->
# sources/distributed-fs/ceph-client/include/trace/events/neigh.h

Purpose: Defines neighbour-subsystem tracepoints for neighbour creation, update, update completion, timer handling, event-send outcomes, and cleanup/release. It makes ARP/ND cache state transitions visible.

Important APIs/types/functions: `neigh_create`, `neigh_update`, `DECLARE_EVENT_CLASS(neigh__update)`, and derived events `neigh_update_done`, `neigh_timer_handler`, `neigh_event_send_done`, `neigh_event_send_dead`, and `neigh_cleanup_and_release`. Entries capture `struct neighbour`, netdev name, protocol family, primary key, hardware address, old/new NUD state, flags, and update return codes.

Control flow: Neighbour table code emits creation when an entry is allocated, update when link-layer address or NUD state changes, then class-based events around timer, solicitation, completion, and cleanup paths. Trace code copies variable-length keys and hardware addresses into fixed trace arrays to avoid lifetime dependence.

State and persistence: The header owns no state. It observes in-memory neighbour cache entries, which persist until garbage collection, timer expiry, explicit deletion, or device teardown.

Dependencies and integration points: Depends on skb/netdevice, `net/neighbour.h`, and tracepoint infrastructure. It integrates with IPv4 ARP, IPv6 neighbour discovery, routing, netdev lifecycle, and ftrace/perf networking diagnostics.

Risks and test signals: Risks include address-length truncation, interpreting family-specific keys incorrectly, racing neighbour deletion, and trace output hiding failed updates. Test ARP and IPv6 ND resolution, failed probes, stale-to-reachable transitions, device unregister, namespace teardown, and GC under tracing.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/neigh.h` completely for this pass (255 lines, 7021 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/neigh.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/neigh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/net.h -->
# sources/distributed-fs/ceph-client/include/trace/events/net.h

Purpose: Supplies core networking tracepoints for transmit start/completion/timeout and receive ingress/exit paths. It is a generic visibility layer for netdev TX queues, skb metadata, and NAPI/GRO/netif receive flows.

Important APIs/types/functions: TX events `net_dev_start_xmit`, `net_dev_xmit`, and `net_dev_xmit_timeout`; `DECLARE_EVENT_CLASS(net_dev_template)` for `net_dev_queue`, `netif_receive_skb`, and `netif_rx`; `DECLARE_EVENT_CLASS(net_dev_rx_verbose_template)` for verbose RX entry events; and `DECLARE_EVENT_CLASS(net_dev_rx_exit_template)` for exit return codes. Fields include skb pointers, lengths, protocol, VLAN tags, queue mappings, transport offsets, GSO details, checksum state, hash, traffic class, device names, and return codes.

Control flow: Net core emits start-xmit before driver handoff, completion after qdisc/dev return, timeout when watchdog detects a stuck queue, and receive events around GRO and `netif_receive_skb`/`netif_rx` entry and exit. Fast assignment snapshots skb fields while still valid.

State and persistence: No persistent state. Events mirror skb and netdev state moving through hot networking paths.

Dependencies and integration points: Depends on skb, netdevice, VLAN/IP, busy-poll, and trace infrastructure. Consumers include tracing tools for qdisc, driver, GRO, and receive-path debugging.

Risks and test signals: Risks are hot-path overhead, stale skb field access, format drift as skb metadata evolves, and inconsistent return-code meaning across call sites. Test with TX/RX traffic, GSO/checksum/VLAN cases, qdisc drops, watchdog timeouts, GRO list receive, and tracing during netdev unregister.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/net.h` completely for this pass (338 lines, 8576 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/net.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h -->
# sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h

Purpose: Provides shared macros used by networking trace headers to snapshot socket tuple fields. It centralizes IPv4/IPv6 address, port, and family extraction for socket-oriented tracepoints.

Important APIs/types/functions: `TP_STORE_ADDR_PORTS`, `TP_STORE_ADDRS_PORTS`, `TP_STORE_ADDR_PORTS_SKB`, and related address-copy helper macros select IPv4 or IPv6 fields and copy source/destination addresses plus ports into trace entries. The header is macro-only and is intended for inclusion inside trace event definitions.

Control flow: A tracepoint fast-assign block invokes these macros with a socket or skb. The macro branches on address family, pulls tuple data from inet/IPv6 socket state or packet headers, and stores normalized fields into the trace entry before `TP_printk`.

State and persistence: No state is owned. It only copies transient socket or skb address fields into a trace record.

Dependencies and integration points: Included by MPTCP and other net probe trace headers that need common tuple formatting. It depends on the including file to provide appropriate structs and trace entry fields.

Risks and test signals: Risks include field-name contract mismatches between macro and trace entry, IPv6-disabled build coverage, byte-order mistakes, and skb header availability assumptions. Test IPv4/IPv6 sockets, mapped addresses, unconnected sockets, skb-based probes, and compile matrices with IPv6 enabled and disabled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h` completely for this pass (115 lines, 3338 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/net_probe_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/netfs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/netfs.h

Purpose: Defines tracepoints and symbolic enums for the network-filesystem helper library. It covers read requests, write requests, subrequests, cache copy, folio state, collection/cleanup progress, reference changes, and folio-queue activity.

Important APIs/types/functions: Exported enum maps include `netfs_read_traces`, `netfs_write_traces`, `netfs_rreq_origins`, `netfs_rreq_traces`, `netfs_sreq_sources`, `netfs_sreq_traces`, `netfs_failures`, reference-trace enums, folio traces, donation traces, and folio-queue traces. Trace events include `netfs_read`, `netfs_rreq`, `netfs_sreq`, `netfs_failure`, `netfs_rreq_ref`, `netfs_sreq_ref`, `netfs_folio`, `netfs_write_iter`, `netfs_write`, `netfs_copy2cache`, `netfs_collect*`, and `netfs_folioq`.

Control flow: Netfs read/write paths emit request and subrequest events as operations are prepared, submitted to server/cache, retried, completed, redirtied, unlocked, or collected. Writeback and streaming-write collection events track gaps, streams, folios, and cleaned/collected offsets. Reference events trace lifecycle ownership.

State and persistence: The header owns no state. It observes `netfs_io_request`, `netfs_io_subrequest`, `folio`, `folio_queue`, cache cookies, inode numbers, flags, offsets, lengths, errors, refs, and stream progress. Durable data remains in backing servers, page cache, and fscache.

Dependencies and integration points: Depends on tracepoints and netfs/fscache structs supplied by including C files. It integrates with network filesystems such as CephFS, AFS, 9P, and cachefiles/fscache debugging.

Risks and test signals: Risks include enum/print mapping drift, tracing freed request/subrequest state, offset overflow in large files, missed error paths, and hot-path overhead during writeback. Test netfs readpage/readahead/direct I/O, writeback/writethrough/unbuffered write, cache copy, short reads, retry/error injection, folio invalidation, and request refcount balancing.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/netfs.h` completely for this pass (786 lines, 25452 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/netfs.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/netfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/netlink.h -->
# sources/distributed-fs/ceph-client/include/trace/events/netlink.h

Purpose: Defines a compact tracepoint for netlink extended-ack messages. It records human-readable extack text emitted by netlink validation and policy code.

Important APIs/types/functions: `netlink_extack` takes a `const char *msg`, stores it with `__string`, and prints it as `msg=%s`.

Control flow: Netlink code calls the tracepoint when an extack diagnostic is set. The trace event copies the message into the tracing buffer so later output does not depend on the original string lifetime.

State and persistence: No persistent state. It observes transient extack text associated with one netlink request.

Dependencies and integration points: Depends on tracepoints and integrates with generic netlink/rtnetlink diagnostics, policy validation, and userspace-visible error reporting.

Risks and test signals: Risks include tracing sensitive messages, missing NULL handling at call sites, and high event volume from malformed request storms. Test invalid rtnetlink/generic-netlink operations, policy failures, namespace-specific extacks, and tracing while fuzzing netlink parsers.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/netlink.h` completely for this pass (29 lines, 485 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/netlink.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h -->
# sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h

Purpose: Provides NILFS2 filesystem tracepoints for segment construction, transaction transitions, segment usage accounting, and metadata block operations. It is aimed at debugging the log-structured write path.

Important APIs/types/functions: Events include `nilfs2_collection_stage_transition`, `nilfs2_transaction_transition`, `nilfs2_segment_usage_check`, `nilfs2_segment_usage_allocated`, `nilfs2_segment_usage_freed`, `nilfs2_mdt_insert_new_block`, and `nilfs2_mdt_submit_block`. Fields include superblock device, collection stage, mode, transaction state, segment number, segment usage checks, inode numbers, block numbers, level, and mode flags.

Control flow: NILFS2 emits collection and transaction events as the segment constructor changes stages and transaction modes. Segment usage events fire when segments are checked, allocated, or freed. Metadata tracepoints track insertion/submission of metadata blocks.

State and persistence: The header stores no state. It observes in-memory NILFS2 transaction and segment metadata that corresponds to persistent log segments on disk.

Dependencies and integration points: Depends on tracepoints and NILFS2 structs supplied by including sources. It integrates with filesystem writeback, cleaner/segment usage management, and block I/O diagnostics.

Risks and test signals: Risks include mismatched symbolic stage/state names, incorrect segment identifiers, and tracing metadata after buffer lifetime changes. Test NILFS2 mount/write/fsync, cleaner activity, segment reuse, metadata updates, remount/recovery, and trace output under error injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h` completely for this pass (229 lines, 5426 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/nilfs2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/nmi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/nmi.h

Purpose: Defines the `nmi_handler` tracepoint used to record non-maskable interrupt handler execution time and return result.

Important APIs/types/functions: `nmi_handler` takes a handler function pointer, duration delta, and handled return code. It prints the handler symbol with `%ps`, the delta, and whether the NMI was handled.

Control flow: NMI dispatch code can emit this event after invoking a registered handler. The tracepoint snapshots timing and result while still in or near NMI context.

State and persistence: No persistent state. It records transient NMI dispatch observations.

Dependencies and integration points: Depends on `ktime`, tracepoints, symbol printing, and architecture NMI handling. It integrates with lockup, perf, watchdog, and platform NMI diagnostics.

Risks and test signals: Risks include using tracing paths from NMI context, symbol resolution overhead, and interpreting time deltas across clock sources. Test NMI watchdog/perf NMI paths, enabled/disabled tracing in NMI context, and lockdep/IRQ tracing configurations.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/nmi.h` completely for this pass (38 lines, 780 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/nmi.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/notifier.h -->
# sources/distributed-fs/ceph-client/include/trace/events/notifier.h

Purpose: Defines trace events for kernel notifier-chain registration, unregistration, and execution. It makes callback chain mutations and invocations observable.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(notifier_info)` captures callback pointer, priority, and return value. Derived events are `notifier_register`, `notifier_unregister`, and `notifier_run`.

Control flow: Notifier infrastructure emits register/unregister events when blocks are added or removed from a chain, and run events as callbacks are invoked. Function pointers are printed symbolically where possible.

State and persistence: No state is owned. Runtime state remains in caller-owned `struct notifier_block` lists, usually protected by the notifier chain type's lock or SRCU.

Dependencies and integration points: Depends on tracepoints and integrates with atomic/blocking/raw/SRCU notifier chains across PM, netdev, CPU hotplug, reboot, and driver subsystems.

Risks and test signals: Risks include tracing callback pointers after module unload, missing chain identity in the record, and overhead in hot notifier chains. Test register/unregister/run for blocking and atomic chains, module unload, priority ordering, and callback return aggregation.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/notifier.h` completely for this pass (69 lines, 1091 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/notifier.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/notifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/objagg.h -->
# sources/distributed-fs/ceph-client/include/trace/events/objagg.h

Purpose: Defines tracepoints for object aggregation lifecycle and tree operations. It is used to diagnose creation, destruction, reference handling, parent assignment, and root management in the `objagg` helper.

Important APIs/types/functions: Events include `objagg_create`, `objagg_destroy`, `objagg_obj_create`, `objagg_obj_destroy`, `objagg_obj_get`, `objagg_obj_put`, `objagg_obj_parent_assign`, `objagg_obj_parent_unassign`, `objagg_obj_root_create`, and `objagg_obj_root_destroy`. Fields capture object aggregator pointers, object pointers, roots, deltas, nesting counts, user counts, and parent/root relation data.

Control flow: Objagg core emits lifecycle events when an aggregator is allocated, objects are created or destroyed, references are taken or dropped, and candidate parent/root relationships are changed. Trace output reconstructs aggregation tree evolution.

State and persistence: No state is stored by the header. It observes in-memory aggregation nodes and reference counts; persistence is owned by subsystem users such as switchdev resource aggregation.

Dependencies and integration points: Depends on tracepoints and objagg structs from including C files. It integrates with networking/switching code that deduplicates hardware resource programming.

Risks and test signals: Risks include pointer reuse confusing traces, reference-count imbalance, parent/root assignment races, and missing tracepoints around failed allocation paths. Test objagg selftests, create/destroy churn, nested aggregation, refcount underflow cases, and switchdev resource programming failures.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/objagg.h` completely for this pass (228 lines, 4691 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/objagg.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/objagg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/oom.h -->
# sources/distributed-fs/ceph-client/include/trace/events/oom.h

Purpose: Provides OOM and memory-reclaim tracepoints for score adjustment, reclaim retry decisions, victim marking, OOM reaper activity, skipped reaping, and compaction retry decisions.

Important APIs/types/functions: Events include `oom_score_adj_update`, `reclaim_retry_zone`, `mark_victim`, `wake_reaper`, `start_task_reaping`, `finish_task_reaping`, `skip_task_reaping`, and `compact_retry`. Fields capture task names/PIDs, order, priority, zone watermarks, reclaimable/scanned pages, OOM flags, MM pointers, and compaction retry metadata.

Control flow: Memory-management code emits these events during allocation failure handling: reclaim retry evaluation, OOM victim selection, reaper wake/start/finish/skip, and compaction retry logic. The tracepoints snapshot task and zone values at decision points.

State and persistence: No persistent state. Observed state lives in tasks, mm structs, zones, watermarks, reclaim counters, and OOM reaper queues.

Dependencies and integration points: Depends on tracepoints and `trace/events/mmflags.h`; integrates with page allocator, reclaim, compaction, memcg/global OOM, and task lifecycle.

Risks and test signals: Risks include racing task exit, stale mm pointers, interpreting zone counters under concurrent reclaim, and excessive output during memory pressure. Test forced OOM, memcg OOM, reaper disabled/skipped paths, compaction retry cases, high-order allocation failures, and tracepoint build coverage.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/oom.h` completely for this pass (223 lines, 5066 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/oom.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/oom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/osnoise.h -->
# sources/distributed-fs/ceph-client/include/trace/events/osnoise.h

Purpose: Defines osnoise/timerlat tracing events that measure operating-system interference, interrupt noise, thread noise, NMI noise, and threshold samples for latency analysis.

Important APIs/types/functions: Events include `osnoise_sample`, `timerlat_sample`, `thread_noise`, `softirq_noise`, `irq_noise`, `nmi_noise`, and `sample_threshold`. They record runtime, noise, max samples, hardware counter usage, IRQ/thread identifiers, vectors, descriptions, and latency thresholds.

Control flow: The tracing/osnoise monitor emits samples at periodic measurement points and emits noise events when a thread, IRQ, softirq, or NMI contributes latency. Timerlat paths report timer wakeup latency and threshold crossing information.

State and persistence: No state is stored in the header. Runtime state is in tracer instances, per-CPU counters, and timing measurements; trace records are ephemeral.

Dependencies and integration points: Depends on tracepoints and integrates with kernel tracing, latency analysis, IRQ/softirq/NMI accounting, and real-time workload validation.

Risks and test signals: Risks include measurement perturbation, incorrect attribution between interrupt classes, CPU hotplug interactions, and clock-source inconsistencies. Test osnoise/timerlat tracers under idle and loaded systems, IRQ storms, softirq load, RT scheduling, CPU isolation/nohz_full, and threshold configuration changes.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/osnoise.h` completely for this pass (238 lines, 5394 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/osnoise.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/osnoise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h -->
# sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h

Purpose: Defines a tracepoint for page-isolation checks used by memory offlining, compaction, and page migration diagnostics.

Important APIs/types/functions: `test_pages_isolated` records a PFN range, isolated start/end PFNs, and the result of an isolation test.

Control flow: Memory isolation code emits the event after testing whether a range can be isolated. It captures both requested and actually isolated spans to explain failures or partial isolation.

State and persistence: No state is owned. It observes zone/pageblock isolation state and page migration conditions in memory-management code.

Dependencies and integration points: Depends on tracepoints and integrates with memory hotplug, CMA, compaction, alloc_contig_range, and page migration workflows.

Risks and test signals: Risks include PFN range off-by-one errors, missing context for why a page failed isolation, and hotplug races. Test memory offline/online, CMA allocation, gigantic page allocation, movable/unmovable page ranges, and isolation failure injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h` completely for this pass (39 lines, 943 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/page_isolation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/page_pool.h -->
# sources/distributed-fs/ceph-client/include/trace/events/page_pool.h

Purpose: Provides tracepoints for network page-pool lifecycle and page reference handoff. It helps debug recycling, release, hold, and NUMA-node updates in high-speed RX paths.

Important APIs/types/functions: Events are `page_pool_release`, `page_pool_state_release`, `page_pool_state_hold`, and `page_pool_update_nid`. Fields include page-pool pointer, netdev info when available, inflight count, hold/release deltas, page pointer, page refcount, DMA address, page flags, and NUMA node.

Control flow: Page-pool code emits release events when pools are destroyed or drained, state events when pages are held or released from the pool, and nid updates when allocation locality changes. Trace records tie a page and DMA address back to a pool.

State and persistence: No state is owned by the header. Runtime state resides in `struct page_pool`, pages, DMA mappings, and driver RX queues; records are transient.

Dependencies and integration points: Depends on `net/page_pool/types.h`, MM flag printing, tracepoints, and network drivers using page_pool for RX recycling.

Risks and test signals: Risks include refcount imbalance, DMA unmap ordering, pool destruction with inflight pages, NUMA drift, and driver misuse of recycled pages. Test high-rate RX, XDP page recycling, pool teardown under traffic, NUMA node updates, and page leak detection with tracing.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/page_pool.h` completely for this pass (119 lines, 2831 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/page_pool.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/page_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/page_ref.h -->
# sources/distributed-fs/ceph-client/include/trace/events/page_ref.h

Purpose: Defines trace classes for page reference-count modifications. It enables low-level debugging of page/folio lifetime bugs.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(page_ref_mod_template)` underlies `page_ref_set`, `page_ref_mod`, and `page_ref_unfreeze`. `DECLARE_EVENT_CLASS(page_ref_mod_and_test_template)` underlies `page_ref_mod_and_test`, `page_ref_mod_and_return`, `page_ref_mod_unless`, and `page_ref_freeze`. Fields include page pointer, PFN, flags, count, mapcount, mapping, mt, val, and return value.

Control flow: Page reference helpers emit events when setting, incrementing/decrementing, freezing, unfreezing, or conditionally modifying counts. The tracepoint snapshots page identity and counters around the atomic operation.

State and persistence: The header owns no state. It observes page/folio refcounts and mapping metadata that control physical page lifetime.

Dependencies and integration points: Depends on `linux/page_ref.h`, MM flags, tracepoints, and memory-management internals. It integrates with debug configs and page lifetime tracing.

Risks and test signals: Risks include high overhead on ubiquitous refcount paths, reading page metadata while it changes, and traces that are hard to interpret after page reuse. Test page_ref debug builds, folio allocation/free, migration, GUP, page cache, slab-backed pages where applicable, and leak/use-after-free investigations.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/page_ref.h` completely for this pass (135 lines, 3058 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/page_ref.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/page_ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pagemap.h -->
# sources/distributed-fs/ceph-client/include/trace/events/pagemap.h

Purpose: Provides tracepoints for LRU insertion and activation in the page cache and memory-management pagemap layer.

Important APIs/types/functions: `mm_lru_insertion` records page/folio pointer, PFN, lru flag state, and whether the insertion is file or anon. `mm_lru_activate` records page/folio activation metadata.

Control flow: MM code emits insertion when pages enter an LRU list and activation when reclaim/access logic promotes pages. Trace fast assignment snapshots flags and mapping-related state.

State and persistence: No state is stored by the header. It observes folio/page LRU state in memory; persistence is only the page cache and backing memory state outside tracing.

Dependencies and integration points: Depends on `linux/mm.h` and tracepoints. It integrates with page cache, reclaim, workingset detection, and memory-pressure diagnostics.

Risks and test signals: Risks include excessive event volume, folio/page terminology drift, flag interpretation errors, and tracing pages during migration or free. Test page cache workloads, anonymous memory pressure, reclaim/activation behavior, memcg pressure, and LRU transitions with tracing enabled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pagemap.h` completely for this pass (83 lines, 2190 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pagemap.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pagemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pci.h -->
# sources/distributed-fs/ceph-client/include/trace/events/pci.h

Purpose: Defines PCI and PCIe tracepoints for hotplug events and link-state changes. It helps diagnose PCI slot notifications and PCIe link speed/width transitions.

Important APIs/types/functions: `pci_hp_event` records slot name, slot number, device/function, and event code. `pcie_link_event` records bus/device/function, link speed, link width, and link state. Symbolic maps decode hotplug events and PCIe link speeds/widths.

Control flow: PCI hotplug and PCIe link-management code emit these events when slot events arrive or link parameters/state are observed. Tracepoint fields are copied from `struct pci_dev` and PCIe capability data.

State and persistence: No state is owned. It observes kernel PCI device and slot state; durable configuration is in hardware/firmware and PCI core data structures.

Dependencies and integration points: Depends on UAPI PCI register definitions and tracepoints. It integrates with PCI hotplug drivers, PCIe link training/power management, and ftrace/perf hardware diagnostics.

Risks and test signals: Risks include stale pci_dev/slot data during hot-remove, incorrect symbolic speed/width decoding, and missing vendor-specific hotplug reasons. Test PCIe hotplug, link retrain, ASPM changes, surprise removal, and builds across PCI configs.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pci.h` completely for this pass (129 lines, 3442 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pci.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h -->
# sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h

Purpose: Defines a tracepoint for PCIe controller LTSSM state transitions. It exposes low-level link-training state-machine movement in host/controller drivers.

Important APIs/types/functions: `pcie_ltssm_state_transition` records device BDF, old state, and new state. Symbolic mapping uses PCIe LTSSM state constants.

Control flow: PCIe controller or endpoint code emits the event when the link-training and status state machine changes. The trace record allows ordering of link bring-up, recovery, and failure states.

State and persistence: No state is stored by the header. It observes controller hardware state and PCI core device identity.

Dependencies and integration points: Depends on PCI register definitions and tracepoints. It integrates with PCIe host controller drivers and low-level link diagnostics.

Risks and test signals: Risks include incomplete LTSSM enum coverage, noisy transitions during unstable links, and reading device identity while link/device is disappearing. Test cold boot link training, reset/retrain, endpoint hotplug, link-down recovery, and controller-specific error injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h` completely for this pass (58 lines, 1329 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pci_controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/percpu.h -->
# sources/distributed-fs/ceph-client/include/trace/events/percpu.h

Purpose: Provides tracepoints for percpu allocator success, failure, chunk creation, chunk destruction, and frees. It helps diagnose allocation size/alignment, atom size, group choice, and fragmentation.

Important APIs/types/functions: Events include `percpu_alloc_percpu`, `percpu_free_percpu`, `percpu_alloc_percpu_fail`, `percpu_create_chunk`, and `percpu_destroy_chunk`. Fields capture reserved/dynamic flag, allocation size, alignment, base/offset, group, bits, unit size, atom size, allocated/free population, and failure reason.

Control flow: The percpu allocator emits events when requests are satisfied, fail, or cause backing chunks to be created/destroyed. Free events record address and allocation characteristics.

State and persistence: No state is owned by the header. It observes in-memory percpu allocator metadata and allocated areas, which live until freed or allocator teardown.

Dependencies and integration points: Depends on tracepoints and MM flag formatting. It integrates with core allocator diagnostics, module loading, networking, scheduler, and any subsystem using per-CPU storage.

Risks and test signals: Risks include hot-path overhead, leaking sensitive addresses in traces, mismatched unit/group interpretation, and missing failure context. Test percpu allocator selftests, module load/unload churn, large alignment requests, fragmentation pressure, NUMA configs, and allocation-failure injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/percpu.h` completely for this pass (137 lines, 3186 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/percpu.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/power.h -->
# sources/distributed-fs/ceph-client/include/trace/events/power.h

Purpose: Defines broad power-management tracepoints covering CPU idle/frequency, PSCI domain idle, wakeup sources, power domains, device PM callbacks, suspend/resume phases, PM QoS, device PM QoS, pstate samples, CPU frequency limits, idle misses, and guest halt polling.

Important APIs/types/functions: Event classes include `cpu`, `psci_domain_idle`, `wakeup_source`, `power_domain`, `cpu_latency_qos_request`, `pm_qos_update`, and `dev_pm_qos_request`. Standalone events include `cpu_idle_miss`, `pstate_sample`, `cpu_frequency_limits`, `device_pm_callback_start`, `device_pm_callback_end`, `suspend_resume`, and `guest_halt_poll_ns`.

Control flow: CPU idle/frequency governors, PSCI, PM domains, wakeup-source accounting, driver-core PM callbacks, suspend/resume core code, PM QoS updates, and virtualization halt-poll code emit events as state changes or callbacks start/end. Trace entries snapshot device names, callback pointers, event names, states, request values, timestamps, and CPU IDs.

State and persistence: No state is owned. It observes runtime PM state in devices, domains, QoS constraints, CPU policy, and suspend/resume sequencing. Trace records are transient.

Dependencies and integration points: Depends on cpufreq, ktime, PM QoS, trace events, and tracepoints. It integrates with driver core, CPU idle/freq, PM domains, wakeup-source infrastructure, suspend/hibernate, and KVM halt-poll tuning.

Risks and test signals: Risks include tracing during fragile suspend/noirq windows, callback pointer symbol drift, inconsistent CPU state naming, and event storms. Test suspend-to-idle/RAM, hibernation, runtime PM, cpufreq transitions, wakeup-source leaks, PM QoS add/update/remove, PSCI idle domains, and guest halt polling changes.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/power.h` completely for this pass (531 lines, 11479 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/power.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h -->
# sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h

Purpose: Defines a trace event for CPU migration decisions tied to power/performance balancing. It exposes source CPU, destination CPU, and load information.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(cpu_migrate)` and the derived migration event record `src_cpu`, `dest_cpu`, and load. The trace system is `power`.

Control flow: Scheduler or power-aware migration code emits the event when a task/load decision moves work between CPUs. The trace entry captures the migration endpoints and load metric used by the caller.

State and persistence: No state is owned. It observes scheduler CPU/load state at a decision point.

Dependencies and integration points: Depends on tracepoints and integrates with scheduler energy-aware scheduling, CPU topology, cpufreq/cpuidle analysis, and power tracing.

Risks and test signals: Risks include ambiguous load units, missing task identity, and high volume on migration-heavy workloads. Test CPU hotplug, schedutil/EAS workloads, asymmetric CPU capacity systems, migration stress, and tracing with scheduler latency tools.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h` completely for this pass (68 lines, 1625 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h -->
# sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h

Purpose: Provides tracepoints for IRQ and preemption enable/disable transitions. These events support latency analysis and tracing of critical sections.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(preemptirq_template)` backs `irq_disable`, `irq_enable`, `preempt_disable`, and `preempt_enable`. Fields include caller instruction pointer, parent instruction pointer, and symbolic caller/parent output.

Control flow: IRQ/preempt instrumentation emits events when code disables or re-enables interrupts or preemption. The tracepoint records call-site identity so long critical sections can be attributed.

State and persistence: No state is stored. It observes transient CPU-local preempt/IRQ state.

Dependencies and integration points: Depends on ktime, tracepoints, string helpers, and `asm/sections.h` for symbol classification. It integrates with ftrace irqsoff/preemptoff latency tracers and lockdep-style debugging.

Risks and test signals: Risks include recursion in tracing instrumentation, symbol resolution costs, NMI/IRQ context constraints, and config-dependent availability. Test irqsoff/preemptoff tracers, lockdep configs, nested disable/enable, module call sites, and architecture build matrices.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h` completely for this pass (70 lines, 1839 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/preemptirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/printk.h -->
# sources/distributed-fs/ceph-client/include/trace/events/printk.h

Purpose: Defines the console tracepoint for printk console output. It allows tracing tools to observe text emitted to consoles.

Important APIs/types/functions: `console` takes a text buffer and length, stores the message with `__string_len`, and prints the copied message.

Control flow: printk/console code emits the event when text is about to be written through console paths. The tracepoint copies the message payload so output is independent of the original buffer lifetime.

State and persistence: No state is owned. It observes printk text; durable log storage remains in printk ring buffers, consoles, pstore, or external logging.

Dependencies and integration points: Depends on tracepoints and printk console paths. It integrates with ftrace/perf debugging of console latency and message ordering.

Risks and test signals: Risks include recursion when tracing printk output, exposing sensitive console messages, length truncation or embedded NUL handling, and high overhead during log storms. Test boot-time printk, long messages, panic/oops paths, console suspend/resume, and tracing recursion protection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/printk.h` completely for this pass (37 lines, 786 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/printk.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pwc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/pwc.h

Purpose: Defines tracepoints for Philips webcam driver handler entry and exit. It tracks USB request handling around driver-specific control or data paths.

Important APIs/types/functions: `pwc_handler_enter` and `pwc_handler_exit` record the USB device pointer, handler identifier/name, and exit status or return value.

Control flow: The PWC driver emits enter before invoking a handler and exit after completion. Trace output pairs start/end records to diagnose handler latency and failures.

State and persistence: No state is owned. It observes `struct usb_device` and handler-local status while the webcam driver owns the device.

Dependencies and integration points: Depends on USB and tracepoint headers. It integrates with the PWC V4L/USB driver, USB device lifecycle, and media debugging.

Risks and test signals: Risks include tracing after USB disconnect, handler-name lifetime issues, and missing pairing on early returns. Test webcam probe, streaming start/stop, control requests, disconnect during active operation, and handler error paths with tracing enabled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pwc.h` completely for this pass (65 lines, 1672 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pwc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pwm.h -->
# sources/distributed-fs/ceph-client/include/trace/events/pwm.h

Purpose: Defines PWM framework tracepoints for waveform conversion, waveform read/write, and state get/apply operations. It exposes period, duty, offset, polarity, and enable state for PWM chips.

Important APIs/types/functions: Events include `pwm_round_waveform_tohw`, `pwm_round_waveform_fromhw`, `pwm_read_waveform`, `pwm_write_waveform`, and event-class `pwm` used by `pwm_apply` and `pwm_get`. Fields capture PWM device/chip identifiers and `struct pwm_waveform` or `struct pwm_state` values.

Control flow: PWM core or drivers emit conversion events when translating generic waveforms to/from hardware representations, read/write events when accessing hardware, and apply/get events around public state APIs.

State and persistence: No state is owned. It observes PWM device runtime state and hardware-facing waveform data; persistent behavior is in device registers and consumer configuration.

Dependencies and integration points: Depends on `linux/pwm.h` and tracepoints. It integrates with PWM consumers such as backlight, fans, haptics, regulators, and SoC PWM drivers.

Risks and test signals: Risks include unit conversion mistakes, overflow in period/duty/offset arithmetic, polarity confusion, and traces diverging from hardware state if drivers round differently. Test apply/get, disabled state, inverse polarity, edge periods/duties, waveform round-trip, and multiple PWM chips.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pwm.h` completely for this pass (178 lines, 3939 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pwm.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/pwm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/qdisc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/qdisc.h

Purpose: Provides traffic-control qdisc tracepoints for enqueue, dequeue, drop, reset, destroy, and create operations. It makes qdisc queueing behavior observable in the network stack.

Important APIs/types/functions: Events include `qdisc_dequeue`, `qdisc_enqueue`, `qdisc_drop`, `qdisc_reset`, `qdisc_destroy`, and `qdisc_create`. Fields capture qdisc pointer, parent handle, ifindex, device name, skb pointer, length, packet count, backlog, return codes, and drop reason symbols.

Control flow: TC/qdisc code emits events when packets enter or leave queues, are dropped, qdiscs are reset/destroyed/created, or enqueue/dequeue actions return. Trace data allows reconstruction of queue depth and drop behavior.

State and persistence: No state is stored. It observes in-memory qdisc and skb state; qdisc configuration persists only via TC/netlink setup outside tracing.

Dependencies and integration points: Depends on skb, netdevice, ftrace, packet scheduler headers, `net/sch_generic.h`, and tracepoints. It integrates with TC, netdev TX scheduling, and drop monitoring.

Risks and test signals: Risks include hot-path overhead, skb lifetime after drop, inconsistent drop-reason coverage, and qdisc pointer reuse. Test pfifo/fq_codel/netem/ingress qdiscs, enqueue/dequeue stress, drops, reset/destroy during traffic, and TC netlink reconfiguration.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/qdisc.h` completely for this pass (204 lines, 5158 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/qdisc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/qdisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/qla.h -->
# sources/distributed-fs/ceph-client/include/trace/events/qla.h

Purpose: Defines a QLogic driver logging trace event class. It provides tracepoint-backed debug logging for QLA driver messages.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(qla_log_event)` and derived `ql_dbg_log` capture a message string, likely produced by QLA debug macros.

Control flow: QLA driver logging code emits the tracepoint when debug messages are generated. The trace event copies the message string into the ring buffer.

State and persistence: No state is owned. It observes transient driver debug messages; hardware and driver state remain in QLA adapter structures.

Dependencies and integration points: Depends on tracepoints and integrates with QLogic SCSI/Fibre Channel driver diagnostics and ftrace/perf logging.

Risks and test signals: Risks include unbounded or sensitive debug text, NULL/non-terminated strings, and volume under error storms. Test QLA probe, link events, I/O errors, debug logging enablement, module unload, and trace output formatting.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/qla.h` completely for this pass (46 lines, 905 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/qla.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/qla.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/qrtr.h -->
# sources/distributed-fs/ceph-client/include/trace/events/qrtr.h

Purpose: Defines QRTR namespace and message tracepoints for Qualcomm IPC Router service discovery and namespace traffic.

Important APIs/types/functions: Events include `qrtr_ns_service_announce_new`, `qrtr_ns_service_announce_del`, `qrtr_ns_server_add`, and `qrtr_ns_message`. Fields capture service, instance, node, port, endpoint node/port, message type, and SQ family data.

Control flow: QRTR namespace code emits announce events when services appear/disappear, server-add events when namespace servers are registered, and message events for namespace messages. Trace records track discovery propagation.

State and persistence: No state is owned. It observes QRTR node/port/service records and namespace messages, which are runtime IPC state.

Dependencies and integration points: Depends on `linux/qrtr.h` and tracepoints. It integrates with Qualcomm remoteproc/subsystem IPC, QRTR sockets, and service discovery.

Risks and test signals: Risks include confusing node/port lifetimes, missing delete events, malformed message decoding, and high trace volume in service churn. Test QRTR service announce/delete, remote subsystem restart, namespace server registration, malformed messages, and tracing across network namespaces if supported.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/qrtr.h` completely for this pass (118 lines, 2590 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/qrtr.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/qrtr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rcu.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rcu.h

Purpose: Defines extensive RCU tracepoints for utilization, grace periods, expedited grace periods, funnel locks, no-CB wakeups, preempted readers, quiescent-state reporting, stall warnings, callback lifecycle, segmented callback stats, batch start/end, callback invocation, torture reads, and barriers.

Important APIs/types/functions: Events include `rcu_utilization`, `rcu_grace_period`, `rcu_future_grace_period`, `rcu_grace_period_init`, `rcu_exp_grace_period`, `rcu_exp_funnel_lock`, `rcu_nocb_wake`, `rcu_preempt_task`, `rcu_unlock_preempted_task`, `rcu_quiescent_state_report`, `rcu_fqs`, `rcu_stall_warning`, `rcu_watching`, `rcu_callback`, `rcu_segcb_stats`, `rcu_batch_start`, `rcu_invoke_callback`, `rcu_invoke_kvfree_callback`, `rcu_invoke_kfree_bulk_callback`, `rcu_sr_normal`, `rcu_batch_end`, `rcu_torture_read`, and `rcu_barrier`.

Control flow: RCU core emits events as readers enter/exit extended quiescent states, grace periods are requested/initialized/advanced/completed, callbacks are queued and invoked, stalls are detected, no-CB kthreads wake, and barriers drain callbacks. Many events use `TRACE_EVENT_RCU` to compile out cleanly when RCU tracing is disabled.

State and persistence: No state is owned. It observes RCU global/per-CPU state, GP sequence numbers, callback queues, task pointers, CPU masks, and stall diagnostics.

Dependencies and integration points: Depends on tracepoints and RCU internals. It integrates with scheduler, idle, callback offload, memory reclamation, torture testing, and ftrace/perf.

Risks and test signals: Risks include recursion or overhead in core synchronization paths, sequence-number misinterpretation, config-gated tracepoint drift, and exposing callback pointers after module unload. Test TREE_RCU/PREEMPT_RCU configs, expedited GP, callback flooding, CPU hotplug, no-CB CPUs, stall injection, rcutorture, and barrier-heavy workloads.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rcu.h` completely for this pass (830 lines, 24365 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rcu.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h

Purpose: Defines RDMA core tracepoints for completion queue scheduling/polling/allocation/free and memory-region allocation/deregistration. It supports diagnosing CQ workqueue behavior and MR resource lifecycle.

Important APIs/types/functions: CQ events include `cq_schedule`, `cq_reschedule`, `cq_process`, `cq_poll`, `cq_drain_complete`, `cq_modify`, `cq_alloc`, `cq_alloc_error`, and `cq_free`. MR events include `mr_alloc`, `mr_integ_alloc`, and `mr_dereg`. Symbolic maps decode `ib_poll_context` and `ib_mr_type`.

Control flow: RDMA core emits CQ events when work is scheduled, rescheduled, processed, polled, drained, modified, allocated, or freed. MR events fire when protection-domain memory regions are allocated, integrity MRs are allocated, or regions are deregistered.

State and persistence: No state is owned. It observes RDMA core objects such as `ib_cq`, `ib_device`, `ib_pd`, `ib_mr`, queue depths, poll contexts, completion counts, and return codes.

Dependencies and integration points: Depends on `rdma/ib_verbs.h` and tracepoints. It integrates with all RDMA providers and upper-layer protocols including RPC/RDMA and storage/network fabrics.

Risks and test signals: Risks include object lifetime races during destroy, provider-specific return code semantics, missing CQ context in errors, and high output under CQ load. Test CQ allocation/free, interrupt and workqueue polling, resize/modify, drain, MR alloc/dereg, provider error injection, and module unload.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h` completely for this pass (394 lines, 7193 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rdma_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/readahead.h -->
# sources/distributed-fs/ceph-client/include/trace/events/readahead.h

Purpose: Defines page-cache readahead tracepoints for unbounded readahead, order-based folio readahead, and sync/async readahead operations.

Important APIs/types/functions: Events include `page_cache_ra_unbounded`, `page_cache_ra_order`, and event-class `page_cache_ra_op` used by `page_cache_sync_ra` and `page_cache_async_ra`. Fields include inode, file pointer, device, index, request count, order, readahead window size, async size, and return/allocated counts.

Control flow: Filemap/readahead code emits events when readahead is triggered directly, when larger-order folios are considered, and when sync or async readahead windows are calculated and submitted.

State and persistence: No state is owned. It observes file readahead state in `struct file_ra_state`, inode/page-cache indices, and allocation results.

Dependencies and integration points: Depends on MM, fs, pagemap, and tracepoints. It integrates with filesystems, page cache, block/network-backed file reads, and performance analysis.

Risks and test signals: Risks include index/count overflow on large files, misreading async window behavior, and high event volume on sequential workloads. Test sequential/random reads, mmap faults, large folio readahead, direct readahead calls, network filesystems, and memory-pressure allocation failures.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/readahead.h` completely for this pass (132 lines, 3680 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/readahead.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/readahead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/regulator.h -->
# sources/distributed-fs/ceph-client/include/trace/events/regulator.h

Purpose: Defines regulator framework trace events for enable/disable, bypass, voltage setting, and operation completion. It helps debug power rail sequencing and constraints.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(regulator_basic)` backs enable/disable/bypass start and completion events. `DECLARE_EVENT_CLASS(regulator_range)` backs `regulator_set_voltage`. `DECLARE_EVENT_CLASS(regulator_value)` backs `regulator_set_voltage_complete`. Fields include regulator name and min/max/value microvolts.

Control flow: Regulator core emits basic events around enable/disable/bypass requests and completion, voltage range events before applying constraints, and value events after a voltage is selected or read back.

State and persistence: No state is owned. It observes runtime regulator device state, constraints, and hardware operations. Persistent power sequencing is defined by board firmware, constraints, and regulator hardware.

Dependencies and integration points: Depends on ktime and tracepoints. It integrates with regulator core, PM, device drivers, board constraints, and power sequencing diagnostics.

Risks and test signals: Risks include missing failed-completion context, name lifetime assumptions, voltage-unit mistakes, and traces during sleep-sensitive power transitions. Test enable/disable nesting, bypass toggles, voltage range constraints, deferred probe, suspend/resume rails, and regulator fault injection.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/regulator.h` completely for this pass (174 lines, 2882 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/regulator.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h

Purpose: Defines SUNRPC GSS authentication tracepoints for client and server GSS-API operations, context lifecycle, sequence-number validation, gssd upcalls, context import, pseudoflavor selection, and mechanism lookup failures.

Important APIs/types/functions: Symbolic maps cover RPC GSS services, GSS major status values, and Kerberos pseudoflavors. Event classes include `rpcgss_gssapi_event`, `rpcgss_ctx_class`, `rpcgss_svc_gssapi_class`, and `rpcgss_svc_seqno_class`. Events include `rpcgss_import_ctx`, client `get_mic`/`verify_mic`/`wrap`/`unwrap`, context init/destroy, server wrap/unwrap/mic/get_mic, wrap/unwrap failure, bad sequence events, accept upcall, authenticate, `rpcgss_seqno`, `rpcgss_need_reencode`, `rpcgss_update_slack`, upcall message/result, context details, `rpcgss_createauth`, and `rpcgss_oid_to_mech`.

Control flow: Client and server SUNRPC auth paths emit events while creating credentials, importing contexts, wrapping/unwrapping/verifying messages, checking sequence windows, talking to gssd, and adjusting XDR slack. Trace entries copy task/client IDs, XIDs, principals, remote addresses, status codes, sequence numbers, and auth sizing.

State and persistence: No state is owned. It observes RPC task/auth/context state, server request state, gssd upcall data, and sequence windows. Security context persistence belongs to RPC/GSS caches and userspace gssd.

Dependencies and integration points: Depends on tracepoints and `trace/misc/sunrpc.h`; integrates with NFS/SUNRPC client and server RPCSEC_GSS authentication.

Risks and test signals: Risks include leaking principal/upcall data, status mapping drift, sequence-window race interpretation, and task/request pointer lifetime issues. Test Kerberos krb5/krb5i/krb5p mounts, context expiry/renewal, bad sequence replay, gssd failure, server accept upcalls, wrap/unwrap failures, and trace output permission handling.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h` completely for this pass (688 lines, 14931 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rpcgss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h

Purpose: Defines the largest RPC/RDMA trace surface, covering client connection management, send/receive completions, memory registration, chunk marshalling, reply decoding, callback setup, server accept/decode/encode/DMA/sendqueue paths, and RDMA device notifications.

Important APIs/types/functions: Event classes include completion, send/receive flush, MR completion, receive success, reply, transport, connection, read/write chunk, MR, callback, server accept, bad request, DMA map, post chunk, sendqueue, client device, and client registration classes. Events cover `xprtrdma_inline_thresh`, connect/disconnect/device removal, MR creation/no-MR errors, read/write/reply chunks, marshal/failure/prepsend, post send/recv, FRWR alloc/dereg/map errors, reply/error/fixup/decode-seg/MR zap, callback setup/call/reply, server accept errors, request decode and short/bad request errors, segment encode/decode, DMA map/unmap/errors, send pullup/send/post/completions, read/write/reply completions, QP errors, SQ full/retry/post errors, and client add/remove/register notifications.

Control flow: Client xprtrdma emits events through connection negotiation, request marshalling, chunk list construction, send/receive posting, CQ completions, memory registration/local invalidation, reply decode, and callback handling. Server svcrdma emits events through RDMA accept, request header decode, chunk segment decode/encode, DMA mapping, send context posting, completion handling, queue pressure, and device removal.

State and persistence: No state is owned. It observes `rpcrdma_xprt`, endpoints, requests, replies, MRs, RDMA CIDs, work completions, CQs, QPs, DMA addresses, chunks, server contexts, and RDMA devices. Persistent NFS/RPC data is outside this header; RDMA resources persist only until deregistration/disconnect.

Dependencies and integration points: Depends on scatterlist, SUNRPC RDMA CID definitions, RDMA CM/verbs, and trace misc helpers for RDMA/SUNRPC. It integrates with NFS over RDMA client/server, RDMA providers, DMA mapping, and RPC transport diagnostics.

Risks and test signals: Risks include object lifetime races in CQ callbacks, exposing DMA addresses/remote keys, endian mistakes in RPC/RDMA header decoding, MR leak or invalidation imbalance, sendqueue credit bugs, provider-specific WC statuses, and trace overhead on high-throughput RDMA. Test NFS/RDMA mount/read/write, krb5 over RDMA where supported, connection loss/reconnect/device removal, FRWR registration failure, remote invalidation, malformed RPC/RDMA headers, SQ exhaustion, CQ error completions, server read/write/reply chunks, and provider unload.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h` completely for this pass (2341 lines, 51394 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rpcrdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rpm.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rpm.h

Purpose: Defines runtime power-management tracepoints for suspend/resume/idle/usage operations, integer return values, and status changes.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(rpm_internal)` backs `rpm_suspend`, `rpm_resume`, `rpm_idle`, and `rpm_usage`. `rpm_return_int` records callback return values, and `rpm_status` records status transitions. Symbolic maps decode runtime PM request, event, and status values.

Control flow: Runtime PM core emits internal events when usage counts or requests drive idle/suspend/resume decisions, return events after callbacks, and status events when device runtime state changes.

State and persistence: No state is owned. It observes `struct device` runtime PM fields, usage counts, disable depth, child counts, request type, status, and errors. Runtime PM state is in-memory and device-lifetime scoped.

Dependencies and integration points: Depends on ktime and tracepoints. It integrates with driver core runtime PM, autosuspend, PM domains, bus callbacks, and device drivers.

Risks and test signals: Risks include tracing under PM locks, confusing request/status symbolic maps, callback return interpretation, and high event volume during autosuspend churn. Test runtime PM get/put balance, autosuspend, forbid/allow, supplier/consumer links, system suspend interaction, callback failures, and device unbind while active.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rpm.h` completely for this pass (149 lines, 3427 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rpm.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rseq.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rseq.h

Purpose: Defines restartable-sequence tracepoints for task rseq pointer updates and instruction-pointer fixups after aborts or signal/preemption events.

Important APIs/types/functions: `rseq_update` records task PID, old rseq pointer, and new rseq pointer. `rseq_ip_fixup` records PID, original IP, fixed IP, and abort IP.

Control flow: rseq syscall or task setup paths emit update events when a task registers/unregisters its rseq area. Architecture/core rseq abort handling emits IP fixup when execution is redirected to an abort handler.

State and persistence: No state is owned. It observes per-task rseq registration and transient instruction pointer correction. The rseq userspace area persists in the task address space while registered.

Dependencies and integration points: Depends on tracepoints and types. It integrates with scheduler preemption, signal delivery, rseq syscall handling, and userspace per-CPU fast paths.

Risks and test signals: Risks include exposing userspace addresses, arch-specific IP correction drift, and tracing during signal/preempt paths. Test rseq selftests, register/unregister, migration/preemption aborts, signal aborts, exec/clone behavior, and 32/64-bit compat paths.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rseq.h` completely for this pass (62 lines, 1482 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rseq.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rtc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rtc.h

Purpose: Defines RTC tracepoints for time/alarm read and set, IRQ frequency/state, alarm IRQ enablement, offset read/set, and RTC timer enqueue/dequeue/fire.

Important APIs/types/functions: `rtc_time_alarm_class` backs `rtc_set_time`, `rtc_read_time`, `rtc_set_alarm`, and `rtc_read_alarm`. Standalone events include `rtc_irq_set_freq`, `rtc_irq_set_state`, and `rtc_alarm_irq_enable`. `rtc_offset_class` backs `rtc_set_offset` and `rtc_read_offset`. `rtc_timer_class` backs `rtc_timer_enqueue`, `rtc_timer_dequeue`, and `rtc_timer_fired`.

Control flow: RTC core/drivers emit events when userspace or kernel callers read/set time or alarms, configure periodic IRQs, enable alarms, adjust offset calibration, or manipulate RTC timers.

State and persistence: No state is owned. It observes RTC time/alarm/timer state; actual persistence is in RTC hardware and driver-managed timers.

Dependencies and integration points: Depends on `linux/rtc.h` and tracepoints. It integrates with RTC class devices, alarmtimer, suspend wake alarms, and userspace `/dev/rtc`/sysfs operations.

Risks and test signals: Risks include time normalization errors, timezone/UTC confusion outside RTC core, alarm enable races, offset unit mistakes, and timer lifetime issues. Test read/set time, alarm wake from suspend, periodic IRQs, offset calibration, timer enqueue/dequeue/fire, invalid times, and RTC device removal.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rtc.h` completely for this pass (206 lines, 3354 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rtc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h

Purpose: Provides a minimal tracepoint used by Rust kernel sample code to report that the sample module loaded.

Important APIs/types/functions: `TRACE_SYSTEM rust_sample`; `rust_sample_loaded` takes a `const char *message`, copies it with `__string`, and prints it.

Control flow: The Rust sample module can call the generated trace function during initialization or demonstration code. The trace event stores the sample message in the ring buffer.

State and persistence: No state is owned. It observes a transient string from sample code.

Dependencies and integration points: Depends on tracepoints and `trace/define_trace.h`. It integrates with Rust-for-Linux sample build paths and the generic tracepoint generation machinery.

Risks and test signals: Risks are mostly build-system and FFI contract issues: string lifetime, Rust/C tracepoint binding drift, and sample availability under config changes. Test Rust sample module load/unload, tracepoint enablement, and builds with Rust support toggled.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h` completely for this pass (31 lines, 683 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rust_sample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h

Purpose: Defines tracepoints for raw MMIO read/write operations and post-read/post-write instrumentation. It helps debug register access ordering and values.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(rwmmio_rw_template)` backs `rwmmio_write` and `rwmmio_post_write`. Standalone events `rwmmio_read` and `rwmmio_post_read` capture caller, MMIO address, width, and value or return value.

Control flow: Instrumented MMIO accessors emit write/read events before or after accessing registers. Post events can confirm ordering or values after barriers/relaxed operations depending on caller usage.

State and persistence: No state is owned. It observes transient register addresses, values, access widths, and call sites. Hardware registers hold the actual state.

Dependencies and integration points: Depends on tracepoints and symbol printing. It integrates with architecture MMIO access instrumentation, driver register debugging, and ftrace/perf.

Risks and test signals: Risks include leaking MMIO addresses/values, perturbing timing-sensitive register access, recursion from tracing backend MMIO, and width/value mismatch. Test read/write instrumentation on platform devices, relaxed vs ordered accessors, 8/16/32/64-bit widths, early boot constraints, and tracing during driver probe/remove.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h` completely for this pass (108 lines, 2731 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rwmmio.h -->
