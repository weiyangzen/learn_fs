<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_unix_test.go

Purpose: Unix integration tests for controller sandbox lookup, sandbox deletion, endpoint ordering, and gateway endpoint selection.

Important APIs/functions: `getTestEnv` builds a controller and optional bridge networks. Tests include `TestControllerGetSandbox`, `TestSandboxAddEmpty`, `TestSandboxAddMultiPrio`, `TestGatewayEndpointRespectsPriorityPerAddressFamily`, and `TestSandboxAddSamePrio`.

Control flow: tests create sandboxes/networks/endpoints, join endpoints with or without priorities, and inspect controller sandbox endpoint ordering. They verify invalid and missing sandbox lookup errors, empty sandbox deletion, priority dominance, internal-network lowest precedence, IPv6/gateway precedence, and separate IPv4/IPv6 gateway endpoint selection.

State and persistence: uses temporary data dirs, bridge network state, endpoint lists, and sandbox controller maps. Cleanup deletes sandboxes/networks and stops controller.

Dependencies and integration points: bridge driver, default IPAM, netns test context, network labels, and join options.

Risks and test signals: protects the endpoint ordering logic that drives default gateway choice and DNS/network preference. Requires Unix network namespace support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_unix_test.go -->
