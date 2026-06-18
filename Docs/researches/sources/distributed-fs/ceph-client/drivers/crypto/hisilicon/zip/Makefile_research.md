# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/Makefile

## Purpose
This Makefile builds the HiSilicon ZIP accelerator driver when `CONFIG_CRYPTO_DEV_HISI_ZIP` is enabled. The composite object `hisi_zip.o` contains ZIP device management, Crypto API compression, and DAE support.

## Important APIs, Types, And Functions
There are no runtime APIs in this file. The key Kbuild lines are `obj-$(CONFIG_CRYPTO_DEV_HISI_ZIP) += hisi_zip.o` and `hisi_zip-objs = zip_main.o zip_crypto.o dae_main.o`.

## Control Flow
Kbuild links `zip_main.o`, `zip_crypto.o`, and `dae_main.o` into the single `hisi_zip` driver object when the config symbol is active.

## State And Persistence
No runtime state exists. This file only controls module/object composition.

## Dependencies And Integration Points
The composition means `zip_main.c` can call DAE helpers and register Crypto API operations from `zip_crypto.c` in one module.

## Risks
The risk is mostly build integration. Omitting `dae_main.o` would leave unresolved DAE symbols used by `zip_main.c`; omitting `zip_crypto.o` would remove Crypto API registration callbacks.

## Test Signals
Build as built-in and module with `CONFIG_CRYPTO_DEV_HISI_ZIP`, confirm `hisi_zip.o` links all three objects, and check for unresolved symbols in modpost.
