# sources/cloud-native/moby/cmd/docker-proxy/network_proxy_linux_test.go

## Purpose
Provides integration-style tests for docker-proxy networking across TCP, UDP, SCTP, IPv4, IPv6, dual-stack, listener inheritance, and backend error recovery.

## APIs, Types, And Functions
The file defines `EchoServer`, `EchoServerOptions`, `StreamEchoServer`, `UDPEchoServer`, listener helpers, `testProxyAt`, protocol helpers, and tests such as `TestTCP4Proxy`, `TestTCP4ProxyHalfClose`, `TestUDPWriteError`, and SCTP IPv4/IPv6 cases.

## Control Flow, State, And Integration
Tests start local echo backends, build proxy configs with either inherited sockets or host ports, run proxies in goroutines, connect clients, send test buffers, and compare echoed data. SCTP listener setup uses low-level `unix` syscalls to create inheritable descriptors.

## Risks And Test Signals
Signals cover real socket behavior, half-close propagation, UDP ICMP write-error recovery, dual-stack routing, and SCTP proxying. Risks include host SCTP support, fixed "hopefully free" ports, timing, and platform/kernel dependencies.
