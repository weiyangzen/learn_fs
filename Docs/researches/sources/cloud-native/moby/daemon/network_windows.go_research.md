# sources/cloud-native/moby/daemon/network_windows.go

## Purpose
This Windows-specific daemon file resolves a container endpoint within a libnetwork network.

## Important APIs, Types, And Functions
`getEndpointInNetwork(name string, n *libnetwork.Network)` trims a leading slash from the container name and calls `n.EndpointByName`.

## Control Flow
The function normalizes Docker's slash-prefixed container names to endpoint names, then delegates lookup to libnetwork.

## State, Persistence, And Dependencies
No state or persistence. Dependencies are `strings` and daemon `libnetwork`.

## Integration Points
`oci_windows.go` uses this helper while building Windows OCI network endpoint lists from container network settings.

## Risks And Edge Cases
If endpoint names diverge from trimmed container names, spec generation silently skips endpoints at the caller. Errors are propagated to the immediate caller there but often continued over.

## Test Signals
No direct tests in this item.
