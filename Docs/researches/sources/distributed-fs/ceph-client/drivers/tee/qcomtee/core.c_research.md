<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/core.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/core.c

## Purpose

`core.c` implements the QTEE object model and transport message engine. It allocates kernel and QTEE object IDs, refcounts object lifetimes, marshals internal `qcomtee_arg` arrays into QTEE inbound/outbound buffers, handles callback requests from secure world, releases QTEE-hosted objects asynchronously, and provides helper calls to bootstrap a privileged client environment and open services.

## Important APIs, Types, and Functions

The file defines the static root object `qcomtee_object_root` with QTEE ID `QCOMTEE_MSG_OBJECT_ROOT`, and treats `qcomtee_primordial_object` as the first non-secure callback object ID (`BIT(31)`). `qcomtee_next_arg_type()` supports the argument iteration macros from `qcomtee_object.h`.

Object lifetime helpers include `qcomtee_object_user_init()`, `qcomtee_object_get()`, `qcomtee_object_put()`, `qcomtee_object_release()`, and QTEE-object allocation/free paths. `qcomtee_idx_alloc()`, `qcomtee_idx_erase()`, `qcomtee_object_id_get()`, and `qcomtee_local_object_get()` bridge local callback objects to QTEE-visible non-secure IDs.

Message conversion is split into `qcomtee_prepare_msg()` for outbound direct calls, `qcomtee_update_args()` for direct-call responses, `qcomtee_prepare_args()` for callback requests, and `qcomtee_update_msg()` for callback responses. `qcomtee_cb_object_invoke()` dispatches QTEE callback requests into local callback objects, including retain/release operations. `qcomtee_object_do_invoke_internal()` is the central invocation loop over SCM calls and callbacks; `qcomtee_object_do_invoke()` is the public checked wrapper. `qcomtee_object_get_client_env()` and `qcomtee_object_get_service()` are convenience bootstrapping helpers.

## Control Flow

Direct invocation first allocates inbound/outbound shared buffers, encodes the target object ID, copies input buffers, reserves output ranges, assigns IDs for input callback objects, and initializes QTEE message counts. It then calls either `qcom_scm_qtee_invoke_smc()` for the first entry or `qcom_scm_qtee_callback_response()` when returning from a callback. If secure world requests a callback (`QCOMTEE_RESULT_INBOUND_REQ_NEEDED`), the loop processes asynchronous messages, prepares callback arguments from the outbound buffer, invokes the local callback object's `dispatch()`, and submits the result on the next SCM call.

When a final direct-call result arrives, output buffers are copied back, output object IDs are converted into local `qcomtee_object` instances, and asynchronous release messages are fetched. QTEE-hosted object final puts are not freed inline: `qcomtee_release_qtee_object()` queues work that invokes QTEE's reserved RELEASE operation from the driver async context, retrying unless the device is gone.

## State and Persistence Behavior

There is no persistent storage. Runtime state is held in object krefs, the per-device `xa_local_objects` xarray, the cyclic local ID cursor, per-invocation `qcomtee_object_invoke_ctx` buffers/flags/current callback object, queued work items for QTEE-object release, and secure-world references retained by QTEE. `QCOMTEE_OIC_FLAG_SHARED` records whether callback-object ownership has already crossed into QTEE so failure cleanup switches from local release to treating the secure link as defunct.

## Dependencies and Integration Points

`core.c` depends on `qcom_scm_qtee_invoke_smc()` and `qcom_scm_qtee_callback_response()`, generic TEE shared-memory APIs for physical addresses via `shm.c`, xarray/RCU/kref/workqueue primitives, user/memory/primordial callback object implementations, and the transport structures in `qcomtee_msg.h`. It is called by `call.c`, by object wrappers in `mem_obj.c` and `user_obj.c`, and by probe-time version discovery.

## Risks and Edge Cases

Object ownership is subtle: input callback objects are handed to QTEE on successful transport entry and must be mimicked with local puts on early failure. `qcomtee_cb_object_invoke()` has a suspicious cleanup loop in the `qcomtee_prepare_args()` failure path that iterates input buffers while treating them as objects, which should be checked because input-object releases are the likely intent. `qcomtee_local_object_get()` returns the loaded pointer even if `qcomtee_object_get()` failed, so callers rely on NULL/zero-ref behavior and RCU timing. `qcomtee_prepare_msg()` does not undo the primary target callback object ID in all later failure modes. `qcomtee_update_msg()` only validates output-buffer sizes, not output-object type expectations. Release work retries indefinitely for transport errors other than `-ENODEV`, which can keep workqueue activity alive during persistent secure-world failure.

## Test Signals

Tests should cover direct calls with every argument kind, callback request/response loops, QTEE RETAIN/RELEASE callbacks, asynchronous release fetching, output object allocation failure, copy faults in input/output buffers, xarray exhaustion, transport errors before and after `QCOMTEE_OIC_FLAG_SHARED`, release-work retry and device removal, root/client-env/service bootstrapping, and static analysis for callback failure cleanup over the correct argument classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/core.c -->
