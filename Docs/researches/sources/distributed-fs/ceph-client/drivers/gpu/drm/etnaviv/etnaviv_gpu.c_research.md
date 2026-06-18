## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.c

### Purpose
`etnaviv_gpu.c` is the main Vivante GPU device implementation for Etnaviv. It handles hardware identification, reset and initialization, command processor startup, fences, event slots, IRQ handling, runtime PM, thermal throttling, scheduler binding, debugfs state, hang recovery, and platform component registration.

### Important APIs, Types, And Functions
Public entry points include `etnaviv_gpu_get_param()`, `etnaviv_gpu_init()`, `etnaviv_gpu_debugfs()`, `etnaviv_gpu_submit()`, `etnaviv_gpu_recover_hang()`, `etnaviv_gpu_wait_fence_interruptible()`, `etnaviv_gpu_wait_obj_inactive()`, `etnaviv_gpu_wait_idle()`, and `etnaviv_gpu_start_fe()`. Internal machinery covers `etnaviv_hw_identify()`, `etnaviv_hw_specs()`, `etnaviv_hw_reset()`, `etnaviv_gpu_hw_init()`, event allocation/free, custom `dma_fence_ops`, sync-point perfmon workers, `irq_handler()`, runtime PM callbacks, and component bind/unbind.

### Control Flow
Probe maps registers, acquires reset, IRQs, and clocks, enables runtime PM, and registers as a component. Bind creates the scheduler, workqueue, fence context, and user-fence xarray. Initialization powers the device, deasserts reset, reads or overrides chip identity, selects security mode, resets hardware, initializes the global MMU, allocates the idle-loop command buffer, configures the linear window, initializes event completions, and programs hardware. Submit allocates one or three events, allocates a fence under `gpu->lock`, starts the FE idle loop when needed, queues PMR sync points and the user command buffer, and returns the fence.

### State, Persistence, And Dependencies
Persistent driver state lives in `struct etnaviv_gpu`: identity fields, GPU state enum, command buffer, event bitmap, fence counters, xarray user fence registry, current MMU context, hangcheck markers, clocks, reset, runtime-PM state, thermal frequency scale, and workqueue. Hardware state is register programming in the HI, FE, MMU, PM, and MC blocks. Dependencies include platform/component APIs, DRM scheduler and fences, Etnaviv MMU/cmdbuf/scheduler/perfmon/dump helpers, generated register headers, runtime PM, reset, clocks, and optional thermal cooling.

### Integration Points
The file connects submit-side scheduler jobs to hardware through `etnaviv_buffer_queue()`, signals fences from IRQ event bits, calls `drm_sched_fault()` on MMU exceptions, and cooperates with `etnaviv_sched.c` for hang recovery. Userspace observes it through get-param ioctls, fence waits, debugfs, and sync fd completion.

### Risks
Reset and clock/power sequencing is hardware-sensitive. Event allocation holds runtime-PM references per event and must free them on every IRQ or error path. MMU faults transition to `ETNA_GPU_STATE_FAULT` and rely on scheduler recovery. FE sync-point workers restart the FE after register sampling, so worker/IRQ ordering is delicate. Fence sequence accounting must handle out-of-order event bits. Identity quirks and HWDB overrides can change exposed UAPI capabilities.

### Test Signals
High-value tests are probe/remove with missing optional clocks, runtime suspend refusal while scheduler credits exist, get-param identity coverage, fence wait timeout and poll behavior, event exhaustion, PMR pre/post sampling, MMU fault interrupt handling, hangcheck forward-progress cases, reset recovery with active events, debugfs reads under runtime PM, and thermal cooling frequency-scale changes.
