# Research: sources/cloud-native/moby/daemon/libnetwork/firewall_others.go

Purpose: provides non-Linux stubs for platform firewall setup. Important APIs are `Controller.selectFirewallBackend` and `Controller.setupPlatformFirewall`.

Control flow: `selectFirewallBackend` always returns nil and `setupPlatformFirewall` does nothing. This keeps shared controller initialization portable while Linux-specific iptables/nftables logic is excluded by build tags.

State/dependencies: there is no state and no external dependency. Integration point is controller startup on Windows or other non-Linux platforms, where firewall behavior is delegated to platform drivers/HNS or omitted. Risk is that config values such as an explicit nftables backend are silently ignored on non-Linux builds, which may be acceptable because those backends are Linux-specific. Test signal is compile-time; no local unit test is needed for these stubs.
