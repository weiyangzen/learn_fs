# sources/cloud-native/moby/integration-cli/docker_api_network_test.go

Purpose: tests Docker Engine network API integration for inspecting networks, creating and deleting user-defined bridge networks, connecting and disconnecting containers, IPAM overlap detection, and rejecting create/delete operations for predefined networks.

Important APIs, types, and functions: `TestAPINetworkInspectBridge`, `TestAPINetworkInspectUserDefinedNetwork`, `TestAPINetworkConnectDisconnect`, `TestAPINetworkIPAMMultipleBridgeNetworks`, `TestAPICreateDeletePredefinedNetworks`, plus helpers `createDeletePredefinedNetwork`, `isNetworkAvailable`, `getNetworkResource`, `createNetwork`, `connectNetwork`, `disconnectNetwork`, and `deleteNetwork`. API payloads use `network.CreateRequest`, `network.IPAM`, `network.IPAMConfig`, `network.ConnectRequest`, `client.NetworkDisconnectOptions`, `network.Inspect`, and `network.CreateResponse`.

Control flow: tests create networks through `/networks/create`, inspect them through `/networks/{id}`, enumerate `/networks`, attach running BusyBox containers via `/connect`, verify addresses against `findContainerIP`, and remove resources through `DELETE /networks/{id}`. The IPAM test creates one bridge network, verifies a second overlapping subnet is forbidden, deletes the first, then verifies the formerly-overlapping network can be created.

State and persistence behavior: state lives in daemon-local network definitions, bridge devices/IPAM allocations, and container endpoint membership. Tests clean up explicit test networks through `deleteNetwork`; the suite teardown handles created containers. Predefined networks are intentionally not mutated because create should return forbidden and delete should not return OK.

Dependencies and integration points: Linux and non-swarm assumptions are enforced with `testRequires`. The file integrates raw API request helpers with Moby network API structs, netip prefix/address parsing, CLI container startup, and `findContainerIP` from the broader integration suite.

Risks and edge cases: fixed private subnets can conflict with host or CI routing. Helper `createNetwork` returns an ID for negative expected status values, but requested tests only use positive expected status codes. Network availability checks are name-based and assume no concurrent unrelated test reuses these names.

Test signals: confirms bridge inspect exposes driver/scope/IPAM/container endpoint data, user-defined network inspect preserves IPAM/options, connect/disconnect updates endpoint state and IP address, overlapping bridge IPAM is rejected until conflicting network removal, automatic IPAM chooses non-overlapping ranges, and predefined `bridge`, `none`, and `host` networks cannot be created or deleted through the API.
