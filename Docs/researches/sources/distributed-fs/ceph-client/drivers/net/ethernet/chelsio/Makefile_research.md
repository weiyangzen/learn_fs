# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Makefile

## Purpose
This Makefile maps Chelsio Kconfig symbols to driver subdirectories. It is the top-level build dispatcher for Chelsio Ethernet support.

## Important Rules
`obj-$(CONFIG_CHELSIO_T1) += cxgb/`, `obj-$(CONFIG_CHELSIO_T3) += cxgb3/`, `obj-$(CONFIG_CHELSIO_T4) += cxgb4/`, `obj-$(CONFIG_CHELSIO_T4VF) += cxgb4vf/`, `obj-$(CONFIG_CHELSIO_LIB) += libcxgb/`, and `obj-$(CONFIG_CHELSIO_INLINE_CRYPTO) += inline_crypto/` are the complete rule set.

## Control Flow and Integration
Kbuild evaluates each `obj-*` assignment from the configured symbols. Selected directories contribute their own Makefiles and objects to either built-in kernel code or modules depending on each tristate value. This file directly integrates with `drivers/net/ethernet/chelsio/Kconfig`.

## State and Persistence
There is no runtime state. The persistent effect is in build outputs chosen by `.config`.

## Dependencies and Risks
The file depends on the subdirectories existing and their Kconfig symbols being defined. Risks are low but include symbol/name drift, missing subdirectory Makefiles, or accidentally omitting a new Chelsio component from the dispatch list.

## Test Signals
Build with each Chelsio symbol as `m` and `y`, verify that expected modules/directories are entered, and run `make W=1` for stale object or missing directory diagnostics.
