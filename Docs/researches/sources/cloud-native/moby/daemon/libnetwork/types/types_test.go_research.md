## sources/cloud-native/moby/daemon/libnetwork/types/types_test.go

Purpose: Unit tests for libnetwork common type helpers, especially error wrappers and IP/mask utilities.

Important tests: `TestErrorConstructors` verifies each public error constructor returns the expected text and containerd errdefs classification, and checks `InternalError`/`MaskableError` marker interfaces. `TestCompareIPMask` validates internal start indexes for IPv4, IPv4-in-IPv6, IPv6, and incompatible masks. `TestGetHostPartIP` and `TestGetBroadcastIP` exercise bitwise host/broadcast extraction without changing representation. `TestParseCIDR` confirms `ParseCIDR` preserves the parsed IP as supplied rather than canonicalizing to the network address.

Control flow and state: Tests are table driven and compare both success values and expected error substrings. They intentionally use mixed representations such as `net.IPv4(...)[12:]` and 16-byte masks to protect compatibility behavior.

Dependencies and integration points: Uses `gotest.tools` assertions and containerd errdefs predicates. It validates helpers used by route, address, and port-mapping code in libnetwork.

Risks covered: Prevents silent regressions in IPv4/IPv6 compatibility, accidental mutation/canonicalization expectations, and error typing. It does not cover `PortBinding.String`, `HostAddr`, `Copy`, or `StaticRoute.Copy`, leaving those utilities with weaker test signals.
