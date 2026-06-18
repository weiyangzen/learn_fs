<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux_test.go

## Purpose
Tests Linux bridge device setup helpers against kernel netlink behavior in isolated namespaces.

## Important APIs, Types, And Functions
Tests include `TestSetupNewBridge`, `TestSetupNewNonDefaultBridge`, `TestSetupDeviceUp`, `TestGenerateRandomMAC`, `TestMTUBiggerThan1500`, and `TestMTUBiggerThan64K`.

## Control Flow
Each netlink test creates an `nlwrap.Handle`, constructs a `networkConfiguration` and `bridgeInterface`, calls setup helpers, then checks link existence, link flags, error types/messages, or MTU syscall errors.

## State And Persistence
State is temporary namespace-local bridge devices and link attributes. Tests clean up by namespace teardown.

## Dependencies And Integration Points
Uses `netnsutils`, `nlwrap`, `netutils`, `syscall`, and `gotest.tools`. It directly validates `setup_device_linux.go`.

## Risks And Edge Cases
Requires netlink privileges. MTU behavior references specific kernel bridge limits, so very old kernels could differ. The random MAC test is probabilistic but the chance of collision is negligible.

## Test Signals
Passing tests signal correct bridge creation semantics, non-default default-bridge rejection as permission denied, link-up refresh, and expected kernel validation for large MTUs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_device_linux_test.go -->
