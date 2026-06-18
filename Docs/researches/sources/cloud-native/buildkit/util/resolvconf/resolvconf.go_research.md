<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf.go -->
# sources/cloud-native/buildkit/util/resolvconf/resolvconf.go

Purpose: parses, modifies, transforms, and regenerates container `resolv.conf` content for host, legacy network, and internal DNS resolver scenarios.

Important APIs and types: `ResolvConf`, `ExtDNSEntry`, `Load`, `Parse`, `SetHeader`, `NameServers`, `OverrideNameServers`, `Search`, `OverrideSearch`, `Options`, `Option`, `OverrideOptions`, `AddOption`, `TransformForLegacyNw`, `TransformForIntNS`, and `Generate`.

Control flow: parsing scans recognized directives, keeping valid nameservers, last search/domain directive, accumulated options, unknown directives, invalid nameserver metadata, and ndots origin. Legacy transform removes host loopback and IPv6 nameservers as needed unless nameservers were overridden, then adds Google fallback resolvers if empty. Internal resolver transform stashes existing nameservers as external DNS entries, marks host-loopback ownership based on overrides, replaces visible nameserver with internalNS, and ensures required options exist while replacing invalid `ndots` values.

State and persistence: all state is held in `ResolvConf` fields and metadata until `Generate` writes bytes. Metadata controls generated debug comments, override tracking, transform labels, invalid nameserver lists, and external server comments.

Dependencies and integration: uses `net/netip`, BuildKit errdefs and logging. Integrated by networking code that needs container DNS config and by internal resolver setup that consumes returned external DNS entries.

Risks: comments can expose source path and external resolver addresses. `OverrideSearch` filters `"."`, but other search validation is minimal. `TransformForLegacyNw` does nothing when nameservers are overridden, even if loopback addresses are unusable in a target network. Internal resolver transform warns but does not inject fallback external servers when no external entries exist.

Test signals: `resolvconf_test.go` thoroughly covers option lookup, overrides, legacy transforms, internal resolver transforms, invalid ndots replacement, load/path behavior, invalid nameserver reporting, headers, unknown directives, and generation benchmark.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolvconf/resolvconf.go -->
