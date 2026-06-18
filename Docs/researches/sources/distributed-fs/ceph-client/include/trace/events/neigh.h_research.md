# sources/distributed-fs/ceph-client/include/trace/events/neigh.h

Purpose: Defines neighbour-subsystem tracepoints for neighbour creation, update, update completion, timer handling, event-send outcomes, and cleanup/release. It makes ARP/ND cache state transitions visible.

Important APIs/types/functions: `neigh_create`, `neigh_update`, `DECLARE_EVENT_CLASS(neigh__update)`, and derived events `neigh_update_done`, `neigh_timer_handler`, `neigh_event_send_done`, `neigh_event_send_dead`, and `neigh_cleanup_and_release`. Entries capture `struct neighbour`, netdev name, protocol family, primary key, hardware address, old/new NUD state, flags, and update return codes.

Control flow: Neighbour table code emits creation when an entry is allocated, update when link-layer address or NUD state changes, then class-based events around timer, solicitation, completion, and cleanup paths. Trace code copies variable-length keys and hardware addresses into fixed trace arrays to avoid lifetime dependence.

State and persistence: The header owns no state. It observes in-memory neighbour cache entries, which persist until garbage collection, timer expiry, explicit deletion, or device teardown.

Dependencies and integration points: Depends on skb/netdevice, `net/neighbour.h`, and tracepoint infrastructure. It integrates with IPv4 ARP, IPv6 neighbour discovery, routing, netdev lifecycle, and ftrace/perf networking diagnostics.

Risks and test signals: Risks include address-length truncation, interpreting family-specific keys incorrectly, racing neighbour deletion, and trace output hiding failed updates. Test ARP and IPv6 ND resolution, failed probes, stale-to-reachable transitions, device unregister, namespace teardown, and GC under tracing.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/neigh.h` completely for this pass (255 lines, 7021 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/neigh.h_research.md`.
