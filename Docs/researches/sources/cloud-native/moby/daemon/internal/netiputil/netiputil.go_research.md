<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil.go -->
# sources/cloud-native/moby/daemon/internal/netiputil/netiputil.go

Purpose: provides conversion, arithmetic, comparison, and optional parsing helpers around Go `net/netip` values for daemon networking code.

Important APIs and types: `ToIPNet`, `ToPrefix`, `HostID`, `SubnetRange`, `AddrPortFromNet`, `LastAddr`, `PrefixCompare`, `PrefixAfter`, `Unmap`, `ParseCIDR`, `MaybeParse`, `MaybeParseAddr`, `MaybeParsePrefix`, and `MaybeParseCIDR`.

Control flow: conversions bridge `net.IPNet` and `netip.Prefix`; arithmetic delegates bit operations to `daemon/libnetwork/ipbits`. `PrefixAfter` computes the next prefix after a previous allocation and returns invalid prefix on address overflow. `Unmap` reproduces Docker's historical IPv4-mapped IPv6 CIDR semantics by unmapping the address and truncating mask length. `MaybeParse` decorates parse functions so empty input returns zero value without error.

State and persistence: pure functions; no state.

Dependencies and integration: used by networking and option parsing paths that are migrating to `netip`.

Risks: `HostID` documents undefined behavior when bits exceed address bit length. `SubnetRange` uses shifts derived from prefix size and assumes valid inputs. `Unmap` intentionally preserves historical quirks that may surprise new callers.

Test signals: `netiputil_test.go` covers last address, next prefix, unmap invalid zero, CIDR parsing compatibility, and optional parse behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil.go -->
