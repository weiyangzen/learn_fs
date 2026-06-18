# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.c

Purpose: groups hardware engines that share resources so the driver can enforce mutual exclusion between long-running faulting execution and DMA-fence mode execution.

Important functions: `xe_hw_engine_setup_groups`, `xe_hw_engine_group_add_exec_queue`, `xe_hw_engine_group_del_exec_queue`, `xe_hw_engine_group_resume_faulting_lr_jobs`, `xe_hw_engine_group_get_mode`, `xe_hw_engine_group_put`, and `xe_hw_engine_group_find_exec_mode`. Local helpers allocate groups, suspend faulting LR jobs, wait for DMA-fence jobs, switch modes, and wait sync dependencies.

Control flow: setup allocates three groups per GT: render/compute, copy, and video decode/enhance. Adding an exec queue links it under `mode_sem`; when adding a fault-mode queue while the group is in DMA-fence mode, it suspends and waits for that queue first. `get_mode` acquires read mode if already correct, otherwise upgrades to write, switches by suspending LR queues or waiting DMA-fence jobs, downgrades to read, and expects caller to release with `put`.

State/persistence: each group owns `exec_queue_list`, `resume_work`, a workqueue, `mode_sem`, and current execution mode. Exec queues are linked through `hw_engine_group_link`.

Dependencies/integration: uses exec queue suspend/resume ops, VM mode helpers, sync waiters, DMA fence waits, GT stats, DRM managed allocation, and workqueue cleanup.

Risks/test signals: lock acquisition is interruptible/killable in public paths. Switching from LR to DMA-fence can return `-EAGAIN` when a faulting LR queue cannot be suspended while dependencies exist; the code waits syncs then retries. Test mode switches with dependency syncs, queue add/delete under mode changes, fault-mode resume work, DMA fence wait errors, and stats counters for suspend/wait latency.
