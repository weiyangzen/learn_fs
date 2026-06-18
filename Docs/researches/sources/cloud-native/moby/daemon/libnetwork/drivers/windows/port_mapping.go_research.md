# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/port_mapping.go

Purpose: manages Windows host port allocation bookkeeping for HNS endpoint NAT policies, mainly for `l2bridge` and `l2tunnel` networks. Important APIs are `AllocatePorts`, internal `allocatePort`, `ReleasePorts`, and `maxAllocatePortAttempts`.

Control flow: `AllocatePorts` walks requested `types.PortBinding` values, allocates each through `portallocator.OSAllocator`, and rolls back all previously allocated bindings if any later allocation fails. `allocatePort` normalizes nil host IP to `0.0.0.0`, fills `HostPortEnd` for non-ranges, retries dynamic host-port allocation up to ten times, but does not retry explicit ports. Successful allocation collapses the host port range to the selected port. `ReleasePorts` attempts every deallocation and returns a joined error so cleanup is best-effort but visible.

State and dependencies: state lives in the supplied allocator, not in this file; operational HNS policies are built later in `windows.go`. Dependencies include `portallocator`, libnetwork `types`, and logging. Risks include Windows' lack of host-IP support, retry churn for ephemeral allocations, and errors during cleanup leaving allocator state inconsistent. Test signal is indirect through Windows driver endpoint creation tests.
