## sources/cloud-native/moby/daemon/libnetwork/types/types.go

Purpose: Shared libnetwork type and utility definitions for IP families, encryption keys, QoS, transport ports, port bindings, protocol parsing, IP network manipulation, static routes, interface statistics, and libnetwork error classification.

Important APIs and types: Exposes `IPFamily` constants (`IP`, `IPv4`, `IPv6`), `EncryptionKey`, `QosPolicy`, `TransportPort`, `PortBinding`, `Protocol` constants (`ICMP`, `TCP`, `UDP`, `SCTP`), `RouteType`, `StaticRoute`, `InterfaceStatistics`, `MaskableError`, and `InternalError`. Key functions include `PortBinding.HostAddr`, `Copy`, `Equal`, `String`, `Protocol.String`, `ParseProtocol`, `GetIPNetCopy`, `GetIPNetCanonical`, `CompareIPNet`, `GetHostPartIP`, `GetBroadcastIP`, `ParseCIDR`, and error constructors wrapping `errdefs`.

Control flow and state: Most functions are pure helpers. `PortBinding.String` conditionally formats host/container IPs, IPv6 brackets, host-port ranges, and protocol suffix. IP utilities clone input bytes to avoid mutating caller-owned slices. `compareIPMask` normalizes IPv4-in-IPv6 representations and validates mask/address compatibility before host/broadcast bit operations.

Dependencies and integration points: Uses Go `net`, SCTP address support from `github.com/ishidawataru/sctp`, `slices.Clone`, and Moby `errdefs`. These types feed endpoint, driver, route, and port-mapping code throughout libnetwork.

Risks: `ParseProtocol` returns zero for unknown input, so callers must distinguish unset/invalid. `StaticRoute.Copy` assumes a non-nil receiver. IP/mask compatibility logic is subtle around IPv4-in-IPv6 forms and non-canonical masks.

Test signals: `types_test.go` covers error constructor classification, IP/mask index calculation, host/broadcast extraction across IPv4/IPv6 representations, and CIDR parsing.
