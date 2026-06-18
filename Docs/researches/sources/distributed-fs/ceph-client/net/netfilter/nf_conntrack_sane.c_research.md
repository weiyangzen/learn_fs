<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sane.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sane.c

## Purpose
Implements a TCP helper for the SANE network scanner protocol. It watches for `SANE_NET_START` requests and successful replies, then installs an expectation for the data connection advertised by the server.

## Important APIs, Types, and Functions
The helper entry point is `help()`. Module registration uses `nf_conntrack_sane_init()`, `nf_conntrack_sane_fini()`, `nf_ct_helper_init()`, and `nf_conntrack_helpers_register()`. Wire structs `sane_request` and `sane_reply_net_start` describe the fields inspected. Helper state is `struct nf_ct_sane_master` with `SANE_STATE_START_REQUESTED`/normal state.

## Control Flow
Only established TCP packets are inspected. Original-direction payloads must exactly match `struct sane_request`; if the RPC code is `SANE_NET_START`, the helper marks the next reply interesting. Reply-direction packets are ignored unless that state is set. A successful reply with zero reserved field yields an expectation from client to server on the returned TCP port; expectation failure drops the packet.

## State and Persistence
Per-connection helper state records whether a start reply is pending, using `READ_ONCE()`/`WRITE_ONCE()`. Expectations persist for up to five minutes with one expected data connection. Module parameters select up to eight server ports, defaulting to `SANE_PORT`.

## Dependencies and Integration Points
Depends on conntrack helper and expectation APIs plus SANE helper header definitions. Registers IPv4 and IPv6 TCP helpers for each configured port.

## Risks
The helper expects exact request length and minimal reply fields, so protocol extensions or segmentation can be missed. It does not perform NAT mangling locally. Dropping on expectation failure can affect scanner setup when expectation limits are exhausted.

## Test Signals
Test default and custom ports, IPv4/IPv6, valid `SANE_NET_START` request/reply, refused status, nonzero reserved field, split TCP payloads, expectation exhaustion, and successful data connection classification as RELATED.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sane.c -->
