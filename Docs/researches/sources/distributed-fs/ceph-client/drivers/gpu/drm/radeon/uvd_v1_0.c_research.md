# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v1_0.c

## Purpose

`uvd_v1_0.c` implements first-generation Radeon UVD ring and block control. It programs UVD firmware memory layout, starts/stops the VCPU and ring buffer controller, emits fences and IB commands, performs ring/IB tests, and provides register pointer callbacks for the Radeon ring infrastructure.

## Important APIs, Types, and Functions

- Ring pointer callbacks: `uvd_v1_0_get_rptr()`, `uvd_v1_0_get_wptr()`, and `uvd_v1_0_set_wptr()` access `UVD_RBC_RB_RPTR/WPTR`.
- `uvd_v1_0_fence_emit()` writes a fence sequence and trap through `UVD_GPCOM_VCPU_*` packet registers.
- `uvd_v1_0_resume()` calls `radeon_uvd_resume()`, splits the firmware/heap/stack/session backing buffer into VCPU cache ranges, writes 40-bit address extension registers, and sets `UVD_FW_START`.
- `uvd_v1_0_init()` raises UVD clocks, starts hardware, marks the ring ready, runs ring test, programs semaphore timeouts/control, applies ASIC workarounds, and lowers clocks.
- `uvd_v1_0_start()` performs reset/stall sequencing, LMI/MPC setup, VCPU boot polling/retry, interrupt enable, ring base/size programming, and ring pointer initialization.
- `uvd_v1_0_stop()` idles RBC, stalls UMC/register bus, resets VCPU, disables VCPU clock, and unstalls buses.
- `uvd_v1_0_ring_test()` verifies ring writes by updating `UVD_CONTEXT_ID`.
- `uvd_v1_0_semaphore_emit()` returns false because V1 hardware does not support UVD semaphores.
- `uvd_v1_0_ib_execute()` emits IB base/size commands, and `uvd_v1_0_ib_test()` submits create/destroy messages and waits on a fence.

## Control Flow

Resume prepares firmware memory ranges first. Init raises clocks, calls start, enables the ring only after the VCPU responds, validates the ring, programs semaphore controls through the ring, then drops clocks. Start sequences multiple resets with delays, boots the VCPU, retries up to ten times if status bit 2 does not appear, and only then exposes the ring buffer to command submission.

IB testing raises clocks, builds a UVD create message, builds a destroy message that returns a fence, waits for completion with `RADEON_USEC_IB_TEST_TIMEOUT`, releases the fence, and drops clocks on all exits.

## State and Persistence Behavior

Persistent state includes UVD firmware BO placement in `rdev->uvd`, ring `wptr/ready`, VCPU cache register ranges, LMI address-extension registers, interrupt enable bits, and block reset/clock state. The file relies on `radeon_uvd_resume()` to populate CPU/GPU firmware buffer state before cache registers are programmed.

## Dependencies and Integration Points

- Uses Radeon ring, fence, UVD message, clock, firmware, and register helper infrastructure.
- Register definitions come from `r600d.h`; ASIC family checks choose clocks and workarounds.
- Integrates with the generic scheduler through ring pointer, fence, semaphore, IB execute, ring test, and IB test callbacks.

## Risks and Edge Cases

- `uvd_v1_0_start()` uses long fixed `mdelay()` polling/retry loops and returns `-1` instead of a specific errno after repeated VCPU failure.
- Firmware memory layout assumes the BO is large and aligned enough for firmware, heap, stack, and all sessions.
- Semaphores are disabled for V1, so synchronization paths must handle a false return and avoid relying on hardware semaphores.
- Several workarounds are ASIC-family-specific and can regress old chips if family classification changes.
- `UVD_RBC_RB_BASE` is written with `ring->gpu_addr` directly; correctness depends on register semantics matching the lower address bits for this generation.

## Test Signals

- Ring tests should observe `UVD_CONTEXT_ID` changing to `0xDEADBEEF` within `usec_timeout`.
- IB tests should complete create/destroy messages and fence wait under raised clocks.
- Resume/start tests should validate programmed cache offsets/sizes, address extensions, ring base/size, and VCPU status.
- Stop/start cycles should leave ring readiness and VCPU reset/clock state consistent across suspend/resume.
