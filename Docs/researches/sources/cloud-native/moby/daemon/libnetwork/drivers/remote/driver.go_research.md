# sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver.go

Purpose: Implements the adapter between libnetwork's driver interfaces and external network driver plugins.

Important APIs and types: `driver` stores plugin client, network type, gateway-allocation capability, and endpoint gateway state. `Register` discovers active plugins, negotiates capabilities, registers drivers, and registers network allocators for global data scope. `getPluginClient` handles v1 clients or HTTP v1 plugin addresses. `getCapabilities`, `call`, `NetworkAllocate`, `NetworkFree`, `CreateNetwork`, `GetSkipGwAlloc`, `DeleteNetwork`, `CreateEndpoint`, `DeleteEndpoint`, `EndpointOperInfo`, `Join`, `Leave`, `ProgramExternalConnectivity`, `revokeExternalConnectivity`, `DiscoverNew`, `DiscoverDelete`, `parseStaticRoutes`, and `parseInterface` implement the API mapping.

Control flow: plugin method names are prefixed with `NetworkDriver.`. Plugin response `Err` fields become errors. CreateEndpoint and Join have rollback defers that call DeleteEndpoint/Leave if applying plugin-returned state fails. ProgramExternalConnectivity tracks gateway identity and passes `NoProxy6To4` when another endpoint handles IPv6.

State and persistence: no datastore. In-memory `nwEndpoints` tracks joined endpoints and gateway status for external connectivity calls. External plugin owns its own persistence.

Dependencies and integration points: central integration with Docker plugin system, libnetwork driverapi/network allocator/discovery interfaces, netlabel options, and API structs.

Risks: endpoint map is keyed only by endpoint id, not network id. Rollback error wrapping order can be confusing. Plugin compatibility requires tolerating missing external connectivity methods. `Join` ignores `DstName` from plugin when setting names, passing an empty destination name.

Test signals: `driver_test.go` covers capabilities, RPC sequence, gateway allocation check, endpoint/join data application, discovery, plugin errors, missing values, and rollback on interface application failure.
