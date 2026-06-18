# sources/cloud-native/containerd/integration/nri_linux_test.go

## Purpose

This Linux file validates that NRI plugins receive correct pod networking attributes during synchronization and lifecycle events. It compares NRI-reported pod IPs and network namespace paths against live netlink inspection.

## Important APIs, Types, And Functions

- `TestNriPluginNetworkingSynchronization` creates multiple pods/containers before connecting a plugin and validates synchronized network data.
- `TestNriPluginNetworkingLifecycle` validates `RunPodSandbox`, `StopPodSandbox`, and `RemovePodSandbox` networking data.
- `getNetworkNamespace` extracts the network namespace path from an NRI pod.
- `getNetworkNamespaceIPs` opens the namespace and lists global unicast addresses on `eth0`.

## Control Flow

Both tests skip when NRI is unavailable. The synchronization test creates three pods with two containers each, connects a mock plugin with a custom `synchronize` hook, filters pods by test prefix, and checks NRI IPs match netlink-discovered IPs. It also verifies all test pods and containers are present in plugin state. The lifecycle test connects a plugin with custom pod hooks, creates/stops/removes one pod, waits for events, and checks network namespace/IP semantics at each stage; removal should keep assigned IPs but no longer have a namespace path.

## State And Persistence Behavior

Plugin state is kept in `mockPlugin.pods`, `mockPlugin.ctrs`, and event queues from `nri_test.go`. Network namespace state is live kernel state, not persisted by the test.

## Dependencies And Integration Points

It integrates with containerd NRI APIs, the local mock plugin framework, CRI pod/container lifecycle, `vishvananda/netns`, `vishvananda/netlink`, and CNI-created `eth0`.

## Risks And Edge Cases

The tests assume pod interfaces are named `eth0` and use global unicast addresses. Network namespace access can fail due to permissions or timing. Hook synchronization uses channels and short timeouts.

## Test Signals

Passing confirms NRI synchronization/lifecycle payloads include accurate network namespace and IP information.
