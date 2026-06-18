# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_network.go

Purpose: Implements macvlan network creation/deletion, parent interface provisioning, option parsing, IPAM processing, and gateway allocation behavior.

Important APIs and functions: `CreateNetwork` rejects empty enabled IP pools, parses options, processes IPAM, supplies dummy parent when missing, calls `createNetwork`, and persists config. `GetSkipGwAlloc` returns true for both families. `createNetwork` allows shared parents except when any involved network uses passthru mode, creates dummy/VLAN parents, and marks shared driver-created links. `parentHasSingleUser` gates deletion of shared created parents. `DeleteNetwork` cleans endpoint links and datastore records, conditionally deletes parent link, and removes config. Parsing helpers map labels to config and subnets.

Control flow: create handles existing same-id network as restore via internal maskable error. Delete only removes driver-created parent links when this network is the last user, unlike ipvlan.

State and persistence: persists network configs/endpoints through store helpers and creates/deletes Linux dummy or VLAN links.

Dependencies and integration points: uses netlabel options, libnetwork IPAM, `types.InternalMaskableErrorf`, and setup helpers.

Risks: type assertions on enable flags assume booleans. Link creation can outlive datastore rollback. Parent sharing requires accurate `CreatedSlaveLink` propagation to avoid deleting links still in use.

Test signals: no direct network lifecycle tests; setup and registration tests cover smaller pieces.
