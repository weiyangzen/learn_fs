<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/call.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/call.c

## Purpose

`call.c` is the Linux TEE character-device integration layer for Qualcomm TEE object invocations. It registers the `qcomtee` platform driver, allocates the `tee_device`, creates the QTEE shared-memory pool, opens the driver-owned context used for asynchronous object releases, exposes QTEE version/capability data, and translates user ioctl OBJREF/UBUF parameters into the internal `qcomtee_arg` object/buffer ABI.

## Important APIs, Types, and Functions

The file owns `qcomtee_ops` and `qcomtee_desc`, wiring `.object_invoke_func`, `.supp_recv`, and `.supp_send` into the generic TEE core. Per-open state is `struct qcomtee_context_data` from `qcomtee.h`, with an IDR of QTEE-hosted objects, an IDR/list/completion for supplicant callback requests, and a `released` flag.

`qcomtee_open()`, `qcomtee_close_context()`, and `qcomtee_release()` allocate, drain, and free per-context IDRs and hold a `tee_device` reference for QTEE-owned callback-object references. `qcomtee_context_add_qtee_object()`, `qcomtee_context_find_qtee_object()`, and `qcomtee_context_del_qtee_object()` manage QTEE-hosted object handles visible to userspace. `qcomtee_objref_to_arg()` and `qcomtee_objref_from_arg()` translate between TEE OBJREF flags (`TEE`, `USER`, `MEM`) and `struct qcomtee_object *`.

`qcomtee_params_check()` enforces QTEE's 64-total and 16-per-kind argument limits. `qcomtee_object_invoke()` is the primary ioctl path, including root-object checks and reserved RELEASE handling. `qcomtee_supp_recv()` and `qcomtee_supp_send()` adapt generic supplicant ioctls to user-object request queues. `qcomtee_probe()` and `qcomtee_remove()` manage device registration, workqueue lifetime, QTEE version discovery, and cleanup.

## Control Flow

On probe, the driver allocates `struct qcomtee`, creates a dynamic QTEE shared-memory pool, allocates and registers a generic TEE device, starts an ordered workqueue for asynchronous releases, opens a private context via `teedev_open()`, initializes the local object xarray, then queries the feature-version service through a privileged client environment.

For `TEE_IOC_OBJECT_INVOKE`, the generic TEE core passes an invoke arg and parameter array into `qcomtee_object_invoke()`. The function validates parameter counts and types, handles `QCOMTEE_MSG_OBJECT_OP_RELEASE` by deleting a context IDR entry, selects root for `TEE_OBJREF_NULL` or finds an existing QTEE object by ID, converts parameters to `qcomtee_arg`, calls `qcomtee_object_do_invoke()`, then copies output sizes/objects back to the user parameter array and releases transient object references.

Supplicant receive requires a meta `VALUE_INOUT` parameter containing an aligned user buffer pointer and size. The user-object layer selects a queued request, fills subsequent parameters, and returns object ID/request ID/op metadata. Supplicant send requires a meta `VALUE_OUTPUT` request ID and forwards response parameters to the queued request.

## State and Persistence Behavior

The file persists no on-disk state. Runtime state is per TEE context: QTEE object ID mappings, supplicant request queues, mutexes, and completion state. Driver-global state lives in `struct qcomtee`: `tee_device`, shared-memory pool, async workqueue, driver context, local object xarray, cyclic ID cursor, and cached QTEE version. Removal drains the private context and waits for the generic TEE device reference count to drop before destroying the workqueue and pool.

## Dependencies and Integration Points

`call.c` integrates with generic TEE core APIs (`tee_device_alloc/register/unregister`, `teedev_open/close`, `tee_shm_pool_free`), the qcomtee object/memory/user object helpers, Linux IDR/xarray/refcount primitives, and Qualcomm SCM transport through `core.c`. Userspace reaches this file through `/dev/tee*` object invoke and supplicant ioctls. It depends on `shm.c` for `qcomtee_shm_pool_alloc()` and on `qcomtee_msg.h` for root/feature operation numbers and version decoding.

## Risks and Edge Cases

`find_qtee_object()` calls `qcomtee_object_get(*object)` even when `idr_find()` returns NULL; this is safe only because `qcomtee_object_get()` treats `NULL_QCOMTEE_OBJECT` as non-retainable, but it makes missing entries collapse to `-EINVAL`. Root-object filtering blocks privileged root operations and null credentials from userspace, but any omission there would expose privileged QTEE actions. Parameter conversion paths have multiple ownership transitions for callback objects; failure cleanup must match the extra driver copy and QTEE ownership handoff exactly. `qcomtee_get_qtee_feature_list()` returns silently on allocation/service lookup failures and may print a zero version. Probe's `platform_set_drvdata()` happens before async setup completes, so error paths must not assume remove semantics.

## Test Signals

Useful tests include open/close under object and supplicant load, invalid parameter counts and unsupported attrs, per-type count limits, root reserved-op denial, RELEASE of valid and invalid object IDs, user/memory/QTEE OBJREF round trips, copy fault injection for UBUF parameters, supplicant receive/send metadata validation, QTEE feature query failure, probe error injection at pool/device/workqueue/context allocation, and module removal while QTEE-object releases are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/call.c -->
