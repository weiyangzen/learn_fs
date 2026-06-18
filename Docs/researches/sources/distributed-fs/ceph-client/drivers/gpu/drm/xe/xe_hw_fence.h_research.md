# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.h

Purpose: public API for Xe hardware fence module, IRQ list handling, fence contexts, allocation/free, and initialization.

Important APIs/constants: `XE_FENCE_INITIAL_SEQNO`, module init/exit, IRQ init/finish/run, context init/finish, `xe_hw_fence_alloc`, `xe_hw_fence_free`, and `xe_hw_fence_init`.

Control flow/state: module init must precede fence allocation; engine/GT setup initializes IRQ and contexts; jobs allocate/init fences; engine IRQs run pending fence signaling.

Dependencies/integration: includes `xe_hw_fence_types.h` and exposes `struct dma_fence`/`iosys_map` users through that header.

Risks/test signals: callers must not free initialized fences with `xe_hw_fence_free`; initialized fences are dma-fence refcounted. Test module unload after pending fences and context seqno progression.
