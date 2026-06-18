# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_amanda.c

## Purpose
`nf_conntrack_amanda.c` is the Amanda backup protocol conntrack helper. It parses Amanda UDP control replies from the server, extracts advertised TCP ports for DATA, MESG, INDEX, and STATE connections, and creates expectations so related TCP data connections can be tracked and NATed.

## Important APIs, Types, And Functions
The helper registers two `struct nf_conntrack_helper` entries for IPv4 and IPv6 UDP port 10080. `amanda_help()` is the packet parser. It uses textsearch configs prepared from `ts_algo` for `CONNECT`, newline, and command tokens. `nf_nat_amanda_hook` is an RCU-exported NAT integration hook. `amanda_exp_policy` allows up to four expected connections.

## Control Flow
Only reply-direction packets are parsed. The helper refreshes the master UDP timeout to `master_timeout`, locates a `CONNECT` line, then scans that line for advertised service tokens. For each valid port string it allocates an expectation, initializes it from the original tuple endpoints and TCP destination port, and either delegates to NAT if the connection is NATed or calls `nf_ct_expect_related()`. Expectation allocation/add failures drop the packet because allowing the control packet through would advertise an untracked data connection.

## State And Persistence
Runtime state consists of module parameters, compiled textsearch objects, helper registration, the RCU NAT hook pointer, and transient expectations attached to master conntracks. No durable state exists.

## Dependencies And Integration Points
The file depends on textsearch, conntrack helpers, conntrack expectations, ecache helper logging, UDP/TCP headers, and optional NAT helper registration via `nf_nat_amanda_hook`.

## Risks
Payload parsing must remain bounded by skb length and line end offsets. Port parsing rejects invalid, zero, or overly long ports. Textsearch preparation failure must unwind prepared configs. NAT hooks run under RCU and can alter packet payload, so offsets relative to UDP payload must remain correct.

## Test Signals
Test IPv4/IPv6 Amanda control replies, delayed replies refreshing UDP timeout, multiple DATA/MESG/INDEX/STATE ports, malformed or partial lines, textsearch algorithm failure, expectation table full, NATed and non-NATed flows, and module unload cleanup.
