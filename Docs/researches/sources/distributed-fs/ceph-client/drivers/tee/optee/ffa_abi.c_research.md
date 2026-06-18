# sources/distributed-fs/ceph-client/drivers/tee/optee/ffa_abi.c

## Purpose
`ffa_abi.c` implements the OP-TEE FF-A transport. It registers the FF-A driver, probes OP-TEE secure partitions, exchanges capabilities, registers shared memory through FF-A memory-share/lend handles, translates FF-A message parameters, performs yielding direct-message calls with RPC handling, manages FF-A notifications, and wires client/supplicant TEE devices to common OP-TEE code.

## Important APIs, Types, And Functions
The FF-A shared-memory handle map uses `struct shm_rhash`, `optee_shm_add_ffa_handle()`, `optee_shm_rem_ffa_handle()`, and `optee_shm_from_ffa_handle()` to translate FF-A global ids back to `tee_shm`. `optee_ffa_to_msg_param()` and `optee_ffa_from_msg_param()` convert between `struct tee_param` and `OPTEE_MSG_ATTR_TYPE_FMEM_*` parameters, using `shm->sec_world_id` as the FF-A global id and `OPTEE_MSG_FMEM_INVALID_GLOBAL_ID` for NULL memrefs.

`optee_ffa_shm_register()` validates memory type, builds an SG table, calls FF-A `memory_share()`, inserts the global handle, and stores it on `shm->sec_world_id`. `optee_ffa_shm_unregister()` tells OP-TEE to unregister, reclaims the FF-A memory object, and removes the handle. The supplicant unregister path skips the OP-TEE unregister call because the free originated from OP-TEE RPC.

`optee_ffa_yielding_call()` sends direct FF-A messages, handles busy returns through `optee_call_queue`, services RPC command or interrupt returns, and resumes with `OPTEE_FFA_YIELDING_CALL_RESUME`. `optee_ffa_do_call_with_arg()` prepares the direct call using the SHM global id and an offset to the message arg. `handle_ffa_rpc_func_cmd_shm_alloc()` and `_free()` service secure-world SHM allocation RPCs using either supplicant application SHM or kernel private SHM.

Protected memory is handled by `optee_ffa_lend_protmem()`, which lends memory via FF-A, assigns the use case with `OPTEE_MSG_CMD_ASSIGN_PROTMEM`, maps the global id, and reclaims on errors; `optee_ffa_reclaim_protmem()` releases and reclaims it. Probe helpers read FF-A API version, OP-TEE OS revision, capabilities, async notification support, RPMB probe capability, and protected memory support.

## Control Flow And State
Probe starts with API compatibility and capability exchange, allocates `struct optee`, creates a page-based SHM pool, allocates/registers client and privileged supplicant TEE devices, initializes the FF-A global-id rhashtable, call queue, supplicant, argument cache, RPMB mutex, internal context, notifications, optional protected memory, and device enumeration. Runtime calls use common OP-TEE message construction but enter secure world through FF-A direct request/response.

Persistent state includes `optee->ffa.global_ids`, `optee->ffa.bottom_half_value`, FF-A notification workqueue/work item, shared-memory pool, internal context, and per-instance common OP-TEE state. Removal relinquishes notification ids, destroys the workqueue, calls common removal, destroys the rhashtable/mutex, and frees `optee`.

## Dependencies And Integration Points
This file depends on the ARM FF-A bus and memory/message/notifier ops, Linux scatterlist APIs, TEE dynamic SHM helpers, common OP-TEE core/session/RPC/protected-memory code, RPMB reachability, and `optee_ffa.h` ABI constants. It registers with `ffa_register()` only when `CONFIG_ARM_FFA_TRANSPORT` is reachable.

## Risks
`optee_ffa_lend_protmem()` allocates `mem_attr` with `kzalloc_objs()` but does not visibly check for NULL before filling it, making low-memory behavior a risk if that helper does not encode allocation failure safely. FF-A SHM unregister removes the local handle before both OP-TEE unregister and memory reclaim, so failed unregister/reclaim leaves local state already gone. `optee_ffa_do_call_with_arg()` rejects nonzero `shm->offset` for argument SHM, so pool behavior must continue to satisfy page-start arguments. Async notification setup treats failures as nonfatal in probe, which means notification-dependent behavior must still work through synchronous RPC fallback.

## Test Signals
Probe with incompatible FF-A API versions, missing capability bits, and failures at each registration step. Register/unregister normal and supplicant SHM and verify global id mapping is removed exactly once. Exercise yielding calls with busy, RPC command, RPC interrupt, and done returns. Test protected memory lend assignment failure and ensure FF-A memory is reclaimed. Trigger notification ids including bottom-half value and normal keys.
