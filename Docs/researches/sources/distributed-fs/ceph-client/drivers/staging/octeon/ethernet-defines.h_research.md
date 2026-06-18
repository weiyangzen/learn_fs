# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-defines.h

## Purpose
Shared compile-time tuning constants and FAU/FPA indices for the Octeon Ethernet driver.

## Important APIs, Types, And Functions
Defines `REUSE_SKBUFFS_WITHOUT_FREE`, `USE_ASYNC_IOBDMA`, `MAX_OUT_QUEUE_DEPTH`, FAU counter locations, and `TOTAL_NUMBER_OF_PORTS`.

## Control Flow
Included by RX/TX/core files to select fast paths, queue cleanup thresholds, and array sizing. `REUSE_SKBUFFS_WITHOUT_FREE` is disabled when netfilter is enabled; async IOBDMA depends on CVMSEG size.

## State And Persistence
No runtime state. Values shape allocation sizes, buffer reuse behavior, and hardware counter addresses.

## Dependencies And Integration Points
Depends on Octeon CVMX constants from architecture headers or `octeon-stubs.h`.

## Risks
Buffer reuse is explicitly performance-oriented and can expose networking-stack lifetime bugs if an skb is reused without full cleanup. FAU address arithmetic must not collide with other registers.

## Test Signals
Compile with and without `CONFIG_NETFILTER`, with CVMSEG enabled/disabled, verify `TOTAL_NUMBER_OF_PORTS` matches `cvm_oct_device[]`, and stress TX queue cleanup depth.
