<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator.go

## Purpose
Core Swarm CNM network allocator. It allocates network IPAM pools/gateways, driver state, service VIPs, task endpoint IPs, and node attachment addresses while tracking enough local state to release them.

## Important APIs, Types, And Functions
`cnmNetworkAllocator` holds plugin getter, IPAM/network registries, allocated networks, services, tasks, and node attachments. Public allocator methods include `Allocate`, `Deallocate`, `AllocateService`, `DeallocateService`, `IsAllocated`, `IsTaskAllocated`, `IsServiceAllocated`, `AllocateTask`, `DeallocateTask`, `IsAttachmentAllocated`, `AllocateAttachment`, and `DeallocateAttachment`. Internal helpers include `allocateVIP`, `deallocateVIP`, `allocateNetworkIPs`, `allocatePools`, `freePools`, `allocateDriverState`, `freeDriverState`, `resolveDriver`, `resolveIPAM`, and `setIPAMSerialAlloc`.

## Control Flow
`NewAllocator` registers global and remote network drivers plus built-in and remote IPAM drivers. Network allocation resolves the driver; node-local networks get minimal driver/IPAM state, while global networks allocate pools/gateways, then driver state, with rollback on failure. Services reconcile desired networks against existing VIPs, allocate missing VIPs, and release stale VIPs, with DNSRR mode freeing all VIPs. Task and node attachment allocation requests addresses per network attachment and rolls back earlier attachments if later allocation fails.

## State And Persistence
Allocator state is in-memory maps keyed by network, service, task, and node IDs. It mutates SwarmKit API objects by writing `IPAM`, `DriverState`, `Endpoint.VirtualIPs`, and attachment `Addresses`. Real persistence is delegated to IPAM/network drivers and the Swarm manager object store outside this file.

## Dependencies And Integration Points
Integrates SwarmKit `networkallocator`, libnetwork driver registries, overlay network allocator, local driver lists, default and remote IPAM, plugin getter, netlabel gateway metadata, and containerd logging.

## Risks And Edge Cases
There is no explicit mutex, so callers must serialize allocator access as SwarmKit expects. `allocateNetworkIPs` returns after allocating one address even if multiple addresses were supplied. `releaseEndpoints` deletes endpoint mappings before IPAM release succeeds, risking local accounting drift on release failures. `dOptions` is mutated during gateway allocation. Pool release logs errors but continues.

## Test Signals
`networkallocator_test.go` covers invalid drivers/IPAMs, deterministic subnet allocation, gateway handling, small subnets, task allocation/free, service VIP updates, ingress VIP reuse, and IPAM option passing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator.go -->
