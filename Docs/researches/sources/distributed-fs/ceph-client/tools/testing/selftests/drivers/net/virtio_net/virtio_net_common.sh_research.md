# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/virtio_net/virtio_net_common.sh

## Purpose
Common shell library for virtio_net driver tests. It defines endpoint discovery assumptions, addressing constants, and helpers for virtio device rebinding and debugfs feature filter manipulation.

## Important APIs, Types, And Functions
Exports forwarding-library variables `REQUIRE_MZ=no`, `NETIF_CREATE=no`, `NETIF_FIND_DRIVER=virtio_net`, and `NUM_NETIFS=2`. Defines IPv4/IPv6 endpoint addresses and `VIRTIO_NET_F_MAC=5`. Helper functions are `virtio_device_get()`, `virtio_device_rebind()`, `virtio_debugfs_get()`, `check_virtio_debugfs()`, `virtio_feature_present()`, `virtio_filter_features_clear()`, and `virtio_filter_feature_add()`.

## Control Flow
Consumers source this file before forwarding lib use. Device helpers resolve `/sys/class/net/$dev/device`, unbind/bind the virtio device, and read/write `/sys/kernel/debug/virtio/$device` feature files.

## State And Persistence
Feature filters persist in debugfs until cleared or device state changes. Rebind changes live device state; helper does not wait for link recreation itself.

## Dependencies And Integration Points
Requires sysfs, virtio bus driver paths, virtio debugfs, and forwarding selftest interface discovery. It is directly used by `basic_features.sh`.

## Risks
Backtick command substitution and unquoted sysfs paths assume simple device names. Rebinding can drop interface state. Missing debugfs causes a kselftest skip from `check_virtio_debugfs()`.

## Test Signals
A valid debugfs directory with `device_features`, `filter_feature_add`, `filter_feature_del`, `filter_features`, and `filter_features_clear` indicates the tests can run.
