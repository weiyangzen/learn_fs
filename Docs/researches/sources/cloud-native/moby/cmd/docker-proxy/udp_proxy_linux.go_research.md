# sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux.go

## Purpose
Implements UDP forwarding for docker-proxy with per-client connection tracking and source-address preservation.

## APIs, Types, And Functions
Important types are `connTrackKey`, `connTrackMap`, `connTrackEntry`, and `UDPProxy`. Key functions are `newConnTrackKey`, `newConnTrackEntry`, `lastWrite`, `NewUDPProxy`, `replyLoop`, `Run`, `readDestFromCmsg`, and `Close`.

## Control Flow, State, And Integration
`Run` reads datagrams and packet-info control messages from the frontend listener. It creates a backend UDP connection per client address, stores it in `connTrackTable`, starts `replyLoop`, and writes incoming datagrams to the backend. Replies are sent back with control messages so the source address matches the host address the client targeted.

## Risks And Test Signals
Risks include conntrack leaks, lock ordering, ICMP port-unreachable retry behavior, packet-info parsing compatibility, timeout cleanup, and IPv4/IPv6 differences. Integration is with Linux UDP socket control messages and Docker port publishing.
