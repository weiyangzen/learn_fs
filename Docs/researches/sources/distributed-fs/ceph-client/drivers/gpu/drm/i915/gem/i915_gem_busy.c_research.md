## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_busy.c

### Purpose

`i915_gem_busy.c` implements the `DRM_IOCTL_I915_GEM_BUSY` uAPI. It reports whether a GEM object has active native i915 read or write fences and encodes the active engine classes in the legacy busy bitfield.

### Important APIs, types, and functions

The exported function is `i915_gem_busy_ioctl()`. Helpers include `__busy_read_flag()`, `__busy_write_id()`, `__busy_set_if_active()`, `busy_check_reader()`, and `busy_check_writer()`. The code understands both single i915 fences and `dma_fence_array` composite fences from parallel submission.

### Control flow

The ioctl looks up the GEM object by handle under RCU, iterates the reservation object with `dma_resv_iter` for read usage, resets `args->busy` if the iterator restarts, and translates write fences to both read and write busy bits while translating read fences to read bits. Native i915 fences are checked against current hardware completion via `i915_request_completed()`. Non-i915 fences are ignored for busy reporting.

### State and persistence behavior

No persistent state is modified. The ioctl samples reservation fences and writes the result to the caller-provided busy field. Because iteration is lockless/restartable, it may observe a moving view of object activity but tries to maintain uABI forward-progress behavior by querying hardware status.

### Dependencies

It depends on DMA fence/reservation APIs, `intel_engine` for engine class IDs, i915 request/fence helpers, and GEM object lookup helpers.

### Integration points

The ioctl is registered in `i915_driver.c` with render-node access. It complements wait/set-domain ioctls but intentionally trades complete foreign-fence visibility for native engine-class detail.

### Risks

Foreign DMA fences are ignored, so the ioctl can report idle while another driver still owns unresolved work. Composite fence handling returns zero if a child is not an i915 composite request, which can under-report mixed fences. Engine class IDs must fit the legacy 16-bit read mask.

### Test signals

igt busy ioctl tests, parallel submission tests, read/write fence reservation tests, lockless lookup races with handle close, and comparisons against wait ioctl behavior for foreign fences.
