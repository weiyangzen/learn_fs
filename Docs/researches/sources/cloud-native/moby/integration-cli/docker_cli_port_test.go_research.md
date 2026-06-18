# sources/cloud-native/moby/integration-cli/docker_cli_port_test.go

Purpose: validates `docker port`, published/exposed port display in `docker ps`, host binding reachability, port range allocation, protocol handling, and internal-network sandbox port behavior.

Important APIs and functions: `DockerCLIPortSuite`, `assertPortList`, `assertPortRange`, `stopRemoveContainer`, Engine API `ContainerInspect`, `client.ContainerInspectOptions`, regex assertions for dynamic ports, and `getNetworkResource`.

Control flow: `TestPortList` runs containers with single, multiple, duplicate, ranged, invalid, host-container range, and mixed TCP/UDP mappings, then compares `docker port` output. `assertPortList` sorts mappings and accepts old IPv6 formatting. `assertPortRange` inspects API port bindings and verifies host ports fall within expected ranges. Other tests check unpublished exposed ports in `ps`, connectivity through host networking, binding release after container removal, and port mapping becoming reachable only after an internal-network container connects to a normal bridge.

State and persistence: creates/removes containers, port bindings, internal and bridge networks, and inspects live network settings. Port allocation reuse is explicitly tested after removal.

Dependencies and integration points: Linux networking, host network mode, busybox `nc`, Engine inspect API, IPv4/IPv6 display, dynamic host port allocation, and user namespace constraints.

Risks: fixed ports can conflict with host services or parallel tests; IPv6 formatting compatibility adds ambiguity; internal network reachability depends on gateway selection and sandbox updates.

Test signals: port mappings must be listed accurately, invalid ranges must fail, exhausted ranges must fail, freed ranges must be reusable, `ps` must show exposed/published ports, and host connectivity must match network attachment state.
