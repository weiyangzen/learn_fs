# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Makefile

## Purpose
Routes top-level Fungible network driver build objects into the core and Ethernet subdirectories according to Kconfig symbols.

## Important APIs, Types, And Functions
Build entries are `obj-$(CONFIG_FUN_CORE) += funcore/` and `obj-$(CONFIG_FUN_ETH) += funeth/`.

## Control Flow
During kbuild, enabling `CONFIG_FUN_CORE` descends into `funcore/`; enabling `CONFIG_FUN_ETH` descends into `funeth/`. The latter also selects the former in Kconfig, so both usually build for Ethernet support.

## State And Persistence
Build metadata only; no runtime state.

## Dependencies And Integration Points
Depends on the sibling subdirectory Makefiles to define actual module objects. It integrates with the kernel's recursive `obj-y/obj-m` build mechanism.

## Risks
Misaligned Kconfig and Makefile symbols can skip required modules. Current mapping is simple, but `FUN_ETH` relies on `FUN_CORE` selection for linkable exported core symbols.

## Test Signals
Build `CONFIG_FUN_CORE=m`, `CONFIG_FUN_ETH=m`, and built-in variants. Confirm `funcore.o` and `funeth.o` are emitted with expected module dependencies.
