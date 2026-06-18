# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group_types.h

Purpose: defines hardware engine group modes and persistent group state.

Important types: `enum xe_hw_engine_group_execution_mode` (`EXEC_MODE_LR`, `EXEC_MODE_DMA_FENCE`) and `struct xe_hw_engine_group` with queue list, resume work/workqueue, read-write semaphore, and current mode.

Control flow/state: the group state is initialized during hardware engine setup and mutated by mode switching and queue add/delete paths.

Dependencies/integration: includes forcewake/LRC/reg state headers indirectly from engine type context, though this file only needs list/workqueue/rwsem declarations via broader includes.

Risks/test signals: `cur_mode` default is zero (`EXEC_MODE_LR`) because groups are zero-allocated; tests should verify initial mode assumptions and resume work lifetime.
