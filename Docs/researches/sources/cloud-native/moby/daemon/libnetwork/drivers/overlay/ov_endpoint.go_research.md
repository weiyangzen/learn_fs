# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_endpoint.go

Purpose: Implements Linux overlay endpoint create/delete and operational-info behavior.

Important APIs and types: `endpointTable` maps endpoint ids. `endpoint` stores id, network id, interface name, MAC, and IP prefix. `CreateEndpoint` lazily configures the driver, locks the network, validates endpoint IP and subnet, uses supplied MAC or generates one from IP, sets MAC in `InterfaceInfo`, and inserts runtime endpoint state. `DeleteEndpoint` removes runtime endpoint state and deletes the container-side veth if it was created. `EndpointOperInfo` returns an empty map.

Control flow: create validates subnet membership before storing endpoint. Delete tolerates missing Linux link by logging debug and returning nil after endpoint removal.

State and persistence: runtime only; no datastore. Delete mutates kernel link state if `ep.ifName` is known.

Dependencies and integration points: integrates with `driver.configure`, `lockNetwork`, `netiputil`, `hashable.MACAddr`, netlink, and libnetwork `InterfaceInfo`.

Risks: no persistent endpoint restore; overlay relies on cluster state and runtime reconstruction. Generated MAC from IP assumes helper returns MAC-48; panic if not. Deleting runtime state before link deletion can leave kernel residue if deletion fails.

Test signals: no direct endpoint tests in this subset.
