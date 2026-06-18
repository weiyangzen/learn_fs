# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/Makefile

## Purpose
Defines the Fungible core service module build composition.

## Important APIs, Types, And Functions
`obj-$(CONFIG_FUN_CORE) += funcore.o` builds the module, and `funcore-y := fun_dev.o fun_queue.o` links PCI/admin-device services with queue/ring services.

## Control Flow
kbuild compiles `fun_dev.c` and `fun_queue.c` into one `funcore.o` object when `CONFIG_FUN_CORE` is enabled.

## State And Persistence
Build metadata only. Runtime state is in the compiled sources.

## Dependencies And Integration Points
The resulting module exports symbols consumed by `funeth`, including device enable/disable, admin command submission, queue allocation/creation, IRQ reservation, and service scheduling.

## Risks
Adding a core source file without updating `funcore-y` would silently omit it. Symbol export/license compatibility matters because the module is dual BSD/GPL while several exports are GPL-only.

## Test Signals
Build coverage should confirm `funcore.o` includes both source objects and that `modpost` resolves exported symbols used by `funeth`.
