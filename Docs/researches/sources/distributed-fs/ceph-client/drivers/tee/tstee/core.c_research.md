<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/core.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tstee/core.c

## Purpose

`tstee/core.c` implements the Arm Trusted Services TEE driver over FF-A. It exposes Trusted Services Secure Partitions as a generic TEE device, maps TEE sessions to Trusted Services interface IDs, shares memory through FF-A memory-share/retrieve/relinquish calls, and invokes service operations using FF-A direct messages.

## Important APIs, Types, and Functions

Transport helpers `arg_list_to_ffa_data()` and `arg_list_from_ffa_data()` convert five 32-bit protocol registers to/from `struct ffa_send_direct_data`. TEE ops are `tstee_get_version()`, `tstee_open()`, `tstee_release()`, `tstee_open_session()`, `tstee_close_session()`, and `tstee_invoke_func()`. Shared-memory hooks are `tstee_shm_register()` and `tstee_shm_unregister()`. Pool helpers allocate a dynamic TEE shm pool using `tee_dyn_shm_alloc_helper()`.

Probe helpers include `tstee_check_rpc_compatible()` and `tstee_probe()`, while `tstee_remove()` unregisters the TEE device and frees the pool. The FF-A device ID table matches `TS_RPC_UUID`.

## Control Flow

Probe switches the FF-A endpoint to 32-bit direct-message mode, asks the management interface for the RPC protocol version, allocates `struct tstee`, creates the dynamic shared-memory pool, allocates/registers a TEE device, and stores driver data on the FF-A device. Open creates an xarray for sessions. Open-session sends `TS_RPC_OP_SERVICE_INFO` with the requested UUID; a successful response yields an interface ID that is stored in a session object and indexed by an xarray session ID returned to userspace.

Invoke loads the session under xarray lock, extracts opcode from `arg->func`, reads shared-memory ID and request length from `param[0].u.value`, optionally resolves the `tee_shm` and checks the request length, then sends the service call with memory handle, request length, and client ID. The response status becomes `arg->ret`, and response length is returned in `param[0].u.value.a` if it fits. Shared-memory registration first FF-A shares the pages, then sends `TS_RPC_OP_RETRIEVE_MEM`; unregister sends `TS_RPC_OP_RELINQ_MEM` and reclaims the memory handle.

## State and Persistence Behavior

Runtime state is held in `struct tstee` for the FF-A device, TEE device, and pool, and per context in an xarray of `struct ts_session` entries containing interface IDs. Shared-memory objects carry FF-A global handles in `shm->sec_world_id` until relinquished/reclaimed. No persistent storage exists.

## Dependencies and Integration Points

The driver depends on the Arm FF-A bus and message/memory ops, generic TEE core, dynamic shared-memory helpers in `tee_shm.c`, protocol constants from `tstee_private.h`, xarray, scatterlist helpers, and UUID matching. Userspace interacts through normal TEE open-session/invoke ioctls rather than object-invoke.

## Risks and Edge Cases

`tstee_invoke_func()` assumes `param[0]` is present and value-typed; it does not validate `arg->num_params` or attr before reading it, so malformed userspace input can reach driver-specific assumptions after generic conversion. Session lookup copies `iface_id` under lock but releases the lock before invocation; close can free the session concurrently after lookup, which is acceptable only because the copied byte is all that is needed. `tstee_shm_register()` must reclaim the FF-A handle on retrieve failure and does so, but unregister returns early on relinquish message failure and then does not reclaim memory. Response length is only returned if it is not larger than the SHM; oversized responses leave the old parameter value.

## Test Signals

Tests should cover RPC version mismatch, service UUID lookup success/failure, session open/close/invoke with invalid IDs, malformed parameter count/type for invoke, SHM ID zero and valid/invalid SHM IDs, request length larger than SHM, FF-A direct-message failures, memory-share retrieve/relinquish/reclaim failure paths, concurrent close during invoke, and module remove with open contexts or shared memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/core.c -->
