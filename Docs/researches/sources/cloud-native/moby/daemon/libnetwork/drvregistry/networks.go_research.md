# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks.go

Purpose: implements the registry for network drivers and network allocators. Important types and APIs are `Networks`, `DriverWalkFunc`, `RegisterDriver`, `Driver`, `WalkDrivers`, `RegisterNetworkAllocator`, `NetworkAllocator`, and `HasDriverOrNwAllocator`.

Control flow: registration rejects blank network types, checks whether an existing builtin driver/allocator blocks replacement, optionally forwards registration to `Notify`, then lazily initializes and updates the local map under lock. Lookup returns stored values without error if absent. Walking snapshots drivers under lock, releases the lock, and invokes the callback until it asks to stop.

State/dependencies: state is mutex-protected maps for drivers and allocators plus optional cascading registration via `Notify`; it is not persisted. Dependencies are `driverapi` for driver, allocator, capability, and active-registration errors. Integration points include platform driver registration and plugin forwarding. Risks include nil driver registration, race windows between duplicate check and final store if another goroutine registers the same key, and randomized walk order. Tests cover basic registration, duplicate builtin rejection, lookup, and walking.
