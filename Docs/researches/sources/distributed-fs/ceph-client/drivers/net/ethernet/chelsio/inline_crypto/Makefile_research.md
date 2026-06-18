# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/Makefile

## Purpose
Routes Chelsio inline crypto build symbols to the appropriate subdirectories.

## Important APIs, Types, And Functions
The Makefile maps `CONFIG_CRYPTO_DEV_CHELSIO_TLS` to `chtls/`, `CONFIG_CHELSIO_IPSEC_INLINE` to `ch_ipsec/`, and `CONFIG_CHELSIO_TLS_DEVICE` to `ch_ktls/`.

## Control Flow
Kbuild evaluates the `obj-$(CONFIG_...)` assignments and descends into enabled subdirectories. There is no runtime behavior.

## State And Persistence
Build state is represented by generated kernel objects/modules under the active kernel build tree. The source file itself persists only build routing.

## Dependencies And Integration Points
This Makefile is reached from `drivers/net/ethernet/chelsio/Makefile` when `CONFIG_CHELSIO_INLINE_CRYPTO` is enabled. It integrates with subdirectory Makefiles that set include paths and module object composition.

## Risks
Wrong symbol-to-directory mapping would silently omit or include the wrong crypto subdriver. Because the top-level inline crypto switch is separate from these tristates, build coverage must include all combinations.

## Test Signals
`make M=drivers/net/ethernet/chelsio/inline_crypto` with each config symbol enabled should build the expected module directories and no others.
