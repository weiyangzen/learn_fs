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
