# sources/cloud-native/moby/daemon/libnetwork/drivers/remote/api/api.go

Purpose: Defines the JSON request/response structs for Docker remote network driver plugin RPCs.

Important APIs and types: `Response`/`GetError` provide common plugin error propagation. Capability, network allocate/free, gateway allocation check, create/delete network, create/delete endpoint, endpoint info, join/leave, external connectivity, revoke connectivity, and discovery notification request/response structs model all supported plugin methods. `EndpointInterface`, `InterfaceName`, and `StaticRoute` represent endpoint and join data.

Control flow: declarative transport contract; `remote/driver.go` serializes these structs through the plugin client.

State and persistence: no runtime state. These structs are wire-contract state exchanged with external plugins.

Dependencies and integration points: ties plugin API to libnetwork `driverapi.IPAMData`, `discoverapi.DiscoveryType`, and `types.RouteType`.

Risks: field names and shapes are plugin API compatibility surface. `DiscoveryData any` relies on JSON encoding preserving useful shape for plugins.

Test signals: `remote/driver_test.go` exercises many request/response shapes through an HTTP test plugin.
