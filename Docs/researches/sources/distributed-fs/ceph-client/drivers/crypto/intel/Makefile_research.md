# sources/distributed-fs/ceph-client/drivers/crypto/intel/Makefile Research

## Purpose
This Makefile routes enabled Intel crypto driver builds into their subdirectories.

## Important APIs, Types, and Functions
There are no runtime APIs. Build rules add `keembay/` and `ixp4xx/` unconditionally to `obj-y`, add `qat/` when `CONFIG_CRYPTO_DEV_QAT` is enabled, and add `iaa/` when `CONFIG_CRYPTO_DEV_IAA_CRYPTO` is enabled.

## Control Flow
Kbuild evaluates the object lists after configuration. If IAA crypto is selected, Kbuild descends into `drivers/crypto/intel/iaa/` and evaluates that directory's Makefile.

## State and Persistence
The file affects build artifacts only. It has no runtime state.

## Dependencies and Integration Points
It depends on symbols defined in child Kconfig files and integrates with the parent `drivers/crypto` Kbuild traversal.

## Risks and Edge Cases
The directory inclusion is symbol-sensitive. A mismatch between Kconfig symbol names and Makefile conditionals would silently skip a selected driver. Here, IAA uses `CONFIG_CRYPTO_DEV_IAA_CRYPTO`, matching the researched IAA Kconfig.

## Test Signals
Enable and disable `CONFIG_CRYPTO_DEV_IAA_CRYPTO` and check that `drivers/crypto/intel/iaa/iaa_crypto.o` is or is not built.
