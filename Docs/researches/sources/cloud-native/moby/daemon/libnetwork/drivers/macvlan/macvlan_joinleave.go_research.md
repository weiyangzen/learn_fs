# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_joinleave.go

Purpose: Implements macvlan sandbox join behavior by creating a macvlan link, selecting gateways from IPAM, setting interface names, disabling gateway service, and persisting the endpoint's source name.

Important APIs and functions: `Join` creates a unique source name, calls `createMacVlan`, records `ep.srcName`, configures IPv4/IPv6 gateway or force-gateway flags when not internal, disables gateway service, sets names through `JoinInfo.InterfaceName`, and persists the endpoint. `Leave` is a no-op. `getSubnetForIP` matches endpoint address to configured subnets by mask and containment.

Control flow: internal networks skip gateway configuration. Missing IPAM gateway forces gateway flags to preserve external-connectivity semantics. Interface name setting honors `netlabel.GetIfname`.

State and persistence: creates Linux macvlan links and persists the updated endpoint source name. Mutates `JoinInfo` route/gateway/interface fields.

Dependencies and integration points: depends on `netutils.GenerateIfaceName`, `createMacVlan`, `driverapi.JoinInfo`, and OpenTelemetry tracing.

Risks: `ep.srcName` update is not locked. Errors after link creation require caller rollback to clean up. Gateway strings are parsed as CIDR.

Test signals: no direct join tests; setup tests cover mode conversion and VLAN parsing used by join/network.
