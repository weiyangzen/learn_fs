
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.h

## Purpose

This header declares the HIBMCGE debugfs lifecycle functions.

## Important APIs, Types, and Functions

It declares `hbg_debugfs_register()`, `hbg_debugfs_unregister()`, and `hbg_debugfs_init()`.

## Control Flow

There is no runtime control flow in the header. `hbg_main.c` calls these functions during module and device initialization/exit.

## State and Persistence

No state is defined here.

## Dependencies and Integration Points

The declarations integrate `hbg_debugfs.c` with the main driver lifecycle.

## Risks and Edge Cases

Prototype drift would break module initialization or leave debugfs resources unmanaged.

## Test Signals

Build coverage and debugfs creation/removal tests validate the header contract.
