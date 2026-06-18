<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netipstringer/stringer.go -->
# sources/cloud-native/moby/daemon/internal/netipstringer/stringer.go

Purpose: provides safe string conversions for `netip` values that return an empty string for invalid addresses/prefixes.

Important APIs and types: `Addr(netip.Addr) string` and `Prefix(netip.Prefix) string`.

Control flow: each function checks `IsValid` and returns `""` for invalid input; otherwise delegates to `String`.

State and persistence: none.

Dependencies and integration: useful for API/config output paths where invalid zero values should serialize as empty fields.

Risks: empty string can conflate invalid values with intentional empty values in callers.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/netipstringer/stringer.go -->
