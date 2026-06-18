# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/Makefile

## Purpose
This Makefile maps Broadcom firmware Kconfig symbols to object files. It is the build glue for the local NVRAM, SPROM, and BNXT TEE implementations.

## Important Targets
`obj-$(CONFIG_BCM47XX_NVRAM) += bcm47xx_nvram.o`, `obj-$(CONFIG_BCM47XX_SPROM) += bcm47xx_sprom.o`, and `obj-$(CONFIG_TEE_BNXT_FW) += tee_bnxt_fw.o` are the only build rules. Their simplicity means the Kconfig symbols fully define whether each feature is compiled and whether it is linked built-in or as a module.

## Control Flow, State, And Persistence
There is no runtime state. Build state flows from Kconfig into kbuild object inclusion. Because `BCM47XX_NVRAM` and `BCM47XX_SPROM` are bools, their objects are built-in when selected; `TEE_BNXT_FW` follows tristate module semantics.

## Dependencies And Integration Points
The Makefile integrates with the parent firmware directory build. It assumes each object supplies its own module metadata or initcall, and that dependency correctness is handled by `Kconfig`.

## Risks And Test Signals
Risk is low, but target names must stay synchronized with source filenames and Kconfig symbols. Test signals are compile-test matrix builds for each symbol and checking that changing `TEE_BNXT_FW=m` produces `tee_bnxt_fw.ko`.
