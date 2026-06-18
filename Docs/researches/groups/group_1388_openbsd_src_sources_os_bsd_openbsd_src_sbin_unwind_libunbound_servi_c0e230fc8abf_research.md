# Group Research: group_1388_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_servi_c0e230fc8abf

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outside_network.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outside_network.c

`outside_network.c` implements Unbound's outbound network engine for resolver traffic. It manages UDP source port/interface selection, random DNS ID assignment, UDP timeout handling, TCP/TLS connection setup, reusable TCP streams, HTTP fetch commpoints, serviced query de-duplication, EDNS fallback, and callback fanout to iterator/request state.

The low-level UDP path stores pending queries in an rbtree keyed by query ID and remote address. `pending_udp_query()` either sends immediately through a randomly selected source interface/port or queues the packet when no UDP commpoint is available. `randomize_and_send_udp()` assigns a unique random ID, selects an IPv4/IPv6 outgoing interface, opens or reuses a UDP socket, sends the packet, starts the timeout timer, and emits dnstap query events when enabled. `outnet_udp_cb()` validates replies by ID, address, and receiving port; unsolicited or wrong-port replies increment defensive counters and can trigger the configured unwanted-reply action. UDP timeouts call back the owner, optionally delay-close the socket to avoid late ICMP side effects, free the pending entry, and drain the queued UDP list.

The TCP path is built around preallocated `pending_tcp` buffers and `waiting_tcp` query records. It can create new TCP/TLS connections, queue queries while buffers are exhausted, or reuse existing connections to the same address/port/TLS-auth key. Reuse state is indexed both by destination (`tcp_reuse`) and by DNS ID (`tree_by_id`) so multiple outstanding queries can share a stream without ID collisions. The file maintains an LRU list of idle reusable streams, closes the oldest stream when a buffer is needed, moves unwritten queries away from failed streams, and preserves written query IDs until replies arrive or streams are decommissioned.

`outnet_tcp_cb()` is the central TCP event state machine. It distinguishes keepalive/read timeouts, write-complete events, stream errors, and replies. Successful writes either schedule the next queued write or switch the stream back to read/keepalive mode. Replies are matched by ID to `waiting_tcp`; unmatched or malformed replies close the stream. Errors trigger callbacks for affected queries and make queued-but-unwritten work eligible for another connection.

The higher-level serviced-query layer coalesces identical upstream requests in `outnet_serviced_query()`. It constructs a canonical query buffer, applies inplace query callbacks and per-upstream EDNS options, checks infra-cache ratelimiting only for new serviced entries, and attaches one or more callbacks to a shared `serviced_query`. A zero-delay timer starts the actual network send outside the mesh call path. `outnet_serviced_query_stop()` removes one callback and cancels the underlying network work when no callbacks remain.

Protocol fallback is handled inside `serviced_udp_callback()` and `serviced_tcp_callback()`. UDP starts with EDNS when infra-cache says it is usable, falls back to smaller EDNS fragmentation sizes on selected timeouts, retries a limited number of UDP timeouts, falls back without EDNS on FORMERR/NOTIMPL or malformed EDNS responses, records EDNS-capability and RTT results in infra-cache, and switches to TCP on TC responses. TCP similarly records TCP usability/RTT and retries without EDNS for EDNS-related FORMERR/NOTIMPL responses.

Query hardening includes random DNS IDs, optional UDP source port randomization, optional UDP `connect()`, optional IPv6 source-prefix randomization, optional 0x20 qname case randomization, DSCP/TCP MSS socket options, TLS peer/SNI setup, DNS-over-TLS padding, and dnstap logging. Callback delivery verifies 0x20 qname echoes for non-PTR replies, lowercases perturbed qnames before handing packets upward, backs up shared response buffers when multiple callbacks must see the same answer, and deletes the serviced entry after callback fanout.

The file also exposes helper commpoint creators for one-off UDP, TCP/TLS, and HTTP/HTTPS transfers, plus memory accounting for the outbound network object, queued UDP/TCP records, preallocated TCP buffers, serviced queries, callback lists, and interface port state. It is tightly coupled to `infra_cache`, `comm_point`, EDNS handling, dnstap, iterator callbacks, and Unbound's regional allocator model.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outside_network.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outside_network.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outside_network.h

`outside_network.h` declares the outbound resolver networking subsystem. `struct outside_network` owns the event base, shared UDP buffer, UDP port pools, pending UDP tree/list state, serviced-query tree, infra-cache pointer, randomness source, TLS context, dnstap environment, TCP buffer pool, TCP wait queues, and reusable TCP connection indexes/LRU list.

The header documents the main internal record types. `port_if` tracks one outgoing interface, its bind address/prefix, available port array, active commpoints, and in-use count. `port_comm` wraps an outgoing UDP commpoint and tracks the bound port, interface, array index, and outstanding query count. `pending` represents a UDP query keyed by ID/address, with timeout, callback, packet copy for queued sends, and link to its `serviced_query`.

