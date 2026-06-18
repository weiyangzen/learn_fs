<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux_test.go

## Purpose
Validates bridge interface helper behavior in isolated Linux network namespaces.

## Important APIs, Types, And Functions
Helpers `cidrToIPNet`, `addAddr`, and `prepTestBridge` create test networks, assign addresses, and create bridge devices. Tests cover `newInterface`, `bridgeInterface.addresses`, and `programIPv6Addresses`.

## Control Flow
Each test uses `netnsutils.SetupTestOSContext` where kernel state is touched. The IPv6 programming test repeatedly mutates `networkConfiguration.AddressIPv6`, calls `programIPv6Addresses`, lists bridge addresses, sorts actual/expected strings, and checks cached bridge/gateway fields.

## State And Persistence
All state is temporary kernel netlink state in the test namespace. The tests specifically observe persistence of the kernel link-local address and multicast autoconf address across daemon-driven address reconciliation.

## Dependencies And Integration Points
Uses `nlwrap`, `netlink`, `unix.IFA_F_MCAUTOJOIN`, and `gotest.tools` assertions. It is the focused test companion for `interface_linux.go` and `setup_device_linux.go`.

## Risks And Edge Cases
Requires netlink and namespace privileges. The prefix-shrink case documents that Linux may keep the old displayed prefix even though the bridge driver updates its cached config. Link-local handling is subtle because nonstandard link-local prefixes may come from IPAM and should be removed.

## Test Signals
Passing tests signal default bridge naming, safe behavior with missing links, accurate family-specific address listing, configured IPv6 insertion, standard link-local preservation, nonstandard link-local cleanup, and multicast preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/interface_linux_test.go -->
