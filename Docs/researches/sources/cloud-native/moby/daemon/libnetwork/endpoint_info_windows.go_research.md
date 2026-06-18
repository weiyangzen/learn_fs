# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_windows.go

Purpose: provides Windows-specific `Endpoint.DriverInfo`, augmenting endpoint driver operational data with gateway-network endpoint information. Important API is `DriverInfo`.

Control flow: the method retrieves the latest endpoint, checks whether it is attached to a sandbox, finds the sandbox gateway-network endpoint if different from the target endpoint, recursively retrieves that gateway endpoint's driver info, then retrieves the target network driver and endpoint operational info. If endpoint info exists, it injects `GW_INFO`; otherwise it returns gateway info alone.

State/dependencies: this is read-only but depends on persisted endpoint/network state, controller sandbox maps, and driver `EndpointOperInfo`. It integrates with Windows NAT/gateway behavior where gateway endpoint data may be needed for inspect/operational consumers. Risks include recursive driver-info failures, nil `GW_INFO` values, and reliance on sandbox state being present for gateway merge. Test coverage is indirect; no local unit test covers this merge behavior.
