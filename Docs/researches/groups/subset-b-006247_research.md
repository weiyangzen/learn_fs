# subset-b-006247 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_sip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_sip.c

## Purpose

`nf_nat_sip.c` is the NAT-side companion for the SIP conntrack helper. It rewrites SIP signalling headers and SDP bodies so that addresses and ports advertised inside SIP payloads match the conntrack/NAT mapping, then installs NAT-aware expectations for related signalling, RTP, and RTCP flows. It is registered as the `"sip"` NAT helper and publishes a `struct nf_nat_sip_hooks` table through the global RCU pointer `nf_nat_sip_hooks`.

## Important APIs, types, and functions

- `mangle_packet()` is the central payload rewrite helper. It computes the payload-relative offset differently for TCP and UDP, calls `__nf_nat_mangle_tcp_packet()` or `nf_nat_mangle_udp_packet()`, refreshes `*dptr`, and adjusts `*datalen`.
- `sip_sprintf_addr()` and `sip_sprintf_addr_port()` format IPv4 and IPv6 literals for SIP and SDP, including bracketed IPv6 forms where URI syntax requires them.
- `map_addr()` compares parsed SIP URI addresses against the current conntrack tuple, chooses the opposite-direction mapped address and port, and rewrites the matched URI if NAT changed it.
- `nf_nat_sip()` rewrites the SIP request URI, Via header and parameters, Contact headers, From, To, and Cisco-style forced reply destination ports.
- `nf_nat_sip_seq_adjust()` records TCP sequence adjustment after payload length changes.
- `nf_nat_sip_expect()` and `nf_nat_sip_expected()` prepare and apply NAT for expected related SIP signalling connections.
- `nf_nat_sdp_addr()`, `nf_nat_sdp_port()`, `nf_nat_sdp_session()`, and `nf_nat_sdp_media()` rewrite SDP owner, connection, and media information and keep `Content-Length` consistent.
- `sip_hooks` binds all exported hook callbacks used by `nf_conntrack_sip`.

## Control flow

Module init registers `nat_helper_sip`, assigns `nf_nat_sip_hooks`, and registers the `"sip"` expectation function. The conntrack SIP helper calls these hooks while parsing SIP messages. `nf_nat_sip()` first distinguishes requests from responses by checking for the `SIP/2.0` status line. Requests may have their request URI rewritten with `ct_sip_parse_request()` plus `map_addr()`. The topmost Via URI is then parsed as UDP or TCP and rewritten only when it belongs to the current flow side. The code also rewrites `maddr=`, `received=`, and `rport=` parameters when they expose pre-NAT addresses or ports.

After Via handling, the helper iterates all Contact headers, then rewrites From and To URIs if they map to translated tuple endpoints. For Cisco forced destination ports, reply-direction UDP packets have `uh->dest` changed and checksums fixed through the NAT mangle path. SDP hooks are invoked by the SIP helper after it has parsed expectations from the body. `nf_nat_sdp_media()` searches for an available even RTP port and matching RTCP port, installs expectations, and rewrites the SDP media port if NAT had to move it.

## State and persistence behavior

The file has no durable storage. Runtime state lives in conntrack objects, conntrack helper private data, and expectations. `struct nf_ct_sip_master` supplies `forced_dport`; expectation fields such as `saved_addr`, `saved_proto`, `dir`, and `expectfn` preserve original values and tell the NAT expectation callback how to map the eventual related connection. TCP sequence state is persisted in the conntrack sequence-adjust extension by `nf_ct_seqadj_set()`. Registration state is held in RCU globals and helper registries until module exit clears them and waits for readers with `synchronize_rcu()`.

## Dependencies and integration points

This file depends heavily on `nf_conntrack_sip` parsing helpers, conntrack expectation APIs, NAT helper APIs, sequence adjustment, and skb payload mutation helpers. It integrates with netfilter through `nf_nat_helper_register()`, `nf_ct_helper_expectfn_register()`, and the RCU `nf_nat_sip_hooks` pointer consumed by the SIP conntrack helper. It handles both IPv4 and IPv6 formatting and both TCP and UDP SIP transports. Related media flows are integrated through conntrack expectations and later NAT setup in `nf_nat_sip_expected()`.

