# sources/cloud-native/moby/daemon/libnetwork/netlabel/labels.go

## Purpose
Defines the reserved libnetwork label namespace and constants used to pass network, endpoint, driver, IPAM, DNS, gateway, and bridge-related options through generic option maps.

## Important APIs, Types, And Functions
Constants include `Prefix`, `DriverPrefix`, `DriverPrivatePrefix`, `GenericData`, `PortMap`, `MacAddress`, `ExposedPorts`, `DNSServers`, `EndpointName`, `EndpointSysctls`, `Ifname`, `EnableIPv4`, `EnableIPv6`, `DriverMTU`, `AdvertiseAddrNMsgs`, `AdvertiseAddrIntervalMs`, `OverlayVxlanIDList`, `Gateway`, `Internal`, `ContainerIfacePrefix`, `HostIPv4`, `HostIPv6`, and `NoProxy6To4`. `GetIfname(opts map[string]any) string` extracts `Ifname` only when the value is a string.

## Control Flow
The file is mostly declarations. `GetIfname` performs a safe type assertion against a possibly nil map and returns `""` when the label is absent or not string-typed.

## State And Persistence
There is no local mutable state. The constants form persistent API keys stored in network/endpoint generic options and serialized datastore values.

## Dependencies And Integration Points
Used heavily by `network.go`, endpoint creation, bridge/windows drivers, IPAM metadata, resolver setup, and tests. `GenericData` is especially important because driver-specific options are nested under it.

## Risks
These string constants are compatibility-sensitive. Renaming or changing semantics can break persisted networks, plugins, API clients, and drivers. `GetIfname` intentionally ignores malformed values; callers must separately validate interface names if needed.

## Test Signals
`labels_test.go` verifies nil, absent, string, empty string, nil value, and non-string `Ifname` cases.
