# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_ftp.h

## Purpose
This header defines FTP conntrack helper state and the NAT hook used when FTP control messages advertise related data connections.

## Important APIs, Types, and Functions
It defines `FTP_PORT` 21, `NF_CT_FTP_SEQ_PICKUP`, `NUM_SEQ_TO_REMEMBER`, and `struct nf_ct_ftp_master`, which stores sequence positions after newlines for each direction and pickup flags useful for conntrackd. `nf_nat_ftp_hook_fn` describes NAT callback arguments, including FTP command type, protocol offset, match offset/length, and expectation. `nf_nat_ftp_hook` is the RCU-published hook pointer.

## Control Flow
The FTP helper parses control commands, tracks newline sequence positions to find complete commands across packets, creates expectations for data connections, and optionally calls the NAT hook to rewrite addresses/ports in payload and adjust expectations.

## State and Persistence
Per-master helper state is stored in `nf_ct_ftp_master` and lives with the master conntrack entry. NAT hook pointer is global RCU state. No durable persistence is defined.

## Dependencies and Integration Points
It depends on netfilter, skb, conntrack expectations, uapi FTP helper definitions, and tuple direction definitions. It integrates with FTP helper parsing, NAT payload rewriting, and conntrackd sequence pickup.

## Risks
TCP stream segmentation and sequence tracking are subtle; wrong offsets can miss commands or corrupt payload. NAT sequence adjustment must match rewritten lengths. RCU hook access and expectation lifecycle must be correct.

## Test Signals
Active/passive FTP through NAT, commands split across packets, retransmissions, conntrackd pickup scenarios, NAT module unload, and checksum/sequence adjustment validation.