## Risks

Payload rewriting is offset-sensitive: every successful mangle must refresh `*dptr` and adjust `*datalen`, or later parser offsets can target stale memory. SDP rewrites must keep `Content-Length` correct, especially when IPv4 to IPv6 address text changes length. Expectation pairing for RTP/RTCP is protected by `nf_conntrack_expect_lock`; incorrect matching can apply source NAT to the wrong media stream. Port allocation failures intentionally drop packets, so high expectation pressure can affect call setup. SIP is syntactically flexible, so malformed or uncommon headers may bypass rewriting if the parser does not recognize them.

## Test signals

Useful tests include SIP over UDP and TCP through NAT with IPv4 and IPv6, request and response rewriting of Via, Contact, From, To, `maddr`, `received`, and `rport`; SDP session and per-media address changes; RTP/RTCP expectation allocation when default ports are free and when collisions force new ports; Cisco forced destination port behavior; TCP sequence adjustment after length-changing rewrites; and failure paths where mangle or expectation insertion returns an error and the packet is dropped with helper logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_sip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_tftp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_tftp.c

## Purpose

`nf_nat_tftp.c` is the NAT helper for TFTP conntrack expectations. TFTP control traffic negotiates a new UDP data flow, and this helper adjusts the related expectation so the data connection follows the NAT mapping of the master control connection.

## Important APIs, types, and functions

- `nat_helper_tftp` is a `struct nf_conntrack_nat_helper` initialized with `NF_CT_NAT_HELPER_INIT("tftp")`.
- `help()` is the callback installed into the global `nf_nat_tftp_hook` RCU pointer. It receives the packet, conntrack direction metadata, and a prepared expectation from the TFTP conntrack helper.
- `nf_ct_expect_related()` commits the adjusted expectation.
- `nf_nat_follow_master` is assigned as `exp->expectfn`, causing the related TFTP data connection to inherit NAT handling from the master flow.
- `nf_nat_tftp_init()` and `nf_nat_tftp_fini()` register and unregister the helper and hook.

## Control flow

On module initialization, the code asserts that no TFTP NAT hook is currently installed, registers the NAT helper, and publishes `help()` through `RCU_INIT_POINTER(nf_nat_tftp_hook, help)`. When the conntrack TFTP helper detects a related data flow, it calls this NAT hook with the expectation. `help()` reads the master conntrack from `exp->master`, saves the original client UDP source port in `exp->saved_proto.udp.port`, sets the expected direction to reply, assigns `nf_nat_follow_master`, and attempts to insert the expectation. Expectation insertion failure logs `"cannot add expectation"` and returns `NF_DROP`; success returns `NF_ACCEPT`.

## State and persistence behavior

There is no persistent storage. The only lasting runtime state is the registered NAT helper, the RCU hook pointer, and fields written into individual `struct nf_conntrack_expect` objects. Module exit unregisters the helper, clears `nf_nat_tftp_hook`, and waits for active RCU readers with `synchronize_rcu()` before unloading.

## Dependencies and integration points

This file depends on UDP headers, conntrack helper and expectation APIs, NAT helper registration, and the public TFTP conntrack hook declaration from `linux/netfilter/nf_conntrack_tftp.h`. It integrates with the TFTP conntrack parser, which owns protocol parsing and expectation allocation, while this file only supplies NAT-specific expectation mapping.

## Risks

The logic is intentionally small, so the main risk is ordering and lifetime: the RCU hook must be cleared only after helper unregistration, and module unload must wait for readers. Failed expectation insertion drops the triggering control packet, which is correct for consistency but can interrupt transfers when expectation table capacity is exhausted. Correctness also depends on the conntrack TFTP helper passing a valid expectation with `master` set.

## Test signals

