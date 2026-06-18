
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_process_queue_manager.c

## Purpose
Implements the per-process queue manager. It allocates queue IDs, creates/destroys user queues, updates queue properties and MQDs, manages GWS assignment, exposes queue snapshots/wave state, and checkpoints/restores queues for CRIU.

## Important APIs, types, and functions
- `pqm_init` and `pqm_uninit` manage `process_queue_manager` lists and qid bitmap.
- `pqm_create_queue`, `pqm_destroy_queue`, `pqm_update_queue_properties`, `pqm_update_mqd`, and `pqm_set_gws` are the core queue lifecycle/update APIs.
- `kfd_process_dequeue_from_device` and `kfd_process_dequeue_from_all_devices` terminate DQM process mappings.
- `kfd_process_get_queue_info`, `kfd_criu_checkpoint_queues`, `kfd_criu_restore_queue`, and checkpoint helpers pack/unpack queue private state.
- `pqm_debugfs_mqds` dumps MQDs through DQM MQD managers.

## Control flow
Queue creation finds or assigns a qid, registers the process with DQM if this is the first queue, optionally allocates MES process context, initializes a user queue, and calls `dqm->ops.create_queue` with optional restore MQD/control-stack data. On success it returns a relative doorbell offset and adds the queue to PQM/procfs. Destroy finds the queue, unrefs BO VAs, calls DQM destroy, removes procfs, releases BOs, frees GWS/MES resources, clears qid, and unregisters the process if it has no queues. Updates validate replacement ring mapping or CU mask constraints before calling DQM update.

## State and persistence behavior
PQM owns a linked list of `process_queue_node` and a bitmap of allocated queue IDs. Queue objects persist until destroy/uninit and carry BO references, MQD pointers, DQM placement, doorbell IDs, GWS state, and MES auxiliary BOs. CRIU persistence stores queue properties, doorbell IDs, GWS flag, SDMA ID, MQD bytes, and control-stack data in `kfd_criu_queue_priv_data` followed by variable data.

## Dependencies and integration points
Depends on DQM ops, kernel queue code, amdgpu GWS helpers, amdgpu reset/MES helpers, queue buffer pinning helpers from `kfd_queue.c`, CRIU structs from `kfd_priv.h`, procfs queue hooks, and MQD-manager checkpoint/debug callbacks.

## Risks
Error paths must clear qid bitmap bits and unregister first-queue process state. Some paths return `-1` instead of a specific errno. MES auxiliary allocations must be freed on every failure and destroy path. Queue BO reference/unreference order is important to keep GPUVM mappings alive while hardware can access them. CRIU restore trusts user-provided sizes after bounds checks and passes raw MQD data to DQM restore. CU masks on WGP ASICs must be pairwise enabled.

## Test signals
Create/destroy compute, SDMA, XGMI SDMA, and SDMA-by-engine queues; hit max queue limits; test first/last queue process register/unregister; update rings and CU masks; assign/remove GWS; exercise MES and non-MES paths; CRIU checkpoint/restore queues with MQD/control-stack data; debugfs MQD dump across XCCs; inject DQM failures to verify cleanup.
