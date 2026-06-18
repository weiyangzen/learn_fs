# sources/distributed-fs/ceph-client/drivers/mmc/core/block.c

## Purpose
MMC/SD block driver (`mmcblk`). It creates Linux block disks, handles read/write/flush/discard/secure erase, routes raw MMC ioctls, manages eMMC partitions and RPMB char devices, performs recovery, and exposes sysfs/debugfs controls.

## Important APIs, Types, And Functions
- `struct mmc_blk_data` owns gendisk, `mmc_queue`, partitions/RPMBs, CMD23/reliable-write flags, read-only state, and active partition cache.
- `struct mmc_rpmb_data` owns RPMB char-device and RPMB framework registration state.
- `mmc_blk_probe()`/`remove()`/PM callbacks implement `struct mmc_driver`.
- `mmc_blk_mq_issue_rq()` dispatches sync, async, and CQE requests.
- `mmc_blk_data_prep()` and `mmc_blk_rw_rq_prep()` translate block requests into MMC commands/data/scatterlists/CMD23/crypto.
- Recovery lives in `mmc_blk_mq_rw_recovery()`, `mmc_blk_reset()`, `mmc_blk_cqe_recovery()`, and completion helpers.
- `mmc_blk_ioctl_cmd()` and `mmc_blk_ioctl_multi_cmd()` serialize raw commands through the queue.

## Control Flow
Module init registers the RPMB bus, char-device range, block major, and `mmcblk` driver. Probe validates block-read support, applies quirks, creates a completion workqueue, allocates main and hardware-partition disks, creates RPMB devices, enables debugfs, and configures runtime PM. Requests enter through the queue, switch to the target partition, are prepared as MMC requests, started through core/CQE paths, then completed, partially completed, retried, reset, or failed.

## State And Persistence
State includes disk minors, capacity/read-only flags, `part_curr`, retry flags, reset-done bits, RPMB devices, workqueues, PM state, and debugfs/sysfs values. Hardware partition selection is cached and restored. Media contents persist by design.

## Dependencies And Integration Points
Depends on MMC core/bus, blk-mq, queue helpers, eMMC/SD protocol helpers, RPMB, debugfs, sysfs, runtime PM, IDA, workqueues, capabilities, user-copy, and optional crypto.

## Risks And Edge Cases
Raw ioctls are powerful despite `CAP_SYS_RAWIO` and whole-disk checks. Partition switching around RPMB must restore state. Recovery depends on accurate bytes transferred, status, busy polling, and reset behavior. Secure erase/trim timeout calculation and RPMB frame sequencing are strict. Hot unplug stresses krefs and disk removal.

## Test Signals
`mmcblk*` creation/removal, filesystem stress, read-only sysfs behavior, discard/trim/flush, ioctl permissions, RPMB routing, suspend/resume partition restoration, CQE/non-CQE I/O, injected timeout/CRC recovery, and debugfs `status`/`ext_csd`.
