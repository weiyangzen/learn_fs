# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_endpoint.go

Purpose: Implements ipvlan endpoint creation and deletion, including IP/MAC validation, unsupported option warnings, datastore persistence, and netlink cleanup.

Important APIs and functions: `CreateEndpoint` validates ids, gets the network, rejects custom MAC addresses, records IPv4/IPv6 addresses from `InterfaceInfo`, warns for port mappings and exposed ports, persists the endpoint, and inserts it into the network. `DeleteEndpoint` validates ids, looks up the endpoint, deletes the generated source link if present, removes datastore state, and removes it from the network map.

Control flow: creation persists before adding to the in-memory endpoint map. Deletion best-effort removes kernel link and datastore record, logging cleanup failures except for the primary lookup/validation errors.

State and persistence: writes and deletes `endpoint` KV objects via `storeUpdate`/`storeDelete`; updates `network.endpoints`; deletes Linux links through `ns.NlHandle`.

Dependencies and integration points: integrates with libnetwork `InterfaceInfo`, netlabel port options, `types.PortBinding`, `types.TransportPort`, `errdefs.System`, and Linux netlink.

Risks: `ep.srcName` is not set until `Join`, so deleting an unjoined endpoint may look up an empty link name. Persistence happens before interface creation, so stale endpoint records are possible if later join fails and rollback does not delete.

Test signals: no direct endpoint tests in this subset; behavior is indirectly constrained by store and registration tests.
