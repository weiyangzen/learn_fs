# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/basic_features.sh

## Purpose
Validates a two-interface virtio_net endpoint setup, including basic IPv4/IPv6 ping and behavior when feature bit `VIRTIO_NET_F_MAC` is filtered via virtio debugfs.

## Important APIs, Types, And Functions
Uses `virtio_device_rebind()`, `virtio_feature_present()`, `virtio_filter_feature_add()`, `virtio_filter_features_clear()`, and `check_virtio_debugfs()` from `virtio_net_common.sh`; uses forwarding helpers `simple_if_init`, `vrf_prepare`, `ping_test`, `ping_do`, `check_driver`, `wait_for_dev`, and kselftest logging. Local functions include `h1_create/destroy`, `h2_create/destroy`, `initial_ping_test()`, `f_mac_test()`, `setup_prepare()`, `setup_cleanup()`, and `cleanup()`.

## Control Flow
The script identifies two virtio_net interfaces from forwarding-library `NETIFS`, validates drivers/debugfs, installs cleanup trap, prepares interfaces, and runs tests. `initial_ping_test()` resets and pings. `f_mac_test()` checks the MAC feature exists, verifies permanent address assignment with the feature present, filters the feature on both devices, rebinds, verifies permanent address assignment is no longer reported, and confirms ping still works.

## State And Persistence
It changes device MTU/address state and virtio debugfs feature filters, then clears filters and rebinds devices during cleanup. No files are persisted.

## Dependencies And Integration Points
Requires a back-to-back two-virtio-interface topology, virtio debugfs, root, forwarding library, VRF support, and ping reachability.

## Risks
Rebinding real virtio interfaces is disruptive. Debugfs feature filter support must be enabled and mounted. The second `virtio_feature_present` check appears to query `$h1` again while reporting `$h2`, so missing feature on the second device may not be independently detected.

## Test Signals
Signals include successful simple ping, expected `addr_assign_type` changes around `F_MAC` filtering, and ping after feature filtering/rebind.
