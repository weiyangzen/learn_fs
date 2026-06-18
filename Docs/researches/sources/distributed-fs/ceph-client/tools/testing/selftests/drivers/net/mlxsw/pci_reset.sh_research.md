# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/pci_reset.sh

## Purpose

PCI reset validation for mlxsw ports and devlink device behavior.

## Important APIs, Types, and Functions

Defines a single `pci_reset_test` using one netif plus `devlink_lib.sh`. The file checks supported reset methods and verifies that the port ifindex changes after issuing the reset.

## Control Flow

The test records the initial port identity/ifindex, inspects reset method exposure, triggers the supported PCI reset path, waits for the device/port to reappear, and compares the resulting ifindex with the original. A changed ifindex indicates the netdevice was recreated as expected.

## State and Persistence Behavior

State includes transient PCI/device reset state and recreated netdevice identity. It may disrupt live networking on the tested adapter and relies on kselftest cleanup/wait helpers after reset.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

This is disruptive and must run only on a dedicated test device. Reset support depends on PCI/firmware/kernel capabilities. If udev or device recreation is slow, the ifindex check can race.

## Test Signals

Signals are expected reset method filtering, successful reset command, and observed ifindex change after the reset.
