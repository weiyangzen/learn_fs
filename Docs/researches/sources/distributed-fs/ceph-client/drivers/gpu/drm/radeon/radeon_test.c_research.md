<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_test.c

## Purpose
`radeon_test.c` provides built-in driver self-tests for GPU memory copies and ring synchronization. These are runtime diagnostics rather than unit tests: they allocate BOs, submit real GPU work, wait on fences, and validate copied data or semaphore ordering.

## Important APIs, types, and functions
`radeon_test_moves` invokes `radeon_do_test_moves` for DMA and/or blit copy engines. `radeon_test_create_and_emit_fence` emits a fence on ordinary rings or uses dummy UVD/VCE create/destroy messages for media rings. `radeon_test_ring_sync`, `radeon_test_ring_sync2`, `radeon_test_sync_possible`, and `radeon_test_syncing` exercise pairwise and three-way semaphore synchronization across ready rings.

## Control flow
The move test allocates a pinned VRAM BO, then iterates 1 MiB GTT BOs across the available GTT aperture. For each GTT BO it writes pointer-pattern data, copies GTT to VRAM through DMA or blit, waits on the fence, verifies VRAM contents, rewrites VRAM with a second pattern, copies back to GTT, waits, and verifies again. Cleanup unwinds pin/reserve/ref state through labeled error paths. Sync tests create a semaphore, submit wait packets before fences, verify fences do not signal early, emit signal packets from another ring, then wait and repeat. The three-ring variant checks that one of two waiting fences signals after the first signal and both complete after the second.

## State, dependencies, and integration points
The file depends on Radeon BO allocation/pin/map, copy callbacks, fences, rings, UVD/VCE dummy messages, semaphores, and DRM logging. It mutates hardware rings and temporary BOs but persists no state after cleanup. Media rings are handled specially because simple fence packets can be unsafe for their VCPU command streams.

## Risks and test signals
These tests can consume substantial VRAM/GTT and take time proportional to aperture size. Bugs in cleanup could leak pinned BOs or fences; bugs in expected patterns can produce false copy failures. Success is reported through `DRM_INFO`; failures use `DRM_ERROR` and `pr_warn`. Valuable signals are copy correctness in both directions, fence timeout behavior, semaphore ordering, and readiness of every configured ring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_test.c -->
