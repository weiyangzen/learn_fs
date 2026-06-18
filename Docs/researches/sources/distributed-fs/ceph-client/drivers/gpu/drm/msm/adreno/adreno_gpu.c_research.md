## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.c

### Purpose
`adreno_gpu.c` is the shared implementation layer for Qualcomm Adreno GPUs in the MSM DRM driver. It handles secure zap-shader loading, IOMMU GPUVM setup, firmware lookup and BO creation, common hardware initialization, ringbuffer flushing/idling, fault capture, userspace parameter plumbing, power-level discovery, OCMEM allocation, and common debug/devcoredump formatting.

### Important APIs, Types, And Functions
The exported helpers include `adreno_zap_shader_load()`, `adreno_create_vm()`, `adreno_iommu_create_vm()`, `adreno_private_vm_size()`, `adreno_fault_handler()`, `adreno_get_param()`, `adreno_set_param()`, `adreno_request_fw()`, `adreno_load_fw()`, `adreno_fw_create_bo()`, `adreno_hw_init()`, `adreno_flush()`, `adreno_idle()`, `adreno_gpu_state_get()`, `adreno_gpu_state_put()`, `adreno_show()`, `adreno_dump_info()`, `adreno_dump()`, `adreno_wait_ring()`, OCMEM helpers, `adreno_read_speedbin()`, `adreno_gpu_init()`, and `adreno_gpu_cleanup()`. The file also defines the `address_space_size` module parameter and a process-wide `zap_available` cache.

### Control Flow
Zap shader loading first checks Qualcomm architecture support and a `zap-shader` reserved-memory child node, then chooses device-tree `firmware-name`, gpulist firmware through `adreno_request_fw()`, or fails for newer targets with no explicit signed image. It sizes and maps the reserved memory, loads the MDT image with the correct legacy or `qcom/` path, and asks SCM to authenticate/reset the PAS ID. GPUVM creation wraps `msm_iommu_gpu_new()`, obtains aperture geometry, starts at at least 16 MiB, and creates an `msm_gem_vm_create()` GPU VM. Hardware init resets ring software pointers, memptr read pointers, and bad fence values before generation-specific code continues.

### State, Persistence, And Dependencies
Persistent driver state is stored in `struct adreno_gpu` and `struct msm_gpu`: firmware pointers, `fwloc`, UBWC config references, fault completion, ringbuffer memptrs, fast OPP rate, and pm-runtime autosuspend configuration. Fault handling mutates `priv->stall_enabled` and `stall_reenable_time`, temporarily disables SMMU stall-on-fault, captures crashstate when the fault was stalled, and completes `fault_coredump_done` for concurrent GMU traffic. Dependencies include Linux firmware APIs, reserved memory, Qualcomm SCM/MDT loader, OPP/nvmem, OCMEM, MSM GEM/MMU/GPUVM helpers, pm-runtime, debugfs/devcoredump printers, and Adreno generation hooks from `adreno_gpu_funcs`.

### Integration Points
`adreno_get_param()` and `adreno_set_param()` implement DRM UAPI parameters for GPU ID, GMEM, chip ID, timestamps, priorities, fault/suspend counters, per-process VA ranges, UBWC fields, ray tracing, PRR, AQE, context command names, sysprof, and VM_BIND enablement. Firmware helpers are used by generation-specific GPU init paths before uploading microcode. Ringbuffer helpers feed command submission paths, while `adreno_show()` and dump helpers integrate with debugfs, devcoredump, hangcheck, and crash analysis tools.

### Risks
Zap firmware path selection is stateful through `fwloc` and `zap_available`; an early unsupported/failed platform path can suppress later zap attempts. `adreno_fw_create_bo()` assumes firmware blobs have a four-byte header and would underflow if handed a too-small blob. Fault handling depends on correct SMMU stall semantics and crashstate serialization. `adreno_private_vm_size()` depends on TTBR1 IAS data when available and falls back to 4 GiB otherwise. Ringbuffer free-space and idle waits are busy jiffies loops, so incorrect rptr/wptr reporting can cause stalls or false timeouts.

### Test Signals
Useful signals include probe on targets with new, legacy, and helper firmware paths; zap shader reserved-memory sizing failures; SCM unavailable and `-EOPNOTSUPP` paths; GPUVM aperture sizing with and without the 4 GiB quirk; UAPI `MSM_PARAM_*` queries including per-process VA rejection on global VM; fault injection with and without `adreno_smmu_fault_info`; ringbuffer wrap-around flush/idling; debugfs/devcoredump output containing ring, BO, VM-log, fault, and register sections; OPP fallback on old a2xx/a320 device trees; and cleanup releasing all loaded firmware.
