<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_bridgenetfiltering.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_bridgenetfiltering.go

## Purpose
Enables bridge netfilter sysctls when packet forwarding is active so bridged packets traverse iptables/ip6tables filtering.

## Important APIs, Types, And Functions
`setupIPv4BridgeNetFiltering` checks global IPv4 forwarding and enables `/proc/sys/net/bridge/bridge-nf-call-iptables`. `setupIPv6BridgeNetFiltering` checks per-bridge IPv6 forwarding and enables `/proc/sys/net/bridge/bridge-nf-call-ip6tables`. Helpers include `loadBridgeNetFilterModule`, `enableBridgeNetFiltering`, `getKernelBoolParam`, and `isRunningInContainer`.

## Control Flow
If forwarding is disabled, setup is a no-op. If enabled, the code loads `br_netfilter`, reads the target sysctl, and writes `1` when needed. Missing bridge sysctls inside a Docker container are logged and ignored; other failures can be ignored via `DOCKER_IGNORE_BR_NETFILTER_ERROR=1`.

## State And Persistence
State is kernel module/sysctl state under `/proc/sys`. Changes persist until the host sysctl is changed or rebooted according to system policy.

## Dependencies And Integration Points
Uses `modprobe.LoadModules`, `os`, `syscall`, and logging. Called during bridge setup when filtering behavior is required for ICC restriction or running without userland proxy.

## Risks And Edge Cases
Host kernel support, containerized daemon environments, and permissions affect behavior. Ignoring errors can leave host traffic less restricted than expected. IPv6 requires a bridge name to check the per-interface forwarding sysctl.

## Test Signals
Indirectly covered by bridge setup tests; targeted tests would mock procfs/module availability and environment variables.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_bridgenetfiltering.go -->
