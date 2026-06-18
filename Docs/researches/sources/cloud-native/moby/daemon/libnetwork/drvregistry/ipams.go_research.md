# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams.go

Purpose: implements the in-process registry for IPAM drivers. Important types and APIs are `ipamDriver`, `IPAMs`, `IPAM`, `RegisterIpamDriverWithCapabilities`, `RegisterIpamDriver`, `IPAMWalkFunc`, and `WalkIPAMs`.

Control flow: registration rejects blank names, locks the registry, blocks replacing an existing builtin driver, lazily initializes the map, and stores driver plus capability. Lookup returns the registered driver/capability pair for a name, with zero values if absent. Walking snapshots registered entries while locked, releases the lock, then invokes the callback until it returns true.

State/dependencies: state is an internal map protected by a mutex; it is not persisted. Dependencies are `ipamapi` and libnetwork `types` for forbidden duplicate errors. Integration points include builtin IPAM registration and controller address allocation. Risks include nil driver values being accepted, absent lookups returning nil without error, and iteration order being map-randomized. Tests verify default/null/windows registration visibility via `WalkIPAMs`.
