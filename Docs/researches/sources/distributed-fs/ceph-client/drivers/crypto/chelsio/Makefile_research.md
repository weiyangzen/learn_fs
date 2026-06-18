# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Makefile

## Purpose

`drivers/crypto/chelsio/Makefile` wires the Chelsio crypto driver into Kbuild. It adds the cxgb4 network-driver include path and builds the `chcr` object when `CONFIG_CRYPTO_DEV_CHELSIO` is enabled.

## Important APIs, Types, And Functions

`ccflags-y` adds `-I $(srctree)/drivers/net/ethernet/chelsio/cxgb4`, allowing Chelsio crypto code to include cxgb4 headers. `obj-$(CONFIG_CRYPTO_DEV_CHELSIO) += chcr.o` registers the module/built-in object. `chcr-objs := chcr_core.o chcr_algo.o` composes the final object from core and algorithm implementation files.

## Control Flow

Kbuild expands `obj-y` or `obj-m` depending on the Kconfig symbol. It compiles `chcr_core.o` and `chcr_algo.o`, links them into `chcr.o`, and either links that into the kernel or emits `chcr.ko`.

## State And Persistence Behavior

There is no runtime state. Build outputs depend on configuration and source timestamps.

## Dependencies And Integration Points

The include path is the integration bridge to the Chelsio T4/T6 network driver. The object list matches the driver module named in Kconfig help.

## Risks And Edge Cases

The Makefile assumes cxgb4 headers are available at the srctree path. Adding implementation files requires updating `chcr-objs`; otherwise code may compile in isolation but not be linked. Include-path coupling can break if the network driver directory is reorganized.

## Test Signals

`make M=drivers/crypto/chelsio` or a full kernel build with `CONFIG_CRYPTO_DEV_CHELSIO=m/y` should produce `chcr.o`/`chcr.ko` from both object files. Header dependency errors usually indicate cxgb4 include path drift.
