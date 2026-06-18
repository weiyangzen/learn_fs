<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/labels.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/labels.go

## Purpose
Defines public bridge-driver option labels used in network creation/configuration.

## Important APIs, Types, And Functions
Constants include `BridgeName`, `EnableIPMasquerade`, `IPv4GatewayMode`, `IPv6GatewayMode`, `EnableICC`, `InhibitIPv4`, `DefaultBindingIP`, `DefaultBridge`, and `TrustedHostInterfaces`.

## Control Flow
There is no executable flow. Other bridge configuration code reads these keys from network labels/options and maps them into `networkConfiguration`.

## State And Persistence
Labels become persisted network configuration through `bridge_store.go` and are visible as user-facing Docker network options.

## Dependencies And Integration Points
No imports. Integrated with Docker CLI/API network creation, `netlabel.GenericData`, config validation, and bridge tests that pass labels.

## Risks And Edge Cases
These string constants are part of a user-facing compatibility surface. Renaming or changing semantics would break existing network creation workflows and persisted configs.

## Test Signals
`TestCreateFullOptionsLabels` validates label decoding for bridge name, default bridge, ICC, masquerade, default binding IP, host IPv4, and IPv6 gateway config.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/labels.go -->
