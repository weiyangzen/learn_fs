<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/shm.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/shm.c

## Purpose

`shm.c` provides QTEE's shared-memory support. It allocates per-invocation inbound and outbound message buffers from the generic TEE shared-memory framework, zeros them for secure-world consumption, and implements a dynamic shared-memory pool backed by Qualcomm TZ memory bridge registration.

## Important APIs, Types, and Functions

`MAX_INBOUND_BUFFER_SIZE` caps direct-call message buffers at 4 MiB, while `MAX_OUTBOUND_BUFFER_SIZE` fixes callback/async outbound buffers at 4 KiB. `qcomtee_msg_buffers_alloc()` computes the inbound size from the argument table plus aligned input/output buffer payloads, allocates inbound and outbound private buffers with `tee_shm_alloc_priv_buf()`, stores virtual addresses/sizes in `oic`, and zeroes both buffers. `qcomtee_msg_buffers_free()` frees both buffers.

The pool implementation uses `qcomtee_shm_register()` to call `qcom_tzmem_shm_bridge_create()` and record `shm->sec_world_id`, `qcomtee_shm_unregister()` to delete that bridge, `pool_op_alloc()` and `pool_op_free()` to delegate to `tee_dyn_shm_alloc_helper()` and `tee_dyn_shm_free_helper()`, and `qcomtee_shm_pool_alloc()` to allocate a `tee_shm_pool` with those ops.

## Control Flow

Before each object invocation, `core.c` calls `qcomtee_msg_buffers_alloc()`. The function calculates a safe inbound buffer size with overflow-aware helpers, allocates dynamic private buffers through the qcomtee pool, gets kernel virtual addresses, and clears the memory because QTEE expects unused areas to be zero. On invocation completion or failure, `qcomtee_msg_buffers_free()` releases both `tee_shm`s, which unregisters bridges and frees pages through the generic TEE pool callbacks.

## State and Persistence Behavior

State is per invocation and per `tee_shm`: inbound/outbound virtual address, size, physical address, and secure-world bridge ID. The shared-memory pool itself is stored in `struct qcomtee` for the lifetime of the device. No state persists after buffers are freed or the device is removed.

## Dependencies and Integration Points

This file depends on generic TEE shared memory (`tee_shm_alloc_priv_buf()`, `tee_shm_free()`), dynamic shared-memory helpers from `tee_shm.c`, Qualcomm TZ memory bridge APIs (`qcom_tzmem_shm_bridge_create/delete`), and qcomtee message sizing helpers from `qcomtee_msg.h`. It is used by the object invocation engine in `core.c` and the platform probe/remove paths in `call.c`.

## Risks and Edge Cases

The inbound size calculation checks Linux-originated argument sizes but QTEE-originated callback/response offsets must still be treated carefully by parsers. `tee_shm_get_va()` can return an ERR_PTR, but this code stores the result without checking, relying on successful private-buffer allocation to imply a valid mapping. Bridge creation failure propagates through allocation, but bridge deletion failures are not reported by `qcomtee_shm_unregister()`. A fixed 4 KiB outbound buffer may be too small for future callback/async formats unless the ABI remains constrained.

## Test Signals

Tests should cover inbound size at zero args, maximum args, large buffers near 4 MiB, size overflow injection, allocation failure for inbound and outbound buffers, bridge create/delete failure paths, zeroing of unused message space, physical-address availability for SCM calls, and parsing rejection for QTEE-provided offsets outside allocated buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/shm.c -->