Exercise a NATed TFTP read and write transfer and verify that the UDP data flow is expected in the reply direction and follows the master NAT mapping. Negative tests should cover expectation insertion failure, helper unload while traffic is active, and absence of stale hook use after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_nat_tftp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_queue.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_queue.c

## Purpose

`nf_queue.c` implements the generic kernel side of netfilter packet queueing. It lets one queue backend, normally nfnetlink_queue, register a handler that receives packets whose netfilter verdict is `NF_QUEUE`. The core captures enough skb, hook, device, socket, bridge, and route state so the backend can later reinject the packet through `nf_reinject()`.

## Important APIs, types, and functions

- `nf_queue_handler` is a single global RCU pointer to `struct nf_queue_handler`.
- `nf_register_queue_handler()` and `nf_unregister_queue_handler()` publish and clear the backend handler.
- `nf_queue_entry_get_refs()` takes references on `state->sk`, input/output devices, and bridge physical devices so queued packets can outlive the original hook call.
- `nf_queue_entry_free()` and `nf_queue_entry_release_refs()` drop those references and free the queue entry.
- `nf_queue_nf_hook_drop()` forwards net namespace hook-drop notifications to the registered backend.
- `nf_ip_saveroute()` and `nf_ip6_saveroute()` snapshot LOCAL_OUT route keys for later reroute decisions.
- `__nf_queue()` builds a `struct nf_queue_entry` and calls `qh->outfn(entry, queuenum)`.
- `nf_queue()` decodes the queue number from the verdict and applies queue-bypass/drop policy.

## Control flow

Backends register once with `nf_register_queue_handler()`, which warns if another handler is already present. When a hook returns an `NF_QUEUE` verdict, `nf_queue()` calls `__nf_queue()` with the queue number encoded in the verdict high bits. `__nf_queue()` drops safely with `-ESRCH` if no backend is registered. It chooses extra route-key storage based on address family, handles prefetched skb sockets that need an explicit reference, allocates `struct nf_queue_entry` plus route storage with `GFP_ATOMIC`, forces dst references when present, copies the hook state, initializes bridge physical devices, and holds all needed refs.

For IPv4 and IPv6 LOCAL_OUT packets, the original source, destination, mark, and IPv4 TOS are saved. The backend `outfn` receives ownership of the queue entry; if it returns an error, the core frees the entry and returns the error. `nf_queue()` then either treats `-ESRCH` as accepted when `NF_VERDICT_FLAG_QUEUE_BYPASS` is set, or frees the skb and reports that the packet did not continue synchronously.

## State and persistence behavior

The registered handler is global RCU state. Per-packet queue state is in `struct nf_queue_entry`, which embeds a copy of `struct nf_hook_state`, the skb pointer, hook index, entry size, optional bridge physical devices, and optional route key data. The queue backend is responsible for reinjecting every accepted entry; queued packets do not persist across backend loss unless the backend flushes them. Device and socket refs are held explicitly and released by `nf_queue_entry_free()`.

## Dependencies and integration points

This file integrates with core netfilter hook traversal, nfnetlink_queue style backends, network namespace hook-drop handling, IPv4/IPv6 routing metadata, bridge netfilter physical-device metadata, skb dst management, and socket lifetime helpers. It exports symbols used by queue backends and reinjection code.

## Risks

Reference lifetime is the main risk. Missing a device, bridge device, socket, or dst reference can leave the backend with dangling state; failing to release refs leaks resources. Queueing occurs in atomic context, so allocation failure and dst forcing failure must be handled by dropping. The single-handler design means backend registration conflicts are not supported. Queue bypass only applies when no backend is registered; other queue errors still drop the skb.

## Test signals

