# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager.go

Purpose: Implements the overlay network allocator responsible for assigning and freeing VXLAN IDs for overlay subnets.

Important APIs and types: `driver` owns a mutex-protected network table and bitmap allocator. VNI allocation range is 4096 through `(1<<24)-1`, avoiding VLAN ID overlap and respecting VXLAN maximum. `Register` registers a network allocator for `overlay`. `NetworkAllocate` parses user-specified VNI list, allocates missing VNIs per IPv4 subnet, stores network state, and returns the normalized `OverlayVxlanIDList`. `NetworkFree` releases all VNIs for a network. `releaseVxlanID` clears bitmap bits. `IsBuiltIn` returns true.

Control flow: user VNIs are consumed in subnet order; extra user VNIs are ignored in returned output beyond subnet count. Allocation failures roll back already-allocated IDs. Duplicate network ids are rejected after releasing new allocations.

State and persistence: in-memory bitmap and network map only; no datastore.

Dependencies and integration points: used by libnetwork's network allocation phase before overlay driver network creation. Depends on bitmap allocator, netlabel, and `overlayutils.AppendVNIList`.

Risks: bitmap size covers full VNI range, which is large but intended. User-specified VNIs below 4096 can be set because only auto-allocation avoids that range; this may be for compatibility but can conflict with Windows constraints.

Test signals: `ovmanager_test.go` covers auto allocation/free and user-defined VNIs with extra values.
