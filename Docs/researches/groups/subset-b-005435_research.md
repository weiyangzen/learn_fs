# subset-b-005435 Research

This grouped report covers Qualcomm QTEE object transport, generic Linux TEE core/shared-memory infrastructure, Arm Trusted Services TEE over FF-A, and two platform thermal drivers under `sources/distributed-fs/ceph-client`. Each section preserves its original source path for source-tree-aligned reconciliation into per-file research documents.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/mem_obj.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/mem_obj.c

## Purpose

`mem_obj.c` wraps generic TEE shared-memory handles as QTEE callback objects so secure world can map Linux memory through QTEE's object protocol. It represents a `tee_shm` as a memory object and reuses that same wrapper as the mapping object returned to QTEE.

## Important APIs, Types, and Functions

`struct qcomtee_mem_object` embeds `struct qcomtee_object`, stores the backing `tee_shm`, and caches page-aligned physical address and size. `is_qcomtee_memobj_object()` identifies this object class by comparing callback ops. `qcomtee_memobj_param_to_object()` converts a userspace OBJREF with `QCOMTEE_OBJREF_FLAG_MEM` into a retained `tee_shm` wrapper. `qcomtee_memobj_param_from_object()` converts the wrapper back to a shared-memory ID if it belongs to the same TEE context. `qcomtee_mem_object_map()` returns physical address, size, RW permission, and a retained mapping object.

## Control Flow

During parameter conversion, the object ID is resolved with `tee_shm_get_from_id()`, a callback object is initialized with a name like `tee-shm-%d`, and the wrapper is returned as an input object to QTEE. Secure world requests mapping indirectly through the primordial object, which calls `qcomtee_mem_object_map()`. Mapping takes another reference to the same wrapper, fills address/length/permission fields, and hands that object back to QTEE; unmap is represented by QTEE releasing the mapping object, which eventually calls `qcomtee_mem_object_release()`.

## State and Persistence Behavior

State is transient. The memory wrapper keeps a reference to `tee_shm` until the object kref reaches zero, at which point `tee_shm_put()` and `kfree()` run. There is no separate map table or persistent mapping state in this file; QTEE owns the lifecycle by retaining and releasing object references.

## Dependencies and Integration Points

This file depends on generic `tee_shm_get_from_id()`/`tee_shm_put()`, the qcomtee object callback API, Qualcomm SCM permission constants (`QCOM_SCM_PERM_RW`), and `primordial_obj.c` for the privileged map operation. It also depends on `tee_shm` exposing physical address and size fields populated by the selected shared-memory pool.

## Risks and Edge Cases

`qcomtee_mem_object_dispatch()` rejects all direct operations, intentionally forcing map through the primordial object to avoid user-forged memory objects. That security property depends on `primordial_obj.c` validating the object type before calling `qcomtee_mem_object_map()`; the current map helper itself assumes the input is a memory object and uses `container_of()`. `qcomtee_memobj_param_from_object()` drops the object reference when exposing the original shm ID, so callers must not reuse that wrapper afterward. The implementation maps the full `tee_shm` with RW permission and has no subrange or read-only controls.

## Test Signals

Test valid and invalid MEM OBJREF IDs, same-context and cross-context conversion back to OBJREF, map requests through the primordial object, release of mapping objects, `tee_shm` lifetime under repeated map/unmap, forged non-memory callback objects passed to map, and physical address/size/page-alignment assumptions for dynamic and reserved shared-memory pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/mem_obj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/primordial_obj.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/primordial_obj.c

## Purpose

`primordial_obj.c` defines the kernel-hosted primordial QTEE callback object. It provides privileged native services to secure world: mapping a Linux memory object, yielding the current thread, and sleeping for a requested duration.

## Important APIs, Types, and Functions

The supported operation IDs are `QCOMTEE_OBJECT_OP_MAP_REGION`, `QCOMTEE_OBJECT_OP_YIELD`, and `QCOMTEE_OBJECT_OP_SLEEP`. `struct qcomtee_mapping_info` is the packed ABI returned to QTEE with physical address, length, and permissions. `qcomtee_primordial_obj_dispatch()` implements the operations. `qcomtee_primordial_obj_notify()` releases a produced map object if the callback response fails. The exported static object is `qcomtee_primordial_object`.

## Control Flow

For YIELD, dispatch calls `cond_resched()` and sets no output object. For SLEEP, it requires one input buffer of at least `u32`, reads milliseconds from the shared callback buffer, calls `msleep()`, and sets no output object. For MAP_REGION, it requires three arguments: output buffer for mapping info, input object for the memory object, and output object for the mapping object. It invokes `qcomtee_mem_object_map()`, places the mapping object into `args[2]`, stores it in `oic->data` for later notify cleanup, and puts the input memory-object reference.

## State and Persistence Behavior

The primordial object is static and not refcounted like normal callback objects. Per-call state is only `oic->data`, used to remember an output mapping object until the response is accepted by QTEE. No data persists after callback completion except references QTEE retains to the returned mapping object.

## Dependencies and Integration Points

This file integrates with `core.c` through the reserved non-secure primordial object ID and callback dispatch path. It depends on `mem_obj.c` for mapping, on the qcomtee object argument ABI, and on kernel scheduler/timer helpers `cond_resched()` and `msleep()`.

## Risks and Edge Cases

The map path does not check `qcomtee_mem_object_map()`'s return value and does not explicitly verify that `args[1].o` is a qcomtee memory object before mapping, so a malformed or unexpected callback object can make `container_of()` unsafe through the helper. Sleep trusts the input buffer value and may block the invoking path for a long time. Yield and sleep are QTEE-triggered scheduling behaviors in the context of the thread currently servicing secure world, so latency and signalability should be evaluated. Mapping cleanup relies on notify being called with an error if QTEE did not receive the response.

## Test Signals

Tests should cover exact argument signatures for all three ops, short input/output buffers, invalid op codes, forged non-memory objects for MAP_REGION, QTEE response failure after creating a mapping object, sleep durations including zero and large values, and callback-loop behavior when yield/sleep occurs during direct invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/primordial_obj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee.h -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee.h

## Purpose

`qcomtee.h` is the internal umbrella header for the Qualcomm QTEE driver. It collects the transport/message and object headers, defines OBJREF flag semantics, declares the main driver and per-context state structures, and exposes cross-file APIs for shared memory, object invocation, user objects, primordial services, and memory objects.

## Important APIs, Types, and Functions

