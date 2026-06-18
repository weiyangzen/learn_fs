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
