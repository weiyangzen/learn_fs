# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/aperture_gm.c

Purpose: allocates and frees per-vGPU graphics memory aperture/hidden GM ranges and hardware fence registers from host GGTT resources.

Important APIs/types/functions: public APIs are `intel_vgpu_alloc_resource()`, `intel_vgpu_free_resource()`, `intel_vgpu_reset_resource()`, and `intel_vgpu_write_fence()`. Internal helpers include `alloc_resource()`, `free_resource()`, `alloc_gm()`, `alloc_vgpu_gm()`, `free_vgpu_gm()`, `alloc_vgpu_fence()`, `free_vgpu_fence()`, and `_clear_vgpu_fence()`.

Control flow: allocation first checks requested low GM, high GM, and fence counts against host-reserved limits and accumulated allocations, records aligned sizes, then inserts low and high GM nodes into the GGTT address manager. Fence allocation reserves host fence registers, stores pointers in the vGPU, and clears hardware fence state. Failure unwinds in reverse order. Freeing removes GGTT nodes, clears/unreserves fences under runtime PM, and decrements allocation counters.

State and persistence: modifies `vgpu->gm.low_gm_node`, `vgpu->gm.high_gm_node`, `vgpu->fence.regs`, per-vGPU size fields, and aggregate `gvt->gm`/`gvt->fence` allocation counters. Hardware fence registers are programmed through uncore writes and cleared on reset/free.

Dependencies and risks: depends on GGTT `drm_mm`, i915 fence reservation APIs, runtime PM, MMIO wakerefs, and vGPU config sizing. Risks include counter mismatches if partial allocation unwind is wrong, resource leaks when fence allocation partially fails, races around GGTT mutex ownership, and invalid fence indices. Test signals include overcommit rejection, partial allocation failure cleanup, reset clearing all owned fences, and repeated create/destroy cycles leaving host counters unchanged.
