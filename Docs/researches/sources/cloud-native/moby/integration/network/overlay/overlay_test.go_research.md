<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/overlay_test.go -->
# sources/cloud-native/moby/integration/network/overlay/overlay_test.go

Purpose: overlay network integration tests for custom container interface names and host-mode swarm port mapping visibility.

Important APIs/types/functions: `TestEndpointWithCustomIfname` creates an attachable overlay network and runs a container with endpoint driver option `netlabel.Ifname`. `TestHostPortMappings` creates a swarm service with host-mode published port and validates `ContainerList` port reporting.

Control flow: custom-ifname test starts and initializes swarm, creates an attachable overlay network, runs a container executing `ip -o link show foobar`, and asserts the output contains the requested interface name. Host-port test starts a swarm node with BusyBox, creates overlay network/service, waits for one task, lists containers, formats public/private port bindings, sorts them, and expects IPv4 plus optional IPv6 wildcard binding.

State/persistence: creates swarm state, overlay networks, services, tasks, and containers, then removes/leaves via cleanup.

Dependencies/integration: swarm helpers, daemon helper, Docker API, container/network helpers, `netlabel.Ifname`, polling, and Linux `ip` inside containers. Rootless mode is skipped because overlay is unsupported there.

Risks: host-mode port list may vary by IPv6 availability, hence the optional second address. Swarm task scheduling/polling can be timing-sensitive. Custom interface-name support depends on overlay driver endpoint implementation.

Test signals: passing tests show overlay endpoints honor custom interface names and `ContainerList` reports the expected one or two host-mode published port bindings for swarm tasks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/overlay_test.go -->
