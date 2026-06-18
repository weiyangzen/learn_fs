# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_store.go

Purpose: Implements ipvlan datastore persistence for network configurations and endpoints, including restore, stale endpoint cleanup, custom JSON formats, and `datastore.KVObject` methods.

Important APIs and types: constants define key prefixes. `configuration` stores network options, IPAM subnets, internal state, and DB metadata. `ipSubnet` stores subnet and gateway strings. `initStore`, `populateNetworks`, and `populateEndpoints` restore persisted objects. `storeUpdate` and `storeDelete` wrap datastore atomic put/delete. `configuration` and `endpoint` implement JSON marshal/unmarshal and KV object methods.

Control flow: init restores networks first so endpoint restoration can attach to existing runtime networks. Endpoints whose network is absent are deleted as stale. Missing store keys are treated as empty state. A nil store logs and makes persistence a no-op.

State and persistence: keys are `ipvlan/network/<id>` and `ipvlan/endpoint/<id>`. Config JSON stores nested subnets as JSON-encoded strings and migrates missing `IpvlanFlag` to `bridge`.

Dependencies and integration points: integrates with libnetwork `datastore`, `types.ParseCIDR`, and network creation via `d.createNetwork`.

Risks: unmarshal uses unchecked type assertions, so corrupted datastore JSON can panic. Endpoint keys are only by endpoint id, assuming global uniqueness. Restore can recreate links and may log but continue on per-network failures.

Test signals: `ipvlan_test.go` checks `initStore` with temp store but does not validate JSON compatibility or stale cleanup.
