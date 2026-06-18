<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil_test.go -->
# sources/cloud-native/moby/daemon/internal/netiputil/netiputil_test.go

Purpose: validates key `netiputil` address arithmetic and parsing compatibility.

Important APIs and types: `TestLastAddr`, `TestPrefixAfter`, `TestUnmap`, `TestParseCIDR`, and `TestMaybeParse`.

Control flow: table tests verify IPv4/IPv6 broadcast-like last addresses and prefix sequencing, including overflow. CIDR parsing compares against legacy `net.ParseCIDR` behavior after setting `net.IP` to the parsed IP. Optional parsing checks empty, invalid, and valid inputs.

State and persistence: none.

Dependencies and integration: uses `gotest.tools/assert` and Go `net/netip`.

Risks: tests do not cover `ToIPNet`, `ToPrefix`, `HostID`, `SubnetRange`, or `AddrPortFromNet`.

Test signals: good coverage of the most contract-sensitive address math and historical IPv4-mapped CIDR behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netiputil/netiputil_test.go -->
