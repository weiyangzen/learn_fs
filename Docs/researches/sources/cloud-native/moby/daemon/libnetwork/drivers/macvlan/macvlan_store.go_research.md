# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_store.go

Purpose: Implements datastore persistence for macvlan network configurations and endpoints, including restore, stale endpoint cleanup, custom JSON, and `datastore.KVObject` methods.

Important APIs and types: key prefixes are `macvlan/network` and `macvlan/endpoint`. `configuration` stores ID, MTU, internal flag, parent, mode, created-link flag, and IPv4/IPv6 subnets. `ipSubnet` stores subnet/gateway strings. `initStore`, `populateNetworks`, `populateEndpoints`, `storeUpdate`, and `storeDelete` manage persistence. `configuration` and `endpoint` marshal/unmarshal JSON and implement KV object methods.

Control flow: restores networks before endpoints; deletes stale endpoints whose networks are absent. Nil store makes update/delete a logged no-op.

State and persistence: config and endpoint records are JSON blobs under driver-specific prefixes. Subnet slices are JSON-encoded strings inside the outer JSON map.

Dependencies and integration points: uses `datastore`, `types.ParseCIDR`, and `d.createNetwork` for restore side effects.

Risks: unchecked JSON type assertions can panic on corrupt store data. Endpoint keys use endpoint id only. Restore of a network can create links and log warnings without stopping all restore.

Test signals: registration tests initialize an empty temp store but do not validate populated restore or migration behavior.