OBJREF flags distinguish QTEE-hosted objects (`QCOMTEE_OBJREF_FLAG_TEE`), userspace callback objects (`QCOMTEE_OBJREF_FLAG_USER`), and memory objects (`QCOMTEE_OBJREF_FLAG_MEM`). `struct qcomtee` holds the registered `tee_device`, shared-memory pool, private async context, reusable invocation context, ordered workqueue, local-object xarray, cyclic ID cursor, and cached version. `struct qcomtee_context_data` holds each open file/context's QTEE object IDR, supplicant request IDR/list, locks, completion, and release state.

The header declares conversion functions for context object mappings and OBJREFs, the internal object invocation entry point, message buffer allocation/free functions, asynchronous request helpers, QTEE shared-memory pool allocation, user-object request select/submit functions, and memory-object map/conversion helpers.

## Control Flow

The declarations reflect the cross-file pipeline: `call.c` receives generic TEE params and uses OBJREF converters; `core.c` marshals objects and messages and calls buffer allocation in `shm.c`; callback dispatch may enter `user_obj.c`, `primordial_obj.c`, or `mem_obj.c`; asynchronous releases use `qcomtee_fetch_async_reqs()` and `qcomtee_idx_erase()` to reconcile secure-world object references with the local xarray.

## State and Persistence Behavior

This header owns no storage, but it defines the state layout for the driver and per-context lifetimes. The state is strictly runtime: open contexts, IDR/xarray mappings, pending requests, completion waiters, shared-memory buffers, and secure-world object handles. There is no file-backed persistence.

## Dependencies and Integration Points

`qcomtee.h` depends on Linux kobject/TEE core definitions and the local `qcomtee_msg.h` and `qcomtee_object.h`. Its declarations are used across every qcomtee `.c` file and by the platform driver's TEE registration. It also creates the contract between QTEE-specific OBJREF flags and the generic TEE ioctl parameter model.

## Risks and Edge Cases

Because ownership rules are mostly documented across function comments instead of encoded in types, it is easy for callers to miss required gets/puts for objects or contexts. The `qcomtee` struct contains a reusable `oic` for async releases, so callers must serialize work through the ordered workqueue as implemented. `struct qcomtee_context_data.released` is protected by `reqs_lock`; any future direct access without the lock would race with supplicant teardown.

## Test Signals

Static checks should verify every declaration is implemented and that qcomtee files include this header rather than duplicating contracts. Runtime tests should stress object/context reference counts, local-object xarray allocation bounds, supplicant queue locking, and the three OBJREF flag classes through both normal and failure conversion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_msg.h -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_msg.h

## Purpose

`qcomtee_msg.h` defines the Qualcomm TEE transport message ABI used in shared inbound and outbound buffers. It documents object IDs, argument layouts, count packing, callback message formats, service operation constants, QTEE version decoding, and conversion from Linux errors to QTEE message results.

## Important APIs, Types, and Functions

`QCOMTEE_MSG_OBJECT_NS_BIT` marks kernel-hosted object IDs. Static QTEE IDs are `QCOMTEE_MSG_OBJECT_NULL` and `QCOMTEE_MSG_OBJECT_ROOT`. `union qcomtee_msg_arg` encodes either a buffer `(offset, size)` pair or object ID. `struct qcomtee_msg_object_invoke` encodes direct calls, while `struct qcomtee_msg_callback` encodes secure-world callback requests and responses.

Count masks (`QCOMTEE_MASK_IB`, `OB`, `IO`, `OO`) and inline helpers compute per-kind counts, starting indexes, total args, and iteration ranges. `qcomtee_msg_init()` packs cumulative argument counters into four 4-bit fields. `qcomtee_msg_buffer_args()` and `qcomtee_msg_offset_to_ptr()` locate buffer payloads after the variable argument array. The header also defines reserved object operations RELEASE/RETAIN, root/client-env/feature service operation IDs, transport result constants, and `qcomtee_msg_set_result()`.

## Control Flow

`core.c` uses this ABI when preparing direct invocation messages in inbound shared memory, parsing final direct-call responses, parsing callback requests in outbound shared memory, and writing callback responses back into the outbound buffer. Arguments are ordered by kind: input buffers, output buffers, input objects, and output objects. Buffer payloads are stored after the message header/argument table and aligned to 64-bit boundaries.

## State and Persistence Behavior

The header is declarative and owns no persistent state. Message structures are transient contents of per-invocation TEE shared-memory buffers. The constants define the stable ABI that both Linux and QTEE must interpret identically across each invocation.

## Dependencies and Integration Points

The header depends on Linux bitfield helpers and is included by `qcomtee_object.h` and `qcomtee.h`. Its root and feature-service constants are used by `call.c` and `core.c`, while error mappings are used during callback response submission. The ABI is also coupled to Qualcomm SCM calls that receive physical addresses and sizes for inbound/outbound buffers.

## Risks and Edge Cases

Each argument-kind count is 4 bits, so callers must enforce the 16-per-kind maximum before calling `qcomtee_msg_init()`. The initializer expects cumulative indexes rather than independent counts, which is compact but easy to misuse. Message parsing assumes QTEE-provided offsets and sizes are within the allocated buffers; allocation code bounds Linux-originated messages, but response/callback offsets from QTEE deserve careful validation. Error mapping collapses many Linux errors into generic QTEE result codes, which can hide actionable failure causes.

## Test Signals

ABI tests should verify count packing/unpacking, argument index calculations for mixed argument lists, 64-bit buffer alignment, struct header sizes, maximum per-kind limits, reserved operation values, root/feature service constants, version decoding macros, and `qcomtee_msg_set_result()` mappings for common kernel errors and user-defined positive errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_object.h -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_object.h

## Purpose

`qcomtee_object.h` defines QTEE's in-kernel object abstraction: object types, invocation arguments, invocation context, callback operations, object lifetime APIs, and helper iteration macros. It is the semantic contract for passing QTEE-hosted objects, kernel callback objects, root/null objects, and buffers through the QTEE transport.

## Important APIs, Types, and Functions

`enum qcomtee_object_type` distinguishes TEE-hosted, callback, root, and null objects. `enum qcomtee_arg_type` distinguishes input/output buffers and input/output objects, with `QCOMTEE_ARGS_PER_TYPE` and `QCOMTEE_ARGS_MAX` defining ABI limits. `struct qcomtee_arg` stores buffer or object data and the `QCOMTEE_ARG_FLAGS_UADDR` marker for userspace buffers. `struct qcomtee_object_invoke_ctx` stores the TEE context, invocation flags, callback status, current object, argument scratch array, inbound/outbound buffers and backing `tee_shm`s, plus opaque callback data.

