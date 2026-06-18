# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_joinleave.go

Purpose: Implements sandbox join behavior for ipvlan endpoints, creating the ipvlan link, configuring gateway/static-route behavior by mode, naming the container interface, and persisting the joined source name.

Important APIs and functions: `Join` starts an OpenTelemetry span, creates a unique source interface name, calls `createIPVlan`, stores `ep.srcName`, handles L3/L3S default connected routes and L2 gateway assignment/force-gateway semantics, disables gateway service, sets interface names with optional user interface name, and persists the endpoint. `Leave` is a no-op. `getSubnetForIP` finds matching same-mask subnets.

Control flow: mode-specific routing is skipped for internal networks. L3/L3S use connected default routes and disable gateway service; L2 chooses explicit gateways from IPAM or forces gateway flags if no gateway exists. The endpoint source name update is noted as not locked.

State and persistence: creates a Linux ipvlan link and records its name in the endpoint datastore. Updates `JoinInfo` with routes, gateway flags, and interface naming.

Dependencies and integration points: depends on `netutils.GenerateIfaceName`, `ns.NlHandle`, `driverapi.JoinInfo`, `netlabel.GetIfname`, libnetwork route types, and OpenTelemetry.

Risks: source-name mutation is not protected by the endpoint/network lock. If errors occur after link creation, cleanup depends on higher-level rollback paths. Gateway parsing assumes IPAM gateway strings are CIDR strings.

Test signals: no direct join tests in this subset; setup tests cover mode/flag conversion used by link creation.
