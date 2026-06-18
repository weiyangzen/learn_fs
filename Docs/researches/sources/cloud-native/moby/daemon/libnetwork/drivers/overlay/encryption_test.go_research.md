# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_test.go

Purpose: Verifies `buildSPI` remains compatible with the legacy FNV-based SPI derivation across IPv4, IPv4-mapped IPv6, and IPv6 inputs.

Important APIs and functions: `legacyBuildSPI` hashes source IP, key tag, and destination IP using `fnv.New32a`. `TestBuildSPI` compares `buildSPI` against legacy results for multiple address combinations and also checks unmapped forms.

Control flow: table-driven assertions build expected values with `net.ParseIP` and actual values with `netip.Addr`.

State and persistence: stateless.

Dependencies and integration points: protects compatibility for XFRM SA identifiers in `encryption.go`.

Risks: only covers SPI derivation, not XFRM programming, firewall rules, or key rotation.

Test signals: strong compatibility signal for a low-level value that must remain stable across daemon versions.
