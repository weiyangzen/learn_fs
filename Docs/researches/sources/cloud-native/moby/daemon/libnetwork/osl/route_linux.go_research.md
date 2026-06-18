## sources/cloud-native/moby/daemon/libnetwork/osl/route_linux.go

Purpose: Linux/FreeBSD route and gateway management for OSL namespaces.

Important APIs/types/functions: accessors `Gateway`, `GatewayIPv6`, `StaticRoutes`; mutators `SetGateway`, `UnsetGateway`, `SetGatewayIPv6`, `UnsetGatewayIPv6`, `AddStaticRoute`, `RemoveStaticRoute`, `SetDefaultRouteIPv4`, `SetDefaultRouteIPv6`, `UnsetDefaultRouteIPv4`, and `UnsetDefaultRouteIPv6`; helpers `programGateway`, `programRoute`, `removeRoute`, `setDefaultRoute`, and `unsetDefaultRoute`.

Control flow: gateway programming first resolves a direct route to the gateway/next-hop through `RouteGet`, then adds or deletes a universe-scope route with the resolved link index. Connected default route methods look up an `Interface` by source name, find an unspecified route matching IPv4 or IPv6, resolve the link by destination name, and add/delete link-scope default route.

State and persistence behavior: mutates namespace routing tables through netlink and mirrors selected state in `Namespace` fields (`gw`, `gwv6`, `staticRoutes`, `defRoute4SrcName`, `defRoute6SrcName`). Accessors return copies for static routes but raw `net.IP` values for gateways.

Dependencies and integration points: depends on `Namespace.nlHandle`, OSL interface metadata, libnetwork `types.StaticRoute`, and vishvananda/netlink. Interface setup uses routes attached to `Interface`; restore paths repopulate route state.

Risks: route programming depends on `RouteGet` returning usable link indexes. `RemoveStaticRoute` removes by pointer identity, not semantic route equality. Gateway accessors return mutable `net.IP` slices, so callers could mutate stored values. FreeBSD build tag shares this file despite netlink dependency, implying package build context must provide compatible files or tags.

Test signals: no direct route tests in this subset. Integration tests should cover gateway add/remove, default connected routes, static route pointer removal, and IPv6 route behavior.
