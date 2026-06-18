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
