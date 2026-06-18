# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_unix.go

Purpose: provides Unix implementation of `Endpoint.DriverInfo`, returning operational endpoint data directly from the endpoint's network driver. Important API is `DriverInfo`.

Control flow: the method retrieves the latest endpoint from the store, retrieves the latest network, obtains the driver with strict lookup, and returns `driver.EndpointOperInfo(networkID, endpointID)`. Errors are wrapped to identify whether endpoint hydration, network lookup, or driver lookup failed.

State/dependencies: this is a read-only bridge from persisted endpoint/network state to driver operational data. Dependencies include platform build tags, network driver interface, and endpoint store helpers. Integration points include Docker inspect-style queries needing MAC/port/driver-specific data. Risks include returning stale or failed data if the store is out of sync with the driver, and requiring the driver to be present even for historical endpoint records. Test signal is indirect; Windows has a separate gateway-info merge path.
