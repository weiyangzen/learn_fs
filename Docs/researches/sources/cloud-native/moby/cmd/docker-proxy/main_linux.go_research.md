# sources/cloud-native/moby/cmd/docker-proxy/main_linux.go

## Purpose
Provides the Linux `docker-proxy` entrypoint that maps host ports to container ports for TCP, UDP, and SCTP traffic.

## APIs, Types, And Functions
Key items are `ProxyConfig`, `main`, `newProxy`, `parseFlags`, and `handleStopSignals`. It uses inherited file descriptors `parentPipeFd` and `listenSockFd`, `net` listeners, SCTP support, Rootless/userland proxy protocol flags, and version printing via `dockerversion`.

## Control Flow, State, And Integration
`main` marks inherited descriptors close-on-exec, parses flags, builds the appropriate proxy, reports startup status to the parent pipe, installs signal handling, and blocks in `Proxy.Run`. `newProxy` either reuses an inherited listener or opens a host listener, configures UDP packet-info control messages, and constructs backend addresses.

## Risks And Test Signals
Risks include inherited descriptor misuse, wrong IP family selection, UDP source-address handling, SCTP availability, and startup reporting deadlocks. Integration is with dockerd's port publishing path and Linux socket behavior.
