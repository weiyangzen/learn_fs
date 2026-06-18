# sources/cloud-native/moby/cmd/docker-proxy/proxy_linux.go

## Purpose
Defines shared Linux docker-proxy protocol abstractions.

## APIs, Types, And Functions
`ipVersion` is a string-like protocol suffix type with IPv4 and IPv6 values. `Proxy` is the common interface implemented by TCP, UDP, and SCTP proxies, with `Run` and `Close` methods.

## Control Flow, State, And Integration
This file has no runtime flow of its own; it establishes compile-time contracts used by `main_linux.go` and protocol-specific proxy implementations. State is held by concrete proxy structs in other files.

## Risks And Test Signals
Risks are low but central: changing the interface breaks all protocol implementations. Integration signals come from docker-proxy tests that instantiate concrete proxies through the shared interface.