`struct qcomtee_object_operations` supplies callback-object `release`, `dispatch`, and `notify` hooks. `struct qcomtee_object` stores name, kref, type, QTEE ID or async context, ops, and release work. Inline helpers classify/name objects, allocate invocation contexts, count args, and iterate by argument kind. Public functions include `qcomtee_object_do_invoke()`, `qcomtee_object_user_init()`, `qcomtee_object_get()/put()`, `qcomtee_next_arg_type()`, and service bootstrap helpers.

## Control Flow

Callers build a `qcomtee_arg` array terminated by `QCOMTEE_ARG_TYPE_INV`, pass it and a root/TEE object to `qcomtee_object_do_invoke()`, and receive updated output buffers/objects in place. Callback objects embed `struct qcomtee_object`, initialize it with callback ops, and are invoked by QTEE through `dispatch()`. `notify()` runs after a callback response is submitted, allowing cleanup that depends on whether QTEE accepted the response.

## State and Persistence Behavior

The header defines runtime-only state: object krefs, QTEE object IDs, async context references, invocation scratch buffers, and callback work. Static root and primordial objects are special and not normal kref-owned objects. No persistent state exists.

## Dependencies and Integration Points

It depends on Linux completion/kref/slab/workqueue APIs and on `tee_context`/`tee_shm` types. Every qcomtee implementation file uses these definitions, and generic TEE object ioctl handling in `call.c` ultimately feeds this object abstraction.

## Risks and Edge Cases

Ownership rules are complex: on successful invocation QTEE takes ownership of input callback objects, while the driver often holds temporary extra references to protect conversion paths. Static objects intentionally bypass kref operations, so code must never assume `qcomtee_object_get()` succeeds for root/null/primordial. The argument array is sentinel-terminated; missing sentinels would cause out-of-bounds iteration. `QCOMTEE_OIC_FLAG_*` meanings are protocol state and must be updated consistently across callback loops.

## Test Signals

Tests should validate object init for allowed and disallowed types, null/root/primordial get/put behavior, argument sentinel handling, per-kind iteration macros, callback release/notify ordering, service bootstrap helpers, and ownership transitions for input/output callback objects under success, QTEE result error, and transport failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/qcomtee_object.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/user_obj.c -->
# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/user_obj.c

## Purpose

`user_obj.c` implements QTEE user objects, also called supplicant callback objects. It lets userspace expose object references to QTEE, queues QTEE callback invocations as supplicant requests, converts callback arguments between QTEE and generic TEE ioctl parameter formats, and delivers userspace responses back to secure world.

## Important APIs, Types, and Functions

`struct qcomtee_user_object` embeds a callback object, stores the owning `tee_context`, userspace object ID, and release-notification flag. `struct qcomtee_ureq` stores queued callback request state, request ID, object ID, op, argument pointer, errno, list node, and completion. Request states are `QUEUED`, `PROCESSING`, and `PROCESSED`, with `empty_ureq` reserving IDs when the invoking thread dies while userspace is processing.

Queue helpers include `ureq_enqueue()`, `ureq_dequeue()`, `ureq_select()`, and `qcomtee_requests_destroy()`. Object operations are `qcomtee_user_object_dispatch()`, `qcomtee_user_object_notify()`, and `qcomtee_user_object_release()`. Public conversion and supplicant APIs are `qcomtee_user_param_to_object()`, `qcomtee_user_param_from_object()`, `qcomtee_user_object_select()`, and `qcomtee_user_object_submit()`.

## Control Flow

When userspace passes an OBJREF with `QCOMTEE_OBJREF_FLAG_USER`, parameter conversion wraps it in a `qcomtee_user_object`, retains the TEE context, and enables release notifications by default. If QTEE invokes the callback, dispatch allocates a `qcomtee_ureq`, queues it on the owning context, wakes supplicant receive waiters, and waits killably/freezably for `qcomtee_user_object_submit()` to complete it. On successful userspace response, `oic->data` retains the request until `notify()`, where output objects are put and the request is freed.

`qcomtee_user_object_select()` is called by supplicant receive. It waits for a queued request, verifies enough parameter slots and user buffer space, marks the request processing, copies input buffers into the supplied user buffer from the end downward with 8-byte alignment, converts input objects to OBJREF parameters, and reports request metadata. `qcomtee_user_object_submit()` removes the request by ID, converts returned output buffers/objects back into QTEE arguments, records errno, and completes the waiting invocation thread.

## State and Persistence Behavior

State is in each context's request IDR/list and completion, plus the callback object's context reference. Requests are transient and tied to a callback invocation, except release notifications that are queued and freed after selection without a response. On context close, `qcomtee_requests_destroy()` marks the context released, rejects new queues, completes queued/processing non-release requests with `-ENODEV`, and frees release notifications.

## Dependencies and Integration Points

This file integrates with `call.c` supplicant ioctls, `core.c` callback dispatch and notify sequencing, generic TEE context reference helpers, qcomtee OBJREF conversion helpers, Linux IDR/list/completion/mutex primitives, and userspace copy helpers. It is central to exposing QTEE callbacks to user processes.

## Risks and Edge Cases

The request structure stores a pointer to the invocation's `qcomtee_arg` array, so lifetime is safe only while dispatch is blocked or `oic->data` retains the request for notify. The interrupted-wait path is delicate: if userspace already processed the request, the dispatcher may still accept the response; if processing is ongoing, `empty_ureq` prevents ID reuse and forces submit failure. `ureq_select()` finds queued requests FIFO but returns `-EINVAL` for insufficient user buffer/params without skipping to later requests, so one oversized request can block the queue until it is completed with error. Output object cleanup in failure paths must account for extra driver references and QTEE ownership. Release notification queuing can be silently dropped under memory pressure or after context release.

## Test Signals

Tests should exercise supplicant receive blocking and interrupt paths, FIFO ordering, undersized parameter array and UBUF space, input buffer copying/alignment, output buffer size rejection, user/memory/QTEE object conversions in callback arguments, response to stale or `empty_ureq` IDs, context close with queued and processing requests, release-notification delivery/drop, and killable wait behavior when invoking and supplicant threads share a process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/qcomtee/user_obj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_core.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_core.c

## Purpose

`tee_core.c` implements the generic Linux TEE character-device core and in-kernel client API. It manages `/dev/tee*` and `/dev/teepriv*` devices, TEE contexts, ioctl decoding/validation, shared-memory parameter resolution, supplicant request forwarding, TEE client bus registration, and exported helper APIs used by TEE drivers and kernel clients.

## Important APIs, Types, and Functions