TCP support is modeled with `pending_tcp`, `waiting_tcp`, and `reuse_tcp`. A `pending_tcp` is a preallocated TCP commpoint slot. A `waiting_tcp` is a single DNS query waiting for a TCP buffer, waiting to be written on a reused stream, or waiting for a reply. `reuse_tcp` describes an open reusable stream, including destination/TLS-auth key, LRU membership, ID-indexed outstanding query tree, write queue, and persistent `comm_point` more-read/more-write flags.

`serviced_query` is the de-duplication and retry unit for upstream DNS queries. It stores the canonical query buffer, destination, zone/delegation name, qtype, DNSSEC/EDNS flags, TCP/TLS policy, EDNS option list, retry/status state, RTT timing, callback list, region, timer, and active pending transport object. The status enum expresses UDP/TCP with or without EDNS, EDNS fallback probes, and reduced-fragment UDP EDNS mode.

The exported API covers lifecycle (`outside_network_create`, delete, quit prepare), raw UDP/TCP query submission, pending deletion, serviced-query creation/stop, memory accounting, TCP reuse helpers, waiting-list helpers, one-off UDP/TCP/HTTP commpoint creation, TCP connect/fd helpers, event callbacks, and rbtree comparators. The header exposes many internals because unit tests and adjacent resolver modules need to inspect or drive the outbound state machines.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outside_network.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/rpz.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/rpz.c

`rpz.c` implements Unbound Response Policy Zone handling. It parses policy-zone RRs into internal trigger stores, removes them for IXFR updates, applies configured overrides, evaluates policies at worker-request and iterator points, synthesizes DNS replies, logs applied policies, updates RPZ statistics, and reports RPZ memory use.

Policy classification starts by mapping RPZ CNAME targets to actions: `CNAME .` becomes NXDOMAIN, `CNAME *.` becomes NODATA, special `rpz-passthru`, `rpz-drop`, and `rpz-tcp-only` names become corresponding actions, TLDs beginning with `rpz-` outside known actions are invalid, and other records become local-data responses. SOA, NS, DNAME, ZONEMD, and DNSSEC-related records are ignored as policy data. Owner names under the RPZ origin are stripped to policy names and classified as QNAME, client-IP, response-IP, NSDNAME, NSIP, or invalid triggers.

Insertion routes each supported trigger into a purpose-built store. QNAME and NSDNAME triggers use `local_zones`, with NSDNAME suffixes stripped to nameserver names before insertion. Response-IP triggers use `respip_set`. Client-IP and NSIP triggers use `clientip_synthesized_rrset` address trees that store RPZ actions plus optional synthesized local-data RRsets. Local-data policy records preserve their RR contents, while non-local-data actions create action-only zones or address nodes. `rpz_finish_config()` initializes parent pointers in response/client/NS address trees after a feed is loaded.

Removal mirrors insertion for IXFR. `rpz_remove_rr()` reclassifies the RR, finds the exact trigger store, deletes matching local-data RRs when needed, and removes empty zones/address nodes. Memory allocated in regions is not individually recycled; deletion unlinks entries and relies on later zone/set teardown for reclamation. The removal code carefully holds the relevant local-zone, response-IP, or synthesized-address locks while mutating shared trees.

Runtime request processing first checks client-IP and QNAME triggers in configured RPZ order through `rpz_callback_from_worker_request()`. It honors disabled RPZs, taglist intersections, action overrides, passthrough behavior, `tcp-only` only for UDP clients, CNAME override actions, local-data synthesis, NXDOMAIN/NODATA/drop/truncate answers, optional clearing of RA on signaled NXDOMAIN, logging, and per-action statistics. Client-IP has precedence over QNAME in this worker-request path unless passthrough or no match leaves QNAME processing to continue.

Iterator callbacks handle policies that require resolution context. `rpz_callback_from_iterator_module()` evaluates NSDNAME and NSIP triggers against the current delegation point before sending upstream queries, with NSDNAME preceding NSIP. `rpz_callback_from_iterator_cname()` rechecks QNAME triggers after CNAME chasing changes the query name. These callbacks can synthesize NXDOMAIN/NODATA/local-data/CNAME-override messages, set `tcp_required`, mark dropped responses, set `rpz_passthru`, or return NULL to continue normal iteration.

Synthesized answers are built as insecure authoritative DNS messages with RPZ-marked packed rrsets. Local-data responses copy configured RRsets and rewrite owner names to the active qname. NXDOMAIN and NODATA helpers optionally attach the RPZ auth-zone SOA in the additional section. Client-IP local-data can answer directly in the worker path using `reply_info_answer_encode()`, while iterator paths allocate `dns_msg` structures in the query region.

