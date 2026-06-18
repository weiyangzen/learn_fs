# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_irq.c

## Purpose
`vmwgfx_irq.c` installs and handles SVGA device interrupts. It acknowledges hardware status bits, wakes FIFO/fence waiters, defers fence and command-buffer work to a threaded IRQ handler, provides fallback wait logic when interrupts or fences are unavailable, and manages IRQ mask waiter reference counts.

## Important APIs, Types, and Functions
- `vmw_irq_handler()` is the fast hardirq handler that reads/acks status, wakes FIFO waiters, and schedules threaded fence/cmdbuf work.
- `vmw_thread_fn()` runs deferred fence updates and command-buffer IRQ processing.
- `vmw_seqno_passed()` checks fence progress using cached seqno, fresh fence update, FIFO-idle fallback, and stale-seqno detection.
- `vmw_fallback_wait()` implements a wait loop on `fence_queue` with timeout, optional FIFO-idle semantics, interruptibility, and low-CPU lazy scheduling.
- `vmw_generic_waiter_add/remove()`, `vmw_seqno_waiter_add/remove()`, and `vmw_goal_waiter_add/remove()` update `irq_mask` and hardware `SVGA_REG_IRQMASK`.
- `vmw_irq_install()` and `vmw_irq_uninstall()` allocate PCI IRQ vectors, request/free threaded IRQs, and clear device status/masks.

## Control Flow
Install allocates between one and `VMWGFX_MAX_NUM_IRQS` vectors, pre-clears pending status, requests each threaded IRQ, and records the number installed. The hardirq reads device status and masks it with the current software IRQ mask. FIFO-progress bits wake the FIFO queue immediately. Fence-goal/any-fence and command-buffer/error bits set pending thread bits and return `IRQ_WAKE_THREAD` if newly scheduled. The thread clears pending bits, updates fences and wakes `fence_queue`, or calls into the command-buffer manager. Uninstall disables the hardware mask, clears status, frees installed IRQs, and releases PCI vectors.

## State and Persistence Behavior
Runtime state includes `dev_priv->irq_mask`, waiter counters, pending thread bits, IRQ vector array/count, `last_read_seqno`, `marker_seq`, and wait queues. No disk persistence exists. IRQ mask bits remain programmed in the virtual hardware until changed or uninstalled.

## Dependencies and Integration Points
This file integrates with `vmwgfx_fence.c` for fence updates, `vmw_cmdbuf_irqthread()` for command buffers, `vmw_cmd_send_fence()`/marker sequence users through wait helpers, PCI IRQ vector APIs, Linux wait queues, and SVGA irq status/mask registers.

## Risks
Interrupt race handling is shared with fence `enable_signaling`; waiter counts must remain balanced or interrupts stay disabled/enabled incorrectly. `vmw_fallback_wait()` reports lockups after timeout but returns success unless interrupted, so callers rely on side effects and logs. FIFO-idle waits temporarily block command submission via command-buffer idle or FIFO rwsem. Install error paths record partial vector count but rely on caller cleanup for already requested IRQs.

## Test Signals
Test IRQ install/uninstall on devices with and without `SVGA_CAP_IRQMASK`, fence interrupt wakeups, FIFO-progress wakeups, command-buffer/error threaded handling, waiter add/remove balance, fallback wait timeout/interruption, and no lost wakeups under concurrent fence creation and signaling.
