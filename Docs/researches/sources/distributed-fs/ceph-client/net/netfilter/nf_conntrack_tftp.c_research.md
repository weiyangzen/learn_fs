<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_tftp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_tftp.c

## Purpose
Implements a UDP helper for TFTP. It watches read/write requests on configured server ports and creates an expectation for the server's subsequent data connection from its chosen transfer ID port.

## Important APIs, Types, and Functions
The helper entry point is `tftp_help()`. Module lifecycle is `nf_conntrack_tftp_init()`/`fini()`. `nf_nat_tftp_hook` is an exported RCU hook pointer for NAT-specific expectation setup. Helpers are registered for IPv4 and IPv6 UDP per configured port.

## Control Flow
The helper reads a TFTP header after the UDP header. RRQ and WRQ allocate an expectation using the reply tuple source/destination addresses and original destination UDP port, then call NAT hook if needed or `nf_ct_expect_related()`. DATA, ACK, ERROR, and unknown opcodes only log debug messages and are accepted.

## State and Persistence
The file has no per-connection private state. Each request can create one expectation with a five-minute timeout. Module parameter `ports` allows up to eight server ports, defaulting to `TFTP_PORT`.

## Dependencies and Integration Points
Depends on UDP/TFTP headers, conntrack helper/expectation/event APIs, and optional NAT TFTP module. It integrates with helper assignment from rulesets or automatic helper configuration.

## Risks
Only the initial RRQ/WRQ packet is meaningful; fragmented or malformed requests are skipped. Expectation failure drops the request to avoid creating an untracked transfer. NAT hook behavior must match expectation tuple rewrite.

## Test Signals
Test RRQ and WRQ over IPv4/IPv6, custom ports, NAT and non-NAT transfers, expectation exhaustion, malformed/short TFTP headers, DATA/ACK/ERROR no-op paths, and RELATED classification of the server transfer flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_tftp.c -->
