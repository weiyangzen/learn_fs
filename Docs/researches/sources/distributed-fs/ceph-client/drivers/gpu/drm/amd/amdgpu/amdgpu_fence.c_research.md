# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c

## Purpose
`amdgpu_fence.c` implements AMDGPU ring fence tracking, signaling, fallback polling, interrupt enable/disable, cleanup, debugfs reporting, and queue-reset reemit support. It bridges GPU-written fence memory with Linux `dma_fence` objects used by schedulers, BO reservations, VM updates, and userspace sync.

## Important APIs, types, and functions
Key fence APIs include `amdgpu_fence_emit()`, `amdgpu_fence_emit_polling()`, `amdgpu_fence_process()`, `amdgpu_fence_wait_empty()`, `amdgpu_fence_wait_polling()`, `amdgpu_fence_count_emitted()`, `amdgpu_fence_last_unsignaled_time_us()`, `amdgpu_fence_update_start_timestamp()`, `amdgpu_fence_driver_init_ring()`, `amdgpu_fence_driver_start_ring()`, `amdgpu_fence_driver_hw_init()`, `amdgpu_fence_driver_hw_fini()`, `amdgpu_fence_driver_sw_fini()`, `amdgpu_fence_driver_set_error()`, and `amdgpu_fence_driver_force_completion()`. Queue reset helpers are `amdgpu_ring_backup_unprocessed_commands()` and `amdgpu_ring_set_fence_errors_and_reemit()`.

## Control flow
Ring initialization allocates a power-of-two fence slot array sized to twice `num_hw_submission`, initializes locks and fallback timer, and later `amdgpu_fence_driver_start_ring()` points the fence driver at the ring's fence memory or UVD firmware-adjacent memory. Emitting a fence increments `sync_seq`, initializes a `dma_fence`, writes a hardware fence packet, takes a runtime-PM reference, waits for an old fence in the same wrapped slot if necessary, stamps start time, and publishes the fence in the slot under RCU. Interrupt handlers or fallback timers call `amdgpu_fence_process()`, which reads the GPU fence value, updates `last_seq`, signals all newly completed fences, drops references, and releases runtime-PM usage.

## State and persistence behavior
Per-ring state is in `ring->fence_drv`: CPU/GPU fence addresses, last and emitted sequence numbers, fence array, fallback timer, spinlock, interrupt source/type, and initialization flag. Fence objects carry ring pointer, start timestamp, IB write-pointer metadata, backup indices, and dma-fence state. No state is durable across driver unload or GPU reset; recovery paths can mark pending fences with errors or force completion.

## Dependencies and integration points
The file depends on dma-fence, DRM scheduler teardown, runtime PM, AMDGPU ring emission, IRQ get/put, reset domains, UVD firmware layout, debugfs, and reset recovery. BO reservations, VM updates, command submission, and scheduler entities consume the produced fences.

## Risks and edge cases
Fence sequence wrapping requires waiting for old slot occupants before reuse. Missing interrupts rely on the fallback timer. Runtime-PM gets in emit must be balanced when fences signal or are forced. Hardware teardown cannot wait forever for unavailable GPU signaling and must set errors. Queue reset reemit must preserve innocent contexts while marking the guilty fence `-ETIME` and other fences from the same context `-ECANCELED`. S0ix interrupt restore skips GFX power-domain rings, so classification must be correct.

## Test signals
Signals include fence signal latency, fallback timer warnings, runtime-PM reference balance, fence wrap stress, ring drain on suspend/remove, forced completion after unplug/reset, debugfs fence counters, manual `amdgpu_gpu_recover`, polling fences, queue reset with guilty context cancellation and innocent command reemit, and scheduler shutdown without leaked fences.
