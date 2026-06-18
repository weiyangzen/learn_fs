# sources/cloud-native/moby/integration/internal/network/ops.go

Purpose: functional options for constructing `client.NetworkCreateOptions` in integration tests.

Important APIs and helpers: `WithDriver`, `WithIPv4`, `WithIPv6`, `WithIPv4Disabled`, `WithIPv6Disabled`, `WithInternal`, `WithConfigOnly`, `WithConfigFrom`, `WithAttachable`, `WithScope`, `WithMacvlan`, `WithMacvlanPassthru`, `WithIPvlan`, `WithOption`, `WithIPAM`, `WithIPAMRange`, and `WithIPAMConfig`.

Control flow: each option mutates create options by setting flags, driver names, options map entries, or IPAM config. `WithIPAMRange` parses subnet/iprange/gateway strings into `netip` values and delegates to `WithIPAMConfig`.

State and persistence: no direct state; options shape subsequent network creation and can cause daemon network objects to persist if used by create helpers.

Dependencies and integration: depends on Moby network API types, `netip`, and client network create options. It integrates with `network.Create` and tests for bridge/macvlan/ipvlan/IPAM behavior.

Risks: parsing helpers use `MustParse`, so invalid input panics. Options that set `Options` maps can overwrite previous map values if not careful, especially `WithMacvlan`.

Test signals: helper-only; ensures tests build network create requests consistently.
