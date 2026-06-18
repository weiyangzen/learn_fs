# sources/distributed-fs/ceph-client/net/xfrm/trace_iptfs.h

Purpose: This trace header defines tracepoints for the IP-TFS implementation in `xfrm_iptfs.c`. It exposes packet geometry, queue decisions, aggregation/fragmentation events, and timer activity for debugging RFC 9347 AGGFRAG behavior.

Important events: `iptfs_egress_recv` records inbound IP-TFS payload skb layout and block offset. The `iptfs_ingress_preq_event` class backs `iptfs_enqueue`, `iptfs_no_queue_space`, and `iptfs_too_big`, capturing queue capacity, protocol hints, PMTU, and GSO status before enqueue. The `iptfs_ingress_postq_event` class backs first dequeue/fragmenting/final-fragment/toobig events. `iptfs_ingress_nth_peek` and `iptfs_ingress_nth_add` track aggregation of subsequent inner packets. `iptfs_timer_start` and `iptfs_timer_expire` expose output timer scheduling and expiry.

Control flow and dependencies: The header expects helper functions `__trace_ip_proto()` and `__trace_ip_proto_seq()` plus `struct xfrm_iptfs_data` fields from `xfrm_iptfs.c`. It follows the standard Linux tracepoint pattern with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` outside the include guard.

State and persistence: Tracepoints do not persist state, but they read live skb and IP-TFS state fields. Their output becomes runtime observability through ftrace/perf/tracefs.

Integration points: Included by `xfrm_iptfs.c` after defining `CREATE_TRACE_POINTS`; trace events align with enqueue, dequeue, fragment sharing, timer, and receive parsing code.

Risks: Trace field expressions access skb fragment metadata and page addresses, so changes to skb layout handling in IP-TFS must keep trace-only code valid. Trace helpers are compiled under tracepoint conditions; missing helper definitions or field drift can produce build failures that appear only with tracing enabled.

Test signals: Build with tracing enabled, enable `iptfs:*` events in tracefs, and run IP-TFS traffic that triggers enqueue, no-space drops, PMTU too-big, fragmentation, aggregation, and timers. Validate no tracepoint dereference warnings occur for linear, paged, frag_list, and GSO skbs.
