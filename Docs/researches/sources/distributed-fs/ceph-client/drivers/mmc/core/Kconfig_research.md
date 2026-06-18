# sources/distributed-fs/ceph-client/drivers/mmc/core/Kconfig

## Purpose
Defines MMC core options for pwrseq helpers, block support, minors, SDIO UART, test driver, and inline crypto.

## Important APIs, Types, And Functions
- `PWRSEQ_EMMC`, `PWRSEQ_SD8787`, `PWRSEQ_SIMPLE` select OF power/reset sequencing helpers.
- `MMC_BLOCK` enables the block device driver.
- `MMC_BLOCK_MINORS` controls minors per block disk.
- `SDIO_UART`, `MMC_TEST`, and `MMC_CRYPTO` enable optional drivers/features.

## Control Flow
Symbols are visible under `MMC` and consumed by the core Makefile to select objects and modules.

## State And Persistence
Compile-time configuration only. Runtime effects include whether block devices, pwrseq, debug test surfaces, SDIO UART, and crypto hooks exist.

## Dependencies And Integration Points
Integrates with OF, BLOCK, RPMB, TTY, BLK_INLINE_ENCRYPTION, and Kbuild.

## Risks And Edge Cases
`MMC_TEST` can overwrite media. `MMC_BLOCK_MINORS` changes partition/device capacity under a fixed major. `MMC_CRYPTO` only enables framework hooks; host support is still required.

## Test Signals
Build matrices for block, pwrseq, crypto, UART, and test options; runtime `mmcblk*`, pwrseq probing, and absence/presence of test debugfs nodes.
