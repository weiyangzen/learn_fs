# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_network_windows.go

Purpose: Implements Windows overlay network create/delete, runtime state, HNS network creation, subnet lookup helpers, and stale VNI network cleanup.

Important APIs and types: `network` stores id, name, HNS ID, provider address, adapter, endpoints, subnets, secure flag, and a port allocator. `subnet` stores VNI, subnet IP, and gateway IP. `CreateNetwork` validates network info and IPv4 IPAM, deletes preexisting same-id network, parses generic labels including network name/interface/HNS ID/VNI list, requires VNIs for all subnets, removes stale networks that reuse a VNI, registers the peer table, adds runtime state, creates the HNS network, and writes the HNS ID back to generic data. `DeleteNetwork` deletes HNS network and runtime state. Helpers add/delete/lookup networks, convert HNS endpoints, create HNS network with VSID policies, and find subnets.

Control flow: VNI conflicts with existing runtime networks are resolved by deleting stale networks before creating the new HNS network. HNS network creation serializes subnets with VSID policies and records returned HNS ID/provider management IP.

State and persistence: runtime driver network table, HNS network state, and mutation of the generic data map with HNS ID. No explicit datastore here.

Dependencies and integration points: integrates with Windows HNS via `hcsshim`, shared overlay VNI label, libnetwork peer table registration, and Windows port allocator for endpoints.

Risks: create mutates caller-provided generic data. Stale-network deletion can remove existing runtime networks sharing a VNI. IPv6 IPAM is not used. Host mode globals are defined but not used in this file.

Test signals: no direct Windows overlay tests in this subset.