Device/context lifecycle functions include `teedev_open()`, `teedev_close_context()`, `teedev_ctx_get()/put()`, `tee_device_alloc()`, `tee_device_register()`, `tee_device_unregister()`, `tee_device_get()/put()`, and `tee_get_drvdata()`. User ioctl handlers cover version, SHM alloc/register/register-fd, open session, invoke, object invoke, cancel, close session, supplicant recv, and supplicant send. Parameter conversion is handled by `params_from_user()`, `params_to_user()`, `params_to_supp()`, `params_from_supp()`, and `param_from_user_memref()`.

The file also implements `tee_session_calc_client_uuid()` using UUIDv5 over Linux uid/gid identities, the exported in-kernel client API (`tee_client_open_context()`, `tee_client_open_session()`, `tee_client_invoke_func()`, etc.), and the `tee_bus_type` plus `tee_client_driver` registration helpers.

## Control Flow

At subsystem init, the TEE class, character-device major range, and client bus are registered. A concrete TEE driver allocates a `tee_device` with mandatory operations, registers it, and userspace opens the character device. Each open creates a `tee_context` and calls the driver's `.open()`. Ioctls copy an argument header from userspace, validate total buffer length against `TEE_MAX_ARG_SIZE`, allocate `struct tee_param` arrays, convert user parameters, call the driver's operation, copy result fields and output parameter sizes/IDs back, then release any retained shared-memory references.

For object invocation, `tee_ioctl_object_invoke()` mirrors classic session invoke but dispatches to `.object_invoke_func` and supports OBJREF parameter types. Supplicant ioctls convert between normal TEE parameter representation and the lighter userspace supplicant format, then call driver `.supp_recv`/`.supp_send`.

## State and Persistence Behavior

Global runtime state includes a 32-device bitmap, global class, device number range, and TEE bus. Each `tee_device` tracks ID, name, device/cdev, descriptor, pool, IDR of shared-memory objects, mutex, user count, and unregister completion. Each `tee_context` tracks the driver context, refcount, release state, and supplicant waiting policy. There is no durable storage.

## Dependencies and Integration Points

The core depends on Linux char-device, driver core, IDR, credentials, uaccess, DMA-buf shared-memory support, SHA-1 for UUIDv5, and public `linux/tee_core.h`/ioctl ABI definitions. Concrete integrations in this work item include qcomtee's object-invoke/supplicant callbacks, tstee's classic open-session/invoke functions, and shared-memory support in `tee_shm.c`, `tee_heap.c`, and `tee_shm_pool.c`.

## Risks and Edge Cases

Length validation relies on overflow-aware `size_add()`/`size_mul()` in most paths; object invoke uses a direct equality with `sizeof(arg) + TEE_IOCTL_PARAM_SIZE()` that should be reviewed for overflow parity. `teedev_ctx_get()` silently returns when `ctx->releasing`, which can make misuse hard to detect. `match_dev()` dereferences `teedev->desc` during class iteration without taking `tee_device_get()`, relying on device lifetime and unregister sequencing. Shared-memory memref conversion must unwind references on any later ioctl error. Object and OBJREF parameter types increase the attack surface for drivers that did not historically handle user-controlled object IDs.

## Test Signals

Tests should cover all ioctl buffer length boundaries and overflow cases, bad user pointers, every supported parameter type, MEMREF null capability, shared-memory ID ownership and refcount cleanup, open-session failure after session creation, object-invoke OBJREF output copying, supplicant recv/send conversions, device unregister with open contexts, class/client-bus probing, and KASAN/refcount checks for context release races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_heap.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_heap.c

## Purpose

`tee_heap.c` implements optional DMA-BUF heap support for TEE protected memory and a static protected-memory pool implementation. It lets TEE drivers expose named protected DMA heaps and translate DMA-BUF allocations back into `tee_shm` objects for secure-world sharing.

## Important APIs, Types, and Functions

When `CONFIG_TEE_DMABUF_HEAPS` is enabled, `struct tee_dma_heap` tracks a heap ID, kref, protected memory pool, owning `tee_device`, shutdown state, and mutex. `struct tee_heap_buffer` stores exported buffer size, pool offset, scatter-gather table, and heap pointer. DMA-BUF ops include `tee_heap_attach()`, `tee_heap_detach()`, `tee_heap_map_dma_buf()`, `tee_heap_unmap_dma_buf()`, and `tee_heap_buf_free()`. `tee_dma_heap_alloc()` allocates from the protected pool and exports a DMA-BUF.

Exported APIs are `tee_device_register_dma_heap()`, `tee_device_put_all_dma_heaps()`, and `tee_heap_update_from_dma_buf()`. Static protected-memory APIs include `tee_protmem_static_pool_alloc()` and ops for alloc/free/update/destroy backed by `gen_pool`.

## Control Flow

A TEE driver registers a protected-memory pool under a known heap ID. The first registration creates a named DMA heap such as `protected,secure-video`; later registrations can reuse a heap entry after shutdown cleared its device pointer. Userspace allocates DMA-BUFs from that heap, and `tee_dma_heap_alloc()` gets a heap reference, allocates protected memory into an SG table, exports a DMA-BUF, and drops the heap reference when the DMA-BUF is released. Registering a DMA-BUF as TEE shared memory calls `tee_heap_update_from_dma_buf()`, which verifies the DMA-BUF ops and owning device, then asks the pool to fill the `tee_shm` physical/security fields.

## State and Persistence Behavior

State is runtime-only in a global xarray keyed by `enum tee_dma_heap_id`, per-heap krefs and shutdown flags, and per-DMA-BUF SG tables. Static protected pools keep a gen_pool and base physical address until destroyed. Device unregister calls `tee_device_put_all_dma_heaps()` to mark matching heaps shutting down and drop the device/pool reference when no buffers remain.

## Dependencies and Integration Points

This file depends on DMA-BUF heap APIs, scatterlist and DMA mapping helpers, xarray, kref, gen_pool, and TEE protected-memory pool interfaces from `tee_core.h`. It integrates with `tee_shm.c` through `tee_shm_register_fd()` and `tee_heap_update_from_dma_buf()`, and with generic TEE device unregister in `tee_core.c`.

## Risks and Edge Cases

The disabled-config stubs return `-EINVAL`, so callers must degrade cleanly when DMA-BUF heaps are not built. Heap reuse after shutdown depends on mutex-protected `teedev` and `pool` replacement; leaked DMA-BUFs keep the old pool alive through krefs. `tee_heap_update_from_dma_buf()` rejects DMA-BUFs not produced by this exact ops table and from other TEE devices, which is correct but can surprise cross-device users. Static pool allocation does not round the requested size before `gen_pool_alloc()`, so callers/pools must provide appropriate sizes. Protected memory may be inaccessible to the kernel while lent to TEE, so CPU mappings and DMA sync assumptions must remain constrained.

