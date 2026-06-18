# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/Makefile

## Purpose
This Makefile builds the legacy HiSilicon SEC platform crypto driver when `CONFIG_CRYPTO_DEV_HISI_SEC` is enabled.

## Important APIs, types, and functions
It declares `hisi_sec.o` as the module object and links it from `sec_algs.o` and `sec_drv.o`. There are no C APIs in the Makefile itself.

## Control flow
Kbuild includes the module only when the config symbol is selected. `sec_drv.o` supplies platform probe/remove and queue/device plumbing; `sec_algs.o` supplies crypto algorithm registration and request handling.

## State and persistence behavior
The file has no runtime state. It controls object composition at build time only.

## Dependencies and integration points
It depends on the kernel Kbuild system and the `CONFIG_CRYPTO_DEV_HISI_SEC` Kconfig option. It integrates the platform device driver and crypto algorithm implementation into one loadable/built-in unit.

## Risks and edge cases
If either object is removed or renamed without updating this file, the module will fail to link. Building only this legacy driver does not include the newer SEC2 QM-backed implementation.

## Test signals
Build tests with `CONFIG_CRYPTO_DEV_HISI_SEC=y` and `=m` should produce `hisi_sec` and resolve symbols between `sec_algs.o` and `sec_drv.o`.
