<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.c

Purpose: implements intel ring-buffer allocation, pinning, mapping, space accounting, reset/unpin/free, and command reservation for i915 engine requests.

Important APIs and functions: `intel_ring_update_space()`, `__intel_ring_pin()`, `intel_ring_pin()`, `intel_ring_reset()`, `intel_ring_unpin()`, `intel_engine_create_ring()`, `intel_ring_free()`, and `intel_ring_begin()`. Internal helpers include `create_ring_vma()` and `wait_for_space()`.

Control flow: ring creation allocates an `intel_ring`, validates power-of-two size and `RING_CTL_SIZE`, sets wrap/effective size, creates a GGTT VMA backed by LMEM, stolen memory, or internal shmem fallback, marks it read-only on GPUs with GGTT read-only support, and initializes space. Pinning increments `pin_count`; the first pin GGTT-pins the VMA with an offset bias to avoid offset-zero wrap hangs, maps it through iomap on non-LLC mappable objects or coherent GEM map otherwise, marks it unshrinkable, resets pointers, and stores `vaddr`. `intel_ring_begin()` reserves qword-aligned command space plus request finalization space, decides whether wrapping is needed, waits for earlier requests if the ring lacks space, fills wrap tail with MI_NOOPs, poisons debug memory, advances `emit`, and returns a CPU pointer for command emission.

State and persistence: `intel_ring` stores kref, VMA, size/effective size, wrap shift, head/tail/emit offsets, free space, pin count, and mapped CPU address. VMA backing persists until ring kref free; mapping and unshrinkable status persist while pinned.

Dependencies and integration points: depends on GEM object creation in LMEM/stolen/internal memory, GGTT pinning, VMA iomap/fenceability, coherent map type selection, i915 requests/timelines for space waits, engine registers/commands, and request reserved-space conventions. Used by LRC contexts, migration command emission, renderstate emission, and general engine request construction.

Risks: ring wrap logic is safety-critical; `need_wrap` writes MI_NOOPs to avoid executing stale commands. Packets must be qword aligned. `reserved_space` is assumed sufficient for request finalization and cannot fail late. Waiting for space relies on timeline request ordering and target postfix offsets. Non-LLC iomap versus GEM map selection must match cache coherency. Read-only ring buffers protect against stray GPU writes only where GGTT supports it.

Test signals: `selftest_ring.c`, request submission stress with small rings, wraparound at end-of-ring, interruptible wait behavior, timeline retire freeing space, non-LLC/stolen/iomap platforms, LMEM ring allocation, reset pointer rebuild, and debug poison checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ring.c -->