## Test Signals

Tests should cover heap registration, duplicate registration, unregister while buffers are open, DMA-BUF allocate/export/release, attach/map/unmap/detach on multiple devices, `tee_shm_register_fd()` for valid and invalid DMA-BUFs, static pool alignment and PFN validation, pool exhaustion, and disabled `CONFIG_TEE_DMABUF_HEAPS` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_private.h -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_private.h

## Purpose

`tee_private.h` declares private interfaces shared by the generic TEE core, shared-memory implementation, and DMA-BUF heap support. It is not a public driver ABI; it coordinates internal shared-memory allocation, registration, file-descriptor export, and DMA-BUF backed TEE shared memory.

## Important APIs, Types, and Functions

`struct tee_shm_dmabuf_ref` extends `struct tee_shm` with DMA-BUF registration metadata: offset, `struct dma_buf *`, and optional parent `tee_shm`. Declared helpers include `tee_shm_get_fd()`, `tee_shm_alloc_user_buf()`, `tee_shm_register_user_buf()`, and `tee_heap_update_from_dma_buf()`.

## Control Flow

`tee_core.c` calls the user-buffer allocation/registration helpers from SHM ioctls and calls `tee_shm_get_fd()` before returning a file descriptor. `tee_shm.c` allocates `tee_shm_dmabuf_ref` for `TEE_IOC_SHM_REGISTER_FD` and calls `tee_heap_update_from_dma_buf()` to resolve protected DMA-BUFs. `tee_heap.c` implements that update hook when heap support is enabled.

## State and Persistence Behavior

The header defines only in-memory structures. DMA-BUF references persist while the corresponding `tee_shm` refcount is nonzero; parent `tee_shm` references can outlive the wrapper when protected-memory heaps require indirection. No persistent storage exists.

## Dependencies and Integration Points

The header depends on Linux cdev, completion, device, DMA-BUF, kref, mutex, and TEE types. It bridges `tee_core.c`, `tee_shm.c`, and `tee_heap.c`, and is intentionally local to the TEE subsystem.

## Risks and Edge Cases

Because this header exposes private helpers, adding users outside the TEE core can create layering problems. `tee_shm_dmabuf_ref` embeds `struct tee_shm`, so code must use the correct `container_of()` path based on `TEE_SHM_DMA_BUF`. Parent shared-memory lifetime must be handled carefully to avoid leaking or prematurely freeing protected-memory mappings.

## Test Signals

Build tests should catch mismatches between declarations and implementations under both enabled and disabled DMA-BUF heap configs. Runtime checks should cover SHM fd export, user SHM registration, DMA-BUF registration with and without parent SHM, and refcount cleanup for wrapper and parent objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_shm.c

## Purpose

`tee_shm.c` implements generic TEE shared-memory allocation, registration, lookup, file-descriptor export, mmap, refcounting, and dynamic helper routines. It supports pool-backed allocations, registered user/kernel buffers, DMA-BUF heap backed protected memory, and private driver buffers.

## Important APIs, Types, and Functions

Allocation APIs include `tee_shm_alloc_user_buf()`, `tee_shm_alloc_kernel_buf()`, `tee_shm_alloc_priv_buf()`, and optional `tee_shm_alloc_dma_mem()`. Registration APIs include `tee_shm_register_user_buf()`, `tee_shm_register_kernel_buf()`, and `tee_shm_register_fd()`. Dynamic pool helpers are `tee_dyn_shm_alloc_helper()` and `tee_dyn_shm_free_helper()`. Access/lifetime APIs are `tee_shm_get_fd()`, `tee_shm_free()`, `tee_shm_get_va()`, `tee_shm_get_pa()`, `tee_shm_get_from_id()`, and `tee_shm_put()`.

Internal helpers include `shm_alloc_helper()`, `register_shm_helper()`, `release_registered_pages()`, and `tee_shm_release()`. `struct tee_shm_dma_mem` wraps DMA pages when DMA heap support is enabled.

## Control Flow

User allocation reserves an IDR slot, allocates from the device pool, then replaces the IDR placeholder with the `tee_shm` and returns an fd. User registration pins/extracts pages from a user iterator, calls driver `.shm_register()`, installs the SHM in the IDR, and returns an fd. Private/kernel allocations are not normally IDR-visible. Registering an fd gets a DMA-BUF, verifies it through `tee_heap_update_from_dma_buf()`, installs a wrapper SHM in the IDR, and returns it.

All refs converge through `tee_shm_put()`: the last ref removes the IDR entry while holding the device mutex so future lookups cannot increment from zero, then `tee_shm_release()` frees according to flags: DMA pages, DMA-BUF wrapper, pool allocation, or dynamic registered memory with unregister and page unpin.

## State and Persistence Behavior

Shared-memory state is runtime-only. Each `tee_shm` tracks refcount, flags, ID, context, virtual/physical address, size, offset, pages, page count, and secure-world ID if assigned by a driver. User-visible allocated/registered SHM persists until all file descriptors, parameter references, and driver references are released.

## Dependencies and Integration Points

This file depends on generic TEE device/context state from `tee_core.c`, per-driver shared-memory pool ops from `tee_shm_pool.c` and qcomtee/tstee pools, optional DMA-BUF heap logic from `tee_heap.c`, Linux page pinning/extraction, anon inode fd creation, and DMA APIs. Concrete drivers use `tee_shm_alloc_priv_buf()` for transport buffers and `.shm_register()`/`.shm_unregister()` callbacks for secure-world registration.

## Risks and Edge Cases

Bounds checks reject offsets `>= shm->size`, so zero-size shared-memory objects would be unusable for VA/PA access. `tee_shm_get_va()` requires `kaddr`; registered user buffers and DMA-BUF wrappers may not have one. `register_shm_helper()` page-count handling after partial extraction is delicate and must unpin exactly what was pinned. `tee_shm_fop_mmap()` refuses user-mapped and DMA-BUF SHM but remaps physical pages for pool-backed memory; cacheability and memory attributes depend on the original allocation. `tee_dyn_shm_free_helper()` calls unregister but ignores its return. IDR removal before release prevents refcount resurrection and is critical to preserve.

## Test Signals

Tests should cover SHM alloc/register/free by fd close and explicit put, lookup by valid/invalid ID and wrong context, memref offset/size boundary checks through `tee_core.c`, mmap allowed and denied cases, dynamic helper allocation/register failure unwind, user page pin/unpin accounting, DMA-BUF registration paths, private buffer VA/PA retrieval, concurrent lookup and final put, and unregister failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm_pool.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_shm_pool.c

