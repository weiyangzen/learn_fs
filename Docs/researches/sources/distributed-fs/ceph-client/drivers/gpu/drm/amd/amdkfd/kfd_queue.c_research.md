
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_queue.c

## Purpose
Provides basic queue object allocation/debug printing, user queue buffer validation/reference management, SVM fallback references for CWSR buffers, and topology-derived context save/restore sizing.

## Important APIs, types, and functions
- `init_queue`, `uninit_queue`, `print_queue_properties`, and `print_queue`.
- `kfd_queue_buffer_get`, `kfd_queue_buffer_put`, `kfd_queue_acquire_buffers`, `kfd_queue_release_buffers`, `kfd_queue_unref_bo_va`, and `kfd_queue_unref_bo_vas`.
- SVM helpers `kfd_queue_buffer_svm_get` and `kfd_queue_buffer_svm_put` when HSA SVM is enabled.
- `kfd_queue_ctx_save_restore_size` computes CWSR, control-stack, debugger, and EOP sizes for topology.

## Control flow
Queue creation copies caller-supplied properties into a zeroed `struct queue`. Buffer acquisition reserves the process VM root BO, validates and refs write/read pointer pages and ring BO, then for compute queues validates EOP and CWSR sizes against topology. CWSR first tries a normal GPUVM BO mapping; if that fails, it drops the VM reservation and tries SVM range references. Release drops BO refs and SVM queue refs. Unref helpers decrement GPUVM `queue_refcount` while the VM root is reserved.

## State and persistence behavior
The queue object owns a copy of `queue_properties`; those properties hold BO references for write pointer, read pointer, ring, EOP, and CWSR. GPUVM mappings track `queue_refcount`; SVM ranges track `queue_refcount` for queue-pinned ranges. Topology node properties persist computed sizes used by later queue validation and userspace ABI reporting.

## Dependencies and integration points
Depends on amdgpu VM mapping lookup/reference APIs, KFD topology, SVM range management, queue properties from `kfd_priv.h`, and device XCC/topology data. PQM calls these helpers during queue create/destroy/update.

## Risks
Expected-size checks must match userspace queue layout, including AQL half-size behavior on GFX7/GFX8. BO VA refcount decrement and BO unref must stay paired. SVM fallback only applies to CWSR and requires ranges to be GPU-accessible and always mapped. CWSR sizing is hardware-generation-specific and can underallocate debug or wave state if formulas are wrong.

## Test signals
Queue creation with valid and invalid write/read/ring/EOP/CWSR mappings; AQL queue size behavior on GFX7/GFX8; CWSR SVM fallback; queue destroy refcount cleanup; topology size outputs for GFX8, GFX9, GFX10, GFX11, and GFX12 variants; debug-memory and EOP buffer size checks.
