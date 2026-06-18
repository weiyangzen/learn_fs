<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.h

## Purpose

`xe_preempt_fence.h` declares the preempt-fence lifecycle and list-link helpers used by VM and exec queue code.

## Important APIs

`xe_preempt_fence_create()` allocates and arms a fence in one step. `xe_preempt_fence_alloc()` creates an unarmed fence, `xe_preempt_fence_free()` frees an unarmed fence, and `xe_preempt_fence_arm()` binds it to an exec queue, context, and seqno. Inline helpers convert between `dma_fence`, `xe_preempt_fence`, and the embedded list link. `xe_fence_is_xe_preempt()` identifies this fence class.

## Control Flow and State

The header defines the intended split between unarmed fences stored on lists and armed fences owned through `dma_fence_put()`. It does not own runtime state beyond accessors to `struct xe_preempt_fence`.

## Dependencies and Integration Points

It includes `xe_preempt_fence_types.h` and is used by scheduler/VM code that tracks pending preemptions before arming.

## Risks and Test Signals

Misusing free paths can double-free or leak fences. Tests should cover link conversion, unarmed list handling, and transition to armed DMA fence ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.h -->