## Purpose

`tee_shm_pool.c` implements a generic reserved-memory TEE shared-memory pool backed by `gen_pool`. It is used by TEE drivers that have a statically reserved shared-memory region rather than dynamic per-buffer registration.

## Important APIs, Types, and Functions

`pool_op_gen_alloc()` allocates aligned zeroed chunks from a `gen_pool`, fills `tee_shm->kaddr`, `paddr`, `size`, and clears `TEE_SHM_DYNAMIC`. `pool_op_gen_free()` frees a chunk and clears `kaddr`. `pool_op_gen_destroy_pool()` destroys the gen_pool and frees the wrapper. `tee_shm_pool_alloc_res_mem()` validates page-aligned virtual address, physical address, and size, creates a gen_pool, adds the virtual/physical range, and returns a `tee_shm_pool`.

## Control Flow

A driver calls `tee_shm_pool_alloc_res_mem()` during probe with a pre-mapped reserved memory range. Generic TEE allocation paths call the pool's `.alloc` op, which rounds allocation size up to the selected alignment, gets a chunk from the gen_pool, zeroes it, and returns physical/virtual fields to the `tee_shm`. Free returns the exact allocated size to the pool. Destroy tears down the gen_pool when the driver is removed.

## State and Persistence Behavior

State is in the gen_pool allocation bitmap and the pool's private_data pointer. Shared-memory chunks persist until the corresponding `tee_shm` is released. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on Linux genalloc, device/DMA headers, and generic TEE pool interfaces. It is exported for drivers using reserved shared-memory carveouts; qcomtee and tstee in this work item use dynamic pools instead.

## Risks and Edge Cases

All inputs must be page aligned; non-page-aligned reserved ranges are rejected. Allocation alignment is the max of requested alignment and the gen_pool minimum order, and the size is rounded to that alignment, so callers may receive larger SHM than requested. Clearing `TEE_SHM_DYNAMIC` means no per-buffer secure registration/unregistration will occur; this is correct only when the reserved pool is already shared or globally known to secure world. Destroying a pool with outstanding allocations would be unsafe and must be prevented by device teardown ordering.

## Test Signals

Tests should cover page-alignment rejection, gen_pool create/add failure, allocation/free with different alignments, zeroing, physical address translation, pool exhaustion, destroy after all allocations are freed, and integration with `tee_shm_alloc_user_buf()` and mmap for reserved memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tee/tstee/Kconfig

## Purpose

`tstee/Kconfig` adds the build-time option for the Arm Trusted Services TEE driver. It exposes Trusted Services Secure Partitions over the generic Linux TEE userspace interface when FF-A transport is available.

## Important APIs, Types, and Functions

The config symbol is `ARM_TSTEE`, a tristate labeled "Arm Trusted Services TEE driver". It depends on `ARM_FFA_TRANSPORT` and defaults to `n`. The help text describes Trusted Services as a framework for Root of Trust services in FF-A Secure Partitions and states that this driver provides the userspace interface missing from the FF-A driver itself.

## Control Flow

When enabled as built-in or module, the Makefile builds `arm-tstee.o`, whose FF-A driver probes Secure Partitions advertising the Trusted Services RPC protocol UUID. If the symbol is disabled, no tstee TEE device is registered.

## State and Persistence Behavior

The Kconfig file has no runtime state. It controls whether driver code is compiled and therefore whether runtime TEE devices can appear for Trusted Services partitions.

## Dependencies and Integration Points

The dependency on `ARM_FFA_TRANSPORT` ensures the FF-A bus and messaging/memory-share operations used by `core.c` are present. The symbol integrates with the TEE core by selecting compilation of the tstee driver but does not itself select `TEE`; the build context must satisfy broader subsystem dependencies.

## Risks and Edge Cases

Because the option defaults off, platforms expecting Trusted Services userspace access must enable it explicitly. The dependency is narrow; any missing implicit dependency on TEE core symbols or architecture support would show up as build failures in unusual configs. The help text is descriptive but does not mention the module name.

## Test Signals

Config tests should build `ARM_TSTEE=y` and `m` with `ARM_FFA_TRANSPORT`, verify it is hidden or rejected without FF-A transport, and run compile tests for module load/unload plus FF-A probe matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tee/tstee/Makefile

## Purpose

`tstee/Makefile` maps the `ARM_TSTEE` Kconfig symbol to the Arm Trusted Services TEE driver object.

## Important APIs, Types, and Functions

It defines `arm-tstee-objs := core.o` and builds `arm-tstee.o` when `CONFIG_ARM_TSTEE` is enabled. There are no functions or runtime APIs in this file.

## Control Flow

Kbuild compiles `core.c` into `core.o`, links it into the composite `arm-tstee.o`, and includes that object as built-in or module according to the tristate value.

## State and Persistence Behavior

The file has no runtime state. It only affects build artifacts and module composition.

## Dependencies and Integration Points

It integrates with Linux Kbuild and the `ARM_TSTEE` symbol defined in `Kconfig`. Any future additional source files for this driver would need to be added to `arm-tstee-objs`.

## Risks and Edge Cases

The assignment uses `obj-$(CONFIG_ARM_TSTEE) = arm-tstee.o` rather than `+=`; this is acceptable in the local file but could overwrite earlier `obj-*` entries if more were added above. The module is single-source today, so dependency tracking is simple.

## Test Signals

Build with `CONFIG_ARM_TSTEE=y` and `m`, verify `core.o` is included in `arm-tstee.o`, and check that disabling the symbol removes the object from the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Makefile -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/tstee_private.h -->
# sources/distributed-fs/ceph-client/drivers/tee/tstee/tstee_private.h

## Purpose

`tstee_private.h` defines the Trusted Services RPC protocol constants and private driver state used by `tstee/core.c`. It encodes FF-A direct-message register positions, management/service opcodes, status bits, and per-device/per-session structures.

## Important APIs, Types, and Functions

`TS_RPC_UUID` is the protocol UUID matched on the FF-A bus. `TS_RPC_PROTOCOL_VERSION` is version 1. Control register helpers define opcode/interface masks, extractors, packer `TS_RPC_CTRL_PACK_IFACE_OPCODE()`, and SAP return/error bits. Management operations include GET_VERSION, RETRIEVE_MEM, RELINQ_MEM, and SERVICE_INFO with register indexes for handles, tags, status, and interface ID. Service-call indexes define memory handle, request length, client ID, RPC status, service status, and response length.

