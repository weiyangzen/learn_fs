<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc_reg.h

Purpose: provides register-state array indices and context-status-buffer constants for Gen8+ logical ring contexts.

Important definitions: `CTX_DESC_FORCE_RESTORE`; `CTX_CONTEXT_CONTROL`, `CTX_RING_HEAD`, `CTX_RING_TAIL`, `CTX_RING_START`, `CTX_RING_CTL`, `CTX_TIMESTAMP`, PDP/PML4 descriptor slots, and `CTX_R_PWR_CLK_STATE`; `ASSIGN_CTX_PDP()` and `ASSIGN_CTX_PML4()` macros; indirect-context default offsets for Gen8-Gen12; execlists status buffer offsets and CSB pointer masks; maximum hardware context ID values for Gen8, Gen11, Gen12, and XeHP.

Control flow: LRC initialization uses these indices to write into the context image array, and submission uses descriptor/CSB constants to force restore and parse status buffers.

State and persistence: this header defines offsets into persistent hardware-saved context images and status buffers. The macros write DMA addresses of PPGTT roots into the register-state image.

Dependencies and integration points: uses Linux types and helper functions/macros supplied by `intel_gtt.h` users, including `i915_page_dir_dma_addr()` and `px_dma()`. Consumed by `intel_lrc.c` and execlists scheduling code.

Risks: array indices include `+ 1` offsets because the context image stores `(register,value)` pairs after command words; off-by-one edits corrupt context state. Context ID maxima reserve special hardware values on Gen12/XeHP and must not be exceeded.

Test signals: LRC layout selftests, live execlists CSB parsing, context ID allocator tests, PPGTT root restore tests, and platform bring-up on each context-layout generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_lrc_reg.h -->
