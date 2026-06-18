# Research: sources/cloud-native/moby/daemon/libnetwork/firewall_linux_test.go

Purpose: integration-tests `DOCKER-USER` chain creation and ordering under Linux iptables. Important tests/helpers are `TestUserChain`, `getRules`, `resetIptables`, and `versionLt`.

Control flow: the test creates isolated network namespace context, resets iptables, starts a controller with iptables enabled or disabled, optionally appends existing `DROP` rules to `FORWARD`, calls `setupUserChains`, and compares chain state to golden files for IPv4/IPv6. It adapts expected "chain missing" error text for older iptables-nft versions. It skips the iptables assertions if nftables backend is enabled.

State/dependencies: tests manipulate real iptables state in a test netns and depend on golden files. Dependencies include bridge config, iptables helpers, nftables enabled state, netns utilities, and `icmd`. Risks covered include preserving user rules, correct jump insertion, no Docker chain creation when iptables disabled, and version-specific error handling. Gaps include firewalld reload service restoration and explicit nftables backend selection errors.
