# sources/distributed-fs/ceph-client/drivers/s390/block/scm_blk.h

Purpose: shared header for the SCM block driver, defining per-device/request state, exported setup/cleanup/interrupt contracts, and debug logging helpers.

Important APIs/types/functions: `struct scm_blk_dev` contains request queue, gendisk, tag set, SCM device, lock, queued count, state, and finished list. `struct scm_request` contains AOB/AIDAW batching state and original request pointers. Public functions include `scm_blk_dev_setup()`, `scm_blk_dev_cleanup()`, `scm_blk_set_available()`, `scm_blk_irq()`, `scm_aidaw_fetch()`, `scm_drv_init()`, and `scm_drv_cleanup()`.

Control flow: the header has no independent runtime flow; it defines the seam between the SCM bus-facing driver (`scm_drv.c`) and the block queue implementation (`scm_blk.c`). `SCM_LOG_STATE()` packages SCM address, operational state, and rank for debug traces.

State and persistence behavior: all state is volatile per-device or per-request block I/O state. The enum `SCM_OPER`/`SCM_WR_PROHIBIT` controls whether writes are accepted.

Dependencies and integration points: depends on blkdev/blk-mq, spinlocks, lists, interrupts, s390 EADM definitions, and s390 debug feature.

Risks and test signals: structure layout is shared across files and interrupt callbacks, so mismatched assumptions break completions. Compile tests plus probe/remove/notify tests validate the contract.
