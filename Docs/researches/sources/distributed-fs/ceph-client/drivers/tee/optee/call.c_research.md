# sources/distributed-fs/ceph-client/drivers/tee/optee/call.c

## Purpose
`call.c` implements OP-TEE generic TEE operations above the transport-specific ABI. It manages secure-world thread admission, cached shared-memory argument buffers, session open/close/invoke/cancel, system-session thread reservation, memory-type validation, and simple internal OP-TEE commands.

## Important APIs, Types, And Functions
`optee_cq_init()`, `optee_cq_wait_init()`, `optee_cq_wait_for_completion()`, and `optee_cq_wait_final()` implement a fairness queue for calls into OP-TEE. They optionally track secure thread counts and prioritize system-thread sessions when one secure thread should be reserved. `optee_cq_incr_sys_thread_count()` and `_decr_...()` adjust the number of sessions needing system-thread priority.

`optee_shm_arg_cache_init()`, `optee_get_msg_arg()`, `optee_free_msg_arg()`, and `optee_shm_arg_cache_uninit()` manage reusable shared-memory pages that hold `struct optee_msg_arg` plus optional RPC argument space. Cache behavior is controlled by `OPTEE_SHM_ARG_ALLOC_PRIV` and `OPTEE_SHM_ARG_SHARED`.

`optee_open_session()` constructs an `OPTEE_MSG_CMD_OPEN_SESSION` message with two meta parameters, converts client params through the selected backend ops, calls secure world, records successful sessions in `optee_context_data`, and copies output params back. `optee_close_session_helper()` sends close to secure world; `optee_close_session()` removes and frees the local session first. `optee_invoke_func()` and `optee_cancel_req()` validate the session and issue command/cancel messages. `optee_system_session()` marks a session as using a reserved system thread when possible.

`optee_check_mem_type()` rejects user memory mappings that are not normal cacheable memory before registering them with OP-TEE. `optee_do_bottom_half()` and `optee_stop_async_notif()` send simple internal commands via `simple_call_with_arg()`.

## Control Flow And State
Session state is per context in `ctxdata->sess_list`, protected by `ctxdata->mutex`. Every secure-world call obtains an argument buffer from the cache, fills an OP-TEE message, calls `optee->ops->do_call_with_arg()`, then returns the cache slot. The selected ABI backend supplies transport-specific parameter conversion and call mechanics.

The call queue persists at `optee->call_queue`. If a finite thread count is known, entering a call decrements `free_thread_count` or waits; exiting increments it and wakes another waiter. System sessions cause normal sessions to leave a thread available when needed.

## Dependencies And Integration Points
This file depends on `optee_private.h`, `optee_msg.h`, Linux TEE core helpers, UUID/client-login helpers, VMA iteration, architecture page attribute definitions, and backend ops from `smc_abi.c` or `ffa_abi.c`. It is used by both client and supplicant devices registered by each ABI backend.

## Risks
`optee_open_session()` calls `optee_close_session()` if output parameter conversion fails after a secure session was created; any bug in session-list insertion or conversion can leak or double-close. The argument cache logs but continues if freeing a non-free entry or clearing an already-free bit, so memory corruption symptoms may be delayed. Memory-type checking is architecture-specific and compile errors on unsupported architectures. `system_thread` is only initialized if a session lookup succeeds; the current flow returns on failed lookup before use, so that invariant must be preserved.

## Test Signals
Stress concurrent open/invoke/close with finite thread counts and system-session reservation. Validate cached argument reuse with `rpc_param_count` zero and nonzero. Fault-inject backend conversion failures after successful secure calls. Register user memory from normal and device mappings to test `optee_check_mem_type()`. Exercise cancellation and bottom-half commands through both SMC and FF-A backends.
