# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ftp.c

## Purpose
`nf_conntrack_ftp.c` is the FTP conntrack helper. It parses FTP control-channel commands and replies, tracks command line boundaries across TCP packets, extracts active/passive data-channel addresses and ports, and creates expectations for related TCP data connections with optional NAT payload mangling.

## Important APIs, Types, And Functions
The helper registers IPv4 and IPv6 `struct nf_conntrack_helper` entries for configured ports, defaulting to FTP port 21. Parser functions include `try_rfc959()`, `try_rfc1123()`, `try_eprt()`, `try_epsv_response()`, `get_port()`, `try_number()`, and `find_pattern()`. Line state is stored in `struct nf_ct_ftp_master` helper data using `find_nl_seq()` and `update_nl_seq()`. `nf_nat_ftp_hook` is the RCU NAT hook.

## Control Flow
The helper only parses established traffic. It linearizes the skb, computes TCP payload boundaries, takes `nf_ftp_lock`, verifies the packet begins at a remembered post-newline sequence, and scans for direction-specific commands: PORT/EPRT from client, 227/229 replies from server. A full match allocates an expectation for the opposite direction, validates address policy using `loose`, and either delegates to NAT or calls `nf_ct_expect_related()`. Partial command matches are dropped to avoid losing parser synchronization. On newline-terminated payloads, it records the next sequence number.

## State And Persistence
Module state includes configured ports, `loose`, helper array, global spinlock, and NAT hook pointer. Per-flow state lives in helper extension data: recent sequence numbers after newlines and pickup flags for userspace-injected conntracks. Expectations are transient related-flow state.

## Dependencies And Integration Points
The helper integrates with TCP conntrack state, conntrack helper extension data, expectations, NAT helper payload rewriting, seqadj, ctnetlink restore via `nf_ct_ftp_from_nlattr()`, IPv4/IPv6 parsing, and module aliasing for helper auto-load.

## Risks
FTP parsing is fragile because commands can span packets, payload can be NAT-mangled, and passive replies are not strictly formatted. Dropping partial matches is intentional but can affect unusual traffic. `nf_ftp_lock` avoids seqadj/NAT deadlock interactions with `ct->lock`; lock ordering must be preserved. `loose=1` can open expectations to third-party addresses.

## Test Signals
Test active PORT, passive PASV, EPRT/EPSV over IPv4/IPv6, commands split across TCP segments, multiple configured ports, NATed payload rewriting and sequence adjustment, ctnetlink-restored flows with pickup flags, strict versus loose policy, malformed numeric fields, partial command drop, expectation table full, and helper unregister.
