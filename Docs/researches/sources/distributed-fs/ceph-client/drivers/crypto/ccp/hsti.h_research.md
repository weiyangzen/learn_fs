# sources/distributed-fs/ceph-client/drivers/crypto/ccp/hsti.h

## Purpose

`hsti.h` declares the PSP security sysfs group and initialization helper used by the PSP and PCI glue code.

## Important APIs, Types, And Functions

It exports `psp_security_attr_group` and declares `psp_init_hsti(struct psp_device *psp)`.

## Control Flow

There is no runtime control flow in the header. Consumers include the header to attach the sysfs group and to populate HSTI state during PSP initialization.

## State And Persistence Behavior

The header defines no storage. State lives in `psp->capability` and sysfs registration owned elsewhere.

## Dependencies And Integration Points

It relies on `struct psp_device` being visible to translation units that include it through `psp-dev.h` or equivalent includes.

## Risks And Test Signals

Risk is limited to declaration drift from `hsti.c`. Build tests with `CONFIG_CRYPTO_DEV_SP_PSP` and sysfs attribute group registration cover it.
