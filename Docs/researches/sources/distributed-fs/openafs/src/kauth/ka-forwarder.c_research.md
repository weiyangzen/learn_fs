# sources/distributed-fs/openafs/src/kauth/ka-forwarder.c

## Purpose
Implements a UDP forwarding daemon for KA requests on AFS database servers. It listens on a local KA port and forwards client requests to one or more fakeka/MIT Kerberos servers, then forwards replies back to the original client.

## Important APIs, Types, And Functions
Important functions are `perrorexit`, `setup_servers`, `setup_socket`, `packet_is_reply`, and `main`. Global state includes `prog`, `num_servers`, `cur_server`, and the dynamically allocated `servers` array. `BUFFER_SIZE` is 2048.

## Control Flow
`main` parses `-p port`, normalizes `optind`, builds the target server list, binds a UDP socket, opens syslog, and enters an infinite receive/forward loop. Incoming packets from configured servers are treated as replies: the first eight payload bytes are interpreted as saved client address and port, and the rest is sent to that client. Other packets are treated as client requests: the forwarder prepends the client address and port, round-robins to the next server, logs the forwarding event, and sends the augmented packet.

## State And Persistence
State is entirely in memory: configured server addresses, the current round-robin index, and one stack packet buffer per loop iteration. There is no durable state except syslog entries.

## Dependencies And Integration Points
The daemon uses BSD sockets, name/service resolution, syslog, and KA port conventions. It bridges legacy AFS KA clients to a fakeka service and assumes that fakeka understands the prepended 8-byte return address header.

## Risks And Test Signals
There is no authentication of reply sources beyond address/port matching the configured server list, no packet length guard before subtracting 8 on replies, and no IPv6 support. `setup_servers` mutates argv strings when splitting `host/port`. Useful tests cover numeric and DNS host parsing, service-name port parsing, round-robin request forwarding, reply forwarding with embedded client address, short reply packets, socket bind failure, and syslog output.
