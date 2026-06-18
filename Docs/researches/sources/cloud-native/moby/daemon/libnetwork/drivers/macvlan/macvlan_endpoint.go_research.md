# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_endpoint.go

Purpose: Implements macvlan endpoint create/delete, including MAC assignment, unsupported option warnings, datastore persistence, and netlink interface cleanup.

Important APIs and functions: `CreateEndpoint` validates ids, gets the network, records IP addresses and optional MAC, generates and assigns a random MAC if absent, warns for port mappings and exposed ports, stores the endpoint, and adds it to the network. `DeleteEndpoint` looks up the endpoint, deletes its source link if present, removes datastore state, and removes runtime state.

Control flow: MAC generation happens before persistence. Persistence precedes runtime insertion. Delete logs netlink and store cleanup failures but removes runtime endpoint state.

State and persistence: writes/deletes endpoint KV records and updates `network.endpoints`; deletes Linux macvlan source interfaces by name.

Dependencies and integration points: depends on libnetwork `InterfaceInfo`, `netutils.GenerateRandomMAC`, netlabel port/expose options, `errdefs.System`, and Linux netlink.

Risks: deleting before join may attempt lookup of an empty source name. Persisting before join can leave stale endpoint records if later join fails without rollback. Port mapping is only warned, not rejected.

Test signals: no direct endpoint tests in this subset.
