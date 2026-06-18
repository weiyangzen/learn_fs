<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_sseu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_sseu.c

## Purpose
`intel_context_sseu.c` reconfigures a Gen8+ context's slice/subslice/EU partitioning by updating the context RPCS register state, including active contexts that need an ordered GPU-side modification.

## Important APIs, Types, and Functions
The public API is `intel_context_reconfigure_sseu()`. Internal helpers are `gen8_emit_rpcs_config()` and `gen8_modify_rpcs()`.

## Control Flow
`intel_context_reconfigure_sseu()` locks the context pin state, compares the requested `intel_sseu` with `ce->sseu`, and if changed asks `gen8_modify_rpcs()` to update active hardware state. If the context is idle/unpinned, the new SSEU is simply stored and will be programmed on next pin. If active, a kernel request is created on the same engine, serialized with the remote context through `intel_context_prepare_remote_request()`, emits a `MI_STORE_DWORD_IMM` to the context image's `CTX_R_PWR_CLK_STATE`, and submits the request. On success, `ce->sseu` is updated.

## State and Persistence
Persistent state is `ce->sseu` and the RPCS dword in the logical render context image. Active updates temporarily pin the target context and add a request that keeps the context image/timeline alive until retirement.

## Dependencies and Integration Points
The file depends on context pinning, engine kernel request creation, ring emission, LRC state offsets, SSEU RPCS encoding, and remote request serialization. It integrates with userspace context parameter changes or internal code that needs per-context EU partitioning.

## Risks and Edge Cases
The path is Gen8+ only and asserts that with `GEM_BUG_ON()`. Updating an active context by CPU writes is not enough, so the GPU-side ordered request is required. Failure after creating the request must still submit/add the request and unpin the context. Callers rely on `pin_mutex` to keep pinned/idle state stable while deciding update mode.

## Test Signals
Tests include SSEU reconfiguration on idle and busy contexts, invalid/unsupported SSEU masks before entry, request ordering relative to work on the target context, and checking that RPCS state changes survive context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_sseu.c -->
