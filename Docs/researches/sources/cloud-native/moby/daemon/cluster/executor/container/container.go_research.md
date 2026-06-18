# Research: sources/cloud-native/moby/daemon/cluster/executor/container/container.go

## sources/cloud-native/moby/daemon/cluster/executor/container/container.go

Purpose: converts a SwarmKit `api.Task` into Docker Engine container, host, networking, volume, service-discovery, and event-filter structures. The central type is `containerConfig`, built by `newContainerConfig` and `setTask`; it validates runtime presence, enforces an image for container tasks, validates mounts, indexes task networks, and expands templated container specs against the node description.

Important APIs include `config`, `hostConfig`, `createNetworkingConfig`, `serviceConfig`, `networkCreateRequest`, `volumeCreateRequest`, `eventFilter`, `convertMount`, `getEndpointConfig`, and `ipamConfig` integration through `network.go`. Control flow is mostly pure translation from SwarmKit protobufs to Engine API types: labels merge user spec labels, task annotation labels, then reserved `com.docker.swarm.*` system labels; command and args are mapped into `Entrypoint` and `Cmd`; host-mode ports become exposed ports and bindings; DNS, ulimits, memory, swap, CPU, capabilities, security options, and logging settings flow into `HostConfig`.

State and persistence are indirect. The file mutates `c.task.Spec.Runtime` after template expansion and derives CSI cluster mount host paths from the dependency getter and task volume attachments. It does not persist data itself, but it feeds daemon create/network/service-binding calls that persist Engine resources and libnetwork service records.

Dependencies and integration points are broad: `github.com/moby/swarmkit/v2/api`, Engine API container/mount/network/volume structs, daemon cluster `convert`, executor backends, libnetwork scope, netip parsing helpers, generic resources, and SwarmKit template expansion. Risks include silent skipping of invalid host ports or endpoint addresses, best-effort JSON unmarshal of tmpfs options, possible missed CSI mount path if dependencies are unavailable, map-by-network-name collisions, and security-sensitive mapping of credential specs, SELinux, seccomp, AppArmor, and `no-new-privileges`.

Test signals come from `container_test.go`, which covers isolation conversion, reserved label precedence, credential-spec security options, and tmpfs option conversion. Mount validation behavior is covered in `validate*_test.go`; health/event behavior is covered separately in `health_test.go`.
