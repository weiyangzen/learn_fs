# sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux_test.go

## Purpose
Regression tests RootlessKit child-host-IP selection without needing a live RootlessKit daemon.

## Important APIs, Types, And Functions
- `TestChildHostIP` builds synthetic `PortDriverClient` values for builtin and slirp4netns-like drivers.

## Control Flow
Each case calls `ChildHostIP` with a protocol and host IP. Expected results cover passthrough, unsupported family/protocol, forced child IP, unspecified/non-loopback translations, and loopback preservation.

## State And Persistence
No external state is used. The test directly populates the client fields that would normally come from RootlessKit `Info`.

## Dependencies And Integration Points
Uses `netip` and `gotest.tools`. It documents the contract consumed by port publishing code.

## Risks
The test does not exercise API connection setup, `AddPort`, cleanup, or RootlessKit error propagation. It is intentionally limited to pure address/protocol decision logic.

## Test Signals
The most important signal is the regression for preserving non-default IPv4 loopback addresses such as `127.0.1.2`, preventing same-port loopback bindings from collapsing to one child address.
