# sources/cloud-native/cri-o/internal/hostport/hostport_manager.go

## Purpose
Defines the CRI-O hostport management interface and the `PortMapping` data model shared by iptables, nftables, meta, and noop hostport managers.

## Important APIs, Types, And Functions
- `HostPortManager` interface declares `Add(id, name, podIP string, hostportMappings []*PortMapping) error` and `Remove(id string, hostportMappings []*PortMapping) error`.
- `PortMapping` contains `HostPort`, `ContainerPort`, Kubernetes `Protocol`, and optional `HostIP`.

## Control Flow
This file has declarations only. Implementations decide backend behavior and cleanup strategy.

## State And Persistence
No state is stored here. Implementations persist hostport mappings in kernel packet filtering state or do nothing.

## Dependencies And Integration Points
Uses Kubernetes core `v1.Protocol`. The interface is consumed by sandbox/container networking code and implemented by iptables, nftables, meta, and noop managers.

## Risks And Edge Cases
`Remove` is explicitly required to work without pod IP, which shapes backend state keys and cleanup algorithms. `HostPort <= 0` filtering is implemented in the meta layer, not the type itself.

## Test Signals
Shared test cases in `hostport_manager_test.go` instantiate `PortMapping` scenarios used by backend tests.
