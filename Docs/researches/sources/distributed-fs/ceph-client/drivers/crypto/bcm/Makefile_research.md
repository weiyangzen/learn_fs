# sources/distributed-fs/ceph-client/drivers/crypto/bcm/Makefile

## Purpose

This Kbuild file defines the Broadcom SPU crypto accelerator build. It produces `bcm_crypto_spu.o` when `CONFIG_CRYPTO_DEV_BCM_SPU` is enabled and links the implementation from `util.o`, `spu.o`, `spu2.o`, and `cipher.o`.

## Important APIs, Types, and Functions

The file has no runtime APIs. The central build rule is `obj-$(CONFIG_CRYPTO_DEV_BCM_SPU) := bcm_crypto_spu.o`, and `bcm_crypto_spu-objs := util.o spu.o spu2.o cipher.o` defines the multi-object module composition. Commented `CFLAGS_* := -DDEBUG` lines document optional per-object debug tracing knobs for developers.

## Control Flow

Build-time control is Kconfig driven. With `CONFIG_CRYPTO_DEV_BCM_SPU=y`, the combined object is built into the kernel. With `m`, it becomes a loadable module. Otherwise none of the SPU implementation objects are included.

## State and Persistence Behavior

There is no runtime state. Persistent impact is the selected build artifact and any developer-local Makefile edits to uncomment debug flags.

## Dependencies and Integration Points

The object list ties `cipher.c` to shared helper and hardware generation code in `util.c`, `spu.c`, and `spu2.c`. `cipher.c` relies on symbols and enums from `spu.h`, `spum.h`, and `spu2.h`, so all listed objects are required for a complete driver.

## Risks and Edge Cases

- Enabling debug CFLAGS can expose sensitive crypto material in logs because `cipher.c` contains packet/key dump paths guarded by debug logging.
- Adding a new hardware-specific helper file without updating `bcm_crypto_spu-objs` will produce unresolved symbols or missing functionality.
- Kconfig dependency mistakes would surface as compile failures across mailbox, crypto API, debugfs, or OF/platform symbols.

## Test Signals

Build with `CONFIG_CRYPTO_DEV_BCM_SPU=y`, `m`, and unset. Confirm the module links all four component objects, and run a debug build only in controlled environments because packet dumps may contain plaintext, keys, IVs, and tags.
