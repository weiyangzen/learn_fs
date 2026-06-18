<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ib.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ib.c

## Purpose

`radeon_ib.c` manages indirect buffers, the GPU-visible command buffers that userspace command streams are copied into and scheduled through Radeon rings. It allocates IB memory from the ring temporary suballocator, records synchronization and VM metadata, emits IB execution packets and fences, initializes/destroys the shared IB pool, tests rings, and exposes debugfs state for the suballocator.

## Important APIs, Types, and Functions

- `radeon_ib_get()`: allocates a `drm_suballoc` from `rdev->ring_tmp_bo`, initializes `ib->sync`, sets CPU/GPU addresses, associates ring and VM, and handles virtual-address placement at `RADEON_VA_IB_OFFSET`.
- `radeon_ib_free()`: releases sync state, frees the suballocated IB after its fence, and drops the fence reference.
- `radeon_ib_schedule()`: validates length/ring readiness, locks ring space, grabs a VM ID when needed, synchronizes against other rings, emits VM flushes, executes optional SI constant-engine IB before the main IB, emits a fence, attaches it to VM state, and commits the ring.
- `radeon_ib_pool_init()` / `radeon_ib_pool_fini()`: create/start and suspend/finalize the suballocator backing IBs, selecting write-combined GTT only for newer families where appropriate.
- `radeon_ib_ring_tests()`: submits per-ring test IBs, disables failed non-GFX rings, and fails hard when the primary GFX ring IB test fails.
- Debugfs helpers `radeon_debugfs_sa_info_show()` and `radeon_debugfs_sa_init()` expose `radeon_sa_bo_dump_debug_info()` as `radeon_sa_info`.

## Control Flow

IB use begins after `radeon_ib_pool_init()` initializes `rdev->ring_tmp_bo` in GTT and marks `ib_pool_ready`. A caller then obtains an IB with `radeon_ib_get()`, fills `ib->ptr`, sets `length_dw`, and passes it to `radeon_ib_schedule()`.

Scheduling first rejects empty IBs or unready rings. It reserves enough ring space for synchronization and fence packets, optionally obtains a VM ID and folds its fence into the IB sync object, waits/emits synchronization against other rings, and flushes VM page-table state if the IB uses a VM. SI constant IBs are executed first and inherit the main fence. The main IB execution packet is written through `radeon_ring_ib_execute()`, `radeon_fence_emit()` creates completion tracking, VM state is fenced, and `radeon_ring_unlock_commit()` publishes the ring writes with optional HDP cache flush.

Ring self-tests iterate all `RADEON_NUM_RINGS`; failures force fence completion and mark that ring not ready. Failure on the graphics ring disables acceleration and returns the error because the driver cannot operate normally without it.

## State and Persistence Behavior

The IB pool is persistent device state in `rdev->ring_tmp_bo` and the `ib_pool_ready` flag. Individual `struct radeon_ib` objects are caller-owned but contain suballocator state, ring index, CPU pointer, GPU address, VM pointer, sync state, constant-IB flag, and fence pointer. Fences persist past scheduling until all users, suballocations, and sync objects release them. VM ID and VM fence updates persist in the per-file or per-VM GPU address space.

## Dependencies and Integration Points

This file depends on Radeon suballocation (`radeon_sa_bo_*`), ring management, fences, sync objects, VM management, debugfs, and per-ASIC `radeon_ring_ib_execute()`. It is used by command submission, ring tests during device bring-up, UVD/VCE/DMA/GFX engines, and KMS open paths that map the IB pool into per-client VMs.

## Risks and Edge Cases

- `radeon_ib_schedule()` assumes `ib->length_dw` is correctly set by command submission validation before scheduling.
- VM ID acquisition and ring sync errors must undo ring locks; this path uses `radeon_ring_unlock_undo()` before returning, and future changes must preserve that cleanup.
- Constant IBs share the main fence but free their sync object with no fence before execution completes, so ownership rules are subtle.
- Pool initialization returns early if already ready but does not validate size/domain compatibility after family changes or resume transitions.
- Ring test failure clears `needs_reset`, marks rings not ready, and may leave partial acceleration available; user-visible capability reporting must align with this.

## Test Signals

Test signals include successful IB ring tests on all enabled rings, forced ring-test failures disabling only affected non-GFX rings, command submission with and without VM, SI constant/main IB ordering, cross-ring synchronization tests, fence signaling under reset, suballocator exhaustion and delayed free behavior, debugfs `radeon_sa_info` readability, and suspend/resume pool teardown/restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ib.c -->
