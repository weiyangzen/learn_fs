# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.h

## Purpose
Declares PTP/TAI register constants and the build-time interface for enabling or stubbing mv88e6xxx PTP support.

## Important APIs, Types, and Functions
Defines TAI config, clock period, event status, event time, global time, and 6165 per-port timestamp status offsets. Under `CONFIG_NET_DSA_MV88E6XXX_PTP`, it declares `mv88e6xxx_ptp_setup`, `mv88e6xxx_ptp_free`, `ptp_to_chip`, and extern PTP ops descriptors. Without PTP config, setup/free become no-op inline functions and the ops descriptors are empty static constants.

## Control Flow and State
There is no runtime control flow except compile-time selection. The constants describe persistent hardware state used by `ptp.c` and hwtstamp logic: TAI event capture configuration, valid/error bits, raw timestamp words, and per-port arrival/departure status blocks.

## Dependencies and Integration Points
Includes `chip.h` and exposes symbols consumed by chip descriptors and the main driver setup/teardown path. It links PTP support to hwtstamp and AVB accessors while allowing the driver to compile with PTP disabled.

## Risks and Test Signals
Risks include config-stub divergence from the enabled implementation and incorrect register offsets affecting timestamp capture. Test signals are allmodconfig and no-PTP builds, PHC registration on enabled builds, and hwtstamp tests that validate arrival/departure status offsets for 6165/6352/6390 families.
