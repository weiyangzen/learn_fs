# sources/distributed-fs/ceph-client/include/linux/firmware/meson/meson_sm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/meson/meson_sm.h` declares the Amlogic Meson secure monitor firmware call interface. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

It defines command indexes for efuse read/write, chip ID, and A1 power-controller set/get. APIs include `meson_sm_call`, `meson_sm_call_write`, `meson_sm_call_read`, and `meson_sm_get`.

## Control Flow

Clients obtain a firmware handle from a device-tree firmware node, then invoke simple calls or buffer read/write calls with a command index and five 32-bit arguments.

## State and Persistence Behavior

The header owns no state. Secure monitor firmware owns command execution and persistent effects such as efuse writes or power-controller settings.

## Dependencies and Integration Points

It integrates with device tree firmware nodes, ARM secure monitor calls, Meson efuse/chip ID/power drivers, and platform firmware infrastructure.

## Risks and Edge Cases

Efuse write operations can be irreversible. Buffer size and command index validation are important. Secure monitor availability depends on platform firmware.

## Test Signals

Meson secure monitor probe tests, chip ID read tests, efuse read/write policy tests, power-controller call tests, and firmware-node lookup failure tests.
