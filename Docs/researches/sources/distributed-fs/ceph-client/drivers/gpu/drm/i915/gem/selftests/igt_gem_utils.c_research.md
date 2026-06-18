# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/igt_gem_utils.c

## Purpose
Provides reusable GEM selftest helpers for request allocation and simple GPU dword-fill batches.

## APIs And Control Flow
Exports `igt_request_alloc()`, `igt_emit_store_dw()`, and `igt_gpu_fill_dw()`. Request allocation resolves the engine-specific `intel_context` before creating a request. Batch emission allocates an internal object, writes generation-specific `MI_STORE_DWORD_IMM` commands for page-spaced dwords, flushes and pins the batch VMA. GPU fill creates a request, marks batch and destination active, emits `emit_bb_start()`, submits, and releases the batch.

## State, Dependencies, Integration, Risks, And Tests
State is transient in batch objects, VMAs, requests, and active tracking. Dependencies include GEM context lookup, request creation, GPU command encodings, chipset flushes, VMA pinning, and engine batch-start ops. Used by many GEM selftests for controlled GPU writes. Risks include generation-specific address encoding and missing active tracking. Signals appear in callers as request/batch failures or readback mismatches.
