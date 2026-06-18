# sources/distributed-fs/ceph-client/net/core/neighbour.c

## Purpose

`neighbour.c` implements the generic Linux neighbor cache used by ARP and IPv6 Neighbor Discovery. It owns neighbor table allocation, lookup, creation, update, garbage collection, proxy-neighbor state, packet queueing during address resolution, rtnetlink APIs, procfs statistics, and sysctl registration for per-table and per-device neighbor parameters.

## Important APIs, Types, And Functions

The central types are `struct neigh_table`, `struct neighbour`, `struct neigh_parms`, `struct pneigh_entry`, `struct neigh_hash_table`, and `struct neigh_statistics`. Exported entry points include `neigh_lookup()`, `__neigh_create()`, `neigh_update()`, `__neigh_event_send()`, `neigh_resolve_output()`, `neigh_connected_output()`, `neigh_direct_output()`, `neigh_ifdown()`, `neigh_carrier_down()`, `neigh_changeaddr()`, `pneigh_create()`, `pneigh_delete()`, `pneigh_enqueue()`, `neigh_parms_alloc()`, `neigh_parms_release()`, `neigh_table_init()`, `neigh_table_clear()`, `neigh_xmit()`, `neigh_for_each()`, `__neigh_for_each_release()`, `neigh_sysctl_register()`, and `neigh_sysctl_unregister()`.

Important internal routines are `___neigh_create()` for allocation plus hash insertion, `__neigh_update()` for NUD state/address/flag transitions, `neigh_timer_handler()` for reachability state progression, `neigh_periodic_work()` and `neigh_forced_gc()` for cleanup, `neigh_proxy_process()` for delayed proxy replies, and the rtnetlink handlers `neigh_add()`, `neigh_delete()`, `neigh_get()`, `neigh_dump_info()`, `neightbl_set()`, and `neightbl_dump_info()`.

## Control Flow

Normal transmit resolution starts with `neigh_xmit()` or a protocol-specific lookup. If no entry exists, `__neigh_create()` allocates one, calls table/device/parameter constructors, grows the RCU hash table if needed, inserts into both the hash bucket and per-device neighbor list, and optionally returns a reference. Output then goes through the function pointer in `neigh->output`. `neigh_resolve_output()` calls `neigh_event_send()` to trigger solicitation and queue packets while incomplete; once valid, it builds the link header and sends via `dev_queue_xmit()`. `neigh_connected_output()` is the fast path for valid connected entries.

State transitions are centralized in `__neigh_update()`. It validates administrative versus protocol updates, updates extended flags (`NTF_EXT_LEARNED`, `NTF_MANAGED`, `NTF_EXT_VALIDATED`), handles `NUD_FAILED`, `NUD_STALE`, `NUD_REACHABLE`, `NUD_DELAY`, `NUD_PROBE`, and permanent states, updates cached hardware addresses under `ha_lock`, adjusts timers, refreshes the header cache, replays queued packets when an entry becomes valid, updates GC and managed lists, emits rtnetlink notifications, calls netevent notifiers, and emits tracepoints.

Timers and workqueues maintain liveness. `neigh_timer_handler()` advances reachable entries to delay, stale, probe, or failed states and sends solicitations until `neigh_max_probes()` is reached. `neigh_periodic_work()` recomputes randomized reachable time and removes old failed/stale entries when thresholds require it. `neigh_managed_work()` periodically probes entries marked `NTF_MANAGED`. Forced GC runs when allocation pressure reaches `gc_thresh2`/`gc_thresh3`.

Proxy neighbor flow uses a separate fixed-size hash (`phash_buckets`) protected by `phash_lock`. `pneigh_create()` and `pneigh_delete()` maintain entries; `pneigh_enqueue()` queues SKBs with a randomized proxy delay; `neigh_proxy_process()` later calls the table `proxy_redo` callback if the device still runs.

## State And Persistence Behavior

All state is in kernel memory. Neighbor entries are reference counted and RCU-freed, with `tbl->entries` tracking live allocations and `tbl->gc_entries` tracking entries subject to GC. Entries can be exempt from GC when permanent, externally learned, externally validated, or on loopback. Neighbor parameters are cloned per device and inherit default table values; sysctl writes mark overridden data-state bits and default writes propagate to device parameter blocks that have not overridden that field.

Hash table state is RCU-protected and can grow dynamically. `neigh_table_init()` allocates per-CPU stats, primary and proxy hashes, delayed work, proxy timer, and procfs stats. `neigh_table_clear()` tears those down. Device teardown flushes both regular and proxy entries and purges queued proxy packets. Sysctl and procfs registration creates user-visible but non-persistent control/state views.

## Dependencies And Integration Points

This file integrates with `struct net_device`, `dst_entry`, header operations, rtnetlink, netevent notifiers, procfs, sysctl, RCU, timers, delayed work, per-CPU counters, and tracepoints from `trace/events/neigh.h`. Protocol tables such as ARP and NDISC provide constructors, hash functions, solicit/error callbacks, proxy callbacks, and family-specific parameter registration.

Rtnetlink exposes `RTM_NEWNEIGH`, `RTM_DELNEIGH`, `RTM_GETNEIGH`, `RTM_GETNEIGHTBL`, and `RTM_SETNEIGHTBL`. Procfs exposes table statistics under `init_net.proc_net_stat`. Sysctl paths are registered as `net/ipv4/neigh/<dev-or-default>` and `net/ipv6/neigh/<dev-or-default>`.

## Risks

The implementation is concurrency-sensitive: table buckets require `tbl->lock`, entries require `neigh->lock`, link-layer address reads use `ha_lock`, proxy hash uses `phash_lock`, and hash readers rely on RCU. Incorrect lock ordering can deadlock with protocol callbacks or device unregister paths. GC threshold logic must not underflow `gc_entries` for exempt allocations. Timer reference handling is subtle because `neigh_add_timer()` takes a reference and `neigh_del_timer()`/timer completion releases it. Netlink validation must preserve strict checks for newer attributes and reject invalid combinations such as permanent plus managed or externally validated invalid states.

## Test Signals

Strong signals are ARP/ND neighbor add/delete/get/dump tests via rtnetlink, namespace-aware dumps, sysctl writes for reachable/retrans/proxy/queue parameters, forced GC threshold tests, packet queue overflow behavior, device unregister/carrier-down flush tests, managed entry refresh behavior, and tracepoint coverage for create/update/timer/event-send/cleanup paths. KASAN, lockdep, RCU stall detection, and refcount debug builds are especially relevant.
