# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_drv.h

## Purpose
`vc4_drv.h` is the shared internal contract for the VC4 DRM driver. It defines device, BO, fence, V3D, HVS, plane, encoder, CRTC, execution, shader-validation, perfmon, and platform data structures; generation constants; register access helpers; wait helpers; and cross-file function prototypes for the VC4 display and render subsystems.

## Important APIs, Types, And Functions
- `enum vc4_gen` differentiates GEN_4, GEN_5, GEN_6_C, and GEN_6_D behavior.
- `struct vc4_dev` embeds `struct drm_device` and carries global state: generation, component pointers, BO cache/labels, purgeable pool, dma-fence context, GEM job lists/seqnos/locks/waitqueue, perfmon state, binner BO allocation, underrun counter, power lock/refcount, hangcheck timer/work, and KMS private objects.
- `struct vc4_bo` extends `drm_gem_dma_object` with tiling, cache/list hooks, shader validation info, labels, active usecount, madvise state, and a madv lock.
- `struct vc4_fence` embeds `dma_fence` and stores the DRM device and VC4 seqno used by fence signaling.
- `struct vc4_hvs`, `struct vc4_hvs_state`, and `struct vc4_plane_state` model HVS registers, display-list/LBM/UPM allocators, FIFO state, plane display-list state, scaling, bandwidth/load, and prefetching.
- `enum vc4_encoder_type`, `struct vc4_encoder`, `struct vc4_crtc_data`, `struct vc4_pv_data`, `struct vc4_crtc`, and `struct vc4_crtc_state` define display topology, encoder hooks, PixelValve capabilities, CRTC event/vblank/display-list state, and atomic channel/margin/load state.
- MMIO macros `V3D_READ/WRITE`, `HVS_READ/WRITE`, `HVS_READ6/WRITE6`, and `VC4_REG32` standardize hardware access and KUnit guard behavior.
- `struct vc4_exec_info` captures one userspace GPU submission: BO array, dma fence, seqno, command-list addresses, shader/uniform pointers, validator flags, tile/binning metadata, unref list, render write BOs, perfmon, and binner BO reference state.
- Inline helpers `vc4_first_bin_job()`, `vc4_first_render_job()`, and `vc4_last_render_job()` are list accessors used by GEM scheduling and hangcheck.
- `__wait_for`, `_wait_for`, and `wait_for` provide a sleep-and-retry timeout pattern that rechecks the condition after timeout.
- The prototype section publishes APIs across BO, CRTC, debugfs, driver, DPI, DSI, fence, GEM, HDMI, VEC, TXP, IRQ, HVS, KMS, plane, V3D, validation, shader validation, and perfmon modules.

## Control Flow
This header does not execute control flow directly, but it shapes the call graph. The top-level driver allocates `struct vc4_dev`; component drivers populate its HVS/V3D/display members; CRTC/encoder/HVS/plane code uses the display structs and callbacks during atomic commits; GEM ioctls allocate and queue `struct vc4_exec_info`; IRQ and workqueue handlers update seqnos and job lists; BO and madvise code track active use and purgeability; perfmon APIs attach counters to job submissions.

The macros also shape hardware access: callers must have an in-scope `vc4` or `hvs` variable for V3D/HVS macros, and KUnit tests are protected from accidental live register IO.

## State And Persistence Behavior
Nearly all persistent driver state is declared here. `vc4_dev` persists for the DRM device lifetime. BO objects persist across GEM handles and dma-buf sharing. `vc4_exec_info` persists from submit ioctl until job completion cleanup. `vc4_crtc_state`, `vc4_hvs_state`, and `vc4_plane_state` are tied to atomic state lifetimes. Perfmon objects are refcounted per userspace-managed object lifetime. Purgeable BO state transitions are stored in each BO and global purgeable lists.

## Dependencies And Integration Points
The header depends on Linux debugfs, delay, OF, refcount, uaccess, KUnit test-bug hooks, and DRM atomic/device/encoder/fourcc/GEM DMA/managed/MM/modeset APIs. It integrates all VC4 source files by exposing platform driver symbols, internal helper APIs, and shared data contracts. It also includes the public VC4 UAPI definitions that define ioctl payloads.

## Risks And Edge Cases
- Changes to shared structs can affect many files and the exact locking/lifetime assumptions around job lists, BO usecounts, HVS MM nodes, and CRTC IRQ state.
- `enum vc4_kernel_bo_type` warns that `vc4_bo.c` label names must be kept in sync.
- Register macros assume local variable names (`vc4`, `hvs`) and will fail to compile or access the wrong context if copied carelessly.
- `wait_for` sleeps and calls `might_sleep()`, so it is not valid in atomic contexts.
- `struct vc4_exec_info` has many validator-populated fields; incomplete initialization can become a security issue because userspace command lists are being validated and relocated.
- The header contains ABI-facing relationships but should not expose unstable internal changes to userspace beyond the included UAPI.

## Test Signals
- Build coverage is the first signal: almost every VC4 file includes this header, so type/prototype mismatches surface broadly.
- KUnit tests should verify that helper constructors can inject CRTC callbacks and that MMIO macros catch accidental hardware access.
- Lockdep and KASAN are useful for shared lifetime changes around job lists, BO purgeability, CRTC state destruction, and HVS MM allocations.
- ABI tests should focus on ioctl structs included through `uapi/drm/vc4_drm.h`, while internal-structure changes need render submission, KMS atomic, hot-unplug, suspend/resume, and debugfs smoke tests.
