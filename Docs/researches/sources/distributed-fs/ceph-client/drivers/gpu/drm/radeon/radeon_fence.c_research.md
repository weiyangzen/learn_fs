# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_fence.c

## Purpose

`radeon_fence.c` implements Radeon GPU/CPU synchronization through per-ring sequence fences integrated with Linux `dma_fence`. It emits fences into GPU rings, reads completion from writeback memory or scratch registers, wakes waiters, detects lockups, supports inter-ring sync bookkeeping, exposes debugfs diagnostics, and provides DMA-fence operations for generic reservation-object users.

## Important APIs, Types, and Functions

- `radeon_fence_emit()` allocates a `struct radeon_fence`, assigns a per-ring sequence, initializes `dma_fence`, emits the GPU fence packet, traces it, and schedules lockup checking.
- `radeon_fence_process()` and `radeon_fence_activity()` update `last_seq` from hardware and wake waiters when progress occurs.
- `radeon_fence_wait_timeout()`, `radeon_fence_wait()`, `radeon_fence_wait_next()`, and `radeon_fence_wait_empty()` wait for specific or aggregate ring progress and return `-EDEADLK` when reset is needed.
- `radeon_fence_enable_signaling()` registers waitqueue callbacks and enables software IRQs or delayed IRQ enablement.
- `radeon_fence_driver_start_ring()`, `radeon_fence_driver_init()`, `radeon_fence_driver_fini()`, and `radeon_fence_driver_force_completion()` manage per-ring fence backend state.
- `radeon_fence_need_sync()` and `radeon_fence_note_sync()` track cross-ring synchronization points.
- `radeon_fence_ops` supplies DMA-fence driver/timeline names, signaling, wait, and status callbacks.

## Control Flow

Fence emission assumes ring emission serialization by the caller. Completion can be discovered by IRQ-driven `radeon_fence_process()`, explicit polling in status checks, wait paths, or delayed lockup work. `radeon_fence_activity()` reads the current hardware sequence, merges 32-bit hardware values into 64-bit software sequence space, atomically advances `last_seq`, reschedules checks if uncompleted fences remain, and wakes the shared fence queue. If delayed work observes no progress and `radeon_ring_is_lockup()` reports a hang, it sets `rdev->needs_reset` and wakes waiters. Waiters then return `-EDEADLK`, letting higher layers trigger `radeon_gpu_reset()`.

## State and Persistence Behavior

Each ring has `rdev->fence_drv[ring]` state: scratch register, CPU/GPU writeback addresses, per-source-ring `sync_seq[]`, atomic `last_seq`, initialized flag, delayed IRQ flag, and lockup work. `rdev->fence_queue` is the shared waitqueue. Fence objects persist through DMA-fence reference counting and carry ring, sequence, owning device, and VM-update marker state.

## Dependencies and Integration Points

The file depends on Radeon ring emit helpers, IRQ enable/disable, writeback memory initialized in `radeon_device.c`, scratch registers, UVD firmware memory for UVD fences, DMA-fence, waitqueues, debugfs, tracepoints, and reset handling. GEM, TTM reservations, IB submission, page flips, suspend, and reset all consume fence APIs.

## Risks and Edge Cases

- Hardware exposes 32-bit fence values while software uses 64-bit sequences; wrap reconstruction must remain correct.
- Lockup work uses try-lock behavior around reset; delayed IRQ enablement is subtle.
- `radeon_fence_driver_force_completion()` writes the last emitted sequence to unblock waiters even if work did not really complete, appropriate only for reset/unload failure paths.
- Wait paths can return `-EDEADLK`, requiring callers to reset and retry where safe.
- Scratch register allocation/free is external-resource-sensitive.

## Test Signals

Test fence emission/completion on every active ring, writeback enabled/disabled, scratch fallback, sequence wrap, interrupt and polling completion, timeout and signal interruption, forced GPU reset via debugfs, suspend drain, unload with stuck fences, cross-ring sync bookkeeping, and DMA-fence reservation waits from GEM/page-flip paths.
