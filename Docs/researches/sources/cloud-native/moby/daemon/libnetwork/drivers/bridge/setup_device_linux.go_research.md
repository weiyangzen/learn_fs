<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux.go

## Purpose
Creates and configures the Linux bridge device: bridge creation, MTU, IPv6 router advertisement sysctl, and link-up state.

## Important APIs, Types, And Functions
`setupDevice` creates a `netlink.Bridge` with a random MAC and enforces default bridge naming rules. `setupMTU` sets MTU. `setupDefaultSysctl` disables IPv6 router advertisements on the bridge when the sysctl exists. `setupDeviceUp` brings the link up and refreshes cached link flags.

## Control Flow
Bridge creation rejects a non-default bridge name when `DefaultBridge` is true, assigns a generated MAC, and calls `LinkAdd`. MTU and sysctl steps are independent. Link-up calls `LinkSetUp`, then attempts `LinkByName` to refresh `bridgeInterface.Link`.

## State And Persistence
State is kernel netlink device state and `/proc/sys/net/ipv6/conf/<bridge>/accept_ra`. The random MAC becomes the bridge hardware address.

## Dependencies And Integration Points
Uses `nlwrap.Handle`, `netlink`, `netutils.GenerateRandomMAC`, `errdefs`, `os`, and logging. Invoked by the bridge setup pipeline and tested in isolated namespaces.

## Risks And Edge Cases
Creating a default bridge with a custom name is forbidden for compatibility. MTU limits are kernel-dependent. Missing IPv6 sysctl is logged as info and ignored, which is appropriate on IPv4-only hosts.

## Test Signals
`setup_device_linux_test.go` validates bridge creation down, rejection of non-default default bridge, link-up, random MAC uniqueness, MTU 9000 success, and MTU 65536 `EINVAL`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux.go -->
