<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_windows.go

Purpose: Windows default dynamic port range and reserved-port implementation.

Important APIs/functions: defines `defaultPortRangeStart = 60000`, `defaultPortRangeEnd = 65000`, `getDynamicPortRange`, and `getReservedPorts`.

Control flow: `getDynamicPortRange` returns constants directly. `getReservedPorts` returns nil, so the shared allocator has no Windows reserved-port skip list.

State and persistence: no OS reads or writes; no persisted state.

Dependencies and integration points: used by the shared allocator and Windows `OSAllocator`.

Risks and test signals: Windows behavior does not consult dynamic system settings here, so configured OS ranges may diverge from Docker allocator defaults. Test signal is primarily Windows build/test coverage outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_windows.go -->
