# sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux.go

## Purpose
Provides Linux RootlessKit port-driver integration so libnetwork can notify RootlessKit when port mappings are added and removed in rootless mode.

## Important APIs, Types, And Functions
- `PortDriverClient` wraps the RootlessKit API client, driver name, supported protocol set, and optional non-loopback child IP.
- `NewPortDriverClient` connects to `$ROOTLESSKIT_STATE_DIR/api.sock`, fetches RootlessKit info, returns nil when no explicit port driver is active, and validates child IP requirements for drivers that disallow loopback child addresses.
- `proto` normalizes `tcp`/`udp` to `tcp4`, `tcp6`, `udp4`, or `udp6` based on host IP family.
- `ChildHostIP` maps host bind addresses to child-namespace addresses, preserving distinct loopback addresses but using family loopback for non-loopback addresses unless a forced child IP exists.
- `ProtocolUnsupportedError` is returned for unsupported protocol/family combinations.
- `AddPort` calls RootlessKit `PortManager.AddPort` and returns a cleanup function that removes the mapping with `context.WithoutCancel`.

## Control Flow
Construction reads environment, establishes API connection, validates driver info, records supported protocols, and optionally records a non-loopback child IP from the network driver. `AddPort` is a no-op for nil clients, rejects unsupported normalized protocols, constructs a `port.Spec` with same parent/child port, and returns a deferred remover.

## State And Persistence
State is held in the client object. Actual persistence/effects are external to Docker: RootlessKit owns the port mapping state behind its API socket. Cleanup depends on the caller invoking the returned function.

## Dependencies And Integration Points
Imports RootlessKit API and port packages. Integrates with rootless port publishing and DNAT rule generation where host IPs need translation into the child namespace.

## Risks
Environment and RootlessKit version are hard prerequisites. Unsupported IPv6 with some drivers is reported at add time. If callers drop the returned cleanup function, RootlessKit mappings may leak until daemon/container cleanup. Child IP mapping correctness is critical to avoid port collisions and unreachable bindings.

## Test Signals
`rootlesskit_client_linux_test.go` focuses on `ChildHostIP`: nil client passthrough, unsupported protocol returning invalid address, forced child IP for slirp4netns, loopback preservation, and IPv4/IPv6 loopback fallback for non-loopback host IPs.
