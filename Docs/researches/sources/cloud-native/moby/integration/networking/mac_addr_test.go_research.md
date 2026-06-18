# sources/cloud-native/moby/integration/networking/mac_addr_test.go

## Purpose
Tests MAC address allocation, persistence, inspect serialization, legacy API migration, and `NetworkConnect` endpoint MAC support. It focuses on distinguishing generated MACs from configured MACs and preserving/omitting them correctly across API versions and restart paths.

## Important APIs, Types, And Functions
Uses `container.WithMacAddress`, `EndpointSettings.MacAddress`, `NetworkConnect`, `ContainerStop`, `ContainerStart`, daemon restart, and low-level `request.Post` to send a legacy `MacAddress` field. The local `legacyCreateRequest` embeds `containertypes.CreateRequest` with deprecated top-level `MacAddress`, and `createLegacyContainer` posts directly to `/v<version>/containers/create`.

## Control Flow
`TestMACAddrOnRestart` verifies a stopped generated-MAC container receives a non-conflicting MAC when restarted after another container may have reused its original address. `TestCfgdMACAddrOnRestart` ensures a configured MAC survives container and daemon restart. `TestInspectCfgdMAC` compares inspect `Config.MacAddress` for generated, endpoint-configured, custom network, and legacy container-wide paths. `TestWatchtowerCreate` uses API 1.25 to migrate container-wide MAC into endpoint settings when network mode uses network ID but endpoint config is keyed by name. `TestNetworkConnectWithMACAddress` connects a running container to a network with a MAC and verifies inspect plus `/sys/class/net/eth1/address`.

## State And Persistence Behavior
Persistent behavior is central: configured MACs must be stored and restored, generated MACs must be regenerated safely when necessary, and legacy container create data must migrate into endpoint state. Inspect output is treated as API state and validated for backward compatibility.

## Dependencies And Integration Points
Depends on libnetwork bridge and macvlan drivers, API version gates (`1.25`, `1.43`, `1.51`), daemon env `DOCKER_MIN_API_VERSION`, request helper raw API calls, and Linux container interface state.

## Risks
MAC allocation tests can depend on address reuse probabilities, though the scenario is designed to expose the original bug. Legacy API behavior is brittle by design and may require updates when deprecated fields are removed. Macvlan availability and Windows/rootless limitations require skips.

## Test Signals
Signals include inspect `NetworkSettings.Networks[*].MacAddress`, raw inspect `Config.MacAddress`, successful container start/restart, expected IP/MAC on macvlan, and in-container interface address validation.