`struct tstee` stores the FF-A device, TEE device, and shared-memory pool. `struct ts_session` stores the Trusted Services interface ID. `struct ts_context_data` stores an xarray of sessions for each TEE context.

## Control Flow

The constants are consumed by `core.c` to format five 32-bit FF-A direct-message arguments. Management calls are sent during probe, session open, and shared-memory register/unregister. Service calls are sent during TEE invoke using the session's interface ID and the lower 16 bits of `arg->func` as opcode.

## State and Persistence Behavior

The header defines runtime-only device and context structures. Sessions persist for the lifetime of a TEE context or until explicitly closed. FF-A memory handles persist in individual `tee_shm` objects until unregistered.

## Dependencies and Integration Points

It depends on Arm FF-A types, bitops/bitfield helpers, TEE core types, UUID, xarray, and integer types. It is private to the tstee driver and tied to the Trusted Services service access protocol ABI referenced in the file comment.

## Risks and Edge Cases

Register indexes and bitfields are ABI constants; any drift from the Trusted Services specification breaks all messaging. The control register reserves SAP status bits but current core logic mostly checks per-call status registers. Interface ID is narrowed to `u8`, so service-info responses above `U8_MAX` are rejected by core. There are no compile-time assertions for the assumed five-register direct-message width.

## Test Signals

Tests should verify packed control register values, opcode/interface extraction, UUID matching, protocol version check, every management register index, interface ID boundary handling, and compatibility with Trusted Services protocol documentation for version 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/tstee_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/thermal/Kconfig

## Purpose

`drivers/thermal/Kconfig` defines the generic Linux thermal subsystem options, default governor selection, cooling-device support, optional diagnostics, and platform thermal driver choices. In this work item it is especially relevant for `AIROHA_THERMAL` and `AMLOGIC_THERMAL`.

## Important APIs, Types, and Functions

The top-level `THERMAL` menuconfig enables thermal zones, trip points, and cooling devices. Options include netlink, statistics, debugfs, emergency poweroff delay, hwmon exposure, device-tree helpers, emulation, governors (`fair_share`, `step_wise`, `bang_bang`, `user_space`, `power_allocator`), CPU/devfreq/PCIe cooling, and many platform drivers.

`AIROHA_THERMAL` is a tristate depending on `ARCH_AIROHA || COMPILE_TEST`, `MFD_SYSCON`, and `OF`. `AMLOGIC_THERMAL` is a tristate defaulting to `ARCH_MESON` and depending on `OF && ARCH_MESON`. The file also includes submenus for Mediatek, Intel, Broadcom, TI, Samsung, ST, Renesas, Tegra, and Qualcomm thermal drivers.

## Control Flow

Kconfig selection controls which thermal core components and platform drivers Kbuild compiles. Selecting a default governor selects the corresponding governor implementation. Enabling OF helpers allows platform drivers to register thermal zones from device tree. Platform symbols map to object files in `drivers/thermal/Makefile`.

## State and Persistence Behavior

Kconfig has no runtime state but determines compiled capabilities and defaults. Runtime thermal state is owned by the thermal core and platform drivers selected here.

## Dependencies and Integration Points

The file integrates the thermal subsystem with networking, hwmon, debugfs, OF, energy model, cpufreq, cpuidle, devfreq, PCIe, MFD/syscon, IIO, architecture symbols, and many platform subdirectories. It feeds directly into the Makefile's `obj-$(CONFIG_...)` selections.

## Risks and Edge Cases

Dependency choices can hide drivers from compile testing or accidentally prevent module builds on relevant platforms. `AMLOGIC_THERMAL` depends directly on `ARCH_MESON`, unlike many drivers that allow `COMPILE_TEST`, reducing broader build coverage. Emulation and emergency poweroff settings are powerful and risky on production systems. Default governor selection must ensure exactly one default and select required governor code.

## Test Signals

Config tests should validate default governor exclusivity, build matrix coverage for `THERMAL=y/m`, `AIROHA_THERMAL`, `AMLOGIC_THERMAL`, OF/hwmon/debugfs combinations, disabled dependency visibility, and generated Makefile object inclusion for selected platform symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Makefile -->
# sources/distributed-fs/ceph-client/drivers/thermal/Makefile

## Purpose

`drivers/thermal/Makefile` maps thermal subsystem Kconfig symbols to core, governor, cooling, platform, and testing object files. It is the Kbuild assembly point for the thermal framework and platform thermal drivers.

## Important APIs, Types, and Functions

The main `thermal_sys.o` composite is built when `CONFIG_THERMAL` is enabled and includes core files such as `thermal_core.o`, `thermal_sysfs.o`, `thermal_trip.o`, `thermal_helpers.o`, and `thermal_thresholds.o`. Conditional additions include netlink, debugfs, hwmon, OF, governors, CPU cooling, devfreq cooling, and PCIe cooling. Platform entries include `obj-$(CONFIG_AIROHA_THERMAL) += airoha_thermal.o` and `obj-$(CONFIG_AMLOGIC_THERMAL) += amlogic_thermal.o`, along with many other vendors and subdirectories.

## Control Flow

Kbuild expands each `obj-$(CONFIG_...)` and `thermal_sys-$(CONFIG_...)` according to the resolved configuration. Core and selected optional pieces are linked into `thermal_sys.o`; platform drivers become separate built-in or module objects depending on their symbols. Include flags are set for thermal core and power allocator governor sources.

## State and Persistence Behavior

The Makefile has no runtime state. It determines which object code is present in the kernel or modules.

## Dependencies and Integration Points

It integrates with `drivers/thermal/Kconfig`, Linux Kbuild, platform subdirectories, and optional subsystem configs. The Airoha and Amlogic driver source files in this work item are selected here.

## Risks and Edge Cases

Spacing is mostly conventional but mixed in a few entries, which is harmless to make. Unconditional `obj-y` subdirectories rely on their own Kconfig/Makefile guards. Missing entries here would make a Kconfig option ineffective; stale entries would cause build failures when source files are moved or renamed.

## Test Signals

Build tests should verify `thermal_sys.o` composition for major option combinations, module vs built-in output for platform drivers, inclusion of `airoha_thermal.o` and `amlogic_thermal.o` under their symbols, and absence of unresolved objects when optional submenus are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/airoha_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/airoha_thermal.c

## Purpose

`airoha_thermal.c` implements a thermal-zone driver for the Airoha EN7581 thermal sensor. It reads an ADC-backed diode sensor through SCU/syscon registers, calibrates raw ADC values from efuse data or a live fallback sample, registers with the thermal OF framework, programs hardware trip monitoring, and handles threshold interrupts.

