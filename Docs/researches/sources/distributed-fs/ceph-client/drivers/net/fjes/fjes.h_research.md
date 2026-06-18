# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes.h

## Purpose
`fjes.h` defines the top-level adapter state and cross-file interfaces for the Fujitsu Extended Socket network driver. It connects platform/netdev state, NAPI, statistics, workqueues, debugfs, and the lower `struct fjes_hw` hardware/shared-memory layer.

## Important APIs and Types
The central type is `struct fjes_adapter`, containing `net_device`, `platform_device`, `napi_struct`, `rtnl_link_stats64`, TX retry timestamps/counters, RX polling timestamps, force-close/reset flags, IRQ registration state, TX/RX and control workqueues, work items, delayed interrupt-watch work, unshare bitmask, embedded `struct fjes_hw`, and optional debugfs dentries. Constants include `FJES_ACPI_SYMBOL`, `FJES_MAX_QUEUES`, TX retry/stall timeouts, open-zone wait time, and IRQ-watch delay. Declared functions include `fjes_set_ethtool_ops()` and debugfs init/exit hooks with no-op inline stubs when debugfs is disabled.

## Control Flow
The header is consumed by `fjes_main.c`, `fjes_hw.c`, `fjes_ethtool.c`, and `fjes_debugfs.c`. `fjes_probe()` allocates a netdev with `struct fjes_adapter` as private data, fills the fields declared here, initializes the work items, embeds hardware state, and registers the netdev. Open/close, interrupt handlers, NAPI, and workqueue callbacks mutate the fields defined here.

## State, Dependencies, and Integration
This header depends on Linux ACPI/netdevice infrastructure and `fjes_hw.h`. It publishes external driver name/version/support-MTU symbols. It is the integration point between the upper Linux network interface and lower endpoint shared-memory protocol.

## Risks and Test Signals
Risks are lifetime ordering of workqueues, NAPI, IRQ registration, and hardware cleanup fields. Because many booleans and bitmasks coordinate asynchronous close/reset/unshare behavior, tests should cover probe failure unwinds, open/close races, forced close scheduling, debugfs enabled/disabled builds, and TX stall/retry state transitions.
