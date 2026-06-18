<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/discoverapi/discoverapi.go -->
# sources/cloud-native/moby/daemon/libnetwork/discoverapi/discoverapi.go

## Purpose
Defines the discovery notification interface and payload types used by network drivers to receive cluster node and encryption-key events.

## Important APIs, Types, And Functions
`Discover` exposes `DiscoverNew` and `DiscoverDelete`. `DiscoveryType` includes `NodeDiscovery`, `EncryptionKeysConfig`, and `EncryptionKeysUpdate`. Payloads include `NodeDiscoveryData`, `DriverEncryptionConfig`, and `DriverEncryptionUpdate`.

## Control Flow
There is no executable flow. Controller code detects drivers implementing `Discover` and sends add/delete events with these typed payloads.

## State And Persistence
No state; pure interface and data contracts.

## Dependencies And Integration Points
Used by controller node discovery and overlay/encryption integrations.

## Risks And Edge Cases
Payload fields are loosely typed through `any` in the interface, so drivers must type-assert correctly. Encryption key semantics rely on positional primary key/tag fields.

## Test Signals
Driver tests should assert expected discovery event types and payloads are delivered on cluster membership and key changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/discoverapi/discoverapi.go -->
