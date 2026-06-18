# Research: sources/cloud-native/moby/daemon/libnetwork/firewall_linux.go

Purpose: selects Linux firewall backend setup and restores libnetwork-managed firewall state after reloads. Important APIs are `Controller.selectFirewallBackend`, `setupPlatformFirewall`, `setupUserChains`, `setupUserChain`, `handleFirewalldReload`, and `handleFirewallReloadService`; constant `userChain` is `DOCKER-USER`.

Control flow: backend selection honors explicit `iptables`, requires successful `nftables.Enable` for explicit `nftables`, and otherwise leaves defaults unchanged. Platform setup creates user chains and registers firewalld reload handlers. `setupUserChains` skips when nftables is enabled, otherwise ensures `DOCKER-USER` exists and `FORWARD` jumps to it for every enabled iptables version, both at setup and reload. Firewalld reload handling snapshots ingress service bindings and restores ingress ports via load-balancer endpoint sandbox/gateway information.

State/dependencies: firewall state lives in iptables/nftables and service binding maps guarded by controller/service locks. Dependencies include `iptables`, internal `nftables`, ingress service/load-balancer helpers, and logging. Risks include reload races, partial IPv4/IPv6 setup errors, and nftables lacking an exact `DOCKER-USER` equivalent. Tests cover iptables user-chain ordering and absence when iptables is disabled.
