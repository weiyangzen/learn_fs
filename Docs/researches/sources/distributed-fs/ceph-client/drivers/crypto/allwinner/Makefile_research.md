<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Makefile

## Purpose

This Makefile dispatches enabled Allwinner crypto drivers to their implementation subdirectories.

## Important APIs, Types, And Functions

It maps `CONFIG_CRYPTO_DEV_SUN4I_SS` to `sun4i-ss/`, `CONFIG_CRYPTO_DEV_SUN8I_CE` to `sun8i-ce/`, and `CONFIG_CRYPTO_DEV_SUN8I_SS` to `sun8i-ss/`.

## Control Flow

There is no runtime control flow. Kbuild descends only into selected driver directories.

## State And Persistence Behavior

It owns no runtime state; build outputs persist as built-in objects or modules selected by Kconfig.

## Dependencies And Integration Points

It connects `drivers/crypto/allwinner/Kconfig` symbols to the subdirectory Makefiles that assemble each driver.

## Risks And Test Signals

Risks include forgotten subdirectory wiring for a new Allwinner driver or symbol drift after renames. Test by enabling each Allwinner driver independently and confirming the expected module objects are built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Makefile -->
