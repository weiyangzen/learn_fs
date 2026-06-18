# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_fence.c

## Purpose
`vmwgfx_fence.c` implements vmwgfx synchronization objects on top of Linux `dma_fence`. It maps SVGA fence sequence numbers into kernel fences, exposes optional userspace TTM base-object handles, supports wait/signaled/unref/event ioctls, and coordinates interrupt waiter programming through `vmwgfx_irq.c`.

## Important APIs, Types, and Functions
- `struct vmw_fence_manager` owns the fence list, spinlock, fifo-down state, device pointer, and dma-fence context id.
- `struct vmw_user_fence` wraps a TTM base object plus `struct vmw_fence_obj` for userspace-visible fences.
- `struct vmw_event_fence_action` stores a dma-fence callback that sends a DRM event, optionally timestamped from the fence signal timestamp.
- `vmw_fence_manager_init()` and `vmw_fence_manager_takedown()` allocate and destroy the manager.
- `vmw_fence_obj_init()`, `vmw_fence_create()`, and `vmw_user_fence_create()` initialize kernel-only or userspace fences.
- `vmw_fences_update()` reads the hardware fence register, signals passed fences in list order, removes interrupt waiters, and publishes `last_read_seqno`.
- `vmw_fence_obj_wait_ioctl()`, `vmw_fence_obj_signaled_ioctl()`, `vmw_fence_obj_unref_ioctl()`, and `vmw_fence_event_ioctl()` are the DRM ABI handlers.
- `vmw_fence_fifo_down()` marks the FIFO down and drains/signals all live fences during teardown/reset.

## Control Flow
Fence creation initializes a `dma_fence` with the manager lock and appends it to the ordered fence list unless the FIFO is down. Signaling paths call `vmw_fences_update()`, which reads the current SVGA seqno and signals each list head that has passed according to wrap-aware arithmetic. `enable_signaling` programs a seqno interrupt waiter and rereads the seqno to close the race between checking the fence and enabling interrupts. Userspace wait ioctl converts microsecond timeout into a jiffies cookie for repeated waits, looks up the TTM object, waits on the dma fence, and can unref the handle on success.

## State and Persistence Behavior
The persistent runtime state is in `vmw_fence_manager::fence_list`, `fifo_down`, fence `waiter_added` bits, TTM object references, and pending DRM events. The manager holds an implicit reference while a fence remains on its list. Event callbacks own a fence reference until the callback sends or synthesizes the event. There is no disk persistence.

## Dependencies and Integration Points
This file integrates with `vmw_execbuf_fence_commands()` for fence emission, `vmwgfx_irq.c` for `vmw_seqno_waiter_add/remove()` and wakeups, TTM object-file lookup/refcounting for userspace handles, DRM event reservation/delivery, and Linux `dma_fence` callback semantics.

## Risks
The most important risks are missed interrupts around `enable_signaling`, unsignaled fence destruction with callbacks, wraparound comparisons, userspace handle type confusion, and event lifetime on already-signaled fences. FIFO-down handling deliberately forces completion after timeout, so lockup recovery can hide the original stalled command but prevents indefinite waits.

## Test Signals
Exercise fence create/wait/signaled/unref ioctls, timeout-cookie reuse, interruptible waits, event delivery with and without requested timestamps, already-signaled event callbacks, FIFO-down teardown, and sync with execbuf fence copyout. Watch for dma_fence warnings, leaked TTM base objects, and stalled `fence_queue` waiters.