Test signals include NFQUEUE operation for IPv4 and IPv6 LOCAL_OUT and forwarded packets, queue-bypass behavior when no backend is loaded, backend `outfn` failure cleanup, reinjection after network device lifetime changes, bridge netfilter packets with physical input/output devices, prefetched skb socket reference handling, and namespace teardown invoking `nf_queue_nf_hook_drop()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_sockopt.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_sockopt.c

## Purpose

`nf_sockopt.c` is the registry and dispatcher for legacy netfilter socket options. Netfilter modules register protocol-family-specific getsockopt and setsockopt numeric ranges, and this file routes user-context socket option calls to the owning module while preventing overlapping ranges.

## Important APIs, types, and functions

- `nf_sockopt_mutex` protects the global `nf_sockopts` list.
- `overlap()` checks exclusive numeric ranges.
- `nf_register_sockopt()` validates that a new `struct nf_sockopt_ops` does not overlap existing set or get ranges for the same protocol family, then links it into the registry.
- `nf_unregister_sockopt()` removes a registered ops block.
- `nf_sockopt_find()` searches by protocol family, option value, and get/set direction, acquiring a module reference with `try_module_get()`.
- `nf_setsockopt()` and `nf_getsockopt()` dispatch to the selected operation and release the module reference afterward.

## Control flow

Registration takes the mutex, walks all existing registrations, and compares both set and get ranges for the same `pf`. Any overlap returns `-EBUSY`; otherwise the new ops is added to `nf_sockopts`. Dispatch calls `nf_sockopt_find()`, which walks the list under the same mutex. For each matching protocol family it first tries to pin the owner module. If the requested value falls inside the relevant exclusive range, it returns that ops with the module pinned. If not, it drops the module reference and continues. No match returns `-ENOPROTOOPT`. The public get/set wrappers invoke the callback outside the mutex and then call `module_put()`.

## State and persistence behavior

The only state is the in-kernel linked list of registered `nf_sockopt_ops` entries. It lasts until modules unregister their entries. There is no per-network-namespace split here, and the file comments explain that sockopts are registered and called from user context, so a simple mutex is sufficient and callbacks may sleep.

## Dependencies and integration points

This file depends on Linux module reference counting, list APIs, mutexes, socket types, `sockptr_t`, and netfilter internal declarations from `nf_internals.h`. It is exported to netfilter modules that still expose control surfaces through socket options rather than newer netlink interfaces.

## Risks

The registry assumes modules unregister only entries they registered. Dispatch correctness depends on exclusive opt ranges and proper owner pointers. `try_module_get()` before range matching is conservative but means each same-family entry briefly pins and unpins while searching. Since callbacks run after releasing the mutex, the module reference is the key lifetime guard; missing owner setup would be unsafe. Because the registry is global by protocol family, option number allocation conflicts can block module load with `-EBUSY`.

## Test signals

Useful coverage includes registering non-overlapping and overlapping ranges, get and set dispatch to the right callback, `-ENOPROTOOPT` for unknown values, module reference behavior when an owner cannot be pinned, unregister followed by no-match behavior, and callback paths that sleep to confirm the mutex is not held during operation execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_sockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_synproxy_core.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_synproxy_core.c

## Purpose

`nf_synproxy_core.c` provides the common SYNPROXY implementation for IPv4 and IPv6. It parses and emits TCP options, encodes SYN cookies and negotiated options, synthesizes client/server handshake packets, installs per-net SYNPROXY templates and statistics, and registers netfilter hooks that translate the proxied handshake back into a normal conntrack-confirmed connection.

## Important APIs, types, and functions

- `synproxy_net_id` identifies per-network-namespace `struct synproxy_net` storage.
- `synproxy_parse_options()` extracts MSS, window scale, timestamp, and SACK-permitted options from a TCP header.
- `synproxy_init_timestamp_cookie()` and `synproxy_check_timestamp_cookie()` encode and decode negotiated option bits in timestamp cookie fields.
- `synproxy_tstamp_adjust()` updates TCP timestamp values after the proxied handshake and fixes checksums.
- Procfs sequence operations expose per-CPU `synproxy_stats` under `/proc/net/stat/synproxy` when procfs is enabled.
- `synproxy_net_init()` allocates a conntrack template with seqadj and synproxy extensions plus per-CPU stats; `synproxy_net_exit()` frees them.
- IPv4 send helpers build IPv4/TCP packets and emit client SYN-ACKs, server SYNs, server ACKs, and client ACKs.
- IPv6 send helpers mirror the IPv4 path using IPv6 routing, `nf_cookie_v6_check()`, and `nf_ipv6_cookie_init_sequence()`.
- `ipv4_synproxy_hook()` and `ipv6_synproxy_hook()` run before conntrack confirm at LOCAL_IN and POST_ROUTING.
- `nf_synproxy_ipv4_init/fini()` and `nf_synproxy_ipv6_init/fini()` reference-count hook registration per namespace.

## Control flow

Module init registers a pernet subsystem. For each net namespace, initialization allocates a confirmed conntrack template in the default zone, adds sequence-adjust and synproxy extensions, allocates per-CPU stats, and creates the proc stats file. Rule/expression frontends call the exported IPv4 or IPv6 init functions to register two hooks when the first user appears.

The SYNPROXY frontend handles the initial SYN elsewhere by creating a SYN-ACK with `synproxy_send_client_synack()` or the IPv6 equivalent. This core then observes packets attached to conntracks that have a synproxy extension. In `TCP_CONNTRACK_SYN_SENT`, a client ACK with a valid SYN cookie is consumed and translated into a synthetic server SYN using the namespace conntrack template. Retransmitted cookie ACKs increment `cookie_retrans`. When the server SYN-ACK reaches `TCP_CONNTRACK_SYN_RECV`, the hook records timestamp offset, strips options not needed in the ACK leg, sends an ACK to the server, initializes sequence adjustment, sends an ACK to the client, consumes the original packet, and returns `NF_STOLEN`. Established traffic then passes with timestamp adjustment applied in both directions.

The IPv6 hook follows the same state machine but locates the TCP header through `ipv6_skip_exthdr()` and builds/routs replies with IPv6-specific helpers.

## State and persistence behavior

Per-net state includes the conntrack template `snet->tmpl`, per-CPU `snet->stats`, and IPv4/IPv6 hook reference counts. Per-connection state lives in `struct nf_conn_synproxy`, including initial sequence number, initial timestamp, and timestamp offset. Sequence translation is stored in the conntrack seqadj extension. No state is persisted beyond kernel memory. Procfs exposes counters for observed SYNPROXY events but does not drive behavior.

## Dependencies and integration points

This file integrates with conntrack, conntrack events, conntrack extensions, TCP SYN cookie helpers, sequence adjustment, IPv4/IPv6 routing and local output, netfilter hook registration, network namespaces, per-CPU stats, and optional procfs reporting. It exports the core functions consumed by nftables/xtables SYNPROXY frontends. Hook priority is `NF_IP_PRI_CONNTRACK_CONFIRM - 1`, which is important because SYNPROXY must manipulate state immediately before conntrack confirmation.

## Risks

Handshake correctness is sensitive to sequence number and timestamp arithmetic. Off-by-one errors in synthetic SYN/ACK generation or seqadj initialization can break established connections after the proxy handshake. TCP option parsing is intentionally tolerant, but malformed option lengths can cause drops or disable negotiated features. IPv6 routing errors and xfrm lookup failures silently free synthetic packets, so SYNPROXY may appear to drop handshakes under routing policy issues. Hook reference counts must remain balanced across frontends. Per-CPU stats and proc output are diagnostic only; they do not prove packets were emitted successfully.

## Test signals

Coverage should include IPv4 and IPv6 SYNPROXY handshakes with MSS, timestamps, SACK, ECN, and window scale; invalid cookie drops; retransmitted client ACK handling; reopened connections from CLOSE state; timestamp adjustment on established packets; seqadj event generation; hook register/unregister reference counting; proc stat output; IPv6 extension-header parsing; routing failure behavior for synthetic packets; and namespace teardown freeing templates and per-CPU stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_synproxy_core.c -->
