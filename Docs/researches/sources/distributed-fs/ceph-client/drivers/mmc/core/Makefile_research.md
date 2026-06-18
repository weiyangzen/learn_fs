# sources/distributed-fs/ceph-client/drivers/mmc/core/Makefile

## Purpose
Defines MMC core object composition and optional modules for Kbuild.

## Important APIs, Types, And Functions
- `mmc_core-y` aggregates core, bus, host, protocol, UHS-II, slot GPIO, and regulator objects.
- Conditional additions include `pwrseq.o`, `debugfs.o`, and `crypto.o`.
- `mmc_block-objs := block.o queue.o` composes the block module.

## Control Flow
Kbuild links selected objects into `mmc_core.o`, `mmc_block.o`, pwrseq helpers, `mmc_test`, and `sdio_uart` according to Kconfig symbols.

## State And Persistence
Build composition only; no runtime state.

## Dependencies And Integration Points
Connects all core MMC implementation files, block queueing, pwrseq, debugfs, test, UART, and crypto support.

## Risks And Edge Cases
Object omissions cause unresolved symbols or missing runtime features. `block.o` and `queue.o` must stay API-compatible.

## Test Signals
Kbuild/link success under relevant configs and expected module/object output from build logs or `modinfo`.
