<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/host_gateway_opts.go -->
# sources/cloud-native/moby/daemon/internal/opts/host_gateway_opts.go

Purpose: validates daemon host-gateway IP configuration.

Important APIs and types: `ValidateHostGatewayIPs([]netip.Addr) error`.

Control flow: iterates addresses and allows at most one IPv4 and at most one non-IPv4 address, returning explicit errors for duplicates.

State and persistence: none.

Dependencies and integration: used by daemon option validation for `host-gateway-ip`-style settings.

Risks: invalid `netip.Addr{}` is treated as non-IPv4 and can count as IPv6-like unless callers validate parsing beforehand.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/host_gateway_opts.go -->
