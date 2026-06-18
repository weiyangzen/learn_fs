# sources/distributed-fs/ceph-client/include/linux/blk-pm.h

## Purpose
`blk-pm.h` declares block-layer runtime power-management hooks for request queues. It lets the block layer coordinate queue state before and after runtime suspend/resume.

## Important APIs, Types, And Functions
With `CONFIG_PM`, exported functions are `blk_pm_runtime_init()`, `blk_pre_runtime_suspend()`, `blk_post_runtime_suspend()`, `blk_pre_runtime_resume()`, and `blk_post_runtime_resume()`. Without power management, only `blk_pm_runtime_init()` remains as an empty inline stub. The header forward-declares `struct device` and `struct request_queue`.

## Control Flow And State
The header defines no state. Runtime PM state is stored in `request_queue` fields under `CONFIG_PM` (`dev` and `rpm_status`) and in the PM core. The pre/post hooks are intended to bracket suspend/resume transitions: pre-suspend can block or drain queue activity, post-suspend records success/failure, pre-resume prepares queue state, and post-resume finishes restoration.

## Dependencies And Integration Points
It integrates with `blkdev.h` queue PM fields, `blk-mq` runtime PM request flags (`RQF_PM` and `BLK_MQ_REQ_PM`), and drivers that call the runtime init helper when binding a queue to a device. It intentionally keeps dependencies low through forward declarations.

## Risks And Test Signals
Risks include missing PM stubs for non-PM builds, queue activity racing with suspend, failing to allow PM requests while normal I/O is blocked, and mismatched pre/post calls. Test signals include builds with and without `CONFIG_PM`, suspend/resume under active I/O, PM-only request submission, and error propagation through `blk_post_runtime_suspend()`.
