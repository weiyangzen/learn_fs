# sources/distributed-fs/ceph-client/drivers/s390/block/scm_drv.c

Purpose: provides the SCM bus driver binding for the SCM block driver: probe, remove, event notify, and EADM interrupt handler registration.

Important APIs/types/functions: `scm_notify()` handles `SCM_CHANGE` and `SCM_AVAIL`; `scm_probe()` validates operational state, allocates `struct scm_blk_dev`, and calls `scm_blk_dev_setup()`; `scm_remove()` calls block cleanup and frees state; `scm_drv` supplies `.notify`, `.probe`, `.remove`, and `.handler = scm_blk_irq`; `scm_drv_init()`/`cleanup()` register/unregister.

Control flow: module init in `scm_blk.c` calls `scm_drv_init()`. For each good SCM increment, probe stores driver data and creates a block disk. Availability notifications restore write access through `scm_blk_set_available()`. Removal tears down the disk and clears driver data.

State and persistence behavior: maintains only per-device driver data pointer and block-device lifetime. SCM hardware capability changes are logged but not persisted.

Dependencies and integration points: depends on the s390 SCM driver model (`struct scm_driver`, `scm_driver_register()`), EADM event delivery, and the block implementation exported by `scm_blk.c`.

Risks and test signals: probe rejects non-good operational state; notify assumes driver data exists for availability events. Test probe failure cleanup, remove after partial setup failure, `SCM_AVAIL` recovery from write-prohibited mode, and event logging for capability changes.
