# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hwtstamp_config.c

## Purpose

This small C utility gets or sets a network interface hardware timestamping configuration through `SIOCGHWTSTAMP` and `SIOCSHWTSTAMP`. It is a kselftest helper for exercising the kernel hwtstamp ioctl ABI.

## Important APIs, Types, and Functions

Important functions are `lookup_value`, `lookup_name`, `list_names`, `usage`, and `main`. It uses `struct ifreq`, `struct hwtstamp_config`, `socket(AF_INET, SOCK_DGRAM, 0)`, and `ioctl` with `SIOCGHWTSTAMP` or `SIOCSHWTSTAMP`. It maps names for `HWTSTAMP_TX_OFF`, `HWTSTAMP_TX_ON`, `HWTSTAMP_TX_ONESTEP_SYNC`, and the supported `HWTSTAMP_FILTER_*` values.

## Control Flow

`main` validates either `if_name` alone or `if_name tx_type rx_filter`, parses names case-insensitively for set mode, opens a datagram socket, fills `ifr_name` and `ifr_data`, performs the ioctl, then prints flags, tx type, and rx filter using symbolic names when known. Invalid usage returns 2, socket/ioctl failures return 1, success returns 0.

## State and Persistence Behavior

The program has only stack-local state. In set mode it requests persistent kernel/device timestamp configuration for the named interface until changed by another ioctl or device reset. In get mode it only reads kernel state.

## Dependencies and Integration Points

It depends on Linux networking headers, `kselftest.h` for `ARRAY_SIZE`, and an interface/driver implementing the hwtstamp ioctl. It integrates with userspace tests that need a simple readable way to configure or inspect hardware timestamping.

## Risks and Edge Cases

Interface names at or above `IFNAMSIZ` are rejected. Unknown numeric ioctl-returned values are printed as integers. The program does not close the socket explicitly before exit, which is harmless. Some drivers may coerce requested filters or reject unsupported modes with errno.

## Test Signals

Signals are exit code 0 plus printed `flags`, `tx_type`, and `rx_filter` for supported get/set operations; exit code 2 for invalid names or arguments; and ioctl errno output for unsupported devices or permissions.