Configuration lifecycle functions create, clear, reconfigure, enable, disable, and delete `struct rpz`. Config fields include taglists, action override, optional CNAME override target, logging flag/name, and NXDOMAIN RA signaling. The implementation is coupled to auth-zone transfer loading, local-zone answer synthesis, response-IP structures, iterator delegation points, worker stats, tag matching, and Unbound's lock hierarchy.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/rpz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/rpz.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/rpz.h

`rpz.h` declares the Response Policy Zone service interface and data structures. It defines RPZ trigger categories for QNAME, client-IP, response-IP, NSDNAME, NSIP, and invalid policy names, plus action categories for NXDOMAIN, NODATA, passthrough, drop, TCP-only, invalid, local-data, disabled override, no override, and CNAME override.

`struct rpz` is the policy container attached to a corresponding auth-zone and linked in configuration order under the auth-zones RPZ lock. It owns QNAME local zones, response-IP data, synthesized client-IP and NSIP address trees, NSDNAME local zones, optional taglist matching, action override state, optional CNAME override rrset, logging options, NXDOMAIN RA signaling, a regional allocator, and a disabled flag.

The header also exposes the synthesized client/NS IP storage records: `clientip_synthesized_rrset` wraps a regional allocator, address tree, and lock; each `clientip_synthesized_rr` has an address-tree node, item lock, action, and optional local-data RRset list.

The public API covers inserting/removing policy RRs from RPZ feed updates, worker-request QNAME/client-IP processing, iterator NSDNAME/NSIP processing, CNAME-chain QNAME processing, RPZ create/delete/clear/config/finish operations, enable/disable toggles, action conversion helpers between RPZ and response-IP/local behavior, action stringification, and memory accounting. Callers are expected to respect auth-zone and RPZ locking contracts documented in the struct comments.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/rpz.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.c

`view.c` implements named view storage for Unbound local-zone authority data. A `views` object owns an rbtree of `view` entries plus a tree lock; each `view` owns its name, optional view-specific `local_zones`, optional response-IP set, `isfirst` fallback flag, and its own data lock.

Creation initializes the view tree and lock protection. `view_create()` duplicates the view name, initializes the per-view lock, and marks the non-rbtree fields as protected. `views_enter_view_name()` creates a view, takes the global tree write lock and the new view write lock, inserts it by name, rejects duplicates, and returns the new view still write-locked so configuration can populate it.

`views_apply_cfg()` iterates configured views, rejects a nameless first view, creates each view, records `isfirst`, and builds view-specific local zones when configured. For `isfirst` views, defaults are suppressed because global local zones can be consulted as fallback; configured `local-zones-nodefault` entries are inserted into the local-zone config as `nodefault` zones so they still shape the view-local tree. Ownership of local-zone config lists is transferred to `local_zones_apply_cfg()` and then nulled in the config view.

Lookup and accounting are straightforward. `views_find_view()` searches by name under the global tree read lock, then locks the found view for read or write before releasing the tree lock. `views_get_mem()` sums the container plus every `view_get_mem()` result; `view_get_mem()` includes the name, local zones, and response-IP set. `views_swap_tree()` exchanges rbtree root/count values with a preallocated `views` object for reload-style replacement.

Deletion destroys locks, deletes local-zone and response-IP contents, frees names, traverses the tree postorder for all views, and frees the container. `views_print()` is intentionally a placeholder.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.h

`view.h` declares named view support for local-zone authority service. `struct views` contains an RW lock and rbtree of `struct view`; the documented lock order places the views lock before forwards, hints, anchors, and local-zone locks.

`struct view` is keyed in the tree by its `name` and holds view-specific `local_zones`, a view response-IP set, an `isfirst` flag controlling fallback to global local zones, and a per-view lock. The name field is deliberately placed immediately after the rbtree node because `view_create()` uses lock-protection pointer arithmetic over the non-node fields.

The API covers create/delete, applying config, comparing tree entries, deleting one view, debug printing, finding a named view with read/write lock acquisition, memory accounting for the tree or one view, and swapping the internal tree with preallocated data. The header exposes the locking expectations needed by config reload and query-time view lookup code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/view.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/Makefile.inc

`sldns/Makefile.inc` is the OpenBSD make include for building the bundled `sldns` subset used by `unwind`'s libunbound copy. It adds `${.CURDIR}/libunbound/sldns` to `.PATH` and appends the selected resolver parsing/formatting sources to `SRCS`: `keyraw.c`, `parseutil.c`, `rrdef.c`, `sbuffer.c`, `sldns_parse.c`, `str2wire.c`, and `wire2str.c`.

The file creates `sldns_parse.c` as a build-time symlink to `libunbound/sldns/parse.c`, then lists that symlink in `CLEANFILES`. This avoids compiling a source file named exactly `parse.c` through the OpenBSD build while still using the upstream parser implementation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/Makefile.inc -->