## Important APIs, Types, and Functions

`struct airoha_thermal_priv` stores the PTP thermal MMIO base, SCU regmap, SCU ADC resource, registered thermal zone, and calibration fields (`init_temp`, slope, offset). Conversion macros `TEMP_TO_RAW()` and `RAW_TO_TEMP()` translate between millicelsius-like thermal values and ADC raw codes using slope/init/offset constants.

Sensor helpers are `airoha_get_thermal_ADC()`, `airoha_init_thermal_ADC_mode()`, `airoha_thermal_get_temp()`, `airoha_thermal_set_trips()`, `airoha_thermal_irq()`, `airoha_thermal_setup_adc_val()`, and `airoha_thermal_setup_monitor()`. Probe maps resources, obtains the `airoha,chip-scu` syscon phandle, requests the IRQ, configures monitor/ADC/calibration, registers the thermal zone, and enables high/low offset interrupts.

## Control Flow

Probe maps the thermal monitor registers, locates the chip SCU regmap and resource, requests a threaded IRQ, configures AHB monitor access to the ADC output register, switches the SCU thermal ADC mux to diode1, waits for ADC enable, derives calibration from efuse fields or fallback raw reading, registers an OF thermal zone, then enables high/low interrupts. `get_temp` reads six ADC samples, drops min and max, averages the remaining four, and converts to temperature. `set_trips` clamps requested high/low thresholds, writes raw offset registers, and enables sensor0 monitoring. The IRQ handler reads status, maps high-offset status to `THERMAL_TRIP_VIOLATED` and low-offset status to an unspecified event, clears status, and updates the thermal zone.

## State and Persistence Behavior

Runtime state is device-managed `struct airoha_thermal_priv`, MMIO register programming, SCU mux/protect state during ADC setup, calibration values, and thermal-zone registration. No persistent state is written; efuse calibration is read-only hardware state.

## Dependencies and Integration Points

The driver depends on platform devices, OF resources/phandles, MFD syscon/regmap, MMIO accessors, threaded IRQs, thermal OF zone registration, and EN7581 register layout. It is selected by `CONFIG_AIROHA_THERMAL` in Kconfig and built from the thermal Makefile.

## Risks and Edge Cases

`airoha_thermal_set_trips()` appears to clamp `low` using `high` as the input argument, which likely corrupts low-threshold programming when only a low trip is supplied. `airoha_thermal_setup_monitor()` writes `FIELD_PREP(EN7581_FILT_INTERVAL, 379)` for the sensor interval instead of using `EN7581_SEN_INTERVAL`, so the intended 379 sample interval may not be programmed. Several comments document hardware bit swaps relative to documentation; regressions can be introduced by "correcting" them without hardware validation. `of_address_to_resource()` return value is ignored, so an invalid SCU resource can be used for ADC valid address programming. Missing efuse calibration falls back to current ADC reading, making absolute temperature dependent on boot conditions.

## Test Signals

Tests should cover probe with missing/malformed `airoha,chip-scu`, IRQ request failure, efuse present and absent paths, raw/temp conversion boundaries, six-sample averaging, high and low trip programming separately and together, IRQ status high/low/noise cases, register programming for monitor intervals and ADC addresses, suspend/resume expectations if added later, and hardware validation for documented swapped bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/airoha_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/amlogic_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/amlogic_thermal.c

## Purpose

`amlogic_thermal.c` implements the Amlogic G12/A1 thermal sensor driver. It maps the TSENSOR register block through regmap, reads calibration trim data from AO secure syscon, enables the sensor clock and analog/filter bits, converts hardware temperature codes to millicelsius, registers an OF thermal zone, and supports suspend/resume.

## Important APIs, Types, and Functions

`struct amlogic_thermal_soc_calib_data` stores calibration constants `A`, `B`, `m`, and `n`. `struct amlogic_thermal_data` stores the efuse offset, calibration parameter pointer, and regmap config. `struct amlogic_thermal` stores device, data, TSENSOR regmap, AO secure regmap, clock, thermal zone, and trim info.

Core functions are `amlogic_thermal_code_to_millicelsius()`, `amlogic_thermal_initialize()`, `amlogic_thermal_enable()`, `amlogic_thermal_disable()`, `amlogic_thermal_get_temp()`, `amlogic_thermal_probe()`, `amlogic_thermal_remove()`, `amlogic_thermal_suspend()`, and `amlogic_thermal_resume()`. OF match data covers `amlogic,g12a-ddr-thermal`, `amlogic,g12a-cpu-thermal`, and `amlogic,a1-cpu-thermal`.

## Control Flow

Probe allocates state, obtains match data, maps the MMIO resource, initializes a regmap, gets the sensor clock, looks up the `amlogic,ao-secure` syscon, registers a device-tree thermal zone, exposes hwmon sysfs, reads trim info and validates calibration version bits, then enables the clock and sensor config bits. Temperature reads pull `TSENSOR_STAT0`, mask the 16-bit code, and run the documented fixed-point formula with calibration constants and signed trim data. Remove and suspend disable sensor bits and clock; resume reenables them.

## State and Persistence Behavior

State is runtime-only except for read-only efuse trim data in secure AO registers. The driver stores trim info, regmap pointers, clock state, and thermal-zone registration in devm-managed memory. Hardware sensor enable state changes across probe, remove, suspend, and resume.

## Dependencies and Integration Points

The driver depends on platform/OF matching, regmap MMIO, syscon regmap lookup, clocks, thermal OF zone registration, thermal hwmon integration, and Amlogic TSENSOR/AO secure register layout. It is selected by `CONFIG_AMLOGIC_THERMAL` and built by the thermal Makefile.

## Risks and Edge Cases

`of_device_get_match_data()` is not checked before dereferencing, so a bad match table state would crash probe. `regmap_read()` return values are ignored in initialization and temperature reads, so bus/register errors can become stale or bogus temperatures. Calibration validation rejects unsupported trim version bits, which is safer than guessing but can disable thermal reporting on unrecognized SoCs. Signed trim calculation uses bitwise complement plus one on the masked value; it should be validated against the efuse format. The driver does not implement interrupt trips or `set_trips`; thermal polling/governor behavior depends on thermal core configuration.

## Test Signals

Tests should cover all OF compatibles and efuse offsets, missing clock/syscon/MMIO resources, calibration valid and invalid trim versions, positive and negative trim values, conversion formula regression against datasheet examples, temperature read error handling expectations, hwmon registration, suspend/resume clock and bit programming, and removal after failed partial probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/amlogic_thermal.c -->
