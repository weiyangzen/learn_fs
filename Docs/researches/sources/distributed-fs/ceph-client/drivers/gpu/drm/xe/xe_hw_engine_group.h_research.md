# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.h

Purpose: public API for hardware engine group setup, exec queue membership, execution mode acquisition/release, mode selection, and async LR queue resume.

Important APIs: `xe_hw_engine_setup_groups`, add/delete exec queue, `xe_hw_engine_group_get_mode`, `xe_hw_engine_group_put`, `xe_hw_engine_group_find_exec_mode`, and `xe_hw_engine_group_resume_faulting_lr_jobs`.

Control flow/state: callers acquire a group mode with `get_mode` before submitting work that requires LR or DMA-fence execution, then release with `put`. Exec queue lifecycle calls add/delete.

Dependencies/integration: uses `struct xe_hw_engine_group`, exec queues, GT, and sync entries.

Risks/test signals: get/put pairing is required because `get_mode` returns with `mode_sem` held for read. Tests should catch missing puts and queue deletion while mode is held.
