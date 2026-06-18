# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.h

## Purpose
`vmwgfx_fence.h` declares the vmwgfx fence abstraction used by execbuf, KMS, IRQ, and ioctl paths. It exposes `struct vmw_fence_obj`, manager lifecycle APIs, reference helpers, wait/signaled/create routines, FIFO up/down hooks, and userspace fence/event ioctls.

## Important APIs, Types, and Functions
- `VMW_FENCE_WAIT_TIMEOUT` is the common five-second wait used by recovery paths.
- `struct vmw_fence_obj` embeds `struct dma_fence base`, tracks whether a seqno interrupt waiter was added, links into the manager list, and stores a type-specific destroy callback.
- `vmw_fence_obj_reference()` and `vmw_fence_obj_unreference()` are thin `dma_fence_get/put` wrappers that NULL caller pointers on put.
- Declared creation paths are `vmw_fence_create()` for kernel fences and `vmw_user_fence_create()` for userspace handles.
- Declared ABI handlers cover wait, signaled, unref, fence event, and explicit event callback queueing.

## Control Flow
Consumers include the header to create fences after command submission, fence BO validation lists, expose handles to userspace, wait during cleanup, and attach DRM events. The header itself has no complex control flow, but its inline reference helpers define the ownership convention used throughout the driver.

## State and Persistence Behavior
The header defines in-memory fence state only. The `dma_fence` base owns refcount, signal state, callbacks, and timestamps; vmwgfx-specific fields connect that base object to SVGA seqno waiter management and manager list lifetime.

## Dependencies and Integration Points
It depends on Linux `dma-fence` and `dma-fence-array` headers and forward-declares DRM and vmwgfx private types. It is included by driver components that need synchronization without exposing `struct vmw_fence_manager` internals.

## Risks
Because this header exposes only an opaque manager and inline reference operations, misuse risks are mostly ownership-related: double put, forgetting to clear a handed-off pointer, or treating a `vmw_fence_obj` as signaled without calling update/wait helpers. The lack of a conventional include-guard `#define` after `#ifndef _VMWGFX_FENCE_H_` is unusual, though the file terminates with the matching `#endif`.

## Test Signals
Compile coverage should catch prototype drift against `vmwgfx_fence.c`. Runtime validation comes from execbuf/KMS fence creation, userspace fence ioctls, and teardown paths that call FIFO up/down and manager takedown.
