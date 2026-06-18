# sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux_test.go

## Purpose
Tests that one-sided UDP traffic keeps conntrack entries alive while clients continue sending even if the backend does not reply.

## APIs, Types, And Functions
`TestUDPOneSided` exercises `NewUDPProxy`, `UDPProxy.Run`, `UDPProxy.Close`, `connTrackTimeout`, and UDP client/backend sockets.

## Control Flow, State, And Integration
The test creates a UDP proxy, sends repeated datagrams without backend replies, and checks connection tracking behavior across timeout windows. State under test is the proxy's `connTrackTable` and `lastW` timestamps.

## Risks And Test Signals
This catches premature conntrack garbage collection for write-only UDP flows. Timing sensitivity is the main risk, but the signal is important for UDP protocols that receive delayed or no replies.
