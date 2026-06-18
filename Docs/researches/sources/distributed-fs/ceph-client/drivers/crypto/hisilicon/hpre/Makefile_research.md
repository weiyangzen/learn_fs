# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/Makefile

## Purpose
This Makefile defines the HPRE driver object composition. When `CONFIG_CRYPTO_DEV_HISI_HPRE` is enabled, it builds the module/object `hisi_hpre.o` from the device-management file `hpre_main.o` and the crypto algorithm implementation file `hpre_crypto.o`.

## Important APIs, Types, and Functions
There are no runtime APIs. The important build rule is `obj-$(CONFIG_CRYPTO_DEV_HISI_HPRE) += hisi_hpre.o`, with `hisi_hpre-objs = hpre_main.o hpre_crypto.o`.

## Control Flow
Kernel build logic links `hpre_main.o` and `hpre_crypto.o` into one HPRE driver unit. This allows `hpre_main.c` to provide PCI/QM lifecycle and `hpre_crypto.c` to register crypto algorithms using symbols declared in `hpre.h`.

## State and Persistence Behavior
No runtime state exists in the Makefile. It persists the module boundary for HPRE.

## Dependencies and Integration Points
The parent HiSilicon Makefile descends into this directory when `CRYPTO_DEV_HISI_HPRE` is enabled. The composed object depends on the shared QM object built from the parent directory.

## Risks and Edge Cases
Build failures will occur if either object is renamed or if new HPRE source files are added without updating `hisi_hpre-objs`. Since both files link into one module, exported/non-exported symbol visibility between them should remain consistent with `hpre.h`.

## Test Signals
Build HPRE as module and built-in, verify `hisi_hpre.ko` includes both device lifecycle and crypto algorithm symbols, and run compile tests after adding any new HPRE source file.